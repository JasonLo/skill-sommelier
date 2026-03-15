#!/usr/bin/env bash
# discover.sh — Search GitHub for new Claude Code skills and create an issue
# with checkbox recommendations. Designed for headless CI (no Claude API needed).
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-JasonLo/skill-sommelier}"
SELF_REPO="JasonLo/skill-sommelier"
PROFILE_PATH=".github/user-profile.md"
SKILLS_DIR="skills"
MAX_RECOMMENDATIONS=10
LABEL="skill-recommendation"
DATE=$(date +%Y-%m-%d)

# ── Helpers ──────────────────────────────────────────────────────────────────

log() { echo "::group::$1"; }
endlog() { echo "::endgroup::"; }

# Extract keywords from user profile (lowercased, deduplicated)
extract_keywords() {
  if [[ -f "$PROFILE_PATH" ]]; then
    grep -E '^\s*-' "$PROFILE_PATH" \
      | sed 's/^[[:space:]]*-[[:space:]]*//' \
      | tr ',' '\n' \
      | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' \
      | tr '[:upper:]' '[:lower:]' \
      | sort -u
  else
    # Fallback generic keywords
    echo -e "python\nautomation\ndevops\ndocker"
  fi
}

# List installed skill names (directory names under skills/)
installed_skills() {
  if [[ -d "$SKILLS_DIR" ]]; then
    ls -1 "$SKILLS_DIR"
  fi
}

# ── Check for existing open issue ────────────────────────────────────────────

log "Checking for existing open recommendation issue"
# Ensure label exists
gh label create "$LABEL" --description "Automated skill recommendations" --color "0e8a16" --repo "$REPO" 2>/dev/null || true

OPEN_ISSUES=$(gh issue list --repo "$REPO" --label "$LABEL" --state open --json number --jq 'length')
if [[ "$OPEN_ISSUES" -gt 0 ]]; then
  echo "Open recommendation issue already exists. Skipping."
  exit 0
fi
endlog

# ── Step 1: Extract keywords and installed skills ────────────────────────────

log "Extracting profile keywords"
KEYWORDS=$(extract_keywords)
echo "Keywords: $(echo "$KEYWORDS" | tr '\n' ', ')"
endlog

log "Listing installed skills"
INSTALLED=$(installed_skills)
echo "Installed: $(echo "$INSTALLED" | tr '\n' ', ')"
endlog

# ── Step 2: Search GitHub ────────────────────────────────────────────────────

log "Searching GitHub for SKILL.md files"

CANDIDATES_FILE=$(mktemp)
SEEN_FILE=$(mktemp)
touch "$SEEN_FILE"

# Search for SKILL.md files with frontmatter markers
gh search code 'filename:SKILL.md "name:" "description:"' --limit 50 --json repository,path \
  | jq -r '.[] | "\(.repository.fullName)\t\(.path)"' \
  >> "$CANDIDATES_FILE" 2>/dev/null || true

# Topic-based repo searches
for topic in claude-code-skills claude-skills agent-skills claude-code-skill; do
  gh search repos --topic="$topic" --sort=stars --limit 20 --json fullName \
    | jq -r '.[].fullName' \
    | while read -r repo_name; do
        # Find SKILL.md files in each repo
        gh api "repos/${repo_name}/git/trees/HEAD?recursive=1" --jq \
          '.tree[] | select(.path | test("SKILL\\.md$")) | .path' 2>/dev/null \
          | while read -r path; do
              echo -e "${repo_name}\t${path}"
            done
      done >> "$CANDIDATES_FILE" 2>/dev/null || true
done
endlog

# ── Step 3: Deduplicate and filter ───────────────────────────────────────────

log "Processing candidates"

RESULTS_FILE=$(mktemp)
DEDUPED_FILE=$(mktemp)
COUNT=0
MAX_FETCH=$((MAX_RECOMMENDATIONS * 3))

# Deduplicate by repo+path into a file (avoids broken pipe from sort|while+break)
sort -u "$CANDIDATES_FILE" > "$DEDUPED_FILE"

while IFS=$'\t' read -r repo_full path; do
  # Skip self
  [[ "$repo_full" == "$SELF_REPO" ]] && continue

  # Skip if we've already processed this repo+skill combo
  skill_key="${repo_full}:${path}"
  if grep -qxF "$skill_key" "$SEEN_FILE" 2>/dev/null; then
    continue
  fi
  echo "$skill_key" >> "$SEEN_FILE"

  # Respect rate limits — stop if we've hit enough
  if [[ $COUNT -ge $MAX_FETCH ]]; then
    break
  fi

  # Fetch SKILL.md content (base64 decode)
  content=$(gh api "repos/${repo_full}/contents/${path}" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null) || continue

  # Extract name and description from frontmatter
  skill_name=$(echo "$content" | sed -n '/^---$/,/^---$/p' | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//')
  skill_desc=$(echo "$content" | sed -n '/^---$/,/^---$/p' | grep -m1 'description:' | sed 's/^description:[[:space:]]*//' | sed 's/^>-[[:space:]]*//')

  # Skip if no name extracted
  [[ -z "$skill_name" ]] && continue

  # Skip already-installed skills
  if echo "$INSTALLED" | grep -qxF "$skill_name"; then
    echo "INSTALLED:${skill_name}" >> "$RESULTS_FILE"
    continue
  fi

  # Get repo metadata (stars, last push)
  repo_meta=$(gh api "repos/${repo_full}" --jq '{stars: .stargazers_count, pushed: .pushed_at}' 2>/dev/null) || continue
  stars=$(echo "$repo_meta" | jq -r '.stars')
  pushed=$(echo "$repo_meta" | jq -r '.pushed')

  # Calculate days since last push
  pushed_epoch=$(date -d "$pushed" +%s 2>/dev/null || echo 0)
  now_epoch=$(date +%s)
  days_ago=$(( (now_epoch - pushed_epoch) / 86400 ))

  if [[ $days_ago -le 1 ]]; then
    age_label="today"
  elif [[ $days_ago -le 7 ]]; then
    age_label="${days_ago}d ago"
  elif [[ $days_ago -le 30 ]]; then
    age_label="$((days_ago / 7))w ago"
  elif [[ $days_ago -le 365 ]]; then
    age_label="$((days_ago / 30))mo ago"
  else
    age_label=">1y ago"
  fi

  # Keyword relevance score (count keyword matches in name + description)
  combined_text=$(echo "${skill_name} ${skill_desc}" | tr '[:upper:]' '[:lower:]')
  relevance=0
  while IFS= read -r kw; do
    [[ -z "$kw" ]] && continue
    if echo "$combined_text" | grep -qi "$kw"; then
      relevance=$((relevance + 1))
    fi
  done <<< "$KEYWORDS"

  # Output: relevance|stars|days_ago|skill_name|repo_full|path|skill_desc|age_label
  echo "${relevance}|${stars}|${days_ago}|${skill_name}|${repo_full}|${path}|${skill_desc}|${age_label}" >> "$RESULTS_FILE"

  COUNT=$((COUNT + 1))
done < "$DEDUPED_FILE"

endlog

# ── Step 4: Rank and build issue body ────────────────────────────────────────

log "Building issue body"

# Separate installed skills and candidates
INSTALLED_LIST=$(grep '^INSTALLED:' "$RESULTS_FILE" 2>/dev/null | sed 's/^INSTALLED://' | sort -u | tr '\n' ', ' | sed 's/,$//' || true)
CANDIDATE_LINES=$(grep -v '^INSTALLED:' "$RESULTS_FILE" 2>/dev/null || true)

if [[ -z "$CANDIDATE_LINES" ]]; then
  echo "No new skill candidates found. Skipping issue creation."
  rm -f "$CANDIDATES_FILE" "$SEEN_FILE" "$RESULTS_FILE" "$DEDUPED_FILE"
  exit 0
fi

# Sort by relevance desc, then stars desc, then recency
SORTED=$(echo "$CANDIDATE_LINES" | sort -t'|' -k1,1rn -k2,2rn -k3,3n | head -n "$MAX_RECOMMENDATIONS")

# Build checkbox list
CHECKBOXES=""
while IFS='|' read -r _rel stars _days skill_name repo_full path skill_desc age_label; do
  [[ -z "$skill_name" ]] && continue
  repo_url="https://github.com/${repo_full}"
  CHECKBOXES="${CHECKBOXES}- [ ] **${skill_name}** | [${repo_full}](${repo_url}) | ${stars} stars | Updated ${age_label}
  > ${skill_desc}

"
done <<< "$SORTED"

# Compose issue body
ISSUE_BODY="## Weekly Skill Recommendations — ${DATE}

Check the skills you want, then comment \`@claude install the checked skills from this issue\`.

${CHECKBOXES}"

if [[ -n "$INSTALLED_LIST" ]]; then
  ISSUE_BODY="${ISSUE_BODY}### Already installed (skipped)
${INSTALLED_LIST}

"
fi

ISSUE_BODY="${ISSUE_BODY}---
*Auto-generated by ss-weekly-discover*"

endlog

# ── Step 5: Create issue ────────────────────────────────────────────────────

log "Creating GitHub issue"

gh issue create \
  --repo "$REPO" \
  --title "Weekly Skill Recommendations — ${DATE}" \
  --label "$LABEL" \
  --body "$ISSUE_BODY"

echo "Issue created successfully."
endlog

# Cleanup
rm -f "$CANDIDATES_FILE" "$SEEN_FILE" "$RESULTS_FILE" "$DEDUPED_FILE"
