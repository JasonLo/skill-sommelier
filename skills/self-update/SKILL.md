---
name: self-update
description: >-
  Check for skill-sommelier plugin updates and apply them. Compares installed
  plugin git HEAD against remote, shows changelog, and pulls updates. Use when
  the user says "update skills", "check for updates", "am I up to date",
  "update skill-sommelier", or "new skills available".
allowed-tools:
  - Bash
  - Read
  - Grep
  - WebFetch
---

# Self-Update

Check if the installed skill-sommelier plugin is up to date and apply updates.

## Phase 1 — Locate installed plugin

Find the installed plugin directory and read the current version.

```
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/skill-sommelier"
```

1. Check if `$PLUGIN_DIR` exists
2. If not found, report: "skill-sommelier is not installed via the marketplace. Install with `/plugin marketplace add JasonLo/skill-sommelier`" and **stop**
3. Run `git -C "$PLUGIN_DIR" rev-parse HEAD` to get the local SHA
4. Run `git -C "$PLUGIN_DIR" log -1 --format="%h %s (%cr)"` to get a human-readable current version

## Phase 2 — Check remote for updates

Fetch the latest remote state without modifying the local clone.

1. Run `git -C "$PLUGIN_DIR" fetch origin main --quiet`
2. Get remote SHA: `git -C "$PLUGIN_DIR" rev-parse origin/main`
3. If the fetch fails (no internet, auth issues), report the error and **stop**

## Phase 3 — Compare versions

Compare local HEAD against remote HEAD.

1. If local SHA == remote SHA → report "skill-sommelier is up to date" with the current SHA short hash, show days since last commit using `git -C "$PLUGIN_DIR" log -1 --format="%cr"`, and **stop**
2. If different, get the changelog:
   ```
   git -C "$PLUGIN_DIR" log --oneline HEAD..origin/main
   ```
3. Count new commits and list changed skills:
   ```
   git -C "$PLUGIN_DIR" diff --name-only HEAD..origin/main -- skills/
   ```

## Phase 4 — Present update summary

Display a clear summary to the user:

- **Installed:** `<short-sha>` (`<date>`)
- **Latest:** `<short-sha>` (`<date>`)
- **New commits:** `<count>`
- **Changed skills:** list each affected skill directory
- **Commit log:** show the oneline log from Phase 3

Ask: "Would you like to update now?"

## Phase 5 — Execute update

Only proceed if the user confirms.

1. Check for local modifications: `git -C "$PLUGIN_DIR" status --porcelain`
   - If there are local changes, warn the user and ask whether to proceed (changes will be overwritten)
2. Pull the update:
   ```
   git -C "$PLUGIN_DIR" pull origin main --ff-only
   ```
3. If `--ff-only` fails (diverged history), try:
   ```
   git -C "$PLUGIN_DIR" reset --hard origin/main
   ```
   Only with user confirmation since this discards local changes.
4. Verify: run `git -C "$PLUGIN_DIR" rev-parse HEAD` and confirm it matches the remote SHA
5. Report success with the new version

## Edge Cases

- **Plugin not installed:** Direct user to `/plugin marketplace add JasonLo/skill-sommelier`
- **No internet / fetch fails:** Report error clearly, do not attempt update
- **Local modifications in plugin dir:** Warn before overwriting
- **Already up to date:** Report and stop early
- **Diverged history:** Offer `reset --hard` with explicit user confirmation
