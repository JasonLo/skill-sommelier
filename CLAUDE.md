# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commit when feature is complete

- try to commit and push when a feature is fully complete, ask user.

## Project Overview

**skill-sommelier** is a personal Claude Code skills manager that discovers, curates, and syncs [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) from GitHub. Skills are `SKILL.md` files that teach Claude Code new capabilities.

The repo serves dual purposes:
1. **Skills library** — stores curated general-purpose skills under `skills/`
2. **Self-managing** — includes meta skills (`sync-skills`, `sync-claude-settings`, `skill-craft`, etc.) that keep itself and `~/.claude/` in sync via symlinks

Skills fall into two categories:
- **Meta** — manage this repo and your Claude Code environment (discover-skills, self-evolve, skill-craft, skill-status, sync-claude-settings, sync-skills)
- **Curated** — general-purpose skills for everyday workflows (make-slides, planning-with-files, python-to-chtc, search-first, simplify-repo, user-profile)

## Architecture

There is no build system, test suite, or application code. The repo is a pure documentation library where each skill is a `SKILL.md` with YAML frontmatter (`name`, `description`) and procedural instructions.

```
skills/
├── <skill-name>/
│   └── SKILL.md              # Required: frontmatter + instructions
│   └── scripts/              # Optional: supporting automation
│   └── references/           # Optional: reference docs for the skill
```

All skill directories are flat under `skills/` — Claude Code does not discover skills recursively.

Both project-level and global skills use a single directory symlink to the repo:

```
.claude/skills → ../skills                          # project-level
~/.claude/skills → /path/to/this/repo/skills        # global
```

## Key Conventions

- Skills follow the [Agent Skills specification](https://agentskills.io/specification)
- Every skill directory must contain a `SKILL.md` with required YAML frontmatter:
  - `name` (required): lowercase, hyphens only, must match directory name
  - `description` (required): what the skill does AND when to trigger it
  - `allowed-tools` (recommended): space-delimited list of tools the skill uses
  - `license`, `compatibility`, `metadata` (optional): per the spec
- Keep SKILL.md under 500 lines; move detailed content to `references/`
- Skills should be self-contained — all references and scripts live inside the skill directory
- The sync repo path is stored in `~/.claude/.sync-repo`
- GitHub Actions (`.github/workflows/claude.yml`) enables `@claude` mentions on issues/PRs

## Post-Commit Doc Check

After every commit, verify that related documentation is still accurate:
- CLAUDE.md sections affected by the change
- SKILL.md frontmatter (name, description, allowed-tools) matches actual behavior
- README or references if they exist in the changed skill directory

Flag any stale docs and offer to fix them before moving on.

## Post-Skill-Run Review

After every skill execution, briefly review the run and suggest improvements in three areas:

1. **Speed** — Could fewer tool calls, parallel execution, or simpler logic make this skill run faster?
2. **Usefulness** — One small, concrete enhancement that would make the output more valuable without adding complexity.
3. **Overlap** — Does this skill duplicate functionality with another skill in the repo? If so, recommend consolidation.

Keep each suggestion to one sentence. Skip any area where there's nothing actionable.

Ask user whether they want to improve the skill based on the review.
