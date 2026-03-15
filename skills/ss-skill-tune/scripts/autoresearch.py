#!/usr/bin/env python3
"""
Generic Autoresearch — Self-improving skill optimization.

Karpathy autoresearch pattern applied to any Claude Code skill:
1. Run test prompts with current SKILL.md as context → collect outputs
2. Evaluate each output against binary criteria via Claude → score
3. Compare against best score — keep winner
4. Mutate the SKILL.md to fix weaknesses
5. Repeat

Usage:
    python3 autoresearch.py config.json              # Run to max_cycles
    python3 autoresearch.py config.json --once        # Single cycle
    python3 autoresearch.py config.json --cycles 5    # Run N cycles
"""

import argparse
import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

EVAL_PROMPT_TEMPLATE = """You are evaluating the output of an AI skill against strict binary criteria.

SKILL CONTEXT: The skill was given this prompt:
---
{test_prompt}
---

SKILL OUTPUT:
---
{output}
---

CRITERIA — Rate each as PASS (true) or FAIL (false). Be strict.

{criteria_block}

Respond in this exact JSON format (no markdown fences, no extra text):
{json_template}

If any criterion fails, set it to false and add a brief reason to the "failures" array.
Example: {{"criterion_1": false, "failures": ["Reason for failure"]}}"""

MUTATION_TEMPLATE = """You are optimizing a Claude Code skill's instructions (SKILL.md). Your goal: modify the instructions so the skill consistently passes ALL evaluation criteria.

CURRENT SKILL.MD (the section being optimized):
---
{current_content}
---

LAST BATCH RESULTS ({score}/{max_score}):
{criteria_scores}

COMMON FAILURES:
{failures}

BEST SCORE SO FAR: {best_score}/{max_score}

RULES FOR YOUR MODIFICATION:
- Preserve the YAML frontmatter exactly as-is (name, description, allowed-tools)
- Only modify the instruction body (phases, rules, guidance)
- For any criterion below 80% pass rate, add VERY explicit constraints
- Be specific and imperative — Claude responds to direct commands
- Do not remove existing phases or structure, only refine instructions within them
- Keep the skill under 500 lines
- Return ONLY the complete new SKILL.md content — no explanation, no markdown fences wrapping the whole file"""


def load_config(config_path: Path) -> dict:
    config = json.loads(config_path.read_text())
    # Resolve skill_path relative to config file location
    config["_config_dir"] = config_path.parent
    config["_data_dir"] = config_path.parent / "data"
    skill_path = config["skill_path"]
    if not Path(skill_path).is_absolute():
        # Try relative to repo root (walk up from config dir)
        repo_root = config_path.parent
        while repo_root != repo_root.parent:
            candidate = repo_root / skill_path
            if candidate.exists():
                config["_skill_path"] = candidate
                break
            repo_root = repo_root.parent
        else:
            config["_skill_path"] = Path(skill_path)
    else:
        config["_skill_path"] = Path(skill_path)
    return config


def load_state(data_dir: Path) -> dict:
    state_file = data_dir / "state.json"
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {"best_score": -1, "run_number": 0}


def save_state(data_dir: Path, state: dict):
    state_file = data_dir / "state.json"
    state_file.write_text(json.dumps(state, indent=2))


# ─── Generation (Claude SDK) ────────────────────────────────────────────────


def generate_one(client, skill_content: str, test_prompt: str, model: str) -> str | None:
    """Run Claude with skill content as system context + test prompt."""
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=f"You are a Claude Code skill. Follow these instructions exactly:\n\n{skill_content}",
            messages=[{"role": "user", "content": test_prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"    GEN ERROR: {e}")
        return None


# ─── Evaluation (Claude SDK) ────────────────────────────────────────────────


def evaluate_one(
    client, output: str, test_prompt: str, criteria: list[dict], model: str
) -> dict | None:
    """Evaluate a single output against binary criteria."""
    criteria_block = "\n".join(
        f"{i+1}. {c['name'].upper()}: {c['question']}"
        for i, c in enumerate(criteria)
    )
    json_fields = {c["name"]: True for c in criteria}
    json_fields["failures"] = []
    json_template = json.dumps(json_fields)

    prompt = EVAL_PROMPT_TEMPLATE.format(
        test_prompt=test_prompt,
        output=output[:8000],  # Truncate very long outputs
        criteria_block=criteria_block,
        json_template=json_template,
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Extract JSON from response (handle markdown fences)
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"    EVAL ERROR: {e}")
        return None


# ─── Mutation (Claude SDK) ──────────────────────────────────────────────────


def mutate_skill(
    client,
    current_content: str,
    criteria: list[dict],
    eval_results: list[dict],
    best_score: int,
    model: str,
) -> str:
    """Use Claude to improve the SKILL.md based on failure analysis."""
    n = len(eval_results)
    max_score = n * len(criteria)

    # Tally per-criterion scores
    criteria_scores_lines = []
    total = 0
    for c in criteria:
        passed = sum(1 for r in eval_results if r.get(c["name"], False))
        total += passed
        criteria_scores_lines.append(f"- {c['name']}: {passed}/{n}")
    criteria_scores = "\n".join(criteria_scores_lines)

    # Collect failures
    all_failures = []
    for r in eval_results:
        for f in r.get("failures", []):
            all_failures.append(f)
    unique_failures = list(dict.fromkeys(all_failures))[:20]
    failures_text = "\n".join(f"- {f}" for f in unique_failures) if unique_failures else "- None"

    prompt = MUTATION_TEMPLATE.format(
        current_content=current_content,
        score=total,
        max_score=max_score,
        criteria_scores=criteria_scores,
        best_score=best_score,
        failures=failures_text,
    )

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ─── Main Cycle ──────────────────────────────────────────────────────────────


def run_cycle(client, config: dict, state: dict) -> dict:
    """Run one autoresearch optimization cycle."""
    data_dir = config["_data_dir"]
    skill_path = config["_skill_path"]
    criteria = config["eval_criteria"]
    test_prompts = config["test_prompts"]
    batch_size = config.get("batch_size", len(test_prompts))
    eval_model = config.get("eval_model", "claude-sonnet-4-6")
    mutate_model = config.get("mutate_model", "claude-sonnet-4-6")
    gen_model = config.get("gen_model", "claude-sonnet-4-6")

    run_num = state["run_number"] + 1
    state["run_number"] = run_num
    run_dir = data_dir / "outputs" / f"run_{run_num:03d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    skill_content = skill_path.read_text()
    best_skill_path = data_dir / "best_skill.md"

    # Use subset of test prompts if batch_size < total
    import random
    prompts = random.sample(test_prompts, min(batch_size, len(test_prompts)))

    max_score = len(prompts) * len(criteria)

    print(f"\n{'='*60}")
    print(f"RUN {run_num} | {datetime.now().strftime('%H:%M:%S')} | Best: {state['best_score']}/{max_score}")
    print(f"{'='*60}")

    # ── Generate ──────────────────────────────────────────────────
    print(f"\n  Generating {len(prompts)} outputs...")
    outputs: list[tuple[int, str, str | None]] = []

    max_workers = config.get("max_gen_workers", 3)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for i, prompt in enumerate(prompts):
            f = pool.submit(generate_one, client, skill_content, prompt, gen_model)
            futures[f] = (i, prompt)

        for f in as_completed(futures):
            i, prompt = futures[f]
            try:
                result = f.result()
            except Exception as e:
                result = None
                print(f"    [{i+1}/{len(prompts)}] ERROR: {e}")

            if result:
                # Save output
                out_file = run_dir / f"output_{i:02d}.txt"
                out_file.write_text(result)
                outputs.append((i, prompt, result))
                print(f"    [{i+1}/{len(prompts)}] generated ({len(result)} chars)")
            else:
                outputs.append((i, prompt, None))
                print(f"    [{i+1}/{len(prompts)}] FAILED")

    successful = [(i, p, o) for i, p, o in outputs if o is not None]
    if not successful:
        print("  ERROR: No outputs generated. Skipping cycle.")
        save_state(data_dir, state)
        return state

    # ── Evaluate ──────────────────────────────────────────────────
    print(f"\n  Evaluating {len(successful)} outputs...")
    eval_results: list[dict] = []

    max_eval_workers = config.get("max_eval_workers", 5)
    with ThreadPoolExecutor(max_workers=max_eval_workers) as pool:
        futures = {}
        for i, prompt, output in successful:
            f = pool.submit(evaluate_one, client, output, prompt, criteria, eval_model)
            futures[f] = (i, prompt)

        for f in as_completed(futures):
            i, prompt = futures[f]
            try:
                result = f.result()
            except Exception as e:
                result = None
                print(f"    [{i+1}] EVAL ERROR: {e}")

            if result:
                eval_results.append(result)
                passed = sum(1 for c in criteria if result.get(c["name"], False))
                fails = result.get("failures", [])
                print(f"    [{i+1}] {passed}/{len(criteria)} | {'; '.join(fails) if fails else 'all pass'}")
            else:
                # Default all-fail
                fail_result = {c["name"]: False for c in criteria}
                fail_result["failures"] = ["eval_error"]
                eval_results.append(fail_result)
                print(f"    [{i+1}] 0/{len(criteria)} | eval failed")

    # ── Score ─────────────────────────────────────────────────────
    score = 0
    print(f"\n  SCORES:")
    for c in criteria:
        passed = sum(1 for r in eval_results if r.get(c["name"], False))
        score += passed
        print(f"    {c['name']:.<30} {passed}/{len(eval_results)}")
    print(f"    {'TOTAL':.<30} {score}/{max_score}")

    # ── Log ───────────────────────────────────────────────────────
    criteria_breakdown = {}
    for c in criteria:
        criteria_breakdown[c["name"]] = sum(
            1 for r in eval_results if r.get(c["name"], False)
        )

    log_entry = {
        "run": run_num,
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "max": max_score,
        "criteria": criteria_breakdown,
        "num_outputs": len(successful),
    }
    results_file = data_dir / "results.jsonl"
    with open(results_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # ── Keep or discard ───────────────────────────────────────────
    if score > state["best_score"]:
        old_best = state["best_score"]
        state["best_score"] = score
        best_skill_path.write_text(skill_content)
        print(f"\n  NEW BEST! {score}/{max_score} (was {old_best})")
    else:
        print(f"\n  No improvement ({score} vs best {state['best_score']})")
        if best_skill_path.exists():
            print("  Reverting to best skill for next mutation")

    # ── Mutate ────────────────────────────────────────────────────
    if score < max_score:
        print("\n  Mutating SKILL.md...")
        base_content = best_skill_path.read_text() if best_skill_path.exists() else skill_content
        new_content = mutate_skill(
            client, base_content, criteria, eval_results, state["best_score"], mutate_model
        )
        skill_path.write_text(new_content)
        print(f"  New SKILL.md written ({len(new_content)} chars)")
    else:
        print(f"\n  PERFECT {max_score}/{max_score}! Skill fully optimized.")

    save_state(data_dir, state)
    return state


# ─── Entry Point ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Generic autoresearch skill optimizer")
    parser.add_argument("config", help="Path to config.json")
    parser.add_argument("--once", action="store_true", help="Run a single cycle")
    parser.add_argument("--cycles", type=int, default=0, help="Run N cycles (0=use config max_cycles)")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    data_dir = config["_data_dir"]
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "outputs").mkdir(parents=True, exist_ok=True)

    if not config["_skill_path"].exists():
        print(f"ERROR: Skill not found: {config['_skill_path']}", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    state = load_state(data_dir)

    cycle_seconds = config.get("cycle_seconds", 120)
    max_cycles_config = config.get("max_cycles", 10)

    print("Autoresearch — Skill Optimizer")
    print(f"  Target:     {config['_skill_path']}")
    print(f"  Criteria:   {len(config['eval_criteria'])}")
    print(f"  Prompts:    {len(config['test_prompts'])}")
    print(f"  Batch size: {config.get('batch_size', len(config['test_prompts']))}")
    print(f"  Cycle:      {cycle_seconds}s")
    print(f"  State:      run {state['run_number']}, best {state['best_score']}")

    if args.once:
        run_cycle(client, config, state)
        return

    max_cycles = args.cycles or max_cycles_config
    plateau_count = 0
    prev_best = state["best_score"]

    for i in range(max_cycles):
        start = time.time()
        try:
            state = run_cycle(client, config, state)
        except Exception as e:
            print(f"\n  CYCLE ERROR: {e}")
            traceback.print_exc()

        # Plateau detection
        if state["best_score"] == prev_best:
            plateau_count += 1
        else:
            plateau_count = 0
            prev_best = state["best_score"]

        if plateau_count >= 3:
            print(f"\n  Plateau detected ({plateau_count} cycles without improvement). Stopping.")
            break

        elapsed = time.time() - start

        if i < max_cycles - 1:
            wait = max(0, cycle_seconds - elapsed)
            if wait > 0:
                print(f"\n  Waiting {wait:.0f}s until next cycle...")
                time.sleep(wait)

    print(f"\nDone. Best score: {state['best_score']}")
    best_path = data_dir / "best_skill.md"
    if best_path.exists():
        print(f"Best SKILL.md: {best_path}")


if __name__ == "__main__":
    main()
