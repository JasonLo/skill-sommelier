---
name: ss-docs-update
description: >-
  Check repo state and update all documentation to reflect reality: README.md,
  docs/ directory, .env.example, CONTRIBUTING.md, CHANGELOG, and other doc files.
  Use when the user says "update docs", "sync docs", "refresh readme", "docs are stale",
  or after adding features, refactoring, changing dependencies, or reorganizing
  project structure.
  Triggers on "update docs", "sync docs", "update readme", "refresh readme",
  "docs are stale", "readme is stale", "update documentation", "fix docs".
allowed-tools:
  - Glob
  - Grep
  - Read
  - Edit
  - Write
---

# Update Documentation

Check the current state of a repository and update all documentation to accurately reflect it.

## Scope

This skill covers all documentation artifacts in a repo:
- `README.md` — project overview, install, usage, structure
- `docs/` directory — guides, API docs, architecture docs
- `.env.example` — environment variable templates
- `CONTRIBUTING.md` — contribution guidelines
- `CHANGELOG.md` — release notes
- `CLAUDE.md` — Claude Code project instructions
- Any other `.md` files or doc directories at the project root

## When to Use
- After adding, removing, or renaming modules, packages, endpoints, or features
- After dependency changes, refactors, or structural reorganization
- When documentation sections are visibly out of date
- When the user says "update docs", "sync docs", "refresh readme", "docs are stale"
- After renaming files, changing env vars, or modifying project configuration

## When NOT to Use
- Writing docs from scratch for a brand new repo — just write them directly
- Auto-generating API reference docs — use the project's doc generator instead

## Phase 1 — Discover Documentation

**Entry:** User triggers docs update.

1. Glob for all documentation files:
   - `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CLAUDE.md`, `LICENSE`
   - `docs/**/*.md`, `docs/**/*.rst`
   - `.env.example`, `.env.sample`, `.env.template`
   - Any other `*.md` files at the project root
2. Read each doc file — note what each claims about the project
3. Glob for project config files to detect the tech stack:
   - `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `docker-compose.yml`, `mkdocs.yml`, etc.
4. Read detected config files — extract:
   - Available commands (scripts, make targets, CLI entrypoints)
   - Dependencies and their versions
   - Build/test/lint tooling
   - Environment variables used
5. Glob for top-level directories and key source files to map project structure
6. Grep for exports, entry points, route definitions, or env var usage in source code

**Exit:** Concrete list of facts about the repo and a catalog of all doc files.

## Phase 2 — Identify Drift

**Entry:** Phase 1 facts collected.

Compare each documentation file against collected facts. Common drift areas:

### README.md
- **Install/setup instructions** — wrong commands, missing steps, outdated dependencies
- **Feature/module lists** — items added or removed but not reflected
- **Usage examples** — reference deleted APIs, wrong flags, outdated syntax
- **Project structure** — directory trees that don't match actual layout
- **Available commands** — scripts added/removed in config files
- **Tech stack/requirements** — version bumps, swapped tools
- **Internal links** — paths that no longer exist (Glob to verify each linked path)

### .env.example
- **Missing variables** — env vars used in code but not listed in .env.example
- **Stale variables** — env vars listed but no longer referenced in code
- **Wrong defaults or descriptions** — comments that don't match actual usage

### docs/ directory
- **Stale guides** — reference removed features or old APIs
- **Broken links** — internal links pointing to moved/deleted files
- **Missing docs** — new major features with no corresponding documentation

### CLAUDE.md
- **Stale conventions** — rules that no longer match the codebase
- **Missing tools/skills** — new capabilities not reflected in instructions

### Other docs
- **CONTRIBUTING.md** — outdated setup steps, wrong branch names, stale CI info
- **CHANGELOG.md** — missing recent releases (check git tags)

For each discrepancy, note: file path, section, what the doc says, what's actually true.

**Exit:** List of specific discrepancies per file. If none found, report "All documentation is up to date" and stop.

## Phase 3 — Update

**Entry:** Discrepancies identified.

1. For each stale section, edit to match current repo state
2. Preserve the existing style, tone, and structure of each file
3. Do NOT add new sections or expand scope — only fix what's inaccurate
4. Do NOT rewrite sections that are already correct
5. Use the Edit tool for each change — one edit per discrepancy for clear diffs
6. For .env.example: add missing variables with sensible placeholder values and comments, remove stale ones

**Exit:** All identified discrepancies resolved.

## Phase 4 — Verify

**Entry:** Edits applied.

1. Re-read each modified doc file
2. For every internal link (`[text](path)`), Glob to confirm the target exists
3. Spot-check two updated sections against repo state
4. Report changes made as a brief summary to the user, grouped by file

**Exit:** All documentation accurately reflects current repo state, all internal links valid.
