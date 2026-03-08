---
name: init
description: >-
  Bootstrap your Claude Code skill collection. Analyzes your profile, discovers
  personalized skills, and installs your selections. Use when users want to
  "get started", "bootstrap skills", "setup skills", "initialize skills",
  "personalized skill setup", or ask for recommended skills. Triggers on
  "init", "bootstrap", "get started with skills", "setup my skills",
  "what skills should I have", "recommended skills for me".
allowed-tools:
  - Skill
  - Bash
  - Read
  - Write
  - Agent
---

# Init

Bootstrap your Claude Code skill collection with personalized recommendations.

## When to Use
- Setting up Claude Code skills for the first time
- Getting personalized skill recommendations
- Bootstrapping a curated skill collection
- Finding skills that match your workflow

## When NOT to Use
- When you already know which specific skill you want — use `discover-skills` directly
- Updating existing skills — use `self-update` instead
- Browsing all available skills — use `discover-skills` without filtering

## Phase 1 — Analyze User Profile

**Entry:** User wants to bootstrap their skill collection

**IMPORTANT:** Be very explicit and transparent with the user about this step.

Say: "I'll analyze your Claude Code usage history to understand your preferences and recommend skills tailored to your workflow. This happens locally on your machine and no data leaves your system."

Then invoke the `user-profile` skill to generate or update the user profile.

Wait for the profile to complete, then briefly summarize what you learned in 2-3 sentences (e.g., "You're a Python developer who works on ML projects, prefers modern tooling, and has an active workflow").

**Exit:** User profile exists at `~/.claude/user-profile.md` and has been read successfully.

## Phase 2 — Generate Search Queries

**Entry:** User profile has been analyzed

Based on the user profile, synthesize exactly **3 search queries** that capture:
1. Primary tech stack (e.g., "python", "docker", "typescript")
2. Work domain (e.g., "machine-learning", "web", "data")
3. Tool preferences or patterns (e.g., "modern-tooling", "automation", "testing")

Make the queries specific and diverse — avoid overlap.

Present the 3 queries to the user and explain the reasoning behind each one.

**Exit:** 3 distinct search queries have been generated.

## Phase 3 — Discover Skills in Parallel

**Entry:** 3 search queries ready

Execute the `discover-skills` skill **3 times in parallel**, once for each query. Use the Skill tool to invoke:
- `/discover-skills {query1}`
- `/discover-skills {query2}`
- `/discover-skills {query3}`

Wait for all three searches to complete, then merge and deduplicate the results (same repo = same skill).

Rank the merged list by relevance to the user profile, then curate down to **exactly 10 skills**.

Present the top-10 as a markdown checklist where the user can select multiple items:

```
Select skills to install (choose as many as you want):

- [ ] 1. **skill-name** — One-line description [owner/repo]
- [ ] 2. **another-skill** — Description [owner/repo]
...
- [ ] 10. **final-skill** — Description [owner/repo]
```

Use `AskUserQuestion` to get the user's selections.

**Exit:** User has selected N skills (where N >= 0).

## Phase 4 — Refine Selected Skills in Parallel

**Entry:** User has selected N skills

For each selected skill, spawn a background agent using the Agent tool to:
1. Fetch the full SKILL.md content from GitHub
2. Invoke the `skill-craft` skill in "improve" mode to review and fix quality issues
3. Save the improved SKILL.md to `skills/{name}/SKILL.md`

All N agents should run **in parallel** for speed.

Wait for all agents to complete. For each skill, report the status:
- ✓ Skill refined and ready
- ⚠ Skill had issues that were fixed
- ✗ Skill could not be refined (rare)

**Exit:** All selected skills have been processed and saved locally.

## Phase 5 — Confirm and Complete

**Entry:** All selected skills are ready for use

Display a summary:

```
## Skills Ready

Your personalized skill collection:
1. **skill-name** — Brief description
2. **another-skill** — Brief description
...

All skills are now available in your `skills/` directory.
```

Remind the user that:
- Skills are immediately available (no restart needed)
- They can run any skill with its name as a command
- They can run `self-update` to check for updates later
- They can run `discover-skills` anytime to find more

**Exit:** Setup complete.

## Error Handling

- If `user-profile` fails (no history), explain that you'll use generic recommendations instead
- If `discover-skills` finds fewer than 10 results total, present what was found
- If a skill-craft refinement fails, install the original SKILL.md without changes
- If the user selects 0 skills, acknowledge and exit gracefully

## Privacy Notes

- All profile analysis happens locally using existing Claude Code metadata
- No data is sent to external services during profile analysis
- The user can delete `~/.claude/user-profile.md` at any time
- Only the selected skills are installed — nothing automatic
