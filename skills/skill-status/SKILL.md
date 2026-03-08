---
name: skill-status
description: Show all repo and local Claude Code skills, compare duplicates with diff.
allowed-tools:
  - Bash
  - Read
  - Glob
---

Compare skills across three locations: the repo's canonical `skills/` directory, the repo's `.claude/skills/` (project-level), and `~/.claude/skills/` (global). Identify sync issues.

## When to Use
- Checking if skills are properly synced across locations
- Diagnosing broken or missing symlinks
- After installing or removing skills

## When NOT to Use
- Syncing skills — use `sync-skills` instead
- Browsing available skills — use `discover-skills`

## Step 1 — Determine paths

Read `~/.claude/.sync-repo` for the repo path. If missing, use `AskUserQuestion` to ask for it. Define:
- `REPO_SKILLS` = `$SYNC_REPO/skills/` — canonical skill sources (source of truth)
- `PROJECT_SKILLS` = `$SYNC_REPO/.claude/skills/` — project-level (should be symlink to `../skills`)
- `GLOBAL_SKILLS` = `~/.claude/skills/` — global (should be symlink to `$SYNC_REPO/skills`)

## Step 2 — Check symlinks

In a **single Bash call**, check all three locations:
```bash
echo "=== REPO ===" && ls -1d "$REPO_SKILLS"*/
echo "=== PROJECT ===" && readlink "$PROJECT_SKILLS" 2>/dev/null || echo "NOT A SYMLINK"
echo "=== GLOBAL ===" && readlink "$GLOBAL_SKILLS" 2>/dev/null || echo "NOT A SYMLINK"
```

## Step 3 — Display overview

Both project and global should be single directory symlinks. Report:

| Location | Expected | Actual | Status |
|----------|----------|--------|--------|
| `skills/` | directory | ... | source of truth |
| `.claude/skills` | symlink → `../skills` | ... | synced / broken / missing |
| `~/.claude/skills` | symlink → `$REPO_SKILLS` | ... | synced / broken / missing |

Then list all skills found in `$REPO_SKILLS`.

## Step 4 — Detect issues

Check for:
- **Broken symlinks** — target doesn't exist
- **Regular directories instead of symlinks** — project or global is a copy, not a symlink
- **Wrong symlink target** — points somewhere unexpected

## Step 5 — Suggest fixes

- If project or global is a regular directory: offer to replace with the correct symlink
- If a symlink is broken: offer to recreate it
- If everything is synced: confirm all clear
