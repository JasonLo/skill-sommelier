---
name: user-profile
description: >-
  Analyze Claude Code user history to build a rich profile: interests, tech stack, work patterns,
  preferences, and personality traits. Use when the user wants to understand their coding habits,
  generate a developer profile, or review how they use Claude Code. Also used by discover-skills
  for personalized ranking. Triggers on "my profile", "who am I", "analyze my usage",
  "developer profile", "coding habits", "how do I use Claude".
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Agent
---

Analyze the user's Claude Code history and project data to build a comprehensive personal profile. This helps Claude understand who the user is across sessions.

## When to Use
- Understanding your coding habits and patterns
- Generating a developer profile for personalization
- Informing other skills (discover-skills uses this for relevance ranking)

## When NOT to Use
- Shared machines where history contains multiple users' data
- When you need real-time stats — this is a point-in-time snapshot

## Step 1 — Gather data from all sources (parallelize)

Spawn an Agent to analyze prompt history while reading other sources in parallel. Skip any source that doesn't exist.

### 1a — Prompt history (delegate to Agent)

Spawn a general-purpose Agent to read and analyze `~/.claude/history.jsonl`. Each line is JSON with keys: `display` (the user's prompt), `timestamp`, `project` (working directory path), `sessionId`.

The agent should produce a structured report covering:

**Projects:** All unique project paths with prompt counts, sorted by frequency.

**Timestamps:**
- Date range (earliest to latest), total active days
- Detect timezone by finding the sleep gap (hours with near-zero activity) and mapping to the most likely UTC offset. Report all times in the inferred local timezone, not UTC.
- Activity by time of day (morning/afternoon/evening/night in local time)
- Day of week distribution
- Top 10 most active days

**Prompts:**
- Total count, questions vs instructions ratio
- Prompt length distribution (short <50 chars, medium 50-200, long 200+)
- Slash commands used (with counts)
- Bang/shell commands used (with counts)
- Top words and bigrams (excluding stopwords)
- Communication style observations (verbosity, tone, politeness, casing)

**Sessions:**
- Total sessions, average/median prompts per session
- Session size distribution and duration stats
- Top 5 longest sessions with project and first prompt

**Technology mentions:** Languages, frameworks, tools, platforms mentioned in prompts with counts.

### 1b — /insights report (if available)

Check for `~/.claude/usage-data/report.html`. If it exists, read it and extract:
- Interaction style observations
- Friction patterns and what works well
- Suggested improvements and features to try
- Impressive workflows identified

Also check `~/.claude/usage-data/facets/` for structured JSON data. These provide richer personality and style analysis than raw history alone.

### 1c — Project memory files

Glob for `~/.claude/projects/*/memory/MEMORY.md` and read each one. These contain curated notes about per-project preferences and context.

### 1d — CLAUDE.md files across projects

For each unique project path found in history (top 10 by frequency), check if `{project}/CLAUDE.md` exists and read it. These describe project purpose and conventions.

### 1e — Settings and configuration

Read `~/.claude/settings.json` for tool preferences, model settings, and plugins.

### 1f — Git contribution stats

For each project that is a git repo, run in a single bash command:
```bash
git -C {project} remote -v 2>/dev/null | head -1
git -C {project} log --oneline -3 2>/dev/null
git -C {project} shortlog -sn --all --no-merges 2>/dev/null | head -3
```

This reveals the user's commit patterns and whether they're the sole contributor or part of a team.

## Step 2 — Analyze and synthesize

Once all data is gathered, synthesize into these dimensions:

### Tech Stack
- **Languages** — inferred from project types, CLAUDE.md toolchains, and prompt mentions
- **Frameworks & Libraries** — from CLAUDE.md dependencies and prompt context
- **Dev Tools** — package managers, linters, editors, CLI tools (pay attention to `uv`, `bun`, `ruff`, etc.)
- **Infrastructure** — cloud, HPC, CI/CD, containers, databases

### Project Portfolio
For each project, determine:
- Domain (web dev, ML, data engineering, DevOps, tooling, etc.)
- Work vs personal (GitHub org repos = work, personal handle = side projects)
- Activity level (prompt count and recency)
- Solo vs team (from git shortlog)

### Work Patterns
- **Schedule** — when they work, in inferred local timezone
- **Session style** — quick bursts vs deep sessions
- **Project focus** — concentrated or scattered
- **Weekday vs weekend** — work/life separation or blended

### Communication Style
- Verbosity (median prompt length, short/long ratio)
- Tone (imperative vs conversational, formal vs casual)
- Autonomy preference (do they confirm or just say "go"?)
- Slash command power-user level (count and variety)

### Personality Indicators
- Risk tolerance — bold experiments or careful steps?
- Tool builder — do they create skills/tools or just use them?
- Learning style — "why" questions vs "how" instructions?
- Customization depth — CLAUDE.md complexity, memory files, settings

## Step 3 — Build the profile

Compose the profile in this format:

```markdown
# User Profile

> TLDR: A single sentence capturing who this person is.

## Quick Summary
2-3 sentences: role, primary domains, what makes them distinctive.

## Tech Identity
| Dimension | Details |
|-----------|---------|
| Languages | ... |
| Frameworks | ... |
| Dev Tools | ... |
| Infrastructure | ... |

## Project Portfolio
| Project | Domain | Type | Activity |
|---------|--------|------|----------|
| name | domain | work/personal | prompt count |

Brief narrative about portfolio shape (what connects the projects).

## Work Patterns
- Schedule summary (timezone, peak hours, weekday/weekend)
- Session style (burst vs marathon, median duration)
- Project focus pattern

## Communication Style
- How they talk to Claude (with specific examples from prompts)
- Autonomy level and confirmation style
- Notable habits (slash commands, bang commands, typo tolerance)

## Personality Sketch
A short narrative paragraph synthesizing personality indicators
into a human portrait. What drives this person, how they think,
what kind of developer/creator they are.

## Raw Stats
- Total prompts: N
- Unique projects: N
- Date range: X to Y (N active days)
- Sessions: N (median M prompts, median D minutes)
- Most active project: name (N prompts)
- Slash commands: N distinct
- Inferred timezone: TZ
```

## Step 4 — Present and offer next actions

Display the full profile, then offer:

1. **Save** — Write to `~/.claude/user-profile.md`
2. **Refine** — User corrects or adds context, regenerate
3. **Deep dive** — Expand any section with more analysis
4. **Done** — End

## Privacy notes

- All analysis is local, no data leaves the machine
- Only reads existing Claude Code metadata (history, memory, settings)
- Does not read conversation transcripts or tool outputs, only user prompts
- The profile can be deleted at any time by removing `~/.claude/user-profile.md`
