---
name: skill-creator
description: Create new Claude Code skills from scratch or from conversation context. Guides through intent capture, SKILL.md drafting, test iteration, and description optimization. Use when users want to create a skill, turn a workflow into a skill, write a SKILL.md, or optimize skill triggering. Triggers on "create a skill", "make a skill", "turn this into a skill", "new skill".
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
---

# Skill Creator

Create new Claude Code skills and iteratively improve them through testing.

## When to Use

- Creating a new skill from scratch
- Turning an existing conversation workflow into a reusable skill
- Optimizing a skill's description for better triggering
- Drafting test prompts to validate a skill works correctly

## When NOT to Use

- Improving an existing skill with known quality issues — use `skill-improver`
- Designing complex multi-step workflow architecture — use `workflow-skill-design` first, then come back here to write the SKILL.md
- One-time tasks that don't need to be reusable

## Phase 1 — Capture Intent

Understand what the skill should do. If the current conversation already contains a workflow the user wants to capture, extract answers from context first.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Does the skill need supporting files (scripts/, references/)?

**Exit criteria:** Clear answers to all four questions, confirmed by the user.

## Phase 2 — Research

1. Check `skills/` for existing skills that overlap — avoid duplication
2. If the skill involves external tools or APIs, research their documentation
3. Note any conventions from existing skills that should be followed

**Exit criteria:** No conflicts with existing skills; sufficient domain knowledge gathered.

## Phase 3 — Write the SKILL.md

Follow repo conventions from CLAUDE.md:

### Required frontmatter
```yaml
---
name: skill-name
description: >-
  What the skill does AND when to trigger it. Be specific about trigger
  phrases and contexts. Err on the side of "pushy" — Claude tends to
  under-trigger skills, so include extra trigger keywords.
allowed-tools:
  - Read
  - Edit
  # ... only tools the skill actually uses
---
```

### Body structure
1. **Title** — `# Skill Name`
2. **When to Use** — bullet list of trigger scenarios
3. **When NOT to Use** — bullet list with specific alternatives ("use X instead")
4. **Numbered phases** — each with entry criteria, actions, and exit criteria
5. **Reference links** — point to `references/` for detailed content (keep SKILL.md under 500 lines)

### Key principles
- Use imperative voice ("Run the command", not "You should run the command")
- Put all trigger info in the `description` field — it's the only thing that controls activation
- Declare `allowed-tools` — only list tools the skill actually uses
- Keep the skill self-contained: scripts in `scripts/`, references in `references/`

**Exit criteria:** SKILL.md written and passes a self-review against the checklist above.

## Phase 4 — Test and Iterate

1. Draft 3-5 test prompts that should trigger the skill
2. Draft 2-3 negative prompts that should NOT trigger the skill
3. Review the skill's description against both sets — would Claude activate correctly?
4. If gaps are found, revise the description and body
5. Ask the user to evaluate the results

**Exit criteria:** User is satisfied with the skill's behavior.

## Phase 5 — Finalize

1. Verify the skill directory structure:
   ```
   skills/<name>/
   ├── SKILL.md          # required
   ├── scripts/          # optional
   └── references/       # optional
   ```
2. Run `skill-status` to verify consistency
3. Commit the new skill

## Description Optimization Tips

The `description` field is critical for triggering. Good descriptions:
- Start with what the skill does (verb phrase)
- Include specific trigger phrases users might say
- List related contexts where the skill applies
- Are slightly "pushy" — better to over-trigger than under-trigger
- Stay under 3 sentences for readability

**Bad:** "Helps with Docker."
**Good:** "Convert Python scripts into production-ready Docker containers with best practices. Use when users need to containerize Python applications, create Dockerfiles, or package code for deployment. Triggers on Docker, container, Dockerfile, containerize."
