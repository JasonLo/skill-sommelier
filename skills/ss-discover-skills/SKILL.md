---
name: ss-discover-skills
description: >-
  Search GitHub for trending Claude Code skills, present a personalized ranked table,
  and install selections. Use when the user wants to find new skills, browse what's available,
  explore the skills ecosystem, or bootstrap their skill collection.
  Also serves as the "init" / bootstrap command — when called with no arguments,
  auto-generates personalized search queries from the user's profile.
  Triggers on "find skills", "discover skills", "search for skills", "what skills exist",
  "browse skills", "trending skills", "new skills", "init", "bootstrap skills",
  "setup skills", "recommended skills", "get started with skills", "what skills should I have".
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
metadata:
  depends-on: ss-user-profile
---

Discover, rank, and install Claude Code skills from GitHub. Personalized to the user's profile.

## When to Use
- Finding new Claude Code skills to install
- Browsing what's trending in the skills ecosystem
- Looking for skills for a specific domain or tool
- Bootstrapping a skill collection for the first time

## When NOT to Use
- Installing a skill you already know the URL for — just clone it directly
- Updating existing skills — use `ss-self-update` instead

## Step 1 — Load or build user profile

Read `~/.claude/user-profile.md`. If it exists, extract tech stack, interests, and project domains for ranking.

If the file does not exist, invoke the `ss-user-profile` skill to generate it (auto-saves to `~/.claude/user-profile.md`). Briefly summarize what you learned in 2-3 sentences.

## Step 2 — Parse arguments and generate search queries

`$ARGUMENTS` can contain:
- A **keyword** (e.g., `python`, `docker`) — filters search results
- A **number** — sets max results (default: 10)
- Both (e.g., `python 20`)
- Empty — no filter, auto-generate queries from profile

**If no keyword provided:** Synthesize **3 search queries** from the user profile:
1. Primary tech stack (e.g., "python", "docker", "typescript")
2. Work domain (e.g., "machine-learning", "web", "data")
3. Tool preferences or patterns (e.g., "modern-tooling", "automation", "testing")

Briefly show the queries with one-line reasoning each.

**If keyword provided:** Use that single keyword for search.

**License filtering:** Default to permissive licenses only (MIT, Apache, BSD, etc.) without asking. Skills with restrictive licenses (GPL, AGPL, LGPL, SSPL) or no license are excluded. Only ask about license preference if the user explicitly mentions wanting to see all licenses.

## Step 3 — Search GitHub for SKILL.md files

Use **two complementary search strategies** and merge results. If multiple queries were generated, run all searches in parallel.

### 3a — Code search (find SKILL.md files directly)

```bash
gh search code 'filename:SKILL.md "name:" "description:"' --limit 30 --json repository,path
```

If a keyword was provided, add it to the query string.

### 3b — Topic search (find repos tagged with skill-related topics)

```bash
gh search repos --topic=claude-code-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=claude-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=agent-skills --sort=stars --limit 20 --json fullName,url
```

For each topic-matched repo, find SKILL.md files by fetching the repo tree.

### 3c — Merge, deduplicate, and pre-filter

Combine results from all searches. Parse into `{owner, repo, path}` objects. Deduplicate by repository. Exclude this repo (`JasonLo/skill-sommelier`) from results.

**Pre-filter for speed** (critical for repos with hundreds of skills):
1. Check repo license first via `gh api repos/{owner}/{repo}/license --jq '.license.spdx_id'`. Skip the entire repo if restrictive or no license.
2. For repos with many SKILL.md files (>20), filter paths by keyword relevance to the user's search queries and profile before fetching content. Only fetch the top 5 most relevant paths per repo.
3. For repos with ≤20 SKILL.md files, fetch all.

This avoids the performance trap of validating thousands of skills from large repos.

## Step 4 — Validate candidates

For each pre-filtered candidate, fetch the file content:

```bash
gh api repos/{owner}/{repo}/contents/{path} --jq '.content'
```

Base64-decode and check for:
1. YAML frontmatter delimiters (`---`)
2. A `name:` field
3. A `description:` field

Extract `name`, `description`, and `license` values. If a skill-level `license` field overrides the repo license with a restrictive license, skip it.

## Step 5 — Fetch repo metadata

For each validated skill's repo:

```bash
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, pushed: .pushed_at}'
```

If you hit a rate limit, present partial results with a note.

## Step 6 — Rank and display table

**Filter already-installed skills:** Before ranking, read the list of existing skill directories under `skills/` and exclude any skill whose base name (without `ss-` prefix) matches an installed skill. Flag near-duplicates (e.g., similar name or overlapping description) with a note rather than silently excluding.

Rank by:
1. **Relevance** (primary) — skills matching user's tech stack, domains, and interests rank higher
2. **Stars** (secondary) — tiebreaker among equally relevant skills
3. **Recency** — last push date as final tiebreaker

Output a markdown table:

```
| # | Skill | Repository | Stars | Relevance | Description |
|---|-------|------------|-------|-----------|-------------|
| 1 | name  | owner/repo | 123   | high      | One-line description |
```

## Step 7 — Select and install

Use `AskUserQuestion` to let the user choose skills by number. Offer:
- **Install by number** — e.g., "1, 3, 5" or "all"
- **View** — show full SKILL.md content for a specific skill
- **Refine** — search again with different keywords
- **Done** — end

For each selected skill, spawn a parallel Agent to:
1. Fetch the full SKILL.md and all sibling files from GitHub
2. **Enforce `ss-` prefix:** If the skill's `name` doesn't already start with `ss-`, prefix it — directory becomes `skills/ss-{name}/` and update the `name:` field in the saved SKILL.md frontmatter to `ss-{name}`. Tell the user: "Installing as `ss-{name}` per repo naming convention."
3. Save to `skills/{name}/SKILL.md` (and `references/` if present)

Before installing, perform security review:
- **List all files** in the skill's directory
- **If executable content found** (`.sh`, `.py`, scripts/) — show content and get explicit approval
- **If no executables** — proceed directly

Report status for each installed skill.

## Error Handling

- If user profile fails (no history), use generic recommendations
- If searches find fewer than 10 results, present what was found
- If the user selects 0 skills, acknowledge and exit gracefully
- If installation fails for a skill, report the error and continue with others
