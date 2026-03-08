---
name: update-readme
description: >-
  Check repo state and update README.md to reflect reality. Use when the user
  says "update readme", "sync readme", "refresh readme", "readme is stale",
  or after adding features, refactoring, changing dependencies, or reorganizing
  project structure.
allowed-tools:
  - Glob
  - Grep
  - Read
  - Edit
---

# Update README

Check the current state of a repository and update README.md to accurately reflect it.

## When to Use
- After adding, removing, or renaming modules, packages, endpoints, or features
- After dependency changes, refactors, or structural reorganization
- When README sections are visibly out of date
- When the user says "update readme", "sync readme", "refresh readme"

## When NOT to Use
- Writing a README from scratch for a brand new repo — just write it directly
- Updating non-README docs (CHANGELOG, API docs) — edit those directly

## Phase 1 — Scan the Repo

**Entry:** Repository has a README.md.

1. Read `README.md` — note every section heading and what each claims
2. Glob for project config files to detect the tech stack:
   - `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `docker-compose.yml`, `mkdocs.yml`, etc.
3. Read detected config files — extract:
   - Available commands (scripts, make targets, CLI entrypoints)
   - Dependencies and their versions
   - Build/test/lint tooling
4. Glob for top-level directories and key source files to map project structure
5. Grep for exports, entry points, or route definitions if the README references them

**Exit:** Concrete list of facts about the repo (commands, deps, structure, tooling).

## Phase 2 — Identify Drift

**Entry:** Phase 1 facts collected.

1. Compare each README section against collected facts. Common drift areas:
   - **Install/setup instructions** — wrong commands, missing steps, outdated dependencies
   - **Feature/module lists** — items added or removed but not reflected
   - **Usage examples** — reference deleted APIs, wrong flags, outdated syntax
   - **Project structure** — directory trees that don't match actual layout
   - **Available commands** — scripts added/removed in config files
   - **Tech stack/requirements** — version bumps, swapped tools
   - **Internal links** — paths that no longer exist (Glob to verify each linked path)
2. For each discrepancy, note: section name, what README says, what's actually true

**Exit:** List of specific discrepancies. If none found, report "README is up to date" and stop.

## Phase 3 — Update

**Entry:** Discrepancies identified.

1. For each stale section, edit to match current repo state
2. Preserve the existing README style, tone, and structure
3. Do NOT add new sections or expand scope — only fix what's inaccurate
4. Do NOT rewrite sections that are already correct
5. Use the Edit tool for each change — one edit per discrepancy for clear diffs

**Exit:** All identified discrepancies resolved.

## Phase 4 — Verify

**Entry:** Edits applied.

1. Re-read README.md
2. For every internal link (`[text](path)`), Glob to confirm the target exists
3. Spot-check two updated sections against repo state
4. Report changes made as a brief summary to the user

**Exit:** README accurately reflects current repo state, all internal links valid.
