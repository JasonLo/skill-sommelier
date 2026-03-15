---
name: ss-skill-tune
description: >-
  Self-improving skill optimization using the Karpathy autoresearch pattern.
  Runs a skill repeatedly, evaluates outputs against binary criteria, mutates
  the SKILL.md to keep winners, and loops until convergence. Use when the user
  wants to tune a skill, optimize a skill, improve skill quality with evals,
  auto-tune a prompt, run autoresearch, benchmark a skill, or self-improve a
  skill. Triggers on "tune skill", "skill tune", "autoresearch", "optimize
  skill", "auto-tune", "eval loop", "self-improving", "benchmark skill",
  "run evals on skill".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
---

# Autoresearch — Self-Improving Skill Optimization

Applies the Karpathy autoresearch pattern to any Claude Code skill: generate outputs, evaluate against binary criteria, keep winners, mutate the prompt, repeat.

## When to Use
- Optimizing a skill's instructions for reliability
- A skill produces inconsistent outputs and needs tuning
- Setting up automated eval loops for a skill
- User says "autoresearch", "optimize this skill", "run evals"

## When NOT to Use
- Creating a new skill from scratch — use `ss-skill-craft`
- One-time skill review without iteration — use `ss-skill-craft` improve mode
- The skill has no measurable output (pure side-effect skills like git helpers)

## Phase 1 — Select Target Skill

**Entry:** User wants to optimize a skill.

1. If user specifies a skill, read its SKILL.md
2. Otherwise, list all skills in `skills/` and ask which to optimize
3. Read the target SKILL.md fully — understand what it does, its phases, and expected outputs

**Exit:** Target skill path confirmed, SKILL.md contents understood.

## Phase 2 — Define Eval Criteria

**Entry:** Target skill selected.

Guide the user to define 3-6 binary (Yes/No) evaluation criteria. These must be:
- **Binary** — PASS or FAIL, no scales. Scales introduce variability and compound probabilities.
- **Observable** — Claude can judge from the output alone (no side-effect checking)
- **Independent** — Each criterion tests one thing
- **Not over-constrained** — Avoid narrow rules (exact word counts, specific phrases) that the model can game without improving quality

Present criteria as a table for confirmation:

| # | Name | Question (Yes = PASS) |
|---|------|-----------------------|
| 1 | legible | Is all text clear, correctly spelled, and grammatical? |
| 2 | structured | Does the output follow a clear logical structure? |
| ... | ... | ... |

Ask the user to confirm or adjust before proceeding.

**Exit:** User-confirmed list of binary eval criteria.

## Phase 3 — Define Test Prompts

**Entry:** Eval criteria confirmed.

1. Draft 5-10 diverse test prompts that trigger the target skill
2. Cover different scenarios the skill should handle
3. Include edge cases if relevant
4. Present to user for confirmation

Good test prompts:
- Exercise different code paths in the skill
- Vary in complexity (simple → complex)
- Represent real usage patterns

**Exit:** User-confirmed list of test prompts.

## Phase 4 — Create Config and Setup

**Entry:** Criteria and test prompts confirmed.

1. Create the config and data directories under the skill-tune skill:

```
skills/ss-skill-tune/runs/<target-skill>/
  config.json        # Criteria, test prompts, settings
  data/
    state.json       # Run number, best score
    results.jsonl    # Append-only experiment log
    outputs/         # Raw outputs per run
      run_001/
      run_002/
```

2. Write `config.json`:

```json
{
  "skill_path": "skills/<name>/SKILL.md",
  "eval_criteria": [
    {
      "name": "criterion_name",
      "question": "Is the output X? (Yes = PASS)"
    }
  ],
  "test_prompts": [
    "prompt 1",
    "prompt 2"
  ],
  "batch_size": 5,
  "cycle_seconds": 120,
  "max_cycles": 10,
  "eval_model": "sonnet",
  "mutate_model": "sonnet"
}
```

3. Initialize `data/state.json`: `{"best_score": -1, "run_number": 0}`

**Exit:** Config file written, directory structure created, user confirms settings.

## Phase 5 — Run Optimization Loop

**Entry:** Config and directory structure ready.

Run the autoresearch script:

```bash
python3 skills/ss-skill-tune/scripts/autoresearch.py skills/ss-skill-tune/runs/<target-skill>/config.json
```

Options:
- `--once` — single cycle (good for testing setup)
- `--cycles N` — run N cycles
- No flag — run until `max_cycles` from config

Each cycle:
1. **Generate** — Run Claude with the target SKILL.md as context + each test prompt via `claude -p` CLI (uses your current session auth, no API key needed). Save raw outputs.
2. **Evaluate** — For each output, ask Claude to judge against every binary criterion. Score = total PASSes across all outputs × all criteria.
3. **Compare** — If score > best_score, keep this SKILL.md version as the new best. Otherwise discard.
4. **Mutate** — Feed Claude the current best SKILL.md, the scores per criterion, and common failures. Claude rewrites the skill instructions to fix weaknesses. Save as the new candidate.
5. **Log** — Append run results to `results.jsonl`.
6. **Wait** — Sleep until next cycle.

**Exit:** Loop completes (max_cycles reached, perfect score, or user stops).

## Phase 6 — Review Results

**Entry:** Optimization loop finished.

1. Read `results.jsonl` and summarize:
   - Starting score vs final best score
   - Per-criterion improvement breakdown
   - Number of runs kept vs discarded
   - Score progression over cycles

2. Show the diff between original SKILL.md and optimized version
3. Ask user whether to:
   - **Accept** — replace original SKILL.md with optimized version
   - **Inspect** — show the full optimized SKILL.md for manual review
   - **Revert** — discard and keep original
   - **Continue** — run more cycles

**Exit:** User decides on final SKILL.md version.

## Phase 7 — Optional Dashboard

If the user wants live monitoring during the loop:

```bash
python3 skills/ss-skill-tune/scripts/dashboard.py skills/ss-skill-tune/runs/<target-skill>/data --port 8501
```

Serves a live dashboard at `http://localhost:8501` with:
- Score-over-time chart with keep/discard coloring
- Per-criterion breakdown charts
- Run history table
- Current best prompt display
- Auto-refreshes every 15s

## Key Principles

1. **Binary evals only** — No 1-10 scales. Binary criteria produce stable, comparable scores across runs.
2. **Always mutate from the best** — Never mutate from a losing candidate. Always use the highest-scoring SKILL.md as the mutation base.
3. **Keep it broad** — Over-constrained criteria lead to gaming (the model satisfies the letter of the rule without improving quality).
4. **Diverse test prompts** — A skill optimized on one prompt will overfit. Use 5-10 diverse prompts per batch.
5. **Know when to stop** — Diminishing returns are real. If scores plateau for 3+ cycles, stop and review.
