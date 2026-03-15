# skill-sommelier

A personal [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) manager that automatically discovers, curates, and syncs skills from GitHub — tailored to your preferences and workflow.

This repo contains zero application code — no Python, no JavaScript, no programming language at all. Every capability is defined purely through natural language instructions in `SKILL.md` files, and Claude Code does the rest.

## How It Works

A closed-loop system where skills manage, improve, and discover other skills:

**Discover** — `ss-skill-discover` searches GitHub for trending Claude Code skills, `ss-user-profile` personalizes ranking to your stack, and `ss-skill-weekly-discover` automates this via weekly GitHub Actions issues.

**Manage** — `ss-skill-validate` enforces quality and naming conventions, `ss-skill-consolidate` merges overlapping skills to reduce bloat, and `ss-skill-craft` creates new skills from scratch.

**Evolve** — `ss-skill-tune` optimizes skills through eval loops (Karpathy autoresearch pattern), `ss-repo-evolve` adopts community patterns, and the cycle repeats — the repo uses its own skills to improve itself.

## Skills

### Meta Skills

Skills that manage the collection itself — discovery, quality, and evolution.

| Skill | Description |
|-------|-------------|
| [ss-skill-discover](skills/ss-skill-discover/SKILL.md) | Search GitHub for trending Claude Code skills and present a personalized ranked table |
| [ss-skill-craft](skills/ss-skill-craft/SKILL.md) | Create, improve, and design Claude Code skills |
| [ss-skill-validate](skills/ss-skill-validate/SKILL.md) | Validate all skills for frontmatter correctness, naming conventions, and structural rules |
| [ss-skill-consolidate](skills/ss-skill-consolidate/SKILL.md) | Identify and merge overlapping skills to reduce redundancy |
| [ss-skill-tune](skills/ss-skill-tune/SKILL.md) | Self-improving skill optimization using the Karpathy autoresearch pattern |
| [ss-skill-weekly-discover](skills/ss-skill-weekly-discover/SKILL.md) | Automated weekly skill discovery via GitHub Actions — creates issues with checkbox recommendations |
| [ss-user-profile](skills/ss-user-profile/SKILL.md) | Analyze Claude Code user history to build a rich profile |
| [ss-repo-evolve](skills/ss-repo-evolve/SKILL.md) | Discover trending Claude Code skills, study their implementations, and evolve this repo |
| [ss-repo-release](skills/ss-repo-release/SKILL.md) | Bump version, tag, and push to trigger the GitHub Actions release workflow |
| [ss-repo-simplify](skills/ss-repo-simplify/SKILL.md) | Audit a repository for unnecessary complexity and propose concrete simplifications |
| [ss-repo-update](skills/ss-repo-update/SKILL.md) | Check for plugin updates, show changelog, and apply them |
| [ss-docs-update](skills/ss-docs-update/SKILL.md) | Update all documentation (README, docs/, .env.example, etc.) to reflect current repo state |
| [ss-search-first](skills/ss-search-first/SKILL.md) | Research-before-coding workflow |

### Domain Skills

Skills that teach Claude Code specific technologies and workflows.

| Skill | Description |
|-------|-------------|
| [ss-arxiv-database](skills/ss-arxiv-database/SKILL.md) | Search and retrieve preprints from arXiv via the Atom API |
| [ss-claude-api](skills/ss-claude-api/SKILL.md) | Build apps with the Claude API or Anthropic SDK |
| [ss-database-optimizer](skills/ss-database-optimizer/SKILL.md) | Optimizes database queries and improves performance across PostgreSQL and MySQL systems |
| [ss-design-postgres-tables](skills/ss-design-postgres-tables/SKILL.md) | PostgreSQL table design reference: data types, constraints, indexes, JSONB patterns, partitioning, and best practices |
| [ss-devops-engineer](skills/ss-devops-engineer/SKILL.md) | Creates Dockerfiles, configures CI/CD pipelines, writes Kubernetes manifests, and generates Terraform/Pulumi infrastructure templates |
| [ss-fastapi-expert](skills/ss-fastapi-expert/SKILL.md) | Build high-performance async Python APIs with FastAPI and Pydantic V2 |
| [ss-fastapi-templates](skills/ss-fastapi-templates/SKILL.md) | Create production-ready FastAPI projects with async patterns and dependency injection |
| [ss-fine-tuning-expert](skills/ss-fine-tuning-expert/SKILL.md) | Fine-tune LLMs, train custom models, and adapt foundation models for specific tasks |
| [ss-huggingface-accelerate](skills/ss-huggingface-accelerate/SKILL.md) | Distributed training API for DeepSpeed/FSDP/Megatron/DDP with automatic device placement |
| [ss-make-slides](skills/ss-make-slides/SKILL.md) | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files |
| [ss-modern-python](skills/ss-modern-python/SKILL.md) | Configure Python projects with modern tooling: uv, ruff, ty |
| [ss-python-to-chtc](skills/ss-python-to-chtc/SKILL.md) | Convert Python scripts into production-ready Docker and Apptainer/Singularity containers |
| [ss-pytorch-lightning](skills/ss-pytorch-lightning/SKILL.md) | High-level PyTorch framework with Trainer, distributed training, and callbacks |
| [ss-web-artifacts-builder](skills/ss-web-artifacts-builder/SKILL.md) | Create elaborate HTML artifacts with React, Tailwind CSS, and shadcn/ui |

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
