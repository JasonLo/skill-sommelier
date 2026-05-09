---
name: ss-spec-new
description: >-
  Draft a language-agnostic service or system specification in the RFC-style
  used by OpenAI's Symphony spec — RFC 2119 keywords, explicit scope boundaries,
  goals/non-goals, domain model, configuration contract, state machine, failure
  model, reference pseudocode, and a conformance checklist. Use when the user
  wants to write a SPEC.md, formalise a system contract, capture
  multi-implementation requirements, or turn a design doc into something a
  porting team could re-implement from scratch. Triggers on "write a spec",
  "draft a SPEC.md", "service specification", "system contract", "RFC-style
  spec", "spec the X", "spec this", "make this re-implementable".
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Spec New

Draft a language-agnostic service/system specification — the kind a second team could re-implement from scratch in a different language.

## When to use this skill

Use this when the artifact needs to:
- Define a contract that **multiple implementations** could conform to
- Survive porting (no language/framework details bleed into normative text)
- Make conformance auditable (reviewers can answer "does this implementation comply?" point by point)

If the user just wants a design doc, ADR, or PRD, suggest `ss-grill` (with-docs) or `ss-to-prd` instead — those have lower ceremony.

## The shape of a good spec

Symphony's SPEC.md is the reference. The 10 sections below are the simplified core. Drop sections that don't apply (e.g., omit the state-machine section for stateless components), but keep their *order* — readers learn the system top-down.

1. **Header** — title, status (`Draft v1`, `Stable v2`), one-sentence purpose
2. **Normative language** — RFC 2119 boilerplate + `Implementation-defined`
3. **Problem statement & scope boundaries** — what it solves; what's explicitly *not* its job
4. **Goals / Non-goals** — parallel bulleted lists
5. **System overview** — components + abstraction layers
6. **Domain model** — entities, fields, types, normalization rules
7. **Configuration contract** — schema, defaults, validation, dynamic reload
8. **State machine & lifecycle** — states, transition triggers (skip if stateless)
9. **Failure model** — failure classes → recovery behavior
10. **Reference algorithms** — language-agnostic pseudocode for non-obvious flows
11. **Conformance checklist** — REQUIRED vs RECOMMENDED, split by extension

Optional appendix: extensions (HTTP API, alternative transports, etc.). Each extension owns its own top-level config key and conformance section.

## Procedure

### Phase 1 — Decide if a spec is the right artifact

Before writing anything, confirm with the user:

- Will multiple teams or implementations need to conform to this?
- Is the system stable enough that an RFC-style document won't be obsolete in a week?
- Does someone need to audit conformance later?

If "no" to all three, recommend a lighter format (PRD, ADR, design doc) and stop.

### Phase 2 — Gather raw material

Before drafting, extract from the user (or existing code/docs):

- **Purpose**: one sentence. "X is a Y that does Z."
- **Boundaries**: what's in scope, what's out. Symphony's example: *"scheduler/runner and tracker reader; ticket writes are out of scope"*.
- **Components**: list the major moving parts and what each owns.
- **External dependencies**: trackers, agents, filesystems, APIs.
- **Domain entities**: nouns the system reasons about (Issue, Workspace, RunAttempt, etc.).
- **Configuration surface**: what knobs operators turn.
- **State machine**: if there's stateful orchestration, list states + transition triggers.
- **Failure modes**: ways things go wrong and how the system recovers.

If the user can't answer one of these, that section either gets omitted or marked `Implementation-defined`.

### Phase 3 — Draft from the template

Copy `references/TEMPLATE.md` to the working directory (default name `SPEC.md`) and fill it in section by section. The template has comments `<!-- ... -->` explaining each section's intent — strip them once filled.

### Phase 4 — Apply the rules

Walk the draft against the rules below before showing it to the user.

---

## Writing rules

These are the rules that make Symphony's spec sharp. Apply them aggressively.

### Use RFC 2119 keywords correctly

- **MUST / MUST NOT** — absolute requirement; non-conformant if violated
- **SHOULD / SHOULD NOT** — strong recommendation; valid reasons to deviate exist but must be understood
- **MAY / OPTIONAL** — purely permissive; either choice conforms

Don't use these words casually. If you write "the system MUST log errors", that becomes a conformance test. If logging is just a good idea, write "SHOULD" or rephrase.

### Use "Implementation-defined" deliberately

When a real choice exists but you don't want to mandate one, write `Implementation-defined` and require the implementation to **document its choice**. Symphony does this for approval policy, sandboxing, and user-input handling. This keeps the spec portable without leaving behavior undefined.

### Make scope boundaries explicit

Every spec needs a "what this is NOT" paragraph. Symphony's:

> Symphony is a scheduler/runner and tracker reader. Ticket writes are typically performed by the coding agent.

This single sentence prevents endless scope-creep arguments later.

### Every entity gets a field schema

For each domain entity, list fields with:
- name
- type (`string`, `integer`, `list of strings`, `timestamp or null`)
- nullability/optionality
- normalization rule (e.g., "labels normalized to lowercase")

If a field is derived, say from where (e.g., "`workspace_key` derived from `issue.identifier` by replacing `[^A-Za-z0-9._-]` with `_`").

### Every config field gets: name, type, default, required-ness

```
- `polling.interval_ms` (integer)
  - Default: `30000`
  - Changes SHOULD be re-applied at runtime without restart.
```

If something is REQUIRED, say so on the field. If it has a default, give the default. If `$VAR` indirection is supported, mention it.

### Every failure class gets a recovery behavior

Don't just list failures — pair each with what the system does. Symphony's pattern:

```
Tracker candidate-fetch failure: log and skip dispatch for this tick.
Reconciliation state-refresh failure: log and keep workers running.
```

### Pseudocode is for non-obvious flows only

Reference algorithms are valuable when the *order of operations* matters (poll-tick sequence, retry handling, reconciliation). They are noise when the flow is "call this function, then return". Include 3–6 small pseudocode blocks max. Use `text` code blocks, not a real language.

### Conformance checklist is the audit surface

Every MUST in the body should have a corresponding bullet in the conformance checklist. Split into:
- **Core conformance** — what every implementation must do
- **Extension conformance** — only required if the extension is implemented
- **Integration profile** — environment-dependent smoke tests (often skipped in CI)

If you can't write a yes/no test for a checklist item, the requirement is too vague — go fix it in the body.

### Extensions are first-class but isolated

Optional features (HTTP server, alternative trackers) live in appendices. Each appendix:
- Owns a top-level config key (e.g., `server.*`, `worker.*`)
- States that core conformance does **not** require it
- Has its own mini-conformance section

This lets implementations stay small without making the spec lie about what's required.

---

## Common mistakes to avoid

- **Mixing prescription and description.** The spec says what implementations must do, not what *this* implementation does. If you find yourself writing "the Python code uses asyncio", lift it to a normative requirement ("the runtime MUST process events concurrently") or move it to an implementation note.
- **Burying requirements in prose.** Numbered lists, bullets, and bold keywords make conformance auditable. Prose paragraphs hide MUSTs.
- **Skipping the failure model.** Specs that only describe the happy path produce implementations that disagree about error behavior. Always include Section 9.
- **Letting examples become normative.** If you show a JSON shape, mark it `Suggested response shape:` not `Required response shape:` unless the field set really is required.
- **Versioning the spec implicitly.** Put a `Status: Draft v1` line at the top. When you make a breaking change, bump the version and note it.

---

## Output

Default output path: `SPEC.md` in the user's working directory (or wherever they specify). After writing, point out:

- Which sections you filled vs. left as `TODO` or `Implementation-defined`
- The conformance checklist size — if it's under ~10 items the spec is probably too thin; if it's over 100 the spec is probably too prescriptive

Then offer to grill the spec with `ss-grill` to find weak spots before it ships.
