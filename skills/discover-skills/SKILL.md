---
name: discover-skills
description: Search GitHub for trending Claude Code skills and present a ranked table with descriptions.
allowed-tools:
  - Bash
  - Write
  - WebFetch
---

Search GitHub for SKILL.md files that follow the Claude Code skill convention, validate them, and present a ranked table. Optionally filter by keyword.

## Step 1 — Parse arguments

`$ARGUMENTS` can contain:
- A **keyword** (e.g., `python`, `docker`) — filters search results
- A **number** — sets max results (default: 10)
- Both (e.g., `python 20`)
- Empty — no filter, 10 results

## Step 2 — Search GitHub for SKILL.md files

Use **two complementary search strategies** and merge results:

### 2a — Code search (find SKILL.md files directly)

```bash
gh search code 'filename:SKILL.md "name:" "description:"' --limit 30 --json repository,path
```

If a keyword was provided, add it to the query string.

### 2b — Topic search (find repos tagged with skill-related topics)

Search for repos using GitHub topics:

```bash
gh search repos --topic=claude-code-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=claude-skills --sort=stars --limit 20 --json fullName,url
gh search repos --topic=agent-skills --sort=stars --limit 20 --json fullName,url
```

If a keyword was provided, add `--match=name,description` with the keyword. For each topic-matched repo, check if it contains a SKILL.md by fetching the repo tree or contents.

### 2c — Merge and deduplicate

Combine results from 2a and 2b. Parse into `{owner, repo, path}` objects. Deduplicate by repository (keep the first match per repo). Exclude this repo (`JasonLo/skill-sommelier`) from results.

## Step 3 — Validate candidates

For each candidate, fetch the file content:

```bash
gh api repos/{owner}/{repo}/contents/{path} --jq '.content'
```

Base64-decode the content and check for:
1. YAML frontmatter delimiters (`---`)
2. A `name:` field
3. A `description:` field

Extract the `name` and `description` values. Skip files that fail validation. Stop once you have enough validated results (the max from Step 1).

## Step 4 — Fetch repo metadata

For each validated skill's repo, fetch star count and last push date:

```bash
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, pushed: .pushed_at}'
```

If you hit a rate limit, present partial results with a note.

## Step 5 — Build and display table

Sort results by stars (descending), then by last push date (most recent first).

Output a markdown table:

```
| # | Skill | Repository | ⭐ | Description |
|---|-------|------------|----|-------------|
| 1 | name  | [owner/repo](https://github.com/owner/repo) | 123 | One-line description |
```

## Step 6 — Offer next actions

Use `AskUserQuestion` to let the user choose:
- **View** — show the full SKILL.md content for a specific skill
- **Install** — download the SKILL.md (and any sibling files) into `skills/<name>/`, following the security review in Step 7
- **Refine** — search again with different keywords
- **Done** — end the session

## Step 7 — Security review (on install)

Before installing a skill, perform a security review:

1. **List all files** in the skill's directory (not just SKILL.md):
   ```bash
   gh api repos/{owner}/{repo}/contents/{skill_directory} --jq '.[].name'
   ```

2. **Check for executable content** — look for `scripts/` directories, `.sh` files, `.py` files, or any non-markdown files.

3. **If executables are found:**
   - Fetch and display the full content of each script to the user
   - Explain what the script does in plain language
   - Use `AskUserQuestion` to get explicit approval before proceeding
   - If the user declines, skip the executables and only install the SKILL.md

4. **If no executables are found**, proceed with installation directly.

5. **Install the skill** into `skills/<name>/`, then suggest running `sync-skills`.
