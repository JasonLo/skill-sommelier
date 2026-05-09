---
name: ss-skill-discover
description: >-
  Build a developer profile from local Claude Code history, then search GitHub
  for trending Claude Code skills, present a personalized ranked table, and
  install selections. Use when the user wants to find new skills, browse
  what's available, bootstrap their skill collection, or just inspect their
  own coding profile. Also serves as the "init" / bootstrap command — when
  called with no arguments, builds (or refreshes) the profile and
  auto-generates personalized search queries.
  Triggers on "find skills", "discover skills", "search for skills",
  "trending skills", "init", "bootstrap skills", "recommended skills",
  "what skills should I have", "my profile", "who am I", "analyze my usage",
  "developer profile", "coding habits".
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

Discover, rank, and install Claude Code skills from GitHub, personalised to a
local developer profile this skill builds and caches.

## Modes

- **Profile-only** — triggered by "my profile" / "who am I" / "developer
  profile" / "coding habits". Run Step 1, present, stop.
- **Discover** (default) — Step 1 (cached) → Steps 2–7.

## Step 1 — Load or build the profile

Cache lives at `~/.claude/user-profile.md` (outside the repo, not git-tracked).

- **Cache hit, Discover mode:** read it, extract tech stack / interests /
  domains, proceed to Step 2.
- **Cache hit, Profile-only mode:** display, offer refresh / deep-dive /
  switch-to-discover.
- **Cache miss or refresh:** build via 1a–1f, then 1g.

### 1a — Prompt history (Agent)

Spawn a general-purpose Agent on `~/.claude/history.jsonl` (each line: `display`,
`timestamp`, `project`, `sessionId`). Ask it to report:

- **Projects** — unique paths, prompt counts, sorted.
- **Time** — date range, active days; infer local TZ from the sleep gap and
  report all hours in local time; activity by time-of-day and weekday; top 10
  active days.
- **Prompts** — total, question/instruction ratio, length distribution
  (<50/50–200/200+), slash + bang commands with counts, top words and bigrams,
  tone/verbosity observations.
- **Sessions** — count, mean/median size, duration stats, top 5 longest with
  project + first prompt.
- **Tech mentions** — languages, frameworks, tools, platforms with counts.

### 1b — Insights data (if present)

Read `~/.claude/usage-data/report.html` and any JSON under
`~/.claude/usage-data/facets/`. These give richer style/personality signal than
raw history.

### 1c — Memory + project docs

Glob `~/.claude/projects/*/memory/MEMORY.md`. For the top 10 projects from 1a,
read `{project}/CLAUDE.md` if present. Read `~/.claude/settings.json` for tool
prefs and plugins.

### 1d — Git stats per top project

For each project that's a git repo:
```bash
git -C {project} remote -v 2>/dev/null | head -1
git -C {project} log --oneline -3 2>/dev/null
git -C {project} shortlog -sn --all --no-merges 2>/dev/null | head -3
```
Reveals solo-vs-team and recency.

### 1g — Synthesise and save

Synthesise into these dimensions: **Tech Stack** (languages, frameworks, dev
tools — note `uv`/`bun`/`ruff` etc. — infrastructure), **Project Portfolio**
(per project: domain, work vs personal, activity, solo vs team), **Work
Patterns** (schedule in local TZ, session style, focus, weekday vs weekend),
**Communication Style** (verbosity, tone, autonomy preference, slash-command
power-user level), **Personality Indicators** (risk tolerance, builder vs user,
learning style, customisation depth).

Write to `~/.claude/user-profile.md` with sections: TLDR, Quick Summary, Tech
Identity (table), Project Portfolio (table), Work Patterns, Communication
Style, Personality Sketch, Raw Stats. Auto-save without asking. Display in
chat.

In Profile-only mode, stop and offer: refine, deep-dive, or proceed to discover.

**Privacy:** all local; only reads existing Claude Code metadata (history,
memory, settings — never transcripts or tool output); delete the file to forget.

---

## Step 2 — Parse args, generate queries

`$ARGUMENTS` may contain a keyword, a number (max results, default 10), both,
or neither.

- **No keyword:** synthesise 3 queries from the profile (primary stack, work
  domain, tool patterns). Show them with one-line reasoning each.
- **Keyword given:** use it directly.

License filter defaults to permissive (MIT/Apache/BSD); skills with restrictive
or missing licences are excluded. Only override if the user asks.

## Step 3 — Search GitHub

Run in parallel and merge:

```bash
# Code search — direct SKILL.md hits
gh search code 'filename:SKILL.md "name:" "description:"' --limit 30 --json repository,path
# Topic search — repos tagged for skills
gh search repos --topic=claude-code-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=claude-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=agent-skills --sort=stars --limit 20 --json fullName,url
```

If a keyword is set, append it to the code search. For topic-matched repos,
fetch the tree to find SKILL.md files.

**Merge + pre-filter:** dedup by repo, exclude `JasonLo/skill-sommelier`. Check
each repo's licence (`gh api repos/{owner}/{repo}/license --jq '.license.spdx_id'`)
and skip if restrictive. For repos with >20 SKILL.md files, keep only the top 5
paths most relevant to the user's queries/profile before fetching content.

## Step 4 — Validate candidates

For each surviving path, fetch and base64-decode:
```bash
gh api repos/{owner}/{repo}/contents/{path} --jq '.content'
```
Require `---` frontmatter, `name:`, and `description:`. Extract `name`,
`description`, and any skill-level `license` (skip if it overrides the repo
licence with a restrictive one).

## Step 5 — Repo metadata

```bash
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, pushed: .pushed_at}'
```
On rate-limit, present partial results with a note.

## Step 6 — Rank and display

Exclude already-installed skills (compare base name without `ss-` prefix
against existing `skills/` dirs). Flag near-duplicates with a note instead of
silently dropping. Rank by relevance (primary), stars (tiebreak), pushed-at
(final tiebreak). Output:

```
| # | Skill | Repository | Stars | Relevance | Description |
```

## Step 7 — Select and install

Ask via `AskUserQuestion`: install by number ("1, 3, 5" or "all"), view full
SKILL.md, refine, or done.

For each selection, spawn a parallel Agent that:
1. Fetches SKILL.md and any sibling files from GitHub.
2. **Enforces `ss-` prefix** — if `name` doesn't start with `ss-`, prefix it
   (directory becomes `skills/ss-{name}/`, frontmatter `name:` updated). Tell
   the user: "Installing as `ss-{name}` per repo naming convention."
3. Saves to `skills/{name}/SKILL.md` (and `references/` if present).

**Security gate before save:** list files; if any executables (`.sh`, `.py`,
`scripts/`), show contents and require explicit approval. Otherwise proceed.

Report status per skill.

## Errors

- Profile build fails (no history) → fall back to generic recommendations.
- <10 search hits → present what was found.
- 0 selected → exit gracefully.
- Per-skill install failure → report and continue with the rest.
