# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commit when feature is complete

- try to commit and push when a feature is fully complete, ask user.

## Project Overview

**skill-sommelier** is a Claude Code plugin that discovers, curates, and manages [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) from GitHub. Skills are `SKILL.md` files that teach Claude Code new capabilities. Distributed via the Claude Code plugin marketplace (`/plugin marketplace add`).

## Architecture

There is no build system, test suite, or application code. The repo is a pure documentation library where each skill is a `SKILL.md` with YAML frontmatter (`name`, `description`) and procedural instructions.

**Skills only — no standalone scripts.** All functionality must be implemented as skills (SKILL.md files). Supporting scripts inside a skill directory (e.g., `scripts/`) are fine, but top-level or standalone scripts are not. If a new capability is needed (install, update, automation), create or extend a skill for it.

```
skills/
├── <skill-name>/SKILL.md
├── <skill-name>/SKILL.md
└── ...
```

For local development, a project-level symlink provides direct access to skills:

```
.claude/skills → ../skills                          # project-level dev symlink
```

## Key Conventions

- Skills follow the [Agent Skills specification](https://agentskills.io/specification)
- Every skill directory must contain a `SKILL.md` with required YAML frontmatter:
  - `name` (required): lowercase, hyphens only, **must start with `ss-`**, must match directory name
  - `description` (required): what the skill does AND when to trigger it
  - `allowed-tools` (recommended): list of tools the skill uses
  - `metadata.depends-on` (recommended): space-delimited list of skills this skill invokes or delegates to
  - `license`, `compatibility`, `metadata` (optional): per the spec
- Keep SKILL.md under 500 lines; move detailed content to `references/`
- Skills should be self-contained — all references and scripts live inside the skill directory
- The `claude.yml` workflow handles `@claude` mentions on issues/PRs

## Update Checks

When a user mentions updates, new skills, or staying current, suggest running the `self-update` skill to check for and apply plugin updates.

## Post-Commit Doc Check

After every commit, verify that related documentation is still accurate:
- CLAUDE.md sections affected by the change
- SKILL.md frontmatter (name, description, allowed-tools) matches actual behavior
- README or references if they exist in the changed skill directory

Flag any stale docs and offer to fix them before moving on.
