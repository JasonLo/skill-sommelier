---
name: ss-autoresearch
description: >-
  Orchestrates end-to-end autonomous AI research projects using a two-loop
  architecture. The inner loop runs rapid experiment iterations; the outer loop
  synthesizes results, identifies patterns, and steers research direction.
  Produces research presentations and papers. Use when asked to run autonomous
  research, design and execute ML experiments end-to-end, or generate a research
  report from a hypothesis.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Agent
  - WebFetch
  - WebSearch
metadata:
  source: K-Dense-AI/claude-scientific-skills
  depends-on: ss-ml-paper-writing ss-arxiv-database
---

# AutoResearch — Autonomous AI Research Loop

Orchestrates end-to-end AI research using a two-loop architecture. The outer
loop steers direction; the inner loop executes experiments rapidly. Outputs
include structured findings, analysis notebooks, and draft papers.

---

## Architecture

```
Outer Loop (strategic)
  └─ sets hypothesis, reads inner-loop summaries, adjusts direction
     Inner Loop (tactical)
       └─ runs experiment → collects metrics → writes summary → repeats
```

---

## Phase 0 — Frame the Research Question

1. Clarify the research objective with the user (one clear hypothesis).
2. Identify baselines, datasets, and evaluation metrics.
3. Create `research/plan.md` with: hypothesis, success criteria, compute budget.
4. Search related work: use `ss-arxiv-database` or WebSearch for prior art.

---

## Phase 1 — Inner Loop: Rapid Experimentation

For each experiment iteration:

### 1.1 Design the experiment
- Pick one variable to change (ablation-friendly).
- Document the change in `research/experiments/<run_id>/config.md`.

### 1.2 Execute
```bash
# Run experiment and capture output
python experiments/run.py --config research/experiments/<run_id>/config.md \
  2>&1 | tee research/experiments/<run_id>/log.txt
```

### 1.3 Record metrics
Write results to `research/experiments/<run_id>/metrics.json`:
```json
{
  "run_id": "<run_id>",
  "hypothesis": "...",
  "metric_name": 0.0,
  "wall_time_s": 0
}
```

### 1.4 Write summary
Append one-paragraph summary to `research/findings.md`:
- What changed, what the metric showed, what it implies.

### 1.5 Decide: continue or surface to outer loop
- **Continue** if the trend is clear and budget remains.
- **Surface** if results are surprising, budget is 80% spent, or a pattern emerges.

---

## Phase 2 — Outer Loop: Synthesis and Steering

Triggered after each inner-loop surface event.

1. Read all `research/experiments/*/metrics.json` and `research/findings.md`.
2. Identify the top-performing configuration and the clearest pattern.
3. Generate a ranked hypothesis list for the next inner-loop batch.
4. Update `research/plan.md` with revised direction.
5. If the research objective is met → proceed to Phase 3.

---

## Phase 3 — Output Generation

### Research Report
Create `research/report.md` containing:
- Abstract (3–5 sentences)
- Introduction with motivation
- Methods: what was varied, how experiments were run
- Results: tables of key metrics, winning configuration
- Analysis: what patterns emerged, why
- Conclusion and future work

### Presentation (optional)
If the user wants slides, invoke `ss-make-slides` with `research/report.md` as input.

### Paper (optional)
If the user wants a publication-ready draft, invoke `ss-ml-paper-writing` with
the report and experiment data.

---

## Guardrails

- **Never delete** experiment logs — always append.
- **Always validate** that code runs before marking an experiment complete.
- **Cap inner-loop iterations** at the compute budget in `research/plan.md`.
- **Reproducibility**: log random seeds, library versions, hardware specs in each config.

---

## Output Files

| File | Purpose |
|------|---------|
| `research/plan.md` | Hypothesis, success criteria, budget |
| `research/findings.md` | Running narrative across all experiments |
| `research/experiments/<id>/config.md` | Per-run configuration |
| `research/experiments/<id>/metrics.json` | Per-run metrics |
| `research/report.md` | Final synthesized report |
