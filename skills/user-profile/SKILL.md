---
name: user-profile
description: Analyze Claude Code user history to build a rich profile — interests, tech stack, work patterns, preferences, and personality traits.
---

Analyze the user's Claude Code history and project data to build a comprehensive personal profile. This helps Claude understand who the user is across sessions.

## Step 1 — Gather data from all available sources

Collect data from these locations (skip any that don't exist):

### 1a — Prompt history

Read `~/.claude/history.jsonl`. Each line is JSON with keys: `display` (the user's prompt), `timestamp`, `project` (working directory path), `sessionId`.

Extract:
- All unique project paths → infer project names and domains
- All prompt texts → analyze topics, vocabulary, intent patterns
- Timestamps → analyze activity patterns (time of day, frequency, streaks)

### 1b — Project memory files

Glob for `~/.claude/projects/*/memory/MEMORY.md` and read each one. These contain curated notes about per-project preferences and context.

### 1c — CLAUDE.md files across projects

For each unique project path found in history, check if `{project}/CLAUDE.md` exists and read it. These describe the project's purpose and conventions.

### 1d — Settings and configuration

Read `~/.claude/settings.json` for tool preferences and model settings.

### 1e — Repo metadata (optional)

For projects that are git repos, run `git -C {project} remote -v` and `git -C {project} log --oneline -5` to understand what each project is about.

## Step 2 — Analyze and categorize

Process all gathered data into these profile dimensions:

### Tech Stack
- **Languages** — inferred from project types, prompts mentioning languages, file extensions
- **Frameworks** — mentioned or used across projects (e.g., Astro, Docker, React)
- **Tools** — CLI tools, editors, platforms referenced in prompts
- **Infrastructure** — cloud, HPC, CI/CD, containers mentioned

### Interests & Domains
- What problem domains do their projects cover? (web dev, data science, research, DevOps, etc.)
- What topics come up repeatedly in prompts?
- Are there hobby/side projects vs. work projects?

### Work Patterns
- **Session frequency** — how often do they use Claude Code?
- **Session depth** — do they tend toward quick one-off questions or deep multi-hour sessions?
- **Time patterns** — when are they most active? (morning/evening/weekend)
- **Project switching** — do they focus on one project or juggle many?

### Communication Style
- How do they phrase requests? (terse commands vs. detailed explanations)
- Do they use technical jargon freely or explain context?
- Tone — formal, casual, playful?
- Do they ask for opinions or just give instructions?

### Preferences & Habits
- Do they prefer certain workflows? (e.g., always commit+push, specific branching strategies)
- Code style preferences visible in their instructions
- Do they customize Claude's behavior heavily (CLAUDE.md, memory files)?
- Any explicit preferences stated in memory files

### Personality Indicators
- Risk tolerance — do they experiment boldly or proceed cautiously?
- Autonomy preference — do they delegate fully or stay hands-on?
- Learning orientation — do they ask "why" or just "how"?
- Creativity — do they explore novel approaches or stick to established patterns?

## Step 3 — Build the profile document

Compose a structured profile with these sections:

```markdown
# User Profile

## Quick Summary
> A 2-3 sentence overview of who this person is as a developer/creator.

## Tech Identity
| Dimension | Details |
|-----------|---------|
| Primary Languages | ... |
| Frameworks | ... |
| Infrastructure | ... |
| Tools | ... |

## Project Portfolio
Brief description of each discovered project and its domain.

## Interests & Domains
Ranked list of interests based on frequency and recency.

## Work Style
- Activity pattern summary
- Session behavior
- Collaboration style with AI

## Communication & Preferences
- How they interact with Claude
- Explicit preferences found in memory/settings

## Personality Sketch
A short narrative paragraph synthesizing the personality indicators
into a human portrait — what drives this person, how they think,
what kind of developer/creator they are.

## Raw Stats
- Total prompts analyzed: N
- Unique projects: N
- Date range: earliest to latest
- Most active project: ...
- Most common topics: ...
```

## Step 4 — Present and offer next actions

Display the full profile to the user, then ask:

1. **Save** — Write the profile to `~/.claude/user-profile.md` for future reference
2. **Refine** — User corrects or adds context, regenerate
3. **Deep dive** — Expand on a specific section with more analysis
4. **Done** — End

## Privacy notes

- All analysis is local — no data leaves the machine
- Only reads existing Claude Code metadata (history, memory, settings)
- Does not read conversation transcripts or tool outputs, only user prompts
- The profile can be deleted at any time by removing `~/.claude/user-profile.md`
