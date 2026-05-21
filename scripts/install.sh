#!/bin/sh
# skill-sommelier bootstrap installer.
#
# Prepares the environment for the skill-sommelier Claude Code plugin:
#   1. Claude Code (required)        — installs if missing
#   2. gh        (optional companion) — used by ss-skill-discover
#   3. uv        (optional companion) — used by Python-flavored skills
#   4. Prints the two slash commands you paste into Claude Code to add
#      the marketplace and install the plugin.
#
# Plugin install itself happens *inside* Claude Code — there is no shell
# entry point for `/plugin marketplace add`. This script just guarantees
# the prerequisites are in place.
#
# Usage:
#   curl -LsSf https://raw.githubusercontent.com/JasonLo/skill-sommelier/v0.6.0/scripts/install.sh | sh
#
# Flags / env:
#   --yes, INSTALLER_ASSUME_YES=1   non-interactive; required deps Y, optional N
#   INSTALL_CLAUDE_CODE=0           never auto-install Claude Code
#   INSTALL_GH=1                    opt in to gh during unattended runs
#   INSTALL_UV=1                    opt in to uv during unattended runs

set -eu

ASSUME_YES="${INSTALLER_ASSUME_YES:-0}"
INSTALL_CLAUDE_CODE_OVERRIDE="${INSTALL_CLAUDE_CODE:-}"
INSTALL_GH_OVERRIDE="${INSTALL_GH:-}"
INSTALL_UV_OVERRIDE="${INSTALL_UV:-}"

while [ $# -gt 0 ]; do
    case "$1" in
        -y|--yes) ASSUME_YES=1; shift ;;
        -h|--help)
            sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) printf 'Unknown flag: %s\n' "$1" >&2; exit 1 ;;
    esac
done

# Pipe-from-curl into a non-TTY shell (CI, Docker RUN, devcontainers) → unattended.
if [ ! -t 0 ] && [ ! -r /dev/tty ]; then
    ASSUME_YES=1
fi

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

confirm() {
    # confirm "<prompt>" <default Y|N>
    prompt="$1"
    default="${2:-N}"
    if [ "$ASSUME_YES" = "1" ]; then
        [ "$default" = "Y" ]
        return
    fi
    printf '%s ' "$prompt"
    read -r reply < /dev/tty || reply=""
    case "$reply" in
        [Yy]) return 0 ;;
        [Nn]) return 1 ;;
        "")   [ "$default" = "Y" ] ;;
        *)    return 1 ;;
    esac
}

have() { command -v "$1" >/dev/null 2>&1; }

# Detect a usable system package manager for installing gh. Empty if none.
detect_pkg_mgr() {
    if   have brew;   then echo brew
    elif have apt-get;then echo apt
    elif have dnf;    then echo dnf
    elif have yum;    then echo yum
    elif have pacman; then echo pacman
    elif have zypper; then echo zypper
    fi
}

# Download a remote install script to a tmp file, then execute. Never pipe
# third-party URLs straight to a shell — the file goes to disk first so it
# could be reviewed if anything looks off.
run_remote_installer() {
    url="$1"
    label="$2"
    runner="${3:-sh}"
    tmp="$(mktemp "${TMPDIR:-/tmp}/skill-sommelier-${label}.XXXXXX.sh")"
    trap 'rm -f "$tmp"' EXIT HUP INT TERM
    if ! curl -fsSL "$url" -o "$tmp"; then
        printf '  ✗ failed to download %s installer from %s\n' "$label" "$url" >&2
        rm -f "$tmp"
        trap - EXIT HUP INT TERM
        return 1
    fi
    "$runner" "$tmp"
    rc=$?
    rm -f "$tmp"
    trap - EXIT HUP INT TERM
    return $rc
}

echo "=== skill-sommelier bootstrap ==="
echo

# ---------------------------------------------------------------------------
# [1/4] Claude Code (required)
# ---------------------------------------------------------------------------

printf '[1/4] Checking Claude Code... '
if have claude; then
    cc_version="$(claude --version 2>/dev/null | head -n1 || echo 'installed')"
    printf '✓ %s\n' "$cc_version"
else
    echo "not found"
    if [ "$INSTALL_CLAUDE_CODE_OVERRIDE" = "0" ]; then
        echo "      INSTALL_CLAUDE_CODE=0 set — skipping. Install Claude Code yourself, then re-run."
        exit 1
    fi
    if confirm "      Install Claude Code? (Y/n)" "Y"; then
        installed=0
        # Anthropic's native installer (preferred — no Node required).
        if run_remote_installer "https://claude.ai/install.sh" "claude-code" "bash"; then
            installed=1
        elif have npm; then
            echo "      native installer failed — falling back to npm"
            if npm install -g @anthropic-ai/claude-code; then
                installed=1
            fi
        fi
        if [ "$installed" = "0" ]; then
            echo "      ✗ Could not install Claude Code automatically." >&2
            echo "        See https://docs.claude.com/claude-code for manual instructions." >&2
            exit 1
        fi
        if ! have claude; then
            echo "      ⚠ 'claude' is installed but not on PATH yet."
            echo "        Open a new shell, or follow the installer's PATH hint above."
        fi
    else
        echo "      Skipped. skill-sommelier requires Claude Code — install it and re-run."
        exit 1
    fi
fi
echo

# ---------------------------------------------------------------------------
# [2/4] gh — optional, used by ss-skill-discover for GitHub search
# ---------------------------------------------------------------------------

printf '[2/4] Optional: gh CLI (for ss-skill-discover)... '
if have gh; then
    printf '✓ %s\n' "$(gh --version 2>/dev/null | head -n1)"
else
    echo "not found"
    default_gh="N"
    [ "$INSTALL_GH_OVERRIDE" = "1" ] && default_gh="Y"
    if confirm "      Install gh? (y/N)" "$default_gh"; then
        pm="$(detect_pkg_mgr)"
        case "$pm" in
            brew)   brew install gh ;;
            apt)    sudo -v && sudo apt-get update && sudo apt-get install -y gh ;;
            dnf)    sudo -v && sudo dnf install -y gh ;;
            yum)    sudo -v && sudo yum install -y gh ;;
            pacman) sudo -v && sudo pacman -S --noconfirm github-cli ;;
            zypper) sudo -v && sudo zypper install -y gh ;;
            *)
                echo "      ⚠ No supported package manager detected."
                echo "        See https://github.com/cli/cli#installation"
                ;;
        esac
        have gh && printf '      ✓ gh installed\n' || true
    else
        echo "      Skipped. ss-skill-discover will prompt you for gh later if it needs it."
    fi
fi
echo

# ---------------------------------------------------------------------------
# [3/4] uv — optional, used by Python skills (ss-modern-python, ss-python-to-chtc, ...)
# ---------------------------------------------------------------------------

printf '[3/4] Optional: uv (for Python skills)... '
if have uv; then
    printf '✓ %s\n' "$(uv --version 2>/dev/null | head -n1)"
else
    echo "not found"
    default_uv="N"
    [ "$INSTALL_UV_OVERRIDE" = "1" ] && default_uv="Y"
    if confirm "      Install uv? (y/N)" "$default_uv"; then
        if run_remote_installer "https://astral.sh/uv/install.sh" "uv" "sh"; then
            have uv && printf '      ✓ uv installed\n' || \
                echo "      ⚠ uv installed but not on PATH yet — open a new shell."
        else
            echo "      ✗ uv install failed. See https://docs.astral.sh/uv/" >&2
        fi
    else
        echo "      Skipped. The Python-flavored skills will work without it, but slower."
    fi
fi
echo

# ---------------------------------------------------------------------------
# [4/4] Plugin install — runs inside Claude Code
# ---------------------------------------------------------------------------

cat <<'EOF'
[4/4] Bootstrap complete.

Open Claude Code and paste these two commands:

    /plugin marketplace add JasonLo/skill-sommelier
    /plugin install skill-sommelier@skill-sommelier

Quickstart once installed:

    /skill-sommelier:ss-skill-discover

Updates:
    /skill-sommelier:ss-update          — check + apply skill-sommelier updates
    /plugin marketplace update          — refresh the marketplace cache

Uninstall later:
    curl -LsSf https://raw.githubusercontent.com/JasonLo/skill-sommelier/v0.6.0/scripts/uninstall.sh | sh
EOF
