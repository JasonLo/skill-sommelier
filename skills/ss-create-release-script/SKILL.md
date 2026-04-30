---
name: ss-create-release-script
description: >-
  Scaffold a Python release script (`scripts/release.py`) into a uv-managed
  project. The script enforces clean-tree + on-main + synced-with-remote
  guards, runs lint and tests, bumps the version with `uv version --bump`,
  commits, tags, atomic-pushes, rolls back on push failure, and creates a
  GitHub release with auto-generated notes. PEP 723 inline-deps (typer,
  rich), so users run it via `uv run scripts/release.py`. Use when the user
  wants to add a release automation script to a uv project, or asks for
  "release.py", "release script", "release manager", "tag and push
  automation", "uv release", "scaffold release". Triggers on "create
  release script", "release.py", "release script", "release manager",
  "uv release", "tag and push script", "release automation".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Create Release Script

Drops a battle-tested Python release script into a uv-managed project, customised to its branch name and quality commands.

## What the script does

When invoked as `uv run scripts/release.py [patch|minor|major|alpha|beta|rc|post|dev]`:

1. **Guards** — refuse to release if not on the default branch, working tree dirty, ahead/behind remote.
2. **Quality** — run lint and tests; abort if either fails.
3. **Bump** — `uv version --bump <increment>` updates `pyproject.toml`.
4. **Commit + tag** — stages `pyproject.toml` (and `uv.lock` if present), commits as `chore: release vX.Y.Z`, creates annotated tag `vX.Y.Z`.
5. **Atomic push** — `git push --atomic <remote> <branch> <tag>` so branch + tag succeed or fail together. **Rolls back local commit and tag on push failure.**
6. **GitHub release** — `gh release create <tag> --generate-notes`.

## When to Use

- Target project uses `uv` for dependency / version management (has `pyproject.toml` with a version field managed by `uv version`).
- User wants release automation that won't tag a broken build.
- User asks for "release.py", "release script", "tag and push automation".

## When NOT to Use

- Target project uses Poetry / hatch / setuptools-scm — the `uv version --bump` call won't work. Tell the user and stop.
- Target project isn't a Python project — wrong tool.
- For releasing **this** plugin (skill-sommelier), use `ss-repo-release` instead — that one bumps `plugin.json` / `marketplace.json`, not `pyproject.toml`.

## Phase 1 — Detect project state

**Entry:** User triggers the skill.

Run these checks in parallel and report findings:

1. **uv project?** — `pyproject.toml` exists at repo root, contains a `[project]` table with a `version` field. If not, abort with a clear message.
2. **uv.lock?** — note whether `uv.lock` exists (the script will stage it if so).
3. **Tests?** — does `tests/` exist, or is `pytest` listed in dependencies / dev-dependencies?
4. **Lint?** — is `ruff` configured (in `pyproject.toml [tool.ruff]` or a `.ruff.toml` / `ruff.toml`)? Or another linter (`flake8`, `pylint`, `mypy`, `ty`)?
5. **Default branch** — `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`. Falls back to `main` if unset.
6. **Existing release script** — does `scripts/release.py` already exist? If yes, ask whether to overwrite, abort, or write to a different path.

**Exit:** Detection report shown to user.

## Phase 2 — Confirm preferences

**Entry:** Detection complete.

Use `AskUserQuestion` to confirm:

1. **Script path** — default `scripts/release.py`. Allow override.
2. **Default branch** — autofilled from detection, confirm.
3. **Lint command** — default `["uv", "run", "ruff", "check", "."]`. Offer alternatives based on detection (`mypy`, `ty`, etc). Allow "skip lint" if no linter is configured.
4. **Test command** — default `["uv", "run", "pytest"]`. Offer "skip tests" if no tests detected (warn this defeats the purpose of the guard).

**Exit:** All four answers collected.

## Phase 3 — Write the script

**Entry:** Preferences confirmed.

1. Read the bundled template at [templates/release.py](templates/release.py).
2. Copy to the chosen path.
3. Apply customisations using `Edit`:
   - If branch ≠ `main`: change `DEFAULT_BRANCH = "main"` to the chosen branch.
   - If lint command differs from `["uv", "run", "ruff", "check", "."]`: replace the `run([...])` call inside `verify_quality()` and update the `console.print(...)` description above it.
   - If test command differs from `["uv", "run", "pytest"]`: same pattern.
   - If user chose "skip lint": delete the two console+run lines for ruff. If "skip tests": delete the two for pytest.
4. `chmod +x` the file.

**Exit:** Customised script in place.

## Phase 4 — Smoke test

**Entry:** Script written.

Run `uv run <script-path> --help` and confirm it prints typer's help output without errors. This validates the PEP 723 header parses correctly and dependencies resolve.

If `uv` isn't installed in the user's environment, skip and tell the user to test it themselves.

**Exit:** Help output verified (or skipped with note).

## Phase 5 — Hand-off

**Entry:** Script verified.

Print a short usage card:

```
Created: <path>

Usage:
  uv run <path>          # patch bump (default)
  uv run <path> minor    # 0.3.0 → 0.4.0
  uv run <path> major    # 0.3.0 → 1.0.0
  uv run <path> alpha    # pre-release bump

Requires: gh CLI authenticated (`gh auth status`) for the GitHub release step.
```

Optionally offer to:
- Add a one-line mention to the project README (a "Releasing" section).
- Add a `[tool.uv.tasks]` shortcut or a justfile recipe.
- Stage and commit the new script.

**Exit:** User has the script and knows how to run it.

## Notes

- The bundled template uses Python 3.14+ (`StrEnum`). If the target project pins an older Python, `uv run` will fetch 3.14 just for this script (PEP 723 is independent of the project's Python version) — that's intended.
- The script intentionally uses `--atomic` push so a permission error on the tag doesn't leave behind an unreverted release commit.
- The rollback path uses `git reset --mixed HEAD~1` (keeps changes in working tree) so the user can retry without re-editing files.
