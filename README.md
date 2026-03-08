# prompt-sync

A library of reusable [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills). Each skill is a `SKILL.md` file that teaches Claude Code a new capability.

## Available Skills

| Skill | Description |
|-------|-------------|
| [make-slides](skills/make-slides/SKILL.md) | Create animation-rich HTML presentations from scratch or convert PowerPoint files |
| [sync-claude-settings](skills/sync-claude-settings/SKILL.md) | Sync `~/.claude` settings to/from a git repo for cross-machine portability |

## Installing a Skill

Copy the skill's `SKILL.md` into your Claude Code skills directory:

```bash
# Example: install make-slides
mkdir -p ~/.claude/skills/make-slides
cp skills/make-slides/SKILL.md ~/.claude/skills/make-slides/SKILL.md
```

Or for a project-local install:

```bash
mkdir -p .claude/skills/make-slides
cp skills/make-slides/SKILL.md .claude/skills/make-slides/SKILL.md
```

## Adding a New Skill

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and instructions
3. Open a PR
