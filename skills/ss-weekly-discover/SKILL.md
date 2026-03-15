---
name: ss-weekly-discover
description: >-
  Automated weekly skill discovery for GitHub Actions. Searches GitHub for new
  Claude Code skills, filters against installed skills and user profile, and
  creates a GitHub issue with recommendations. Triggers on "weekly discover",
  "automated discovery", "skill recommendations".
allowed-tools:
  - Bash
  - Read
  - Glob
metadata:
  depends-on: ss-discover-skills
---

Automated weekly skill discovery that runs as a GitHub Actions cron job. The workflow searches GitHub for new Claude Code skills, filters them against your installed skills and user profile, and creates a GitHub issue with checkbox-based recommendations.

## How It Works

1. **Cron fires** (Sunday 2 PM UTC) via `.github/workflows/weekly-discover.yml`
2. **`discover.sh`** runs with only `GITHUB_TOKEN` — no Claude API needed
3. **Issue created** with checkbox list of recommended skills
4. **User reviews** and checks desired skills
5. **User comments** `@claude install the checked skills from this issue`
6. **Claude** (via `claude.yml`) reads the issue, installs checked skills, creates a PR

## Manual Trigger

The workflow supports `workflow_dispatch` for on-demand runs.

## Configuration

Edit `.github/user-profile.md` to customize discovery keywords. The profile contains your tech stack and interests used to rank skill relevance.

## Files

- `scripts/discover.sh` — headless discovery script (bash + `gh` CLI)
- `.github/workflows/weekly-discover.yml` — cron workflow
- `.github/user-profile.md` — user profile for keyword matching
