# skill-sommelier

A self-improving [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) manager. It discovers skills from GitHub, ranks them to your profile, installs them, then uses its own skills to validate, optimize, and evolve the collection — a closed loop where the tool improves itself.

The entire system is written in natural language. No Python, no JavaScript — just `SKILL.md` files that Claude Code executes directly.

## Features

- **Personalized discovery** — searches GitHub for Claude Code skills and ranks them to your stack via `ss-user-profile`
- **Automated recommendations** — weekly GitHub Actions creates issues with new skill suggestions
- **Quality enforcement** — validates frontmatter, naming conventions, and merges overlapping skills
- **Self-improving** — optimizes skills through eval loops and adopts community patterns automatically

## Skills

### Meta Skills

Skills that manage the collection itself — discovery, quality, and evolution.

#### Discovery

| Skill | Description |
|-------|-------------|
| [ss-skill-discover](skills/ss-skill-discover/SKILL.md) | Search GitHub for trending Claude Code skills and present a personalized ranked table |
| [ss-user-profile](skills/ss-user-profile/SKILL.md) | Analyze Claude Code user history to build a rich profile |

#### Quality

| Skill | Description |
|-------|-------------|
| [ss-skill-craft](skills/ss-skill-craft/SKILL.md) | Create, improve, and design Claude Code skills |

#### Repo Management

| Skill | Description |
|-------|-------------|
| [ss-repo-update](skills/ss-repo-update/SKILL.md) | Check for plugin updates, show changelog, and apply them |

### Maintainer-only skills

These live under `maintainer-skills/` and exist purely to maintain *this* repo. Claude Code only auto-loads skills under a plugin's `skills/` directory, so they are **not distributed** when end users install via `/plugin marketplace add` — only contributors with a working clone of the repo can run them.

| Skill | Description |
|-------|-------------|
| [ss-repo-evolve](maintainer-skills/ss-repo-evolve/SKILL.md) | Discover trending Claude Code skills, study their implementations, and evolve this repo |
| [ss-repo-release](maintainer-skills/ss-repo-release/SKILL.md) | Bump version, tag, and push to trigger the GitHub Actions release workflow |
| [ss-skill-validate](maintainer-skills/ss-skill-validate/SKILL.md) | Validate all skills for frontmatter correctness, naming conventions, and structural rules |
| [ss-skill-consolidate](maintainer-skills/ss-skill-consolidate/SKILL.md) | Identify and merge overlapping skills to reduce redundancy |
| [ss-skill-weekly-discover](maintainer-skills/ss-skill-weekly-discover/SKILL.md) | Automated weekly skill discovery via GitHub Actions — creates issues with checkbox recommendations |

### My Collection

Skills discovered and installed via the sommelier — tailored to your stack.

#### Python & Containers

| Skill | Description |
|-------|-------------|
| [ss-modern-python](skills/ss-modern-python/SKILL.md) | Configure Python projects with modern tooling: uv, ruff, ty |
| [ss-python-to-chtc](skills/ss-python-to-chtc/SKILL.md) | Convert Python scripts into production-ready Docker and Apptainer/Singularity containers (incl. CHTC/HPC) |

#### Engineering Discipline

| Skill | Description |
|-------|-------------|
| [ss-diagnose](skills/ss-diagnose/SKILL.md) | Disciplined diagnosis loop for hard bugs and perf regressions: build a feedback loop, hypothesise, instrument, fix, regression-test |
| [ss-tdd](skills/ss-tdd/SKILL.md) | Test-driven development with red-green-refactor and tracer-bullet vertical slices |
| [ss-improve-architecture](skills/ss-improve-architecture/SKILL.md) | Find deepening opportunities — refactors that turn shallow modules into deep ones |
| [ss-grill](skills/ss-grill/SKILL.md) | Relentless interview about a plan — lite (Q&A only) or with-docs (updates `CONTEXT.md`/ADRs inline) |

## Install

```
/plugin marketplace add JasonLo/skill-sommelier
/plugin install skill-sommelier@skill-sommelier
```

Skills are namespaced as `/skill-sommelier:<skill-name>` (e.g., `/skill-sommelier:ss-skill-discover`).

**Update** to latest skills: `/plugin marketplace update`

## Quickstart

1. Run `/skill-sommelier:ss-user-profile` to build your developer profile
2. Run `/skill-sommelier:ss-skill-discover` to find and install skills tailored to you

## Development

```bash
git clone https://github.com/JasonLo/skill-sommelier.git
cd skill-sommelier
# Project-level skills work automatically via the .claude/skills/ directory of symlinks
# (see CLAUDE.md for the rebuild command if you add or move a skill)
```

## Credits

Several skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the full list and license text.
