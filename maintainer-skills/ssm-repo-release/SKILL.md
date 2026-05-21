---
name: ssm-repo-release
description: >-
  Create a new versioned release: bump version, tag, and push to trigger the
  release workflow. Use when the user says "release", "new version",
  "bump version", "ship it", "cut a release", or "publish".
allowed-tools:
  - Bash
  - Read
  - Edit
---

# Self-Release

Bump the version, create an annotated git tag, and push to trigger the GitHub Actions release workflow.

## When to Use

- User wants to publish a new version
- User says "release", "ship it", "bump version", "cut a release"
- After a set of features/fixes are merged and ready to ship

## When NOT to Use

- User just wants to commit — use normal git workflow instead
- User wants to update the installed plugin — use `ss-update` instead
- User wants to preview changes without releasing — just review the git log

## Phase 1 — Preflight

**Entry:** User triggered a release.

1. Check for a clean working tree:
   ```
   git status --porcelain
   ```
   If uncommitted changes exist, report them and **stop** — ask to commit or stash first.

2. Confirm on the `main` branch:
   ```
   git branch --show-current
   ```
   If not on `main`, warn and **stop**.

3. Ensure local main is synced with remote:
   ```
   git fetch origin main --quiet
   git rev-list --count HEAD..origin/main
   ```
   If behind, report how many commits behind and **stop** — ask to pull first.
   If ahead, warn and ask whether to push before releasing.

**Exit:** Clean tree, on `main`, synced with remote.

## Phase 2 — Gather History

**Entry:** Preflight passed.

1. Read the current version from `.claude-plugin/plugin.json` (the `version` field).

2. Find the latest version tag:
   ```
   git tag --list 'v*' --sort=-version:refname | head -1
   ```
   If no tags exist, note this is the **first release** and use the full commit log on `main`.

3. List commits since the last tag (or all commits if first release):
   ```
   git log <last-tag>..HEAD --oneline
   ```
   If no commits since the last tag, report "No changes since last release" and **stop**.

4. Display the commit log.

**Exit:** Current version known, commit list collected, at least one new commit exists.

## Phase 3 — Suggest Bump

**Entry:** Commit list available from Phase 2.

Apply these rules to the commits:
- Any commit message contains `BREAKING` (case-insensitive) → suggest **major**
- Any commit message starts with `feat:` or `feat(` → suggest **minor**
- Otherwise (`fix:`, `improve:`, `cleanup:`, `docs:`, `chore:`, etc.) → suggest **patch**

Present all three options with the resulting version number:
- **patch:** `X.Y.Z` → `X.Y.(Z+1)`
- **minor:** `X.Y.Z` → `X.(Y+1).0`
- **major:** `X.Y.Z` → `(X+1).0.0`

Highlight the suggested option. Ask the user to choose.

**Exit:** User confirmed the new version number.

## Phase 4 — Bump Version

**Entry:** New version number confirmed.

1. Edit `.claude-plugin/plugin.json` — update the `"version"` field
2. Edit `.claude-plugin/marketplace.json` — update the `"version"` field inside `metadata`
3. Bump the pinned installer URLs in `README.md`, `scripts/install.sh`, and `scripts/uninstall.sh`. One sed handles all of them — they all match `JasonLo/skill-sommelier/v<old>/scripts/`:
   ```bash
   # NEW_VERSION already has no leading "v", e.g. 0.7.0
   git ls-files README.md scripts/install.sh scripts/uninstall.sh | \
     xargs sed -i -E "s|(JasonLo/skill-sommelier/)v[0-9]+\.[0-9]+\.[0-9]+(/scripts/)|\1v${NEW_VERSION}\2|g"
   ```
   Then verify with `grep -n "JasonLo/skill-sommelier/v" README.md scripts/install.sh scripts/uninstall.sh` — every line should show the new tag.

   If `scripts/` doesn't exist in this repo, skip step 3 (older releases predate the bootstrap installer).

4. Read all bumped files back to confirm the version is correct.

**Exit:** All files show the new version.

## Phase 5 — Commit, Tag, Push

**Entry:** Version bumped in all relevant files.

**⚠ SAFETY GATE:** Before proceeding, display this summary and wait for explicit confirmation. Use `git diff --stat` to list the files that actually changed — don't hard-code the list, since older releases may not have the bootstrap installer:

```
Ready to release:
  Version: v<NEW_VERSION>
  Files:   <list from git diff --stat>
  Action:  commit → tag → push (triggers GitHub release workflow)

Proceed? (yes/no)
```

Only continue after user confirms.

1. Stage every file that was actually changed in Phase 4 (use `git diff --name-only` rather than a hard-coded list):
   ```
   git add $(git diff --name-only)
   ```

2. Commit with a release message:
   ```
   git commit -m "release: v<NEW_VERSION>"
   ```

3. Create an annotated tag:
   ```
   git tag -a "v<NEW_VERSION>" -m "Release v<NEW_VERSION>"
   ```

4. Push the commit and tag together:
   ```
   git push origin main --follow-tags
   ```

5. Report success:
   - New version number
   - Tag name
   - GitHub Actions release workflow triggered
   - Link: `https://github.com/JasonLo/skill-sommelier/actions`

**Exit:** Tag pushed, release workflow triggered.

## Edge Cases

- **Dirty working tree:** Stop at Phase 1, ask to commit or stash
- **Not on main:** Stop at Phase 1, warn
- **Behind remote:** Stop at Phase 1, ask to pull
- **No commits since last tag:** Stop at Phase 2, nothing to release
- **First release (no tags):** Use full commit history for changelog
