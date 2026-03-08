---
name: skill-status
description: Show all repo and local Claude Code skills, compare duplicates with diff.
---

Compare skills across three locations: the repo's canonical `skills/` directory, the repo's `.claude/skills/` (project-level), and `~/.claude/skills/` (global). Identify sync issues between any of them.

## Step 1 — Determine paths

Read `~/.claude/.sync-repo` for the repo path. If missing, use `AskUserQuestion` to ask for it. Define:
- `REPO_SKILLS` = `$SYNC_REPO/skills/` — canonical skill sources
- `PROJECT_SKILLS` = `$SYNC_REPO/.claude/skills/` — project-level skills (should symlink to `../../skills/<name>`)
- `GLOBAL_SKILLS` = `~/.claude/skills/` — global skills (should symlink to `$SYNC_REPO/skills/<name>`)

## Step 2 — Gather skills

1. List all directories in `REPO_SKILLS` — these are **repo skills** (the source of truth).
2. List all entries in `PROJECT_SKILLS` — note whether each is a symlink (and its target) or a regular directory.
3. List all entries in `GLOBAL_SKILLS` — note whether each is a symlink (and its target) or a regular directory.

## Step 3 — Display overview

Print a table with columns: **Skill**, **Repo** (`skills/`), **Project** (`.claude/skills/`), **Global** (`~/.claude/skills/`), **Status**.

Status values:
- **synced** — exists in repo, and both project and global entries are symlinks pointing (directly or transitively) to the repo copy
- **partial** — exists in some locations but not all three, or a symlink is missing/broken
- **duplicate** — exists in multiple locations but at least one is a regular directory (not symlinked)
- **repo only** — exists in repo `skills/` but missing from both project and global
- **project only** — exists in `.claude/skills/` but not in repo `skills/`
- **global only** — exists in `~/.claude/skills/` but not in repo `skills/`

## Step 4 — Diff duplicates

For every skill with status **duplicate**:

1. Run `diff -ru` between the repo copy and whichever non-symlinked copy exists (project or global).
2. Display the diff output to the user.
3. If the diff is empty (files are identical), note that the content matches but recommend converting to a symlink for consistency.

## Step 5 — Suggest actions

After showing results, suggest next steps:
- For **duplicate** skills with differences: ask if the user wants to keep the local or repo version, then symlink.
- For **duplicate** skills without differences: offer to replace with a symlink.
- For **partial** skills: offer to create the missing symlinks.
- For **repo only** skills: offer to symlink them into both `.claude/skills/` and `~/.claude/skills/`.
- For **project only** or **global only** skills: offer to copy into the repo and replace with a symlink.
