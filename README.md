# skill-sommelier

A personal [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) manager that automatically discovers, curates, and syncs skills from GitHub — tailored to your preferences and workflow.

This repo contains zero application code — no Python, no JavaScript, no programming language at all. Every capability is defined purely through natural language instructions in `SKILL.md` files, and Claude Code does the rest.

## How It Works

1. **Harvest** — Scans GitHub for Claude Code skills (`SKILL.md` files) across public repos
2. **Curate** — Ranks and recommends skills based on your personal preference profile
3. **Install** — Symlinks curated skills into `~/.claude/skills/` so they're always up to date
4. **Sync** — Keeps your skill collection portable across machines via this repo

## Skills

| Skill | Audience | Description |
|-------|----------|-------------|
| [design-postgres-tables](skills/design-postgres-tables/SKILL.md) | everyone | PostgreSQL table design reference: data types, indexes, constraints, JSONB, partitioning |
| [discover-skills](skills/discover-skills/SKILL.md) | everyone | Search GitHub for trending Claude Code skills and present a ranked table |
| [make-slides](skills/make-slides/SKILL.md) | everyone | Create animation-rich HTML presentations from scratch or convert PowerPoint files |
| [modern-python](skills/modern-python/SKILL.md) | everyone | Modern Python tooling reference: uv, ruff, ty, PEP 723 scripts, migration guides |
| [planning-with-files](skills/planning-with-files/SKILL.md) | everyone | Use persistent markdown files as working memory for complex multi-step tasks |
| [python-to-chtc](skills/python-to-chtc/SKILL.md) | everyone | Convert Python scripts into Docker/Apptainer containers for HPC environments |
| [search-first](skills/search-first/SKILL.md) | everyone | Research existing tools and libraries before writing custom code |
| [simplify-repo](skills/simplify-repo/SKILL.md) | everyone | Audit a repository for unnecessary complexity and propose simplifications |
| [skill-status](skills/skill-status/SKILL.md) | everyone | Show all repo and local skills, compare duplicates with diff |
| [sync-skills](skills/sync-skills/SKILL.md) | everyone | Sync `~/.claude/skills/` to/from this repo using symlinks |
| [user-profile](skills/user-profile/SKILL.md) | everyone | Analyze Claude Code user history to build a rich profile |
| | | |
| [self-evolve](skills/self-evolve/SKILL.md) | dev | Discover trending skills and evolve this repo by adopting valuable patterns |
| [skill-craft](skills/skill-craft/SKILL.md) | dev | Create, improve, and design Claude Code skills |

## Install

Open Claude Code and say:

> Clone https://github.com/JasonLo/skill-sommelier and symlink `~/.claude/skills` to its `skills/` directory.

Or if you already have skill-sommelier installed somewhere, use the built-in skill:

> `/sync-skills install`

To update to latest skills: `/sync-skills update`

## Development

```bash
git clone https://github.com/JasonLo/skill-sommelier.git
cd skill-sommelier
# Project-level skills work automatically via .claude/skills → ../skills symlink
```

## Adding a Skill

1. Create a directory under `skills/` with the skill name
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and instructions
3. It's immediately available in this project (via the `.claude/skills` symlink) — no restart needed
