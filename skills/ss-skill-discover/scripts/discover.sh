#!/usr/bin/env bash
# discover.sh — Search GitHub for Claude Code skills, fetch metadata,
# filter, rank, and emit ranked candidates as JSON.
#
# This is the single source of truth for the discovery pipeline shared by
# `ss-skill-discover` (interactive) and `ssm-skill-weekly-discover` (cron).
# Keeping it in one place avoids the drift that previously existed across
# two SKILL.md files and one workflow.
#
# Usage:
#   discover.sh [--keyword TEXT] [--limit N]
#               [--installed-dir DIR] [--exclude-repo OWNER/REPO]
#               [--profile FILE] [--no-license-filter]
#
# Output (stdout): JSON array, sorted by (relevance desc, stars desc,
# pushed_at desc). Each element:
#   { name, description, repo, path, stars, pushed_at,
#     license, relevance, age_label }
#
# Logs go to stderr. Exit code is 0 even if 0 candidates remain — callers
# check `length` on the JSON.
#
# Requires: gh (authenticated), jq, base64, date (GNU).

set -uo pipefail

keyword=""
final_limit=10
installed_dir="skills"
exclude_repo=""
profile_file=""
license_filter=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keyword)            keyword="$2";              shift 2 ;;
    --limit)              final_limit="$2";          shift 2 ;;
    --installed-dir)      installed_dir="$2";        shift 2 ;;
    --exclude-repo)       exclude_repo="$2";         shift 2 ;;
    --profile)            profile_file="$2";         shift 2 ;;
    --no-license-filter)  license_filter=0;          shift   ;;
    -h|--help)
      sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *)
      echo "discover.sh: unknown arg: $1" >&2
      exit 2 ;;
  esac
done

log() { printf '[discover] %s\n' "$*" >&2; }

for bin in gh jq base64 date; do
  command -v "$bin" >/dev/null 2>&1 || { echo "discover.sh: missing dependency: $bin" >&2; exit 2; }
done

# ── Relevance corpus ─────────────────────────────────────────────────────────
query_keywords=""
if [[ -n "$keyword" ]]; then
  query_keywords="$keyword"
elif [[ -n "$profile_file" && -f "$profile_file" ]]; then
  query_keywords=$(tr '[:upper:]' '[:lower:]' < "$profile_file" \
    | tr -cs 'a-z0-9' '\n' \
    | awk 'length>=4 && $0 !~ /^[0-9]+$/' \
    | sort -u \
    | head -40 \
    | tr '\n' ' ')
fi
log "relevance keywords: ${query_keywords:-<none>}"

# ── Installed-skill names (with ss- prefix stripped for comparison) ──────────
installed_names=""
if [[ -d "$installed_dir" ]]; then
  for d in "$installed_dir"/*/; do
    [[ -d "$d" ]] || continue
    n=$(basename "$d")
    installed_names+="${n#ss-}"$'\n'
  done
fi

# ── Search GitHub ────────────────────────────────────────────────────────────
log "code search…"
code_query='filename:SKILL.md "name:" "description:"'
[[ -n "$keyword" ]] && code_query="$code_query $keyword"
code_hits=$(gh search code "$code_query" --limit 50 \
  --json repository,path 2>/dev/null \
  | jq -c '[.[] | {repo: .repository.nameWithOwner, path: .path}]') \
  || code_hits='[]'

log "topic search…"
topic_repos='[]'
for topic in claude-code-skills claude-skills agent-skills claude-code-skill; do
  r=$(gh search repos --topic="$topic" --sort=stars --limit 20 \
    --json fullName 2>/dev/null \
    | jq -c '[.[].fullName]') || r='[]'
  topic_repos=$(jq -c --argjson new "$r" '. + $new | unique' <<<"$topic_repos")
done

topic_hits='[]'
while IFS= read -r repo; do
  [[ -z "$repo" ]] && continue
  paths=$(gh api "repos/$repo/git/trees/HEAD?recursive=1" \
    --jq '[.tree[] | select(.path | test("SKILL\\.md$")) | .path]' 2>/dev/null) \
    || paths='[]'
  topic_hits=$(jq -c --arg repo "$repo" --argjson paths "$paths" \
    '. + [$paths[] | {repo: $repo, path: .}]' <<<"$topic_hits")
done < <(jq -r '.[]' <<<"$topic_repos")

# Merge and dedupe code + topic hits, cap to 30 before any per-candidate API
# calls — keeps us well under GitHub's authenticated rate limit.
all_hits=$(jq -c -s 'add | unique_by(.repo + ":" + .path) | .[0:30]' \
  <(printf '%s' "$code_hits") <(printf '%s' "$topic_hits"))
if [[ -n "$exclude_repo" ]]; then
  all_hits=$(jq -c --arg ex "$exclude_repo" '[.[] | select(.repo != $ex)]' <<<"$all_hits")
fi
n=$(jq 'length' <<<"$all_hits")
log "candidates after dedupe: $n"

# ── Per-candidate fetch + filter ─────────────────────────────────────────────
permissive_licenses="MIT Apache-2.0 BSD-2-Clause BSD-3-Clause ISC Unlicense 0BSD"
results='[]'

for i in $(seq 0 $((n - 1))); do
  row=$(jq -c ".[$i]" <<<"$all_hits")
  repo=$(jq -r '.repo' <<<"$row")
  path=$(jq -r '.path' <<<"$row")

  # One repo call: stars, pushed_at, license — saves a request vs the old flow.
  meta=$(gh api "repos/$repo" \
    --jq '{stars: .stargazers_count, pushed: .pushed_at, license: (.license.spdx_id // "")}' \
    2>/dev/null) || { log "skip $repo: meta fetch failed"; continue; }
  stars=$(jq -r '.stars' <<<"$meta")
  pushed=$(jq -r '.pushed' <<<"$meta")
  license=$(jq -r '.license' <<<"$meta")

  if [[ "$license_filter" -eq 1 ]]; then
    case " $permissive_licenses " in
      *" $license "*) ;;
      *) log "skip $repo: license=$license"; continue ;;
    esac
  fi

  # Fetch SKILL.md content
  content=$(gh api "repos/$repo/contents/$path" --jq '.content' 2>/dev/null \
    | base64 -d 2>/dev/null) || { log "skip $repo/$path: SKILL.md fetch failed"; continue; }

  fm=$(printf '%s\n' "$content" | sed -n '/^---$/,/^---$/p' | sed '1d;$d')
  [[ -z "$fm" ]] && { log "skip $repo/$path: no frontmatter"; continue; }

  name=$(printf '%s\n' "$fm" | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//' | tr -d '"' \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  desc=$(printf '%s\n' "$fm" | awk '
    /^description:[[:space:]]*[>|][-+]?[[:space:]]*$/ { flag=1; next }
    /^description:/ { sub(/^description:[[:space:]]*/,""); print; exit }
    flag && /^[a-zA-Z_-]+:/ { exit }
    flag { sub(/^[[:space:]]+/,""); printf "%s ", $0 }
  ' | tr -s ' ' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | head -c 280)

  if [[ -z "$name" || -z "$desc" ]]; then
    log "skip $repo/$path: missing name or description"
    continue
  fi

  # Already-installed filter — compare bare name (without ss- prefix).
  bare="${name#ss-}"
  if [[ -n "$installed_names" ]] && printf '%s' "$installed_names" | grep -Fxq "$bare"; then
    log "skip $repo/$path: already installed as $name"
    continue
  fi

  # Relevance: count keyword hits in name + description.
  rel=0
  if [[ -n "$query_keywords" ]]; then
    hay=$(printf '%s %s' "$name" "$desc" | tr '[:upper:]' '[:lower:]')
    for kw in $query_keywords; do
      [[ "$hay" == *"$kw"* ]] && rel=$((rel + 1))
    done
  fi

  # Age label
  pushed_epoch=$(date -d "$pushed" +%s 2>/dev/null || echo 0)
  now=$(date +%s)
  days=$(( (now - pushed_epoch) / 86400 ))
  if   [[ $days -le 1   ]]; then age="today"
  elif [[ $days -le 7   ]]; then age="${days}d ago"
  elif [[ $days -le 30  ]]; then age="$((days / 7))w ago"
  elif [[ $days -le 365 ]]; then age="$((days / 30))mo ago"
  else                            age=">1y ago"
  fi

  results=$(jq -c \
    --arg name "$name" --arg desc "$desc" --arg repo "$repo" --arg path "$path" \
    --argjson stars "$stars" --arg pushed "$pushed" --arg license "$license" \
    --argjson rel "$rel" --arg age "$age" \
    '. + [{name: $name, description: $desc, repo: $repo, path: $path,
           stars: $stars, pushed_at: $pushed, license: $license,
           relevance: $rel, age_label: $age}]' <<<"$results")
done

# ── Rank ────────────────────────────────────────────────────────────────────
# jq's sort is stable. Sort by least-significant key first, then reverse:
# pushed_at → stars → relevance, then reverse → relevance desc, stars desc
# within relevance ties, pushed_at desc within stars ties.
jq --argjson n "$final_limit" \
  '. | sort_by(.pushed_at) | sort_by(.stars) | sort_by(.relevance)
     | reverse | .[0:$n]' <<<"$results"
