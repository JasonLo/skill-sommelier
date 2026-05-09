---
name: ss-skill-weekly-discover
description: >-
  Automated weekly skill discovery for GitHub Actions. Uses claude-code-action
  to search GitHub for new Claude Code skills, filter against installed skills
  and user profile, and create a GitHub issue with recommendations. Triggers on
  "weekly discover", "automated discovery", "skill recommendations".
allowed-tools:
  - Read
metadata:
  depends-on: ss-skill-discover
---

Automated weekly skill discovery that runs as a GitHub Actions cron job. The workflow uses `claude-code-action` to search GitHub for new Claude Code skills, filter them against your installed skills and user profile, and create a GitHub issue with checkbox-based recommendations.

## How It Works

1. **Cron fires** (Sunday 2 PM UTC) via `.github/workflows/weekly-discover.yml`
2. **claude-code-action** runs with a discovery prompt — searches GitHub, validates candidates, ranks by relevance
3. **Issue created** with checkbox list of recommended skills
4. **User reviews** and checks desired skills
5. **User comments** `@claude install the checked skills from this issue`
6. **Claude** (via `claude.yml`) reads the issue, installs checked skills, creates a PR

## Manual Trigger

The workflow supports `workflow_dispatch` for on-demand runs.

## Configuration

Edit `.github/user-profile.md` to customize discovery keywords. The profile contains your tech stack and interests used to rank skill relevance.

## Files

- `.github/workflows/weekly-discover.yml` — cron workflow using claude-code-action
- `.github/user-profile.md` — user profile for keyword matching
