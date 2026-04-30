---
name: ss-mcp-builder
description: >-
  Guide for creating high-quality MCP (Model Context Protocol) servers that
  enable LLMs to interact with external services through well-designed tools.
  Use when building MCP servers to integrate external APIs or services, whether
  in Python (FastMCP) or Node/TypeScript (MCP SDK).
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
  - WebSearch
metadata:
  source: anthropics/skills
---

# MCP Server Development Guide

Create MCP (Model Context Protocol) servers that enable LLMs to interact with
external services through well-designed tools. Quality is measured by how well
the server enables LLMs to accomplish real-world tasks.

---

## Phase 1 — Research and Planning

### 1.1 Understand the API
- Review the target service's API docs: endpoints, auth, rate limits, data models.
- Fetch the MCP spec overview: `https://modelcontextprotocol.io/specification/draft.md`
- Fetch the SDK README:
  - TypeScript: `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
  - Python: `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`

### 1.2 Choose your stack

**Recommended: TypeScript + Streamable HTTP**
- TypeScript SDK has the best compatibility across MCP clients.
- Streamable HTTP for remote servers (stateless, scales easily).
- stdio for local/CLI servers.

**Python (FastMCP)** is a good alternative for data-heavy or scientific integrations.

### 1.3 Plan your tools

Prioritize **comprehensive API coverage** over workflow shortcuts:
- List key endpoints to expose as tools.
- Use consistent naming: `<service>_<action>` (e.g., `github_create_issue`).
- Plan pagination for list endpoints.
- Plan error messages that guide the agent toward a fix.

---

## Phase 2 — Implementation

### 2.1 TypeScript project setup

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
npx tsc --init
```

`package.json` scripts:
```json
{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

### 2.2 Python (FastMCP) setup

```bash
pip install mcp fastmcp httpx
```

### 2.3 Core server pattern (TypeScript)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

server.registerTool(
  "service_list_items",
  {
    description: "List items from the service with optional filtering.",
    inputSchema: {
      query: z.string().optional().describe("Search query"),
      limit: z.number().min(1).max(100).default(20).describe("Max results"),
    },
    annotations: { readOnlyHint: true },
  },
  async ({ query, limit }) => {
    // Call the external API
    const data = await fetchFromApi(query, limit);
    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }],
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 2.4 Core server pattern (Python / FastMCP)

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("my-server")

@mcp.tool()
async def service_list_items(query: str = "", limit: int = 20) -> str:
    """List items from the service with optional filtering."""
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, params={"q": query, "limit": limit})
        r.raise_for_status()
        return r.text

if __name__ == "__main__":
    mcp.run()
```

### 2.5 Tool design checklist

For each tool:
- [ ] Clear, action-oriented name with service prefix
- [ ] Concise description (one sentence + parameter notes)
- [ ] Input schema with constraints and descriptions
- [ ] Proper annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`)
- [ ] Actionable error messages ("Not found. Try listing first with `service_list_items`.")
- [ ] Pagination for list operations (`cursor`/`page` parameter)
- [ ] Return structured JSON when output schema is defined

---

## Phase 3 — Build and Test

### TypeScript
```bash
npm run build
npx @modelcontextprotocol/inspector dist/index.js
```

### Python
```bash
python -m py_compile server.py
fastmcp dev server.py
```

### Quality review
- No duplicated code (DRY).
- Consistent error handling across all tools.
- Full type coverage (no `any` in TypeScript, no untyped params in Python).
- Tool descriptions are discoverable — would a model know when to use each one?

---

## Phase 4 — Evaluations

Create 10 evaluation Q&A pairs to verify the server enables real tasks.

**Question criteria:**
- Independent (not dependent on other questions)
- Read-only (non-destructive operations only)
- Complex (requires ≥ 3 tool calls)
- Realistic (a real user would ask this)
- Verifiable (single, stable, string-comparable answer)

**Output format** (`evals/eval.xml`):
```xml
<evaluation>
  <qa_pair>
    <question>How many open issues labeled "bug" exist in the repository?</question>
    <answer>42</answer>
  </qa_pair>
</evaluation>
```

---

## Transport Reference

| Transport | When to use |
|-----------|------------|
| stdio | Local/CLI server, single user |
| Streamable HTTP (stateless) | Remote/cloud server, multiple users |
| SSE (legacy) | Only if the client requires it |

---

## Error Message Guidelines

Bad: `"Error: 404"`
Good: `"Item 'foo' not found. Use service_list_items to see available items."`

Always include:
1. What failed.
2. Why it failed (if known).
3. What the agent should try next.
