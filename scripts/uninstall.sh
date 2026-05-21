#!/bin/sh
# skill-sommelier uninstaller.
#
# Removes whatever the bootstrap installer touched outside of Claude Code.
# The plugin itself lives inside Claude Code's marketplace cache and can only
# be removed via slash commands — this script prints those for you.
#
# Usage:
#   curl -LsSf https://raw.githubusercontent.com/JasonLo/skill-sommelier/v0.6.0/scripts/uninstall.sh | sh
#
# Flags:
#   --yes    skip confirmation prompts (also auto-enabled when not on a TTY)

set -eu

ASSUME_YES="${INSTALLER_ASSUME_YES:-0}"

while [ $# -gt 0 ]; do
    case "$1" in
        -y|--yes) ASSUME_YES=1; shift ;;
        -h|--help)
            sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) printf 'Unknown flag: %s\n' "$1" >&2; exit 1 ;;
    esac
done

if [ ! -t 0 ] && [ ! -r /dev/tty ]; then
    ASSUME_YES=1
fi

confirm() {
    [ "$ASSUME_YES" = "1" ] && return 0
    printf '%s (y/N): ' "$1"
    read -r reply < /dev/tty || reply=""
    case "$reply" in [Yy]) return 0 ;; *) return 1 ;; esac
}

echo "=== skill-sommelier uninstaller ==="
echo

cat <<'EOF'
The skill-sommelier plugin is managed by Claude Code, not by this script.
To remove it, open Claude Code and run:

    /plugin uninstall skill-sommelier@skill-sommelier
    /plugin marketplace remove JasonLo/skill-sommelier

EOF

# Optional cleanup of skill-sommelier's own profile cache (built by ss-skill-discover).
PROFILE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/skill-sommelier"
if [ -d "$PROFILE_DIR" ]; then
    if confirm "Delete locally cached profile at $PROFILE_DIR?"; then
        rm -rf "$PROFILE_DIR"
        printf '  ✓ removed %s\n' "$PROFILE_DIR"
    else
        printf '  Kept %s\n' "$PROFILE_DIR"
    fi
fi

# The bootstrap installer offered Claude Code, gh, and uv. Removing those is
# out of scope for this uninstaller — they're general-purpose tools you may
# use elsewhere. To remove them yourself:
cat <<'EOF'

The bootstrap installer also offered Claude Code, gh, and uv. Those are
left in place — remove them yourself if you no longer need them:

    Claude Code:  see https://docs.claude.com/claude-code
    gh:           your package manager (e.g. `brew uninstall gh`)
    uv:           uv self uninstall    (or `rm ~/.cargo/bin/uv` on older installs)

Done.
EOF
