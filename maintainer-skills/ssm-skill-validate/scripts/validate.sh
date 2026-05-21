#!/usr/bin/env bash
# Validate every SKILL.md under a given directory against the repo conventions.
#
# Usage: validate.sh <dir> <expected-name-prefix>
# Example: validate.sh skills ss-
#          validate.sh maintainer-skills ssm-
#
# Exit code: 0 if all checks pass (warnings allowed), 1 if any FAIL.

set -uo pipefail

dir="${1:?usage: validate.sh <dir> <prefix>}"
prefix="${2:?usage: validate.sh <dir> <prefix>}"

if [ ! -d "$dir" ]; then
  echo "FAIL: directory '$dir' does not exist"
  exit 1
fi

exit_code=0
total=0
fails=0
warns=0

for skill_dir in "$dir"/*/; do
  [ -d "$skill_dir" ] || continue
  total=$((total + 1))
  skill_name=$(basename "$skill_dir")
  skill_file="${skill_dir}SKILL.md"

  # Check 1 — SKILL.md exists
  if [ ! -f "$skill_file" ]; then
    echo "FAIL: $skill_name — missing SKILL.md"
    exit_code=1
    fails=$((fails + 1))
    continue
  fi

  # Check 2 — valid frontmatter delimiters
  if ! head -1 "$skill_file" | grep -q '^---$'; then
    echo "FAIL: $skill_name — file does not start with ---"
    exit_code=1
    fails=$((fails + 1))
    continue
  fi
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_file" | sed '1d;$d')
  if [ -z "$frontmatter" ]; then
    echo "FAIL: $skill_name — empty or unterminated frontmatter"
    exit_code=1
    fails=$((fails + 1))
    continue
  fi

  # Check 3 — name field
  fm_name=$(printf '%s\n' "$frontmatter" | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//')
  if [ -z "$fm_name" ]; then
    echo "FAIL: $skill_name — missing name field"
    exit_code=1
    fails=$((fails + 1))
    continue
  fi

  # Check 4 — description field
  if ! printf '%s\n' "$frontmatter" | grep -q '^description:'; then
    echo "FAIL: $skill_name — missing description field"
    exit_code=1
    fails=$((fails + 1))
  fi

  # Check 5 — name matches directory
  if [ "$fm_name" != "$skill_name" ]; then
    echo "FAIL: $skill_name — name '$fm_name' does not match directory"
    exit_code=1
    fails=$((fails + 1))
  fi

  # Check 6 — name has expected prefix
  case "$fm_name" in
    "$prefix"*) ;;
    *)
      echo "FAIL: $skill_name — name '$fm_name' missing '$prefix' prefix"
      exit_code=1
      fails=$((fails + 1))
      ;;
  esac

  # Check 7 — allowed-tools (WARN if missing)
  if ! printf '%s\n' "$frontmatter" | grep -q '^allowed-tools:'; then
    echo "WARN: $skill_name — missing allowed-tools (recommended)"
    warns=$((warns + 1))
  fi

  # Check 8 — line count under 500 (WARN)
  lines=$(wc -l < "$skill_file")
  if [ "$lines" -gt 500 ]; then
    echo "WARN: $skill_name — $lines lines (over 500; consider moving content to references/)"
    warns=$((warns + 1))
  fi

  # Check 9 — referenced subdirs exist
  # Only match real markdown links into the skill's own subdirs: [text](references/...)
  # Bare prose mentions like `scripts/install.sh` in instructions don't count.
  if grep -qE '\]\(references/' "$skill_file" && [ ! -d "${skill_dir}references" ]; then
    echo "FAIL: $skill_name — SKILL.md links into 'references/' but directory does not exist"
    exit_code=1
    fails=$((fails + 1))
  fi
  if grep -qE '\]\(scripts/' "$skill_file" && [ ! -d "${skill_dir}scripts" ]; then
    echo "FAIL: $skill_name — SKILL.md links into 'scripts/' but directory does not exist"
    exit_code=1
    fails=$((fails + 1))
  fi

  # Check 11 — depends-on targets exist (search both top-level dirs)
  depends_on=$(printf '%s\n' "$frontmatter" | grep 'depends-on:' | sed 's/.*depends-on:[[:space:]]*//')
  if [ -n "$depends_on" ]; then
    for dep in $depends_on; do
      if [ ! -d "skills/$dep" ] && [ ! -d "maintainer-skills/$dep" ]; then
        echo "FAIL: $skill_name — depends-on target '$dep' not found in skills/ or maintainer-skills/"
        exit_code=1
        fails=$((fails + 1))
      fi
    done
  fi

  echo "OK: $skill_name"
done

echo
echo "Summary for $dir: $total checked, $fails failures, $warns warnings"
exit $exit_code
