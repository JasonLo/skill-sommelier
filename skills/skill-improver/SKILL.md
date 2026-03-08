---
name: skill-improver
description: Review and fix quality issues in existing Claude Code SKILL.md files through automated fix-review cycles. Use when improving skill quality, fixing frontmatter issues, strengthening trigger descriptions, enforcing conventions, or iteratively refining a skill. Triggers on "fix my skill", "improve skill quality", "skill review", "audit skills".
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
---

# Skill Improver

Iteratively review and fix quality issues in SKILL.md files until they meet standards.

## When to Use

- A skill has known quality issues (weak description, missing sections, broken references)
- Enforcing conventions across all skills in the repo
- Auditing skill quality after bulk additions
- Polishing a skill before publishing

## When NOT to Use

- Creating a new skill from scratch — use `skill-creator`
- Designing workflow architecture — use `workflow-skill-design`
- One-time quick edit — just edit the file directly

## Phase 1 — Select Target

1. If the user specifies a skill, use that
2. Otherwise, list all skills in `skills/` and ask which to review
3. To audit all skills, iterate through each one

**Exit criteria:** Target skill(s) identified.

## Phase 2 — Review

Read the target SKILL.md and check against this quality rubric:

### Critical Issues (MUST fix — blocks skill loading)

- [ ] Missing `name` in frontmatter
- [ ] Missing `description` in frontmatter
- [ ] Invalid YAML frontmatter syntax
- [ ] Referenced files (references/, scripts/) that don't exist

### Major Issues (MUST fix — degrades effectiveness)

- [ ] Weak or vague `description` — Claude won't know when to trigger
- [ ] No `allowed-tools` declared
- [ ] Missing "When to Use" section
- [ ] Missing "When NOT to Use" section (should name specific alternatives)
- [ ] Uses second person ("you should") instead of imperative voice
- [ ] SKILL.md exceeds 500 lines without using `references/`
- [ ] Phases not numbered or missing entry/exit criteria

### Minor Issues (evaluate before fixing)

- [ ] Style preferences that don't affect functionality
- [ ] Optional enhancements with unclear benefit
- [ ] Formatting suggestions with low impact

## Phase 3 — Fix

1. Fix all critical issues immediately
2. Fix all major issues
3. For each minor issue, evaluate: does fixing this genuinely improve the skill?
   - If yes, fix it
   - If unclear, skip it and note why

Apply one category at a time to keep changes reviewable.

## Phase 4 — Verify

1. Re-read the modified SKILL.md
2. Re-run the Phase 2 checklist — all critical and major issues should be resolved
3. Verify any referenced files still exist: `ls skills/<name>/references/ skills/<name>/scripts/`

**Exit criteria:** No critical or major issues remain.

## Phase 5 — Report

Present a summary:

```
## Skill Review: <name>

**Issues found:** X critical, Y major, Z minor
**Issues fixed:** A critical, B major, C minor
**Issues skipped:** (list with rationale)

### Changes made:
- (bullet list of what was changed and why)
```

## Batch Mode

When auditing all skills:

1. Run Phase 2 on every skill in `skills/`
2. Present a summary table:

| Skill | Critical | Major | Minor | Status |
|-------|----------|-------|-------|--------|
| name  | 0        | 2     | 1     | Needs fix |

3. Ask the user which skills to fix (or "all")
4. Run Phases 3-5 on selected skills
