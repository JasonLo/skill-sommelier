---
name: ssm-skill-weekly-discover
description: >-
  Automated weekly skill discovery for GitHub Actions. Runs the shared
  discovery pipeline against the user profile, filters against installed
  skills, and opens a GitHub issue with ranked recommendations. Triggers on
  "weekly discover", "automated discovery", "skill recommendations".
allowed-tools:
  - Read
metadata:
  depends-on: ss-skill-discover
---

# Weekly Skill Discovery

GitHub Actions cron that surfaces new Claude Code skills as a checkbox-based
recommendation issue. The user checks what they want and `@claude install ...`
takes it from there.

## How It Works

1. **Cron fires** (Sunday 2 PM UTC) via `.github/workflows/weekly-discover.yml`.
2. **Workflow runs `skills/ss-skill-discover/scripts/discover.sh`** with
   `--profile .github/user-profile.md`. That script — the single source of
   truth shared with `ss-skill-discover` — does GitHub search, license
   filtering, dedupe against already-installed skills, and ranking, and
   emits JSON.
3. **Workflow shapes the JSON into an issue body** with `jq` and opens it via
   `gh issue create --label skill-recommendation`. No LLM in this path.
4. **User reviews** the issue and checks desired skills.
5. **User comments** `@claude install the checked skills from this issue`.
6. **`claude.yml`** picks that up, installs checked skills, and opens a PR.

## Why this skill is thin

All discovery logic lives in `skills/ss-skill-discover/scripts/discover.sh`.
This skill exists to document the cron-driven entry point and the issue
contract — not to re-implement the pipeline. Any change to search topics,
ranking, or license rules belongs in the script, not here.

## Manual Trigger

The workflow supports `workflow_dispatch` for on-demand runs.

## Configuration

Edit `.github/user-profile.md` to shape relevance scoring. The profile is
tokenised and matched against candidate `name` + `description` text.

## Files

- `.github/workflows/weekly-discover.yml` — cron workflow (bash + `gh`)
- `.github/user-profile.md` — user profile for relevance scoring
- `skills/ss-skill-discover/scripts/discover.sh` — shared discovery pipeline
