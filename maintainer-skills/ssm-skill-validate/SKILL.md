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

### Check 10 — Trigger phrase overlap (WARN if found)
Compare each skill's `description:` trigger phrases against all other skills. Warn if two skills share significant trigger keywords that could cause ambiguous activation. List the overlapping pair and the shared phrases.

### Check 11 — `metadata.depends-on` targets exist (FAIL if broken)
If frontmatter contains `metadata.depends-on:`, verify each space-delimited skill name corresponds to an existing directory under `skills/`.

### Check 12 — `metadata.related-skills` targets exist (WARN if broken)
If frontmatter contains `metadata.related-skills:`, verify each comma-separated skill name (trimmed) corresponds to an existing directory under `skills/`. Warn on missing targets — these are cross-references, not hard dependencies.

**Exit:** All checks run for all skills. Results collected.

## Phase 3 — Report

**Entry:** Validation results from Phase 2.

Output a report in this format:

```
## Skill Validation Report

| Skill | SKILL.md | name | description | name=dir | ss- prefix | allowed-tools | <500 lines | refs exist | triggers | meta.depends-on | meta.related-skills | Status |
|-------|----------|------|-------------|----------|------------|---------------|------------|------------|----------|-----------------|---------------------|--------|
| ss-foo | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | N/A | N/A | PASS |
| ss-bar | PASS | PASS | PASS | PASS | PASS | WARN | PASS | N/A | WARN | PASS | WARN | WARN |

### Summary
- Total skills: N
- Passed: N
- Warnings: N
- Failed: N

### Failures (if any)
- ss-bad-skill: name "wrong-name" does not match directory "ss-bad-skill"

### Warnings (if any)
- ss-bar: missing allowed-tools (recommended)
```

**Exit:** Report displayed to user.

## Phase 4 — CI Output

**Entry:** Report generated.

If running in CI context or user requests CI output:

1. Exit with code 0 if no FAILs
2. Exit with code 1 if any FAILs
3. Warnings do not cause failure

**Exit:** Validation complete.

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
