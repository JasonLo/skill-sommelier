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
| [discover-skills](skills/discover-skills/SKILL.md) | Search GitHub for trending Claude Code skills and present a ranked table |
| [make-slides](skills/make-slides/SKILL.md) | Create animation-rich HTML presentations from scratch or convert PowerPoint files |
| [planning-with-files](skills/planning-with-files/SKILL.md) | Use persistent markdown files as working memory for complex multi-step tasks |
| [python-to-chtc](skills/python-to-chtc/SKILL.md) | Convert Python scripts into Docker/Apptainer containers for HPC environments |
| [search-first](skills/search-first/SKILL.md) | Research existing tools and libraries before writing custom code |
| [self-evolve](skills/self-evolve/SKILL.md) | Discover trending skills and evolve this repo by adopting valuable patterns |
| [simplify-repo](skills/simplify-repo/SKILL.md) | Audit a repository for unnecessary complexity and propose simplifications |
| [skill-craft](skills/skill-craft/SKILL.md) | Create, improve, and design Claude Code skills (router: create/improve/design) |
| [skill-status](skills/skill-status/SKILL.md) | Show all repo and local skills, compare duplicates with diff |
| [sync-claude-settings](skills/sync-claude-settings/SKILL.md) | Sync `~/.claude` settings to/from a git repo for cross-machine portability |
| [sync-skills](skills/sync-skills/SKILL.md) | Sync `~/.claude/skills/` to/from this repo using symlinks |
| [user-profile](skills/user-profile/SKILL.md) | Analyze Claude Code user history to build a rich profile |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/JasonLo/skill-sommelier.git
cd skill-sommelier

# Project-level skills work automatically via .claude/skills → ../skills symlink

# For global access, symlink the entire skills directory
ln -sf "$(pwd)/skills" "$HOME/.claude/skills"
```

## Adding a Skill

1. Create a directory under `skills/` with the skill name
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and instructions
3. It's immediately available in this project (via the `.claude/skills` symlink) — no restart needed
