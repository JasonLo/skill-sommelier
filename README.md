# skill-sommelier

A personal [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) manager that automatically discovers, curates, and syncs skills from GitHub — tailored to your preferences and workflow.

This repo contains zero application code — no Python, no JavaScript, no programming language at all. Every capability is defined purely through natural language instructions in `SKILL.md` files, and Claude Code does the rest.

## How It Works

1. **Harvest** — Scans GitHub for Claude Code skills (`SKILL.md` files) across public repos
2. **Curate** — Ranks and recommends skills based on your personal preference profile
3. **Install** — Available as a Claude Code plugin via the marketplace
4. **Update** — Stay current with `/plugin marketplace update`

## Skills

| Skill | Description |
|-------|-------------|
| [ss-design-postgres-tables](skills/ss-design-postgres-tables/SKILL.md) | PostgreSQL table design reference: data types, constraints, indexes, JSONB patterns, partitioning, and best practices |
| [ss-discover-skills](skills/ss-discover-skills/SKILL.md) | Search GitHub for trending Claude Code skills and present a personalized ranked table |
| [ss-init](skills/ss-init/SKILL.md) | Bootstrap your Claude Code skill collection with personalized recommendations |
| [ss-make-slides](skills/ss-make-slides/SKILL.md) | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files |
| [ss-modern-python](skills/ss-modern-python/SKILL.md) | Configure Python projects with modern tooling: uv, ruff, ty |
| [ss-python-to-chtc](skills/ss-python-to-chtc/SKILL.md) | Convert Python scripts into production-ready Docker and Apptainer/Singularity containers |
| [ss-search-first](skills/ss-search-first/SKILL.md) | Research-before-coding workflow |
| [ss-self-evolve](skills/ss-self-evolve/SKILL.md) | Discover trending Claude Code skills, study their implementations, and evolve this repo |
| [ss-self-release](skills/ss-self-release/SKILL.md) | Bump version, tag, and push to trigger the GitHub Actions release workflow |
| [ss-self-update](skills/ss-self-update/SKILL.md) | Check for plugin updates, show changelog, and apply them |
| [ss-simplify-repo](skills/ss-simplify-repo/SKILL.md) | Audit a repository for unnecessary complexity and propose concrete simplifications |
| [ss-skill-craft](skills/ss-skill-craft/SKILL.md) | Create, improve, and design Claude Code skills |
| [ss-update-readme](skills/ss-update-readme/SKILL.md) | Scan skills/ directories and update README.md skills table to match actual repo state |
| [ss-user-profile](skills/ss-user-profile/SKILL.md) | Analyze Claude Code user history to build a rich profile |

## Install

```
/plugin marketplace add JasonLo/skill-sommelier
/plugin install skill-sommelier@skill-sommelier
```

Skills are namespaced as `/skill-sommelier:<skill-name>` (e.g., `/skill-sommelier:discover-skills`).

**Update** to latest skills: `/plugin marketplace update`

## Development

```bash
git clone https://github.com/JasonLo/skill-sommelier.git
cd skill-sommelier
# Project-level skills work automatically via .claude/skills symlink
```

## Adding a Skill

1. Create a directory under `skills/` with the skill name
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and instructions
3. It's immediately available in this project — no restart needed
