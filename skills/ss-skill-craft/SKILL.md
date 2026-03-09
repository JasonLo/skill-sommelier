---
name: ss-skill-craft
description: >-
  Create, improve, and design Claude Code skills. Routes between three modes:
  create (new skill from scratch), improve (fix quality issues in existing skills),
  and design (architect multi-step workflow skills). Use when users want to create
  a skill, turn a workflow into a skill, write a SKILL.md, improve skill quality,
  fix frontmatter, audit skills, design workflow architecture, or structure
  multi-step skills. Triggers on "create a skill", "make a skill", "turn this
  into a skill", "new skill", "fix my skill", "improve skill quality", "skill
  review", "audit skills", "design a workflow skill", "skill architecture",
  "multi-step skill".
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
---

# Skill Craft

Create, improve, and design Claude Code skills.

## Route Selection

Determine which mode to use based on user intent:

| Signal | Mode |
|--------|------|
| "create", "make", "new", "turn this into" | **Create** |
| "improve", "fix", "review", "audit", "polish" | **Improve** |
| "design", "architect", "workflow", "multi-step", "structure" | **Design** |

If unclear, ask the user.

---

## Mode: Create

Create a new skill from scratch or from conversation context.

### Phase 1 — Capture Intent

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Does the skill need supporting files (scripts/, references/)?

**Exit:** Clear answers to all four questions, confirmed by the user.

### Phase 2 — Research

1. Check `skills/` for existing skills that overlap
2. If the skill involves external tools or APIs, research their documentation
3. Note conventions from existing skills

**Exit:** No conflicts; sufficient domain knowledge.

### Phase 3 — Write the SKILL.md

Follow repo conventions:

**Required frontmatter:**

> All skills in this repo must use the `ss-` prefix in their name.

```yaml
---
name: ss-skill-name
description: >-
  What the skill does AND when to trigger it. Be specific about trigger
  phrases. Err on the side of "pushy" — Claude tends to under-trigger.
allowed-tools:
  - Tool1
  - Tool2
---
```

**Body structure:**
1. Title — `# Skill Name`
2. When to Use — bullet list of trigger scenarios
3. When NOT to Use — bullet list with specific alternatives
4. Numbered phases — each with entry criteria, actions, exit criteria
5. Reference links — point to `references/` for detailed content (keep under 500 lines)

**Key principles:**
- Imperative voice ("Run the command", not "You should run")
- All trigger info in `description` — it controls activation
- Only list tools the skill actually uses in `allowed-tools`
- Self-contained: scripts in `scripts/`, references in `references/`

**Exit:** SKILL.md written and passes self-review.

### Phase 4 — Test and Iterate

1. Draft 3-5 test prompts that should trigger the skill
2. Draft 2-3 negative prompts that should NOT trigger
3. Review description against both sets
4. Revise if gaps found
5. Ask user to evaluate

**Exit:** User satisfied.

### Phase 5 — Finalize

1. Verify directory structure: `skills/<name>/SKILL.md` + optional `scripts/`, `references/`
2. Commit the new skill

### Description Tips

- Start with what the skill does (verb phrase)
- Include specific trigger phrases users might say
- List related contexts
- Stay under 3 sentences

**Bad:** "Helps with Docker."
**Good:** "Convert Python scripts into production-ready Docker containers. Use when users need to containerize, create Dockerfiles, or package code. Triggers on Docker, container, Dockerfile, containerize."

---

## Mode: Improve

Review and fix quality issues in existing SKILL.md files.

### Phase 1 — Select Target

1. If user specifies a skill, use that
2. Otherwise, list all skills in `skills/` and ask
3. To audit all: iterate through each

### Phase 2 — Review

Check against this rubric:

**Critical (MUST fix — blocks loading):**
- Missing `name` or `description` in frontmatter
- Invalid YAML syntax
- Referenced files that don't exist

**Major (MUST fix — degrades effectiveness):**
- Weak/vague `description` — Claude won't trigger
- No `allowed-tools` declared
- Missing "When to Use" / "When NOT to Use"
- Second person instead of imperative voice
- SKILL.md over 500 lines without `references/`
- Phases not numbered or missing exit criteria

**Minor (evaluate before fixing):**
- Style preferences that don't affect functionality
- Optional enhancements with unclear benefit

### Phase 3 — Fix

1. Fix all critical issues immediately
2. Fix all major issues
3. For minor: only fix if genuinely improves the skill

### Phase 4 — Verify

1. Re-read the modified SKILL.md
2. Re-run checklist — all critical/major resolved
3. Verify referenced files still exist

### Phase 5 — Report

```
## Skill Review: <name>
**Issues found:** X critical, Y major, Z minor
**Issues fixed:** A critical, B major, C minor
**Issues skipped:** (list with rationale)
### Changes made:
- (bullet list)
```

### Batch Mode

When auditing all skills:
1. Run Phase 2 on every skill
2. Present summary table: `| Skill | Critical | Major | Minor | Status |`
3. Ask which to fix
4. Run Phases 3-5 on selected

---

## Mode: Design

Design multi-step workflow skills with reliable structure.

### Essential Principles

1. **Description is the trigger** — The `description` field is the ONLY thing that controls activation. Put keywords, use cases, and exclusions there.

2. **Numbered phases with entry/exit criteria** — Unnumbered prose is unreliable.

3. **Declare allowed-tools** — Only tools actually used. Never Bash for operations with dedicated tools.

4. **Progressive disclosure** — Keep SKILL.md under 500 lines. Use `references/` for details. One level deep only.

5. **Scalable tool patterns** — Combine searches into one regex. Use batching for subagents. Apply the 10,000-file test.

6. **Match specificity to fragility:**

| Freedom | When | Example |
|---------|------|---------|
| Low (exact) | Fragile ops — migrations, crypto, destructive | "Run exactly this" |
| Medium (pseudo) | Preferred patterns with variation | "Use this template" |
| High (heuristic) | Variable — review, exploration, docs | "Analyze and suggest" |

### Pattern Selection

| Pattern | When |
|---------|------|
| **Linear Pipeline** (1→2→3→Done) | Same steps every time |
| **Router** (Input→A/B/C) | Multiple independent paths by input |
| **Loop with Gate** (1→2→Pass?→Done / Fail?→1) | Iterative improvement |
| **Phased with Safety Gates** (1→2→[CONFIRM]→3) | Irreversible operations |

### SKILL.md Template

```markdown
---
name: ss-skill-name
description: >-
  What. When. Trigger phrases.
allowed-tools:
  - Tool1
---

# Skill Name

One-line summary.

## When to Use
- Scenario 1

## When NOT to Use
- Scenario — use `alternative` instead

## Phase 1 — Name
**Entry:** preconditions
1. Action
**Exit:** what's true when done

## Phase 2 — Name
**Entry:** Phase 1 complete
1. Action
**Exit:** what's true when done
```

### Anti-Patterns

1. Unnumbered phases — leads to skipped steps
2. Prose instructions — not actionable
3. Tool sprawl — listing unused tools
4. Reference chains — references pointing to references
5. Monolithic SKILL.md — over 500 lines without references/
6. Unbounded loops — always include exit condition
