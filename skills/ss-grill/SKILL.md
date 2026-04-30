---
name: ss-grill
description: >-
  Relentless interview about a plan or design — walk down each branch of the
  decision tree, resolve dependencies between decisions one-by-one, and
  recommend an answer for each open question. Two modes: **lite** (just
  Q&A, no side-effects) and **with-docs** (challenge against `CONTEXT.md` /
  ADRs and update them inline as decisions crystallise). Use when the user
  wants to stress-test a plan, get grilled on a design, sharpen domain
  vocabulary, or capture decisions as ADRs. Triggers on "grill me",
  "interview me", "stress-test my plan", "challenge my plan", "challenge
  my design", "interrogate my approach", "grill with docs", "update
  CONTEXT.md", "update ADRs", "domain language review".
allowed-tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Bash
---

# Grill

Interview the user relentlessly about every aspect of this plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one at a time. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for the user's response before moving to the next.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.

## Modes

Pick a mode at the start of the session:

- **Lite mode** — pure Q&A. No file writes. Use when the user says "grill me" without any doc keywords, or when no `CONTEXT.md` exists and the user hasn't asked for one.
- **With-docs mode** — challenge against the existing domain model (`CONTEXT.md`, `docs/adr/`) and update those files inline as decisions land. Use when any of these are true:
  - User mentions "docs", "ADR", `CONTEXT.md`, "domain language", or "with docs"
  - A `CONTEXT.md` already exists at the repo root or in a relevant subtree
  - User explicitly asks to capture decisions

If unclear, ask the user once: "Lite (just questions) or with-docs (also update `CONTEXT.md`/ADRs)?"

When in **lite mode**, skip everything below the "## Domain awareness" heading. End the session with a summary of the resolved design tree the user can paste into a PRD, ticket, or commit message.

When in **with-docs mode**, do everything below.

## Domain awareness

During codebase exploration, also look for existing documentation:

### File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

Don't couple `CONTEXT.md` to implementation details. Only include terms that are meaningful to domain experts.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
