#!/usr/bin/env bash
# Rebuild .claude/skills/ as a symlink farm pointing at skills/ and
# maintainer-skills/, so project-level skill discovery picks up both public
# and maintainer skills.
#
# Idempotent: safe to re-run. Removes only existing symlinks in
# .claude/skills/ (preserves any real files or directories), then re-creates
# one symlink per skill directory. Exits non-zero on any error.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

mkdir -p .claude/skills

find .claude/skills -maxdepth 1 -mindepth 1 -type l -delete

shopt -s nullglob
count=0
for dir in skills/*/ maintainer-skills/*/; do
  name="$(basename "$dir")"
  ln -s "../../$dir" ".claude/skills/$name"
  count=$((count + 1))
done

echo "Synced $count skill symlinks under .claude/skills/."
