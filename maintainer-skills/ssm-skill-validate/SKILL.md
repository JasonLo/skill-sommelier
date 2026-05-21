---
name: ssm-skill-validate
description: >-
  Validate all skills in this repo for frontmatter correctness, naming conventions,
  and structural rules. Use when adding a new skill, before releases, or in CI.
  Triggers on "validate skills", "lint skills", "check skills", "audit frontmatter",
  "skill validation", "pre-release check".
allowed-tools:
  - Bash
  - Glob
  - Grep
  - Read
---

# Validate Skills

Run automated checks against every skill in `skills/` and produce a pass/fail report.

## When to Use
- After creating or modifying a skill
- Before cutting a release
- As a CI gate in GitHub Actions
- When auditing repo health

## When NOT to Use
- To improve skill content quality — use `ss-skill-craft` improve mode instead

## Phase 1 — Discover Skills

**Entry:** User triggers validation.

1. Glob for all `skills/*/SKILL.md` files
2. Also glob for `skills/*/` directories and flag any that lack a `SKILL.md`
3. Build a list of `(directory_name, skill_md_path)` pairs

**Exit:** Complete list of skill directories and their SKILL.md status.

## Phase 2 — Validate Each Skill

**Entry:** Skill list from Phase 1.

For each skill, run these checks and record pass/warn/fail per check:

### Check 1 — SKILL.md exists (FAIL if missing)
Directory must contain a `SKILL.md` file.

### Check 2 — Valid YAML frontmatter (FAIL if broken)
File must start with `---` and contain a closing `---`. Parse the frontmatter block.

### Check 3 — Required field: `name` (FAIL if missing)
Frontmatter must contain a `name:` field.

### Check 4 — Required field: `description` (FAIL if missing)
Frontmatter must contain a `description:` field.

### Check 5 — Name matches directory (FAIL if mismatch)
The `name:` value must exactly match the directory name under `skills/`.

### Check 6 — Name has `ss-` prefix (FAIL if missing)
The `name:` value must start with `ss-`.

### Check 7 — `allowed-tools` declared (WARN if missing)
Frontmatter should contain `allowed-tools:`. This is recommended, not required.

### Check 8 — Line count under 500 (WARN if over)
Count total lines in SKILL.md. Warn if over 500; suggest moving content to `references/`.

### Check 9 — Referenced directories exist (FAIL if broken)
If the SKILL.md body mentions `references/` or `scripts/`, verify those directories exist in the skill folder.

### Check 11 — `metadata.depends-on` targets exist (FAIL if broken)
If frontmatter contains `metadata.depends-on:`, verify each space-delimited skill name corresponds to an existing directory under `skills/` or `maintainer-skills/`.

### Check 12 — `metadata.related-skills` targets exist (WARN if broken)
If frontmatter contains `metadata.related-skills:`, verify each comma-separated skill name (trimmed) corresponds to an existing directory under `skills/` or `maintainer-skills/`. Warn on missing targets — these are cross-references, not hard dependencies.

**Exit:** All per-skill checks run. Results collected.

## Phase 3 — Cross-Skill Checks

**Entry:** Per-skill checks complete.

### Check 10 — Trigger phrase overlap (WARN if 3+ phrases shared)
Extract double-quoted phrases from each skill's `description:` block (the conventional location for trigger phrases). For every pair of skills, count exact phrase matches after lowercasing. Warn when a pair shares **3 or more** distinct quoted phrases — that's a strong signal they'll compete for activation. Use `ssm-skill-consolidate` to merge them or rewrite descriptions to disambiguate.

**Exit:** Pairwise comparison done across the entire run.

## Phase 4 — Report

**Entry:** All checks complete.

The script emits one line per check result:

```
OK: ss-foo
FAIL: ss-bar — name 'bar' does not match directory
WARN: ss-baz — missing allowed-tools (recommended)
WARN: trigger overlap — ss-foo vs ss-quux (4 shared phrases: create a skill; new skill; make skill)
```

Followed by a summary:

```
Summary for skills: N checked, X failures, Y warnings
```

**Exit code:** `0` if no FAILs (warnings allowed), `1` if any FAIL. CI gates use the exit code directly.

## How to Run

The deterministic checks live in `scripts/validate.sh`. Run it locally:

```bash
bash maintainer-skills/ssm-skill-validate/scripts/validate.sh skills ss-
bash maintainer-skills/ssm-skill-validate/scripts/validate.sh maintainer-skills ssm-
```

Exit code is `0` if all checks pass (warnings allowed), `1` on any FAIL.

## CI Integration

The script is wired into two workflows:

- `.github/workflows/validate.yml` — runs on every PR and push to `main` that touches `skills/`, `maintainer-skills/`, or the validator itself.
- `.github/workflows/release.yml` — the `release` job has `needs: validate`, so a tag push cannot ship a broken skill.

When adding a new check, edit `scripts/validate.sh` and the rules listed above in lockstep.
