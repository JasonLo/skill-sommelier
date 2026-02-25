#!/usr/bin/env bash
input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd')
branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
if [ -n "$branch" ]; then
  printf '\033[01;32m%s@%s\033[00m:\033[01;34m%s\033[00m \033[01;33m(%s)\033[00m' "$(whoami)" "$(hostname -s)" "$cwd" "$branch"
else
  printf '\033[01;32m%s@%s\033[00m:\033[01;34m%s\033[00m' "$(whoami)" "$(hostname -s)" "$cwd"
fi
