---
name: ss-simplify-repo
description: >-
  Audit a repository for unnecessary complexity, dead code, outdated dependencies, and
  stale TODOs, then propose concrete simplifications. Use when the repo feels bloated,
  after a big refactor, or to find dead code and overengineering.
  Triggers on "simplify", "clean up this repo", "reduce complexity", "find dead code",
  "audit complexity", "overengineered", "too complex", "code health", "tech debt".
allowed-tools:
  - Read
  - Edit
  - Bash
  - Glob
  - Grep
---

Audit the current repository for unnecessary complexity — dead code, overengineered abstractions, redundant config, bloated dependencies, and anything that makes the codebase harder to understand than it needs to be. Propose simplifications, get user approval, then apply them.

## When to Use
- Repository feels harder to navigate than it should
- Suspecting dead code, unused dependencies, or premature abstractions
- After a big refactor or feature removal — cleaning up leftovers

## When NOT to Use
- Active feature development — simplify after, not during
- Repos you don't own — suggest changes via PR instead
- Performance optimization — this is about code clarity, not speed

## Step 1 — Scan the repository

Perform a broad audit across these dimensions:

### 1a — Structure & file organization
- Are there unnecessary nesting levels or deeply nested directories?
- Empty or near-empty files that serve no purpose?
- Redundant config files (multiple configs doing the same thing)?
- Files that duplicate each other or could be merged?
- Orphaned files not referenced by anything?

### 1b — Dead code detection
Systematically identify code with no live references:
- **Unused imports** — imported modules/symbols never referenced in the file
- **Unused variables & functions** — declared but never called or read
- **Commented-out code blocks** — stale code left behind after changes
- **Unreachable branches** — conditions that can never be true, dead `else` paths
- **Unused exports** — symbols exported but not imported anywhere in the project
Verify each finding to avoid false positives from dynamic imports, reflection, or plugin architectures.

### 1c — Code complexity
- Premature abstractions — wrappers, helpers, or utilities used only once
- Over-parameterized functions with options/flags that are never varied
- Unnecessary indirection (layers that just pass through to the next layer)
- Overly generic solutions for specific problems
- Long functions, deep nesting, and code duplication

### 1d — Dependencies & tooling
- **Unused dependencies** in package.json, requirements.txt, Cargo.toml, etc.
- **Outdated dependencies** — check for major version drift or known vulnerabilities (run `npm audit`, `pip-audit`, `cargo audit`, or equivalent if available)
- Dependencies that duplicate built-in functionality
- Overly complex build/CI configuration for what the project actually does
- Lock files, generated files, or artifacts that shouldn't be committed

### 1e — Configuration & boilerplate
- Config files copied from templates but never customized
- Excessive linting/formatting rules beyond what the team uses
- README sections that are aspirational rather than accurate
- Unnecessary GitHub Actions, hooks, or automation

### 1f — TODO/FIXME audit
- Scan for all `TODO`, `FIXME`, `HACK`, and `XXX` comments
- Check if each references a tracked issue (e.g., `TODO(#123)` or a link)
- Flag stale TODOs that have no issue reference and appear older than the last few commits
- Flag TODOs whose referenced issue is already closed

### 1g — Documentation vs reality
- Do docs describe features that don't exist?
- Are there TODOs or FIXMEs that are stale?
- Is the project structure documented accurately?

## Step 2 — Score and categorize findings

For each finding, assess:
- **Impact**: How much simpler would the repo be without this? (high / medium / low)
- **Risk**: Could removing this break something? (safe / needs-testing / risky)
- **Category**: structure / code / dependencies / config / docs

Sort findings by impact (high first), then by risk (safe first).

## Step 3 — Present the audit report

Output a structured critique:

```markdown
# Repository Simplification Audit

## Summary
> One paragraph: overall assessment of complexity level and main themes.

## Findings

### High Impact
| # | Category | Finding | Risk | Proposed Change |
|---|----------|---------|------|-----------------|
| 1 | ...      | ...     | ...  | ...             |

### Medium Impact
| # | Category | Finding | Risk | Proposed Change |
|---|----------|---------|------|-----------------|

### Low Impact
| # | Category | Finding | Risk | Proposed Change |
|---|----------|---------|------|-----------------|

## Metrics
- Files scanned: N
- Total findings: N
- Estimated lines removable: ~N
- Estimated files removable: ~N
```

## Step 4 — Ask for confirmation

Use `AskUserQuestion` to present the user with options:

1. **Apply all safe changes** — execute all findings marked as "safe" risk
2. **Pick and choose** — let the user select specific findings by number
3. **Deep dive** — explain a specific finding in more detail before deciding
4. **Export** — save the audit report to a file without applying changes
5. **Done** — end without changes

## Step 5 — Apply approved changes

For each approved change:
1. State what you're about to do in one line
2. Make the change (delete file, remove code, simplify config, etc.)
3. Confirm the change was applied

After all changes are applied, run a final check:
- If the project has a build command, run it to verify nothing broke
- If the project has tests, run them
- Show a `git diff --stat` summary of all changes made

## Step 6 — Summary

Output a before/after comparison:

```markdown
## Simplification Complete

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Files  | N      | N     | -N    |
| Lines  | N      | N     | -N    |
| Dependencies | N | N   | -N    |

Changes applied: N of M findings
```

## Guiding principles

- **Complexity must earn its place.** If something doesn't solve a current problem, it's dead weight.
- **Three similar lines > one premature abstraction.** Duplication is cheaper than the wrong abstraction.
- **Fewer files > more files.** Merging small related files reduces navigation overhead.
- **Built-in > dependency.** If the language/framework already provides it, don't add a package.
- **Accurate docs > comprehensive docs.** Delete lies before writing new truths.
- **Be bold but not reckless.** Flag risky removals clearly and let the user decide.
