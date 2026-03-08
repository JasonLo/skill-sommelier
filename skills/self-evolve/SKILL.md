---
name: self-evolve
description: >-
  Discover trending Claude Code skills, study their implementations, and evolve this repo
  by adopting valuable patterns. Runs in a loop until stopped. Use when the user wants to
  improve the skills collection, adopt community best practices, or keep the repo current.
  Triggers on "evolve", "self-evolve", "improve skills repo", "adopt new patterns",
  "update skills from community".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - Agent
---

Autonomously evolve this skill-sommelier repo by discovering trending skills, studying them, and integrating valuable ideas. Run in a loop until the user wants to stop.

## When to Use
- Periodic maintenance to keep the repo current with the skills ecosystem
- Looking for inspiration from trending skills
- Bulk-improving existing skills based on community patterns

## When NOT to Use
- Targeted skill creation — use `skill-craft` instead
- Just browsing skills without intent to change the repo — use `discover-skills`

## Step 1 — Read repo context

1. Use the current repo root as `SYNC_REPO` and set `SKILLS_DIR` to `$SYNC_REPO/skills/`.
2. List all current skills in `$SKILLS_DIR` — note their names, descriptions (from SKILL.md frontmatter), and any supporting files (scripts/, references/).
3. Read the repo's `CLAUDE.md` to understand current conventions and architecture.

## Step 2 — Discover trending skills

1. Invoke the `discover-skills` skill to search GitHub for trending Claude Code skills.
2. Collect the results — skill names, descriptions, repo URLs, and star counts.

## Step 3 — Deep study of promising candidates

For each trending skill that looks potentially valuable (not already in the repo, and relevant to a personal skills manager):

1. Use `WebFetch` to read the skill's SKILL.md or README from its GitHub repo (use raw URLs).
2. Study the implementation details: frontmatter structure, step-by-step instructions, supporting scripts, reference files.
3. Note any patterns, conventions, or techniques that differ from or improve upon what this repo does.

## Step 4 — Analyze and plan improvements

Based on what was discovered, identify improvements in these categories:

1. **New skills to add** — trending skills that would be valuable in this repo, adapted to fit the repo's conventions.
2. **Existing skill enhancements** — ideas from trending skills that could improve skills already in the repo (better instructions, missing steps, useful scripts).
3. **Repo-level improvements** — patterns seen across popular skills that suggest changes to CLAUDE.md, directory structure, or conventions.

Present a summary table to the user:

| Category | Item | Source | Rationale |
|----------|------|--------|-----------|
| New skill | ... | repo/skill | Why it fits |
| Enhancement | ... | repo/skill | What it improves |
| Repo improvement | ... | repo/skill | What pattern it follows |

## Step 5 — Decide and act

For each proposed improvement:

1. **Low-risk changes** (new skills, adding scripts/references to existing skills): proceed automatically. Create the skill directory, write the SKILL.md, and add any supporting files.
2. **Medium-risk changes** (modifying existing SKILL.md instructions, changing CLAUDE.md conventions): show the proposed diff to the user and ask for approval before applying.
3. **High-risk changes** (deleting skills, restructuring the repo, changing the plugin configuration): stop and ask the user for a decision. Do not proceed without explicit approval.

After making changes:
- Run `skill-status` to verify everything is consistent.
- Commit and push the changes (ask the user before pushing).

## Step 6 — Loop

After completing one cycle:

1. Summarize what was done in this iteration (skills added, enhancements made, things skipped).
2. Ask the user: **"Continue evolving? (yes/no)"**
   - If **yes** or no response after a reasonable pause: go back to Step 2 with fresh discovery.
   - If **no**: stop and present a final summary of all changes made across all iterations.
   - If the user gives other instructions (e.g., "focus on X", "skip Y"): incorporate the feedback and loop back to Step 2.

## Guardrails

- Never delete existing skills without explicit user approval.
- Never modify the plugin distribution method without asking.
- After adding a new feature or skill, commit and push (ask the user before pushing).
- If a discovered skill conflicts with an existing one, always ask before proceeding.
- Keep all new skills self-contained per repo conventions (SKILL.md + optional scripts/ and references/).
- Respect the YAML frontmatter format: `name` and `description` are required fields.
