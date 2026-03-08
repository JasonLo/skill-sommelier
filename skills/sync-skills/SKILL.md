---
name: sync-skills
description: >-
  Sync ~/.claude/skills/ to/from a git repo using symlinks. Install skill-sommelier on a new machine,
  push to save new skills, pull to symlink repo skills, or update to get latest skills from remote.
  Use when setting up Claude Code skills on a new machine, syncing skills, or updating skill-sommelier.
  Triggers on sync skills, install skills, update skills, pull skills, push skills.
allowed-tools:
  - Bash
  - Read
  - Write
---

Sync your local `~/.claude/skills/` to or from a git repository using a single directory symlink.

## Arguments

`$ARGUMENTS` may be `install`, `push`, `pull`, `update`, or empty. If empty, ask the user.

| Argument | What it does |
|----------|-------------|
| `install` | Clone skill-sommelier repo and set up symlinks from scratch |
| `push` | Commit and push local skill changes to the repo |
| `pull` | Symlink `~/.claude/skills` to the repo's `skills/` |
| `update` | Pull latest changes from remote into the local repo |

## Step 1 — Determine direction and sync repo

### If `install`

Skip to Step 2 (Install).

### If `push`, `pull`, or `update`

Do both of these in a **single parallel tool call**:
- If `$ARGUMENTS` is set, use that. Otherwise use `AskUserQuestion` with options: **Install**, **Push**, **Pull**, **Update**.
- Read `~/.claude/.sync-repo` to get the repo path. If missing or empty, ask the user and write it.

Set `SYNC_REPO` to the repo path and `SKILLS_DIR` to `$SYNC_REPO/skills/`.

## Step 2 — Install (new machine setup)

For first-time setup on a new machine.

1. Ask the user for the repo URL if not obvious. Default: `https://github.com/JasonLo/skill-sommelier.git`
2. Set `INSTALL_DIR` to `~/.local/share/skill-sommelier`.
3. In **one Bash call**:
   ```bash
   mkdir -p ~/.local/share && git clone "$REPO_URL" "$INSTALL_DIR"
   ```
4. If the directory already exists and is a git repo, skip cloning and run `git -C "$INSTALL_DIR" pull --ff-only` instead.
5. Set up symlinks and config in **one Bash call**:
   ```bash
   mkdir -p ~/.claude
   rm -f ~/.claude/skills
   ln -sf "$INSTALL_DIR/skills" ~/.claude/skills
   echo "$INSTALL_DIR" > ~/.claude/.sync-repo
   ```
6. Verify with `ls ~/.claude/skills/*/SKILL.md | wc -l` and report the number of skills installed.
7. Remind the user to restart Claude Code.

## Step 3 — Push (local → repo)

1. Check if `~/.claude/skills` is already a symlink to `$SKILLS_DIR`. If so, any new skills are already in the repo — just stage and commit.
2. If `~/.claude/skills` is a regular directory, copy its contents to `$SKILLS_DIR/`, remove the directory, and create the symlink: `ln -sf $SKILLS_DIR ~/.claude/skills`
3. Stage, check for changes, and commit in **one Bash call**: `git -C $SYNC_REPO add skills/ && git -C $SYNC_REPO diff --cached --quiet || git -C $SYNC_REPO commit -m "chore: sync skills from $(hostname -s) $(date +%Y-%m-%d)"`
4. Push to remote.

## Step 4 — Pull (repo → local)

1. Verify `$SKILLS_DIR` exists and is non-empty. If not, tell the user no skills have been pushed yet and stop.
2. In **one Bash call**, remove any existing `~/.claude/skills` (whether directory or broken symlink) and create the symlink:
   ```bash
   rm -rf ~/.claude/skills && ln -sf "$SKILLS_DIR" ~/.claude/skills
   ```
3. Verify with `ls -la ~/.claude/skills` and report success. Remind the user to restart Claude Code.

## Step 5 — Update (get latest from remote)

1. Check for uncommitted local changes: `git -C $SYNC_REPO status --porcelain`
   - If dirty, warn the user and ask whether to stash or abort.
2. Pull latest: `git -C $SYNC_REPO pull --ff-only`
   - If fast-forward fails (diverged history), report the issue and suggest manual resolution.
3. Report what changed: `git -C $SYNC_REPO log --oneline HEAD@{1}..HEAD`
   - If no new commits, report "Already up to date."
   - Otherwise, list the new commits and count of updated skills.
