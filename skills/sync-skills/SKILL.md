---
name: sync-skills
description: Sync ~/.claude/skills/ to/from a git repo using symlinks. Push to save new skills, pull to symlink repo skills into ~/.claude/skills/.
---

Sync your local `~/.claude/skills/` directory to or from a git repository using symlinks.

## Arguments

`$ARGUMENTS` may be `push`, `pull`, or empty. If empty, ask the user.

## What gets synced

Only `~/.claude/skills/` — each skill directory is symlinked (not copied) to the repo.

Never sync settings.json, keybindings, statusline scripts, session history, cache, telemetry, or other runtime files.

## Step 1 — Determine direction

If `$ARGUMENTS` is `push` or `pull`, use that. Otherwise use `AskUserQuestion` with two options:
- **Push** — save any non-symlinked skills from `~/.claude/skills/` into the repo, then replace with symlinks
- **Pull** — symlink all repo skills into `~/.claude/skills/`

## Step 2 — Determine sync repo

Read the file `~/.claude/.sync-repo` to get the configured repo path. If it doesn't exist or is empty:

1. Use `AskUserQuestion` to ask: "Which local git repo should store your Claude skills? Enter the full path (e.g. ~/repo/prompt_sync)."
2. Expand `~` and validate that the path exists and is a git repository (contains a `.git` directory).
3. Write the resolved absolute path to `~/.claude/.sync-repo`.

Set `SYNC_REPO` to the repo path and `SKILLS_DIR` to `$SYNC_REPO/skills/`.

## Step 3 — Push (local → repo)

1. Verify `~/.claude/skills/` exists and is non-empty. If not, tell the user there are no skills to push.
2. Create `$SKILLS_DIR` if it doesn't exist.
3. For each directory in `~/.claude/skills/`:
   - If it's already a symlink pointing into `$SKILLS_DIR`, skip it.
   - Otherwise, copy it to `$SKILLS_DIR/`, remove the original, and create a symlink: `ln -s $SKILLS_DIR/<name> ~/.claude/skills/<name>`
4. In `$SYNC_REPO`, stage: `git add skills/`
5. Check for staged changes: `git diff --cached --quiet`. If none, tell the user nothing changed and stop.
6. If changes exist, commit: `git commit -m "chore: sync skills from $(hostname -s) $(date +%Y-%m-%d)"`
7. Ask the user if they want to push to remote. If yes, run `git push` from `$SYNC_REPO`.

## Step 4 — Pull (repo → local)

1. Verify `$SKILLS_DIR` exists and is non-empty. If not, tell the user no skills have been pushed yet.
2. Create `~/.claude/skills/` if it doesn't exist.
3. For each directory in `$SKILLS_DIR`:
   - If `~/.claude/skills/<name>` is already a symlink to the correct target, skip it.
   - If `~/.claude/skills/<name>` exists as a regular directory, warn the user and ask before replacing.
   - Otherwise, create symlink: `ln -s $SKILLS_DIR/<name> ~/.claude/skills/<name>`
4. Tell the user which skill directories were linked and remind them to restart Claude Code to pick up changes.
