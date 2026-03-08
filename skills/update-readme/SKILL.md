---
name: update-readme
description: >-
  Analyze repo structure, code, and config then update README.md to reflect
  current state. Use when the user says "update readme", "sync readme",
  "refresh readme", "readme is stale", or after significant repo changes.
allowed-tools:
  - Glob
  - Grep
  - Read
  - Edit
  - Bash
---

# Update README

Analyze the current state of a repository and update README.md to accurately reflect it.

## When to Use
- After adding, removing, or renaming modules, packages, endpoints, or features
- When README sections are visibly out of date
- When the user says "update readme", "sync readme", "refresh readme"
- After major refactors, dependency changes, or structural reorganization

## When NOT to Use
- Writing a README from scratch for a brand new repo — just write it directly
- Updating non-README docs (CHANGELOG, API docs) — edit those directly

## Phase 1 — Understand the Repo

**Entry:** Repository has a README.md.

1. Read `README.md` to understand its current structure and sections
2. Scan the repo to build a picture of its actual state:
   - Project structure: top-level dirs, key files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, etc.)
   - Entry points and exports
   - Dependencies and tooling
   - Available commands (scripts, make targets, CLI commands)
   - Configuration files and environment setup
3. Identify what the README claims vs what actually exists

**Exit:** Clear understanding of both README content and actual repo state.

## Phase 2 — Identify Stale Sections

**Entry:** Phase 1 complete.

1. Compare README claims against repo reality. Common drift areas:
   - **Install/setup instructions** — wrong commands, missing steps, outdated dependencies
   - **Feature/module lists** — items added or removed but not reflected
   - **Usage examples** — reference deleted APIs, wrong flags, outdated syntax
   - **Project structure** — directory trees that don't match
   - **Available commands** — scripts added/removed in package.json, Makefile, etc.
   - **Tech stack/requirements** — version bumps, swapped tools
2. List each stale section with what's wrong

**Exit:** List of sections that need updating, with specific discrepancies.

## Phase 3 — Update

**Entry:** Stale sections identified.

1. For each stale section, update to match current repo state
2. Preserve the existing README style, tone, and structure
3. Do NOT add new sections or expand scope — only fix what's inaccurate
4. Do NOT rewrite sections that are already correct
5. Use the Edit tool for each change

**Exit:** All identified stale sections updated.

## Phase 4 — Verify

**Entry:** Edits applied.

1. Re-read README.md
2. Spot-check updated sections against repo state
3. Report changes made as a brief summary

**Exit:** README accurately reflects current repo state.
