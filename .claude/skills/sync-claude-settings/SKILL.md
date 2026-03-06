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

## Step 3 — Push (local → repo with stow)

1. Check if `stow` is installed: `which stow`. If not found, tell the user to install it first:
   - macOS: `brew install stow`
   - Ubuntu/Debian: `sudo apt install stow`
   - Arch: `sudo pacman -S stow`
2. Create the stow package structure: `mkdir -p $CLAUDE_DIR/.claude`
3. Copy files into the stow package directory `$CLAUDE_DIR/.claude/`:
   - `cp ~/.claude/settings.json $CLAUDE_DIR/.claude/settings.json` (if it exists)
   - `cp ~/.claude/statusline-command.sh $CLAUDE_DIR/.claude/statusline-command.sh` (if it exists)
   - `cp ~/.claude/keybindings.json $CLAUDE_DIR/.claude/keybindings.json` (if it exists)
4. If `~/.claude/skills/` exists, copy it recursively: `cp -r ~/.claude/skills $CLAUDE_DIR/.claude/`
5. Remove existing non-symlink files/dirs in `~/.claude/` that will be replaced by stow:
   - Check if files/dirs exist and are NOT symlinks, then back them up and remove:
   - `[ ! -L ~/.claude/settings.json ] && [ -f ~/.claude/settings.json ] && mv ~/.claude/settings.json ~/.claude/settings.json.backup`
   - `[ ! -L ~/.claude/statusline-command.sh ] && [ -f ~/.claude/statusline-command.sh ] && mv ~/.claude/statusline-command.sh ~/.claude/statusline-command.sh.backup`
   - `[ ! -L ~/.claude/keybindings.json ] && [ -f ~/.claude/keybindings.json ] && mv ~/.claude/keybindings.json ~/.claude/keybindings.json.backup`
   - `[ ! -L ~/.claude/skills ] && [ -d ~/.claude/skills ] && mv ~/.claude/skills ~/.claude/skills.backup`
6. Unstow any previous configuration to clean up: `cd $SYNC_REPO && stow -D claude-settings -t ~ 2>/dev/null || true`
7. Stow the configuration (create symlinks): `cd $SYNC_REPO && stow -v claude-settings -t ~`
8. Verify symlinks were created successfully by checking one: `ls -la ~/.claude/settings.json` should show a symlink.
9. If the current working directory is inside a git repo (check with `git rev-parse --show-toplevel`), copy the `sync-claude-settings` skill into the project-local `.claude/skills/` directory: `mkdir -p .claude/skills && cp -r ~/.claude/skills/sync-claude-settings .claude/skills/`
10. In `$SYNC_REPO`, stage: `git add claude-settings/ .claude/skills/`
11. Check for staged changes: `git diff --cached --quiet`. If none, tell the user nothing changed and stop.
12. If changes exist, commit: `git commit -m "chore: sync Claude settings from $(hostname -s) $(date +%Y-%m-%d)"`
13. Ask the user if they want to push to remote. If yes, run `git push` from `$SYNC_REPO`.

**Note**: After stowing, `~/.claude/` files become symlinks to the repo. Any changes to files in `~/.claude/` will automatically update the repository files.

## Step 4 — Pull (repo → local with stow)

1. Check if `stow` is installed: `which stow`. If not found, tell the user to install it first (same instructions as Step 3).
2. Verify `$CLAUDE_DIR/.claude` exists. If not, tell the user no settings have been pushed yet.
3. Remove existing non-symlink files/dirs in `~/.claude/` that will be replaced by stow:
   - Check if files/dirs exist and are NOT symlinks, then back them up:
   - `[ ! -L ~/.claude/settings.json ] && [ -f ~/.claude/settings.json ] && mv ~/.claude/settings.json ~/.claude/settings.json.backup`
   - `[ ! -L ~/.claude/statusline-command.sh ] && [ -f ~/.claude/statusline-command.sh ] && mv ~/.claude/statusline-command.sh ~/.claude/statusline-command.sh.backup`
   - `[ ! -L ~/.claude/keybindings.json ] && [ -f ~/.claude/keybindings.json ] && mv ~/.claude/keybindings.json ~/.claude/keybindings.json.backup`
   - `[ ! -L ~/.claude/skills ] && [ -d ~/.claude/skills ] && mv ~/.claude/skills ~/.claude/skills.backup`
4. Unstow any previous configuration to clean up: `cd $SYNC_REPO && stow -D claude-settings -t ~ 2>/dev/null || true`
5. Stow the configuration (create symlinks): `cd $SYNC_REPO && stow -v claude-settings -t ~`
6. Verify symlinks were created: `ls -la ~/.claude/` should show symlinks pointing to `$CLAUDE_DIR/.claude/`
7. If `~/.claude/statusline-command.sh` exists, ensure it's executable: `chmod +x ~/.claude/statusline-command.sh`
8. Tell the user which files were restored and remind them to restart Claude Code to pick up any settings changes.

**Note**: After stowing, `~/.claude/` files become symlinks to the repo. Any changes will be automatically reflected in the repository.
