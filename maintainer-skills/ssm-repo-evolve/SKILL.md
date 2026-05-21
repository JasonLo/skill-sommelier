---
name: ssm-repo-evolve
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
metadata:
  depends-on: ss-skill-discover ssm-skill-validate
---

Autonomously evolve this skill-sommelier repo by discovering trending skills, studying them, and integrating valuable ideas. Run in a loop until the user wants to stop.

## When to Use
- Periodic manual maintenance to keep the repo current with the skills ecosystem
- Looking for inspiration from trending skills
- Bulk-improving existing skills based on community patterns

> **Note:** This skill runs manually on demand. For automated weekly discovery, see `ssm-skill-weekly-discover` which uses a pure-bash GitHub Action to create recommendation issues (no Claude API needed in CI).

## When NOT to Use
- Targeted skill creation — use `ss-skill-craft` instead
- Just browsing skills without intent to change the repo — use `ss-skill-discover`

## Step 1 — Read repo context

1. Use the current repo root as `SYNC_REPO` and set `SKILLS_DIR` to `$SYNC_REPO/skills/`.
2. List all current skills in `$SKILLS_DIR` — note their names, descriptions (from SKILL.md frontmatter), and any supporting files (scripts/, references/).
3. Read the repo's `CLAUDE.md` to understand current conventions and architecture.

## Step 2 — Discover trending skills

Run the shared discovery pipeline. Do **not** re-implement search/fetch/filter
inline — `skills/ss-skill-discover/scripts/discover.sh` is the single source
of truth (shared with `ss-skill-discover` and the weekly cron):

```bash
bash skills/ss-skill-discover/scripts/discover.sh \
  --profile .github/user-profile.md \
  --limit 30 \
  --installed-dir skills \
  --exclude-repo JasonLo/skill-sommelier \
  > /tmp/evolve-candidates.json
```

The script handles code + topic search, license filtering (permissive only),
SKILL.md fetch, frontmatter parse, dedupe, installed-skill exclusion, and
ranking by `(relevance, stars, pushed_at)`. Each candidate in the JSON has
`{name, description, repo, path, stars, pushed_at, license, relevance, age_label}`.

Use the resulting JSON as the input to Step 3.

## Step 3 — Deep study and diff against existing skills

For each trending skill, classify it as **new** (no equivalent in repo) or **overlapping** (similar to an existing skill):

### 3a — New skill candidates
For skills with no equivalent in the repo:
1. Fetch the full SKILL.md via `gh api` (raw content, base64-decode).
2. Study implementation: frontmatter, phases, supporting files.
3. Assess fit: does it complement the existing collection?

### 3b — Diff overlapping skills against existing ones
For skills that overlap with an existing repo skill:
1. Fetch the external SKILL.md content.
2. Read the corresponding local skill's SKILL.md.
3. **Produce a structured diff** comparing the two side-by-side across these dimensions:

| Dimension | Local skill | External skill | Gap |
|-----------|-------------|----------------|-----|
| Scan/audit sections | What it covers | What it covers | Missing sections or techniques |
| Phases/steps | Count + names | Count + names | Missing phases or exit criteria |
| Tool usage | Listed tools | Listed tools | Tools used externally but not locally |
| Trigger phrases | Description keywords | Description keywords | Missing trigger terms |
| Supporting files | scripts/, references/ | scripts/, references/ | Missing reference material |

4. For each gap found, draft a **specific, line-level enhancement** — not just "adopt X pattern" but the actual content to add/change.

## Step 4 — Analyze and plan improvements

Based on what was discovered, identify improvements in these categories:

1. **New skills to add** — trending skills that would be valuable in this repo, adapted to fit the repo's conventions.
2. **Existing skill enhancements** — specific line-level changes derived from the Step 3b diff. Each enhancement must include: the target file, the section to modify, and the proposed content.
3. **Repo-level improvements** — patterns seen across popular skills that suggest changes to CLAUDE.md, directory structure, or conventions.

Present a summary table to the user:

| Category | Item | Source | Rationale |
|----------|------|--------|-----------|
| New skill | ... | repo/skill | Why it fits |
| Enhancement | target-skill: section | repo/skill | Specific gap from diff |
| Repo improvement | ... | repo/skill | What pattern it follows |

## Step 5 — Decide and act

For each proposed improvement:

1. **Low-risk changes** (new skills, adding scripts/references to existing skills): proceed automatically. Create the skill directory, write the SKILL.md, and add any supporting files.
2. **Medium-risk changes** (modifying existing SKILL.md instructions, changing CLAUDE.md conventions): show the proposed diff to the user and ask for approval before applying.
3. **High-risk changes** (deleting skills, restructuring the repo, changing the plugin configuration): stop and ask the user for a decision. Do not proceed without explicit approval.

After making changes:
- Run `ssm-skill-validate` to verify frontmatter and conventions are consistent.
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
