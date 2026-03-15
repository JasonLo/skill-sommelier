---
name: ss-search-first
description: >-
  Research-before-coding workflow. Search for existing tools, libraries, packages,
  MCP servers, and skills before writing custom code. Use when starting a new feature,
  adding a dependency, or about to write a utility that likely already exists. Triggers
  on "add X functionality", "implement Y", "build a Z" — any time custom code is about
  to be written for a common problem.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
---

# Search First

Research existing solutions before writing custom code.

## When to Use

- Starting a new feature that likely has existing solutions
- Adding a dependency or integration
- About to write a utility, helper, or abstraction
- Any time you think "this must already exist"

## When NOT to Use

- The task is clearly project-specific with no reusable solution
- You've already confirmed no existing solution fits
- Quick one-off scripts or throwaway code

---

## ⚠️ STEP 0 — THE NEED STATEMENT (THIS IS YOUR FIRST OUTPUT, ALWAYS)

**YOUR VERY FIRST OUTPUT MUST BE A NEED STATEMENT. NO EXCEPTIONS.**

Format exactly:

> **Need:** [one sentence describing the specific functionality required]

**Examples:**
- `**Need:** A Python library to parse and write CSV files with support for custom delimiters.`
- `**Need:** A rate limiter for FastAPI that limits requests per IP per route.`
- `**Need:** A JavaScript package to generate UUIDs without external dependencies.`

### VERIFICATION CHECK BEFORE YOU WRITE ANYTHING ELSE:
Ask yourself: "Is the first thing I am about to output a line starting with `**Need:**`?"
- If YES → proceed
- If NO → stop, write the Need statement first, then continue

**You MUST NOT write Phase headers, search reports, tool results, or any other text before the Need statement.**

---

## Phase 1 — Clarify Constraints (AFTER NEED STATEMENT ONLY)

After writing the Need statement, answer:
- What language/framework constraints exist?
- Are there size/dependency constraints?

---

## MANDATORY EXECUTION ORDER

You MUST follow phases 2–5 in strict order. Do NOT skip ahead. Do NOT combine phases.

---

## Phase 2 — Parallel Search (REQUIRED: AT LEAST 3 WORKING TOOL CALLS)

### CRITICAL RULE ON WHAT COUNTS AS A VALID TOOL CALL

A source counts toward the **3-source minimum** ONLY if:
- The tool call **executes and returns actual data** (even if that data is "nothing found"), OR
- The tool call **returns a meaningful error** (e.g., "command not found", "no results")

**The following do NOT count:**
- Permission/authorization errors (e.g., tool blocked by permissions)
- "Based on my knowledge" or any claim without a tool call
- Deciding a source is unavailable without attempting a tool call

**If a tool call is blocked by permissions, you MUST try an alternative tool for that same source.**
For example: if `gh` CLI is blocked, use `WebSearch` to search GitHub instead. If `pip` is blocked, use `WebFetch` to query PyPI's JSON API. If `Bash` is blocked, use `Read` or `Grep` as alternatives.

You MUST make actual tool calls for at least 3 of the 5 sources below. For each source, write the report line AFTER making the tool call:

### 2a — Check the codebase first
Use Grep to search for related function names, class names, or imports.
- If Grep is blocked, use Read on likely files.
```
Report: "Codebase search for '<term>': [found X at path:line / nothing found / tool error: <message>]"
```

### 2b — Package registries
Run the appropriate command with Bash:
```bash
# Python → pip index versions <package> OR curl https://pypi.org/pypi/<package>/json
# JavaScript/TypeScript → npm search <term>
# Go → curl https://pkg.go.dev/search?q=<term>
```
- If Bash is blocked, use WebFetch to query the registry API directly (e.g., `https://pypi.org/pypi/<package>/json`).
```
Report: "Package registry search for '<term>': [found X / nothing found / tool error: <message>]"
```

### 2c — MCP servers
Use Bash or Read to check `~/.claude/settings.json`:
```bash
cat ~/.claude/settings.json | grep -i mcp
```
- If Bash is blocked, use Read on `~/.claude/settings.json`.
```
Report: "MCP servers checked: [list relevant ones / none installed / tool error: <message>]"
```

### 2d — Existing skills
Use Glob or Bash to check for installed skills:
```bash
ls ~/.claude/skills/ 2>/dev/null || echo "no skills directory"
```
- If Bash is blocked, use Glob with pattern `~/.claude/skills/*/SKILL.md`.
```
Report: "Skills/plugins checked: [found X / none relevant / tool error: <message>]"
```

### 2e — GitHub
Use Bash with `gh` or WebSearch:
```bash
gh search repos '<keywords>' --sort=stars --limit 10
```
- If `gh` is blocked, use WebSearch with query `site:github.com <keywords>`.
```
Report: "GitHub search for '<keywords>': [found X / nothing found / tool error: <message>]"
```

### PHASE 2 COMPLETION GATE

Before proceeding to Phase 3, count your valid tool calls (excluding permission-blocked calls with no fallback attempted):

- **3 or more valid tool calls** → proceed to Phase 3
- **Fewer than 3 valid tool calls** → you MUST attempt additional sources or fallback tools before proceeding

**Exit criteria:** Report lines present for all 5 sources (2a–2e), with at least 3 backed by actual working tool calls.

---

## Phase 3 — Evaluate Candidates

Score each candidate found in Phase 2:

| Criterion | Weight | Check |
|-----------|--------|-------|
| Functionality match | High | Does it do what we need? |
| Maintenance | High | Recent commits? Active maintainers? |
| Community | Medium | Stars, downloads, issues activity? |
| Documentation | Medium | Clear docs and examples? |
| License | High | Compatible with project? |
| Dependencies | Low | Minimal transitive deps? |

If no candidates were found, state: "No candidates found. Recommending Build."

---

## Phase 4 — Decide and STOP FOR CONFIRMATION

Based on research, select exactly one decision:

| Signal | Action |
|--------|--------|
| Exact match, well-maintained, permissive license | **Adopt** — install and use directly |
| Partial match, good foundation | **Extend** — install + write thin wrapper |
| Multiple weak matches | **Compose** — combine 2-3 small packages |
| Nothing suitable found | **Build** — write custom, informed by research |

Write your decision in this format:

> **Decision:** [Adopt/Extend/Compose/Build] — [specific package(s) or approach]
> **Rationale:** [one or two sentences explaining why]
> **Alternatives considered:** [what was rejected and why]

**HARD RULE — MANDATORY STOP:** After presenting the decision, you MUST ask the user:

> "Shall I proceed with [decision]? (yes/no or suggest alternative)"

**Do NOT write any implementation code until the user explicitly confirms.** Wait for the user's response before moving to Phase 5.

**Exit criteria:** Decision presented, user has confirmed in writing.

---

## Phase 5 — Implement (ONLY AFTER USER CONFIRMATION)

Only begin this phase after the user confirms the Phase 4 decision.

Based on the decision:

- **Adopt:** Install the package, show basic usage
- **Extend:** Install + write minimal wrapper code
- **Compose:** Install multiple packages, write glue code
- **Build:** Write custom code, but reference what was found during research

Document the decision in a code comment:
```
# Chose <package> over <alternatives> because <reason>
# Searched: [sources from Phase 2]
```