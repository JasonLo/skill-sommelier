---
name: planning-with-files
description: >-
  Use persistent markdown files as working memory for complex multi-step tasks.
  Creates task_plan.md, findings.md, and progress.md to track phases, decisions,
  and discoveries. Use when asked to plan, break down, or organize a multi-step
  project, research task, or any work requiring many tool calls. Triggers on
  "plan this", "break this down", "organize this project", "complex task".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Planning with Files

Use persistent markdown files as working memory for complex tasks.

## When to Use

- Multi-step projects requiring 5+ tool calls
- Research tasks that accumulate findings over time
- Any work where losing context mid-task would be costly
- Tasks that might span multiple sessions

## When NOT to Use

- Simple single-step tasks (quick edits, one-off questions)
- Tasks where all context fits easily in the conversation

## Core Pattern

```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)

Anything important gets written to disk.
```

## Phase 1 — Create Planning Files

Before starting any complex task, create three files in the project root:

### task_plan.md
```markdown
# Task Plan

## Objective
One-sentence goal.

## Phases

### Phase 1 — Name
- [ ] Step 1
- [ ] Step 2
Status: not_started

### Phase 2 — Name
- [ ] Step 1
Status: not_started

## Decisions
| Decision | Rationale | Date |
|----------|-----------|------|

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
```

### findings.md
```markdown
# Findings

## Key Discoveries
- (logged as discovered)

## Research Notes
- (logged during exploration)
```

### progress.md
```markdown
# Progress Log

## Session: YYYY-MM-DD
- Started: HH:MM
- (actions logged as completed)
```

**Exit criteria:** All three files exist in the project root.

## Phase 2 — Work with the 2-Action Rule

While executing the task:

1. After every **2 search/read/browse operations**, save key findings to `findings.md`
2. Before any **major decision**, re-read `task_plan.md` to refresh goals in context
3. After completing any **phase**, update `task_plan.md`:
   - Mark steps as complete: `- [ ]` to `- [x]`
   - Update phase status: `not_started` → `in_progress` → `complete`
   - Log any errors encountered

## Phase 3 — Handle Errors

Every error goes in the plan file. This prevents repeating failures.

```markdown
## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError | 1 | Created default config |
| API timeout | 2 | Added retry logic |
```

**Rule:** Never repeat a failed action without changing the approach.

## Phase 4 — Session Recovery

If resuming work after a break or `/clear`:

1. Read `task_plan.md` — check phase statuses
2. Read `progress.md` — see what was done last
3. Read `findings.md` — recover research context
4. Run `git diff --stat` to see code changes since last session
5. Resume from the first incomplete phase

## Critical Rules

1. **Create plan first** — never start a complex task without `task_plan.md`
2. **2-action rule** — save findings after every 2 search/read operations
3. **Read before decide** — re-read the plan before major decisions
4. **Update after act** — mark phases complete as you go
5. **Log all errors** — every failure gets recorded with its resolution
6. **Never repeat failures** — change approach before retrying
