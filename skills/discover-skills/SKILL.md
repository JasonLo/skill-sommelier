---
name: discover-skills
description: >-
  Search GitHub for trending Claude Code skills and present a personalized ranked table.
  Use when the user wants to find new skills, browse what's available, or explore the skills ecosystem.
  Triggers on "find skills", "discover skills", "search for skills", "what skills exist",
  "browse skills", "trending skills", "new skills".
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Agent
  - WebFetch
---

Search GitHub for SKILL.md files that follow the Claude Code skill convention, validate them, and present a ranked table personalized to the user's profile. Optionally filter by keyword.

## When to Use
- Finding new Claude Code skills to install
- Browsing what's trending in the skills ecosystem
- Looking for skills for a specific domain or tool

## When NOT to Use
- Installing a skill you already know the URL for — just clone it directly
- Searching for general GitHub repos — use `gh search` instead

## Step 1 — Load user profile

Read `~/.claude/user-profile.md`. If it exists, extract tech stack, interests, and project domains to use for ranking in Step 5.

If the file does not exist, run the `user-profile` skill first (it will save the profile), then read the result.

Store the profile context for use in ranking.

## Step 2 — Parse arguments

`$ARGUMENTS` can contain:
- A **keyword** (e.g., `python`, `docker`) — filters search results
- A **number** — sets max results (default: 10)
- Both (e.g., `python 20`)
- Empty — no filter, 10 results

## Step 3 — Search GitHub for SKILL.md files

Use **two complementary search strategies** and merge results:

### 3a — Code search (find SKILL.md files directly)

```bash
gh search code 'filename:SKILL.md "name:" "description:"' --limit 30 --json repository,path
```

If a keyword was provided, add it to the query string.

### 3b — Topic search (find repos tagged with skill-related topics)

Search for repos using GitHub topics:

```bash
gh search repos --topic=claude-code-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=claude-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=agent-skills --sort=stars --limit 20 --json fullName,url
```

If a keyword was provided, add `--match=name,description` with the keyword. For each topic-matched repo, check if it contains a SKILL.md by fetching the repo tree or contents.

### 3c — Merge and deduplicate

Combine results from 3a and 3b. Parse into `{owner, repo, path}` objects. Deduplicate by repository (keep the first match per repo). Exclude this repo (`JasonLo/skill-sommelier`) from results.

## Step 4 — Validate candidates

For each candidate, fetch the file content:

```bash
gh api repos/{owner}/{repo}/contents/{path} --jq '.content'
```

Base64-decode the content and check for:
1. YAML frontmatter delimiters (`---`)
2. A `name:` field
3. A `description:` field
4. An optional `license:` field

Extract the `name`, `description`, and `license` values (if present). Skip files that fail validation. Stop once you have enough validated results (the max from Step 1).

## Step 5 — Fetch repo metadata

For each validated skill's repo, fetch star count and last push date:

```bash
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, pushed: .pushed_at}'
```

If you hit a rate limit, present partial results with a note.

## Step 6 — Rank and display table

Rank results using both popularity and **relevance to the user's profile**:
1. **Relevance** (primary) — skills matching the user's tech stack, domains, and interests rank higher
2. **Stars** (secondary) — tiebreaker among equally relevant skills
3. **Recency** — last push date as final tiebreaker

Output a markdown table:

```
| # | Skill | Repository | ⭐ | Relevance | Description |
|---|-------|------------|----|-----------|-------------|
| 1 | name  | [owner/repo](https://github.com/owner/repo) | 123 | high/med/low | One-line description |
```

The **Relevance** column reflects how well the skill matches the user's profile (high = directly matches tech stack or active domains, med = related area, low = unrelated but popular).

## Step 7 — Offer next actions

Use `AskUserQuestion` to let the user choose:
- **View** — show the full SKILL.md content for a specific skill
- **Install** — download the SKILL.md (and any sibling files) into `skills/<name>/`, following the security review in Step 8
- **Refine** — search again with different keywords
- **Done** — end the session

## Step 8 — Security review (on install)

Before installing a skill, perform a security review:

1. **Check license compliance:**

   a. If the skill has a `license` field in its YAML frontmatter:
      - Check if it's a permissive license: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense, CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0
      - If permissive → proceed
      - If restrictive (GPL-2.0, GPL-3.0, AGPL-3.0, SSPL, or any proprietary license) → warn user and require explicit confirmation
      - If unknown/unrecognized → warn and ask user to verify

   b. If the skill does NOT have a `license` field in frontmatter, fetch the repo's license:
      ```bash
      gh api repos/{owner}/{repo}/license --jq '{license: .license.spdx_id, url: .html_url}'
      ```
      - If repo has a permissive license → proceed (but suggest the skill author add `license:` field)
      - If repo has restrictive license → warn and require confirmation
      - If repo has no license → **warn that the code is "All Rights Reserved" by default** and require explicit user approval to proceed

   **Permissive licenses (auto-approve):**
   - MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense
   - CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0

   **Restrictive licenses (require confirmation):**
   - GPL-2.0, GPL-3.0, LGPL-2.1, LGPL-3.0, AGPL-3.0, SSPL-1.0
   - Any proprietary or source-available licenses

   **Important:** Never install skills with restrictive licenses without explicit user approval. This protects the user from licensing conflicts.

2. **List all files** in the skill's directory (not just SKILL.md):
   ```bash
   gh api repos/{owner}/{repo}/contents/{skill_directory} --jq '.[].name'
   ```

3. **Check for executable content** — look for `scripts/` directories, `.sh` files, `.py` files, or any non-markdown files.

4. **If executables are found:**
   - Fetch and display the full content of each script to the user
   - Explain what the script does in plain language
   - Use `AskUserQuestion` to get explicit approval before proceeding
   - If the user declines, skip the executables and only install the SKILL.md

5. **If no executables are found**, proceed with installation directly.

6. **Install the skill** into `skills/<name>/`, then suggest running `sync-skills`.
