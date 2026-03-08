# skill-sommelier

A personal [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) manager that automatically discovers, curates, and syncs skills from GitHub — tailored to your preferences and workflow.

This repo contains zero application code — no Python, no JavaScript, no programming language at all. Every capability is defined purely through natural language instructions in `SKILL.md` files, and Claude Code does the rest.

## How It Works

1. **Harvest** — Scans GitHub for Claude Code skills (`SKILL.md` files) across public repos
2. **Curate** — Ranks and recommends skills based on your personal preference profile
3. **Install** — Symlinks curated skills into `~/.claude/skills/` so they're always up to date
4. **Sync** — Keeps your skill collection portable across machines via this repo

## Installed Skills

| Skill | Description |
|-------|-------------|
| [make-slides](skills/make-slides/SKILL.md) | Create animation-rich HTML presentations from scratch or convert PowerPoint files |
| [python-to-chtc](skills/python-to-chtc/SKILL.md) | Convert Python scripts into Docker/Apptainer containers for HPC environments |
| [sync-claude-settings](skills/sync-claude-settings/SKILL.md) | Sync `~/.claude` settings to/from a git repo for cross-machine portability |
| [skill-status](skills/skill-status/SKILL.md) | Show all repo and local skills, compare duplicates with diff |
| [discover-skills](skills/discover-skills/SKILL.md) | Search GitHub for trending Claude Code skills and present a ranked table |
| [sync-skills](skills/sync-skills/SKILL.md) | Sync `~/.claude/skills/` to/from this repo using symlinks |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/JasonLo/skill-sommelier.git
cd skill-sommelier

# Project-level skills work automatically via .claude/skills → ../skills symlink

# For global access, symlink each skill into ~/.claude/skills/
for skill in skills/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/skills/$name" "$HOME/.claude/skills/$name"
done
```

## Adding a Skill

1. Create a directory under `skills/` with the skill name
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and instructions
3. It's immediately available in this project (via the `.claude/skills` symlink) — no restart needed
