---
name: ss-validate-skills
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
- To find dead code or complexity — use `ss-simplify-repo` instead

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

## GitHub Actions Integration

Add this job to `.github/workflows/` to run validation on PRs:

```yaml
name: Validate Skills
on:
  pull_request:
    paths:
      - 'skills/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate skill frontmatter
        run: |
          exit_code=0
          for dir in skills/*/; do
            skill_name=$(basename "$dir")
            skill_file="$dir/SKILL.md"

            # Check 1: SKILL.md exists
            if [ ! -f "$skill_file" ]; then
              echo "FAIL: $skill_name — missing SKILL.md"
              exit_code=1
              continue
            fi

            # Extract frontmatter (between first two ---)
            frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_file" | sed '1d;$d')

            # Check 3: name field exists
            fm_name=$(echo "$frontmatter" | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//')
            if [ -z "$fm_name" ]; then
              echo "FAIL: $skill_name — missing name field"
              exit_code=1
              continue
            fi

            # Check 4: description field exists
            if ! echo "$frontmatter" | grep -q '^description:'; then
              echo "FAIL: $skill_name — missing description field"
              exit_code=1
            fi

            # Check 5: name matches directory
            if [ "$fm_name" != "$skill_name" ]; then
              echo "FAIL: $skill_name — name '$fm_name' does not match directory"
              exit_code=1
            fi

            # Check 6: ss- prefix
            if [[ "$fm_name" != ss-* ]]; then
              echo "FAIL: $skill_name — name missing ss- prefix"
              exit_code=1
            fi

            # Check 7: allowed-tools (warn only)
            if ! echo "$frontmatter" | grep -q '^allowed-tools:'; then
              echo "WARN: $skill_name — missing allowed-tools"
            fi

            # Check 8: line count
            lines=$(wc -l < "$skill_file")
            if [ "$lines" -gt 500 ]; then
              echo "WARN: $skill_name — $lines lines (over 500)"
            fi

            # Check 11: depends-on targets exist
            depends_on=$(echo "$frontmatter" | grep 'depends-on:' | sed 's/.*depends-on:[[:space:]]*//')
            if [ -n "$depends_on" ]; then
              for dep in $depends_on; do
                if [ ! -d "skills/$dep" ]; then
                  echo "FAIL: $skill_name — depends-on target '$dep' not found"
                  exit_code=1
                fi
              done
            fi

            # Check 12: related-skills targets exist
            related=$(echo "$frontmatter" | grep 'related-skills:' | sed 's/.*related-skills:[[:space:]]*//')
            if [ -n "$related" ]; then
              IFS=',' read -ra rels <<< "$related"
              for rel in "${rels[@]}"; do
                rel=$(echo "$rel" | xargs)  # trim whitespace
                if [ -n "$rel" ] && [ ! -d "skills/$rel" ]; then
                  echo "WARN: $skill_name — related-skills target '$rel' not found"
                fi
              done
            fi

            echo "OK: $skill_name"
          done
          exit $exit_code
```
