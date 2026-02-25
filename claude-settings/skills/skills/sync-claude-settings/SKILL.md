---
name: sync-claude-settings
description: Sync ~/.claude settings (settings.json, statusline script, keybindings, global skills) to/from a git repo for cross-machine portability. Push to save, pull to restore on a new machine.
---

Sync your local `~/.claude/` configuration files to or from a git repository.

## Arguments

`$ARGUMENTS` may be `push`, `pull`, or empty. If empty, ask the user.

## Files synced

- `~/.claude/settings.json`
- `~/.claude/statusline-command.sh` (if it exists)
- `~/.claude/keybindings.json` (if it exists)
- `~/.claude/skills/` directory (global user skills) — the entire directory, recursively

Never sync session history, cache, telemetry, or other runtime directories.

## Step 1 — Determine direction

If `$ARGUMENTS` is `push` or `pull`, use that. Otherwise use `AskUserQuestion` with two options:
- **Push** — save local `~/.claude/` settings into the repo
- **Pull** — restore settings from the repo into `~/.claude/` on this machine

## Step 2 — Determine sync repo

Read the file `~/.claude/.sync-repo` to get the configured repo path. If it doesn't exist or is empty:

1. Use `AskUserQuestion` to ask: "Which local git repo should store your Claude settings? Enter the full path (e.g. ~/repo/meta-automation)."
2. Expand `~` and validate that the path exists and is a git repository (contains a `.git` directory).
3. Write the resolved absolute path to `~/.claude/.sync-repo`.

Set `SYNC_REPO` to the repo path and `CLAUDE_DIR` to `$SYNC_REPO/claude-settings/`.

## Step 3 — Push (local → repo)

1. Create `$CLAUDE_DIR` if it doesn't exist.
2. Copy files into `$CLAUDE_DIR`:
   - `~/.claude/settings.json` → `$CLAUDE_DIR/settings.json`
   - `~/.claude/statusline-command.sh` → `$CLAUDE_DIR/statusline-command.sh` (if it exists)
   - `~/.claude/keybindings.json` → `$CLAUDE_DIR/keybindings.json` (if it exists)
3. If `~/.claude/skills/` exists, copy it recursively to `$CLAUDE_DIR/skills/` using `cp -r ~/.claude/skills/ $CLAUDE_DIR/skills/`.
4. In `$SYNC_REPO`, stage: `git add claude-settings/`
5. Check for staged changes: `git diff --cached --quiet`. If none, tell the user nothing changed and stop.
6. If changes exist, commit: `git commit -m "chore: sync Claude settings from $(hostname -s) $(date +%Y-%m-%d)"`
7. Ask the user if they want to push to remote. If yes, run `git push` from `$SYNC_REPO`.

## Step 4 — Pull (repo → local)

1. Verify `$CLAUDE_DIR` exists. If not, tell the user no settings have been pushed yet.
2. Copy files back to `~/.claude/`:
   - `$CLAUDE_DIR/settings.json` → `~/.claude/settings.json`
   - `$CLAUDE_DIR/statusline-command.sh` → `~/.claude/statusline-command.sh` (if it exists in the repo)
   - `$CLAUDE_DIR/keybindings.json` → `~/.claude/keybindings.json` (if it exists in the repo)
3. If `$CLAUDE_DIR/skills/` exists, copy it recursively to `~/.claude/skills/`.
4. Ensure `~/.claude/statusline-command.sh` is executable: `chmod +x ~/.claude/statusline-command.sh`
5. Tell the user which files were restored and remind them to restart Claude Code to pick up any settings changes.
