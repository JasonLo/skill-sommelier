---
name: search-first
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

## Phase 1 — Define the Need

Before searching:

1. What functionality is needed? (one sentence)
2. What language/framework constraints exist?
3. Are there size/dependency constraints?

**Exit criteria:** Clear one-sentence description of what's needed.

## Phase 2 — Parallel Search

Search multiple sources simultaneously:

### 2a — Check the codebase first
```
Does this already exist in the repo?
Grep for related function names, class names, or imports.
```

### 2b — Package registries
```bash
# Python
pip search <term>  # or search PyPI web
# JavaScript/TypeScript
npm search <term>
# Go
go search on pkg.go.dev
```

### 2c — MCP servers
Check `~/.claude/settings.json` for installed MCP servers that might provide this functionality.

### 2d — Existing skills
Check `~/.claude/skills/` for skills that already handle this.

### 2e — GitHub
Search for well-maintained implementations:
```bash
gh search repos '<keywords>' --sort=stars --limit 10
```

**Exit criteria:** Results from at least 3 sources reviewed.

## Phase 3 — Evaluate Candidates

Score each candidate on:

| Criterion | Weight | Check |
|-----------|--------|-------|
| Functionality match | High | Does it do what we need? |
| Maintenance | High | Recent commits? Active maintainers? |
| Community | Medium | Stars, downloads, issues activity? |
| Documentation | Medium | Clear docs and examples? |
| License | High | Compatible with project? |
| Dependencies | Low | Minimal transitive deps? |

## Phase 4 — Decide

| Signal | Action |
|--------|--------|
| Exact match, well-maintained, permissive license | **Adopt** — install and use directly |
| Partial match, good foundation | **Extend** — install + write thin wrapper |
| Multiple weak matches | **Compose** — combine 2-3 small packages |
| Nothing suitable found | **Build** — write custom, informed by research |

Present the decision with rationale to the user before proceeding.

**Exit criteria:** Clear adopt/extend/compose/build decision, confirmed by user.

## Phase 5 — Implement

Based on the decision:

- **Adopt:** Install the package, show basic usage
- **Extend:** Install + write minimal wrapper code
- **Compose:** Install multiple packages, write glue code
- **Build:** Write custom code, but reference what was found during research

Document the decision in a code comment:
```
# Chose <package> over <alternatives> because <reason>
# Searched: PyPI, GitHub, existing codebase
```
