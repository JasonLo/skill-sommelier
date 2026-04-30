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
| [ss-skill-weekly-discover](skills/ss-skill-weekly-discover/SKILL.md) | Automated weekly skill discovery via GitHub Actions — creates issues with checkbox recommendations |
| [ss-user-profile](skills/ss-user-profile/SKILL.md) | Analyze Claude Code user history to build a rich profile |

#### Quality

| Skill | Description |
|-------|-------------|
| [ss-skill-craft](skills/ss-skill-craft/SKILL.md) | Create, improve, and design Claude Code skills |
| [ss-skill-validate](skills/ss-skill-validate/SKILL.md) | Validate all skills for frontmatter correctness, naming conventions, and structural rules |
| [ss-skill-consolidate](skills/ss-skill-consolidate/SKILL.md) | Identify and merge overlapping skills to reduce redundancy |
| [ss-skill-tune](skills/ss-skill-tune/SKILL.md) | Self-improving skill optimization using the Karpathy autoresearch pattern |

#### Repo Management

| Skill | Description |
|-------|-------------|
| [ss-repo-evolve](skills/ss-repo-evolve/SKILL.md) | Discover trending Claude Code skills, study their implementations, and evolve this repo |
| [ss-repo-release](skills/ss-repo-release/SKILL.md) | Bump version, tag, and push to trigger the GitHub Actions release workflow |
| [ss-repo-simplify](skills/ss-repo-simplify/SKILL.md) | Audit a repository for unnecessary complexity and propose concrete simplifications |
| [ss-repo-update](skills/ss-repo-update/SKILL.md) | Check for plugin updates, show changelog, and apply them |

### My Collection

Skills discovered and installed via the sommelier — tailored to your stack.

#### Python & APIs

| Skill | Description |
|-------|-------------|
| [ss-modern-python](skills/ss-modern-python/SKILL.md) | Configure Python projects with modern tooling: uv, ruff, ty |
| [ss-fastapi-expert](skills/ss-fastapi-expert/SKILL.md) | Build high-performance async Python APIs with FastAPI and Pydantic V2 |
| [ss-fastapi-templates](skills/ss-fastapi-templates/SKILL.md) | Create production-ready FastAPI projects with async patterns and dependency injection |
| [ss-claude-api](skills/ss-claude-api/SKILL.md) | Build apps with the Claude API or Anthropic SDK |

#### ML & Training

| Skill | Description |
|-------|-------------|
| [ss-fine-tuning-expert](skills/ss-fine-tuning-expert/SKILL.md) | Fine-tune LLMs, train custom models, and adapt foundation models for specific tasks |
| [ss-pytorch-lightning](skills/ss-pytorch-lightning/SKILL.md) | High-level PyTorch framework with Trainer, distributed training, and callbacks |
| [ss-huggingface-accelerate](skills/ss-huggingface-accelerate/SKILL.md) | Distributed training API for DeepSpeed/FSDP/Megatron/DDP with automatic device placement |

#### Data & Research

| Skill | Description |
|-------|-------------|
| [ss-database-optimizer](skills/ss-database-optimizer/SKILL.md) | Optimizes database queries and improves performance across PostgreSQL and MySQL systems |
| [ss-design-postgres-tables](skills/ss-design-postgres-tables/SKILL.md) | PostgreSQL table design reference: data types, constraints, indexes, JSONB patterns, partitioning, and best practices |
| [ss-arxiv-database](skills/ss-arxiv-database/SKILL.md) | Search and retrieve preprints from arXiv via the Atom API |

#### DevOps & Containers

| Skill | Description |
|-------|-------------|
| [ss-devops-engineer](skills/ss-devops-engineer/SKILL.md) | Creates Dockerfiles, configures CI/CD pipelines, writes Kubernetes manifests, and generates Terraform/Pulumi infrastructure templates |
| [ss-python-to-chtc](skills/ss-python-to-chtc/SKILL.md) | Convert Python scripts into production-ready Docker and Apptainer/Singularity containers |
| [ss-create-release-script](skills/ss-create-release-script/SKILL.md) | Scaffold a uv-based Python release script with guards (clean tree, on-main, synced), lint+tests, atomic push, rollback, and `gh release create` |

#### Frontend

| Skill | Description |
|-------|-------------|
| [ss-web-artifacts-builder](skills/ss-web-artifacts-builder/SKILL.md) | Create elaborate HTML artifacts with React, Tailwind CSS, and shadcn/ui |
| [ss-make-slides](skills/ss-make-slides/SKILL.md) | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files |

#### Engineering Discipline

| Skill | Description |
|-------|-------------|
| [ss-diagnose](skills/ss-diagnose/SKILL.md) | Disciplined diagnosis loop for hard bugs and perf regressions: build a feedback loop, hypothesise, instrument, fix, regression-test |
| [ss-tdd](skills/ss-tdd/SKILL.md) | Test-driven development with red-green-refactor and tracer-bullet vertical slices |
| [ss-improve-architecture](skills/ss-improve-architecture/SKILL.md) | Find deepening opportunities — refactors that turn shallow modules into deep ones |
| [ss-zoom-out](skills/ss-zoom-out/SKILL.md) | Get a higher-level map of relevant modules and callers when an area is unfamiliar |
| [ss-grill](skills/ss-grill/SKILL.md) | Relentless interview about a plan — lite (Q&A only) or with-docs (updates `CONTEXT.md`/ADRs inline) |

#### Workflow & Issue Tracking

| Skill | Description |
|-------|-------------|
| [ss-to-prd](skills/ss-to-prd/SKILL.md) | Synthesise the current conversation context into a PRD and publish it to the issue tracker |
| [ss-to-issues](skills/ss-to-issues/SKILL.md) | Break a plan or PRD into independently-grabbable tracer-bullet issues |
| [ss-triage](skills/ss-triage/SKILL.md) | Move issues through a triage state machine (bug/enhancement × needs-triage/needs-info/ready-for-agent/etc.) |

#### JS/TS Tooling

| Skill | Description |
|-------|-------------|
| [ss-setup-pre-commit](skills/ss-setup-pre-commit/SKILL.md) | Set up Husky pre-commit hooks with lint-staged, Prettier, typecheck, and tests |
| [ss-migrate-shoehorn](skills/ss-migrate-shoehorn/SKILL.md) | Migrate TS test files from `as` assertions to `@total-typescript/shoehorn` |
| [ss-git-guardrails](skills/ss-git-guardrails/SKILL.md) | Install a PreToolUse hook that blocks dangerous git commands in Claude Code |

#### Productivity

| Skill | Description |
|-------|-------------|
| [ss-citation-cff](skills/ss-citation-cff/SKILL.md) | Generate CITATION.cff files for GitHub repositories with APA and BibTeX export |
| [ss-docs-update](skills/ss-docs-update/SKILL.md) | Update all documentation (README, docs/, .env.example, etc.) to reflect current repo state |
| [ss-cli2task](skills/ss-cli2task/SKILL.md) | Generate VS Code tasks.json from Python CLI commands (typer, click, argparse) |
| [ss-search-first](skills/ss-search-first/SKILL.md) | Research-before-coding workflow |
| [ss-edit-article](skills/ss-edit-article/SKILL.md) | Restructure and tighten article drafts, treating information as a DAG so prerequisites come first |
| [ss-caveman](skills/ss-caveman/SKILL.md) | Ultra-compressed reply mode that drops filler while keeping technical accuracy |

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
# Project-level skills work automatically via .claude/skills symlink
```

## Credits

Several skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the full list and license text.
