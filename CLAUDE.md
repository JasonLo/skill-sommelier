# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**skill-sommelier** is a personal Claude Code skills manager that discovers, curates, and syncs [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) from GitHub. Skills are `SKILL.md` files that teach Claude Code new capabilities.

The repo serves dual purposes:
1. **Skills library** — stores curated skills under `skills/`
2. **Self-managing** — includes skills (`sync-skills`, `sync-claude-settings`) that keep itself and `~/.claude/` in sync via symlinks

## Architecture

There is no build system, test suite, or application code. The repo is a pure documentation library where each skill is a `SKILL.md` with YAML frontmatter (`name`, `description`) and procedural instructions.

```
skills/
├── <skill-name>/
│   └── SKILL.md              # Required: frontmatter + instructions
│   └── scripts/              # Optional: supporting automation
│   └── references/           # Optional: reference docs for the skill
```

The project-level `.claude/skills` is a symlink to `../skills`, so Claude Code automatically sees all skills when working in this repo. For global access, `~/.claude/skills/` is symlinked per-skill:

```
.claude/skills → ../skills                          # project-level (single symlink)
~/.claude/skills/<name> → /path/to/this/repo/skills/<name>  # global (per-skill symlinks)
```

## Key Conventions

- Every skill directory must contain a `SKILL.md` with `name` and `description` in YAML frontmatter
- Skills should be self-contained — all references and scripts live inside the skill directory
- The sync repo path is stored in `~/.claude/.sync-repo`
- GitHub Actions (`.github/workflows/claude.yml`) enables `@claude` mentions on issues/PRs
