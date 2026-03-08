---
name: sync-skills
description: Sync ~/.claude/skills/ to/from a git repo using symlinks. Push to save new skills, pull to symlink repo skills into ~/.claude/skills/.
allowed-tools:
  - Bash
  - Read
  - Write
---

Sync your local `~/.claude/skills/` directory to or from a git repository using symlinks.

## Arguments

`$ARGUMENTS` may be `push`, `pull`, or empty. If empty, ask the user.

## What gets synced

Only `~/.claude/skills/` — each skill directory is symlinked (not copied) to the repo.

Never sync settings.json, keybindings, statusline scripts, session history, cache, telemetry, or other runtime files.

## Step 1 — Determine direction and sync repo (parallel)

Do both of these in a **single parallel tool call**:
- If `$ARGUMENTS` is `push` or `pull`, use that. Otherwise use `AskUserQuestion` with two options: **Push** or **Pull**.
- Read `~/.claude/.sync-repo` to get the repo path. If missing or empty, ask the user and write it.

Set `SYNC_REPO` to the repo path and `SKILLS_DIR` to `$SYNC_REPO/skills/`.

## Step 2 — Push (local → repo)

1. In a **single Bash call**, list `~/.claude/skills/` and check which entries are already symlinks into `$SKILLS_DIR`. If none need syncing, stop.
2. Copy non-symlinked directories to `$SKILLS_DIR/`, remove originals, and create symlinks — all in **one Bash call**.
3. Stage, check for changes, and commit in **one Bash call**: `git -C $SYNC_REPO add skills/ && git -C $SYNC_REPO diff --cached --quiet || git -C $SYNC_REPO commit -m "chore: sync skills from $(hostname -s) $(date +%Y-%m-%d)"`
4. Ask the user if they want to push to remote. If yes, run `git push` from `$SYNC_REPO`.

## Step 3 — Pull (repo → local)

In a **single parallel tool call**, read `~/.claude/skills/` (via `ls -la`) and list `$SKILLS_DIR` directories. Then:

1. If `$SKILLS_DIR` is empty, tell the user no skills have been pushed yet and stop.
2. In **one Bash call**, create `~/.claude/skills/` if needed and symlink all missing/incorrect entries. Use a loop like:
   ```bash
   for d in "$SKILLS_DIR"/*/; do
     name=$(basename "$d")
     target="$HOME/.claude/skills/$name"
     [ -L "$target" ] && [ "$(readlink "$target")" = "$d" ] && continue
     [ -d "$target" ] && echo "WARN: $name is a regular directory, skipping" && continue
     ln -sf "$d" "$target"
     echo "linked: $name"
   done
   ```
3. Report which skills were linked (or that all were already up to date). Remind the user to restart Claude Code.
