---
name: sync-skills
description: Sync ~/.claude/skills/ to/from a git repo using symlinks. Push to save new skills, pull to symlink repo skills into ~/.claude/skills/.
allowed-tools:
  - Bash
  - Read
  - Write
---

Sync your local `~/.claude/skills/` to or from a git repository using a single directory symlink.

## Arguments

`$ARGUMENTS` may be `push`, `pull`, or empty. If empty, ask the user.

## What gets synced

Only `~/.claude/skills/` — symlinked as a whole directory to `$SYNC_REPO/skills/`.

Never sync settings.json, keybindings, statusline scripts, session history, cache, telemetry, or other runtime files.

## Step 1 — Determine direction and sync repo (parallel)

Do both of these in a **single parallel tool call**:
- If `$ARGUMENTS` is `push` or `pull`, use that. Otherwise use `AskUserQuestion` with two options: **Push** or **Pull**.
- Read `~/.claude/.sync-repo` to get the repo path. If missing or empty, ask the user and write it.

Set `SYNC_REPO` to the repo path and `SKILLS_DIR` to `$SYNC_REPO/skills/`.

## Step 2 — Push (local → repo)

1. Check if `~/.claude/skills` is already a symlink to `$SKILLS_DIR`. If so, any new skills are already in the repo — just stage and commit.
2. If `~/.claude/skills` is a regular directory, copy its contents to `$SKILLS_DIR/`, remove the directory, and create the symlink: `ln -sf $SKILLS_DIR ~/.claude/skills`
3. Stage, check for changes, and commit in **one Bash call**: `git -C $SYNC_REPO add skills/ && git -C $SYNC_REPO diff --cached --quiet || git -C $SYNC_REPO commit -m "chore: sync skills from $(hostname -s) $(date +%Y-%m-%d)"`
4. Push to remote.

## Step 3 — Pull (repo → local)

1. Verify `$SKILLS_DIR` exists and is non-empty. If not, tell the user no skills have been pushed yet and stop.
2. In **one Bash call**, remove any existing `~/.claude/skills` (whether directory or broken symlink) and create the symlink:
   ```bash
   rm -rf ~/.claude/skills && ln -sf "$SKILLS_DIR" ~/.claude/skills
   ```
3. Verify with `ls -la ~/.claude/skills` and report success. Remind the user to restart Claude Code.
