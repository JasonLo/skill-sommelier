---
name: workflow-skill-design
description: Design and structure multi-step workflow-based Claude Code skills with numbered phases, decision trees, subagent delegation, and progressive disclosure. Use when creating skills that involve sequential pipelines, routing patterns, safety gates, phased execution, or any multi-step workflow. Also use when reviewing or refactoring existing workflow skills for quality. Triggers on "design a workflow skill", "skill architecture", "multi-step skill".
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Designing Workflow Skills

Build workflow-based skills that execute reliably by following structural patterns.

## When to Use

- Designing a new skill with multi-step workflows or phased execution
- Creating a skill that routes between multiple independent tasks
- Building a skill with safety gates (destructive actions requiring confirmation)
- Structuring a skill that uses subagents or task tracking
- Reviewing or refactoring an existing workflow skill for quality

## When NOT to Use

- Simple single-purpose skills with no workflow — just write the SKILL.md directly
- Writing the actual domain content of a skill — this teaches structure, not domain expertise
- Quick skill edits — use `skill-improver` instead

## Essential Principles

### 1. Description is the trigger

The `description` field is the **only** thing that controls when a skill activates. Claude decides whether to load a skill based solely on its frontmatter `description`. The body (including "When to Use") is only read AFTER activation.

Put trigger keywords, use cases, and exclusions in the description.

### 2. Numbered phases with entry/exit criteria

Unnumbered prose produces unreliable execution. Every phase needs:
- A number (Phase 1, Phase 2, ...)
- Entry criteria (what must be true before starting)
- Numbered actions (what to do)
- Exit criteria (how to know it's done)

### 3. Declare allowed-tools

Use `allowed-tools:` in frontmatter. Only list tools the skill actually uses. Never use Bash for operations that have dedicated tools (Glob, Grep, Read, Write, Edit).

### 4. Progressive disclosure

Keep SKILL.md under 500 lines. It contains only what's needed for every invocation:
- Principles and routing logic
- Quick references and decision trees
- Links to `references/` for detailed content

One level deep — no reference chains.

### 5. Scalable tool patterns

Every workflow instruction becomes tool calls at runtime. Design for scale:
- Combine searches into one regex, not N separate calls
- Use batching for subagents, not one per file
- Apply the 10,000-file test: mentally run the workflow against a large repo and verify tool call count stays bounded

### 6. Match specificity to fragility

Not every step needs the same level of prescription:

| Freedom Level | When to Use | Example |
|---------------|-------------|---------|
| **Low** (exact commands) | Fragile operations — migrations, crypto, destructive actions | "Run exactly this script" |
| **Medium** (pseudocode) | Preferred patterns with acceptable variation | "Use this template, customize as needed" |
| **High** (heuristics) | Variable tasks — review, exploration, documentation | "Analyze and suggest improvements" |

## Pattern Selection

Choose the right pattern for your skill's structure:

### Linear Pipeline
One path, always the same steps in order.
```
Phase 1 → Phase 2 → Phase 3 → Done
```
**Use when:** Every invocation follows the same sequence (build, deploy, test).

### Router
Multiple independent paths selected by input.
```
Input → Route A (if condition)
      → Route B (if condition)
      → Route C (default)
```
**Use when:** The skill handles several distinct sub-tasks (e.g., "sync push" vs "sync pull").

### Loop with Gate
Repeat until a quality bar is met.
```
Phase 1 → Phase 2 (check) → Pass? → Done
                            → Fail? → Phase 1
```
**Use when:** Iterative improvement (review/fix cycles, test/refine loops).

### Phased with Safety Gates
Linear pipeline with confirmation checkpoints before destructive actions.
```
Phase 1 → Phase 2 → [CONFIRM] → Phase 3 (destructive) → Done
```
**Use when:** The skill includes irreversible operations (delete, push, deploy).

## SKILL.md Template

```markdown
---
name: skill-name
description: >-
  What the skill does. When to trigger it. Specific trigger phrases.
allowed-tools:
  - Tool1
  - Tool2
---

# Skill Name

One-line summary.

## When to Use
- Scenario 1
- Scenario 2

## When NOT to Use
- Scenario — use `alternative-skill` instead
- Scenario — just do X directly

## Phase 1 — Name

**Entry:** preconditions
1. Action
2. Action
**Exit:** what's true when done

## Phase 2 — Name

**Entry:** Phase 1 complete
1. Action
2. Action
**Exit:** what's true when done
```

## Anti-Patterns to Avoid

1. **Unnumbered phases** — leads to skipped or reordered steps
2. **Prose instructions** — "then you might want to consider..." is not actionable
3. **Tool sprawl** — listing tools the skill doesn't use
4. **Reference chains** — references pointing to other references
5. **Monolithic SKILL.md** — over 500 lines without using references/
6. **Unbounded loops** — always include a max iteration count or exit condition
