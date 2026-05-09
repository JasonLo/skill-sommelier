<!--
  Spec template — simplified RFC-style.
  Strip these <!-- ... --> comments once each section is filled.
  Drop sections that don't apply (e.g., omit §7 for a stateless component),
  but keep the remaining sections in order.
-->

# {{System Name}} Specification

Status: Draft v1 (language-agnostic)

Purpose: {{One sentence — "X is a Y that does Z."}}

## Normative Language

The key words `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`, `SHOULD NOT`, `RECOMMENDED`, `MAY`, and
`OPTIONAL` in this document are to be interpreted as described in RFC 2119.

`Implementation-defined` means the behavior is part of the implementation contract, but this
specification does not prescribe one universal policy. Implementations MUST document the selected
behavior.

## 1. Problem Statement

<!--
  3–6 sentences. Describe what the system does, what operational problems it solves,
  and the trust/safety posture (if any).
-->

{{Describe the system in plain language. What does it do? Why does it exist?}}

The service solves these operational problems:

- {{Problem 1}}
- {{Problem 2}}
- {{Problem 3}}

**Boundaries** (what this is NOT):

- {{Out-of-scope concern 1 — e.g., "writing back to the issue tracker"}}
- {{Out-of-scope concern 2}}

## 2. Goals and Non-Goals

### 2.1 Goals

- {{Goal 1 — should be testable / observable}}
- {{Goal 2}}
- {{Goal 3}}

### 2.2 Non-Goals

- {{Non-goal 1 — explicit, prevents scope creep}}
- {{Non-goal 2}}

## 3. System Overview

### 3.1 Components

<!-- One numbered entry per major moving part. Each lists what the component owns. -->

1. `{{Component Name}}`
   - {{What it does}}
   - {{What it owns}}

2. `{{Component Name}}`
   - {{What it does}}

### 3.2 Abstraction Layers

<!--
  How the components stack. Use this to make porting easy — readers should be able
  to swap out one layer without touching the others.
-->

1. `Policy Layer` — {{repo-defined rules, prompts}}
2. `Configuration Layer` — {{typed getters, defaults, env resolution}}
3. `Coordination Layer` — {{orchestration, scheduling}}
4. `Execution Layer` — {{the actual work}}
5. `Integration Layer` — {{external system adapters}}
6. `Observability Layer` — {{logs, metrics, status surface}}

### 3.3 External Dependencies

- {{Dependency 1 — e.g., "PostgreSQL 14+"}}
- {{Dependency 2}}

## 4. Domain Model

<!--
  Each entity gets: a one-line purpose, then fields with type / nullability / normalization.
-->

### 4.1 `{{EntityName}}`

{{One-line purpose.}}

Fields:

- `id` (string) — {{stable identifier}}
- `name` (string)
- `state` (string) — {{normalized to lowercase}}
- `created_at` (timestamp or null)

### 4.2 `{{EntityName}}`

Fields:

- `field_name` (type) — {{notes}}

### 4.3 Identifier and Normalization Rules

- `{{IdName}}` — {{how it's derived, what charset}}
- Compare `{{state-like field}}` after `lowercase`.

## 5. Configuration Contract

### 5.1 Source and Resolution

<!--
  Where config comes from (file, env, CLI), and the resolution order.
-->

Configuration is resolved in this order:

1. {{Highest-precedence source}}
2. {{Next source}}
3. Built-in defaults

### 5.2 Schema

<!--
  Group config under top-level keys. For each field: type, default, required-ness.
  This section IS the cheat sheet — don't duplicate.
-->

#### `{{section_key}}` (object)

- `{{field}}` ({{type}})
  - REQUIRED. {{Description.}}
- `{{field}}` ({{type}})
  - Default: `{{value}}`
  - {{Description and any reload semantics.}}

#### `{{section_key}}` (object)

- `{{field}}` ({{type}})
  - Default: `{{value}}`

### 5.3 Validation

Startup validation:

- Validate configuration before starting.
- If validation fails, fail startup and emit an operator-visible error.

Runtime validation:

- {{When and how the system re-validates}}.

### 5.4 Dynamic Reload (OPTIONAL — keep if config can change at runtime)

- The software MUST detect changes to the config source.
- On change, it MUST re-apply config without restart.
- Invalid reloads MUST NOT crash the service; keep the last known good config and emit a warning.

## 6. State Machine and Lifecycle

<!--
  Drop this whole section for stateless components.
  Otherwise: list states, list lifecycle phases inside one "attempt" or "run",
  list transition triggers.
-->

### 6.1 States

1. `{{State1}}` — {{condition}}
2. `{{State2}}` — {{condition}}
3. `{{Terminal state}}` — {{condition}}

### 6.2 Lifecycle Phases

A single {{run / attempt / request}} transitions through:

1. `Preparing`
2. `Running`
3. `Finishing`
4. `Succeeded` | `Failed` | `TimedOut` | `Cancelled`

### 6.3 Transition Triggers

- `{{Trigger}}` — {{what it does to state}}
- `{{Trigger}}` — {{...}}

### 6.4 Idempotency Rules

- {{Mutations serialized through one authority}}.
- {{Duplicate-dispatch checks}}.

## 7. Failure Model and Recovery

### 7.1 Failure Classes

1. `{{Class}}` — {{e.g., Configuration failures}}
   - {{specific failures}}
2. `{{Class}}` — {{e.g., External dependency failures}}
   - {{specific failures}}
3. `{{Class}}` — {{e.g., Internal execution failures}}
   - {{specific failures}}

### 7.2 Recovery Behavior

<!-- Pair each failure class with what the system does. -->

- {{Class 1 failures}}: {{response — e.g., "skip new work, keep service alive, retry on next tick"}}.
- {{Class 2 failures}}: {{response}}.
- {{Class 3 failures}}: {{response}}.

### 7.3 Restart Recovery

- {{What survives restart}}.
- {{What does not}}.
- {{How the service rebuilds useful state on startup}}.

## 8. Reference Algorithms

<!--
  Pseudocode for the non-obvious flows. 3–6 blocks max. Use `text` code blocks.
  Drop this section if all the flows are obvious from §6.
-->

### 8.1 {{Flow Name — e.g., Startup}}

```text
function start():
  load_config()
  validate_or_fail()
  initialize_state()
  schedule_first_tick()
  event_loop()
```

### 8.2 {{Flow Name}}

```text
on_tick(state):
  state = reconcile(state)
  if validation_fails: skip dispatch
  for item in fetch_candidates():
    if no_slots: break
    if eligible(item): state = dispatch(item, state)
  schedule_next_tick()
  return state
```

## 9. Security and Operational Safety

<!-- Keep concise — most projects don't need all subsections. -->

### 9.1 Trust Boundary

{{State whether the system is intended for trusted environments, restricted environments, or both.}}

### 9.2 Mandatory Invariants

- {{Path safety, sandbox boundary, etc.}}
- {{Input validation that must hold before {{action}}}}.

### 9.3 Secret Handling

- Support `$VAR` indirection in config.
- Do not log secrets.
- Validate presence of secrets without printing them.

## 10. Conformance Checklist

<!--
  Every MUST in the body should map to a bullet here.
  Each bullet should be a yes/no test someone could run.
-->

### 10.1 Core Conformance (REQUIRED)

- {{Component X loads config from the documented sources}}
- {{Validation rejects invalid `{{field}}` at startup}}
- {{Failure class Y produces the documented recovery behavior}}
- {{Identifier sanitization enforces `[A-Za-z0-9._-]`}}
- {{Logs include the documented context fields}}

### 10.2 Extension Conformance (REQUIRED only if extension is shipped)

- If the {{HTTP server / alternative tracker / ...}} extension is implemented:
  - {{Specific behavior 1}}
  - {{Specific behavior 2}}

### 10.3 Integration Profile (RECOMMENDED for production)

- A real {{external dependency}} smoke test passes with valid credentials.
- {{Other environment-dependent checks}}.

---

## Appendix A. {{Optional Extension Name}}

<!--
  Use appendices for optional extensions. Each appendix:
  - States it is OPTIONAL and not required for core conformance
  - Defines its own top-level config key
  - Has its own mini conformance list
-->

This appendix is OPTIONAL and is not required for core conformance.

### A.1 Configuration

- `{{ext_key}}.{{field}}` ({{type}}, OPTIONAL)
  - {{Description}}

### A.2 Behavior

{{What the extension does and how it integrates with the core.}}

### A.3 Conformance

If this extension is implemented:

- {{Behavior 1}}
- {{Behavior 2}}
