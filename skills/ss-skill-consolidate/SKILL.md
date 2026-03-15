---
name: ss-skill-consolidate
description: >-
  Identify similar or overlapping skills in this repo and merge them into one
  coherent skill. Reduces maintenance burden by eliminating redundancy across
  skills that share trigger phrases, functionality, or domain. Use when the
  skill collection feels bloated, two skills seem to do the same thing, or
  after adding many skills and wanting to deduplicate.
  Triggers on "consolidate skills", "merge skills", "deduplicate skills",
  "combine skills", "overlapping skills", "too many similar skills",
  "reduce skill count", "skill overlap".
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
metadata:
  depends-on: ss-validate-skills
---

# Skill Consolidate

Identify similar or overlapping skills and merge them into fewer, more coherent skills.

## When to Use
- Two or more skills cover the same domain or trigger on similar phrases
- After a growth spurt of new skills — time to deduplicate
- Skill validation warns about trigger phrase overlap
- Users report confusion about which skill to use for a task

## When NOT to Use
- Improving a single skill's quality — use `ss-skill-craft` improve mode
- Auditing repo complexity broadly — use `ss-simplify-repo`
- Skills are genuinely distinct but related — cross-reference with `metadata.related-skills` instead

## Phase 1 — Inventory All Skills

**Entry:** User triggers consolidation.

1. Glob for all `skills/*/SKILL.md` files
2. For each skill, extract from frontmatter:
   - `name`
   - `description` (full text)
   - `allowed-tools`
   - `metadata.depends-on` (if present)
3. Build an inventory table:

| Skill | Description (first line) | Tools | Depends On |
|-------|--------------------------|-------|------------|

**Exit:** Complete inventory of all skills.

## Phase 2 — Detect Overlap

**Entry:** Inventory from Phase 1.

Analyze skills pairwise across three dimensions:

### 2a — Trigger phrase overlap
Extract trigger phrases from each skill's `description`. Compare all pairs. Flag pairs that share 3+ significant trigger keywords (ignore common words like "use", "when", "the").

### 2b — Functional overlap
Read the body of each skill. Flag pairs where:
- Both skills perform the same core action (e.g., both audit code quality)
- One skill is a strict subset of another
- Both skills produce the same type of output

### 2c — Domain overlap
Group skills by domain (e.g., "skill management", "code quality", "infrastructure", "discovery"). Flag domains with 3+ skills — these are candidates for consolidation.

### Output — Overlap Report

```markdown
## Overlap Analysis

### High Overlap (strong merge candidates)
| Skill A | Skill B | Shared Triggers | Functional Overlap | Recommendation |
|---------|---------|-----------------|-------------------|----------------|

### Medium Overlap (consider merging or cross-referencing)
| Skill A | Skill B | Shared Triggers | Functional Overlap | Recommendation |
|---------|---------|-----------------|-------------------|----------------|

### Domain Groups
| Domain | Skills | Count | Action |
|--------|--------|-------|--------|
```

**Exit:** Overlap report generated with concrete merge recommendations.

## Phase 3 — Propose Merge Plan

**Entry:** Overlap report from Phase 2.

For each recommended merge:

1. **Name the merged skill** — pick the more general name, or propose a new one (must start with `ss-`)
2. **Define the merged description** — combine trigger phrases from both, deduplicate
3. **Outline the merged body** — identify which phases/sections to keep from each source skill:
   - Sections unique to Skill A → keep
   - Sections unique to Skill B → keep
   - Overlapping sections → pick the better version or combine
   - Conflicting approaches → flag for user decision
4. **List what gets deleted** — which skill directories will be removed after merge
5. **Check dependents** — grep for any skill that has `depends-on` or references the skills being merged. These need updating.

Present the merge plan to the user:

```markdown
## Merge Plan

### Merge 1: ss-skill-a + ss-skill-b → ss-merged-name
**Rationale:** [why these should be one skill]

**Kept from ss-skill-a:**
- [sections/phases]

**Kept from ss-skill-b:**
- [sections/phases]

**Conflicts to resolve:**
- [any conflicting approaches]

**Dependents to update:**
- [skills that reference either source skill]
```

**Exit:** Merge plan presented to user.

## Phase 4 — Get User Approval

**Entry:** Merge plan from Phase 3.

Use `AskUserQuestion` to confirm:

1. **Approve all merges** — proceed with the full plan
2. **Select specific merges** — user picks which merges to execute
3. **Modify a merge** — user wants to change the merged skill name, keep different sections, etc.
4. **Cancel** — abort without changes

**Exit:** User has approved specific merges to execute.

## Phase 5 — Execute Merges

**Entry:** Approved merge plan from Phase 4.

For each approved merge:

1. **Create or update the target skill:**
   - If keeping one skill's directory, edit its SKILL.md in place
   - If creating a new name, create the directory and write the merged SKILL.md
2. **Combine supporting files:**
   - Merge `scripts/` directories if both skills have them
   - Merge `references/` directories if both skills have them
   - Resolve filename conflicts by prefixing with original skill name
3. **Update dependents:**
   - For each skill that had `depends-on` referencing a removed skill, update to the merged name
   - For any SKILL.md body text referencing the old skill name, update the reference
4. **Remove the absorbed skill directory** (the one that was merged into the other)
5. **Verify** the merged SKILL.md:
   - Frontmatter is valid YAML
   - `name` matches directory
   - `name` starts with `ss-`
   - Line count under 500 (move content to `references/` if needed)

**Exit:** All merges applied, old directories removed.

## Phase 6 — Validate and Report

**Entry:** Merges executed from Phase 5.

1. Run `ss-validate-skills` to verify repo consistency
2. Show a `git diff --stat` summary
3. Present final report:

```markdown
## Consolidation Complete

| Merge | Source Skills | Result Skill | Lines Saved |
|-------|-------------|--------------|-------------|

### Summary
- Skills before: N
- Skills after: N
- Skills removed: N
- Dependents updated: N
```

4. Ask user if they want to commit the changes.

**Exit:** Consolidation complete, repo validated.

## Guardrails

- **Never delete a skill without user approval** — always confirm before removing directories
- **Preserve all unique functionality** — merging must not lose capabilities from either source skill
- **Update all references** — broken `depends-on` or cross-references are unacceptable
- **Keep merged skill under 500 lines** — use `references/` for overflow
- **One merge at a time** — execute and validate each merge before starting the next to prevent cascading errors
