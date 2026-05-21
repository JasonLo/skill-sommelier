# Self-Update Patterns

Strategies for implementing auto-update functionality in CLI tools.

## Overview

Auto-update allows users to easily upgrade to the latest version without reinstalling. Choose the pattern that fits your project's distribution method.

## Pattern 1: Built-in Self-Update Command

Best for: Compiled binaries, Python tools via uv/pipx

### Implementation (uv tool)

```bash
#!/bin/bash
# Add this to your CLI tool as a subcommand

case "${1:-}" in
    update|self-update|--update)
        echo "Updating $(basename "$0")..."
        REPO="git+https://github.com/USER/PROJECT.git"
        uv tool upgrade --from "$REPO" PROJECT_NAME
        echo "✓ Updated successfully"
        exit 0
        ;;
esac
```

### Implementation (cargo binary)

```rust
// In your Rust CLI tool
use std::process::Command;

fn self_update() -> Result<(), Box<dyn std::error::Error>> {
    println!("Updating...");
    let status = Command::new("cargo")
        .args(&["install", "--git", "https://github.com/USER/PROJECT", "--force"])
        .status()?;

    if status.success() {
        println!("✓ Updated successfully");
    } else {
        println!("✗ Update failed");
    }
    Ok(())
}

// In main.rs
match args.command {
    Command::Update => self_update()?,
    // ...
}
```

### Usage

```bash
mytool update
# or
mytool --self-update
```

## Pattern 2: Separate Update Script

Best for: Git-cloned tools, shell scripts

### Implementation

Create `scripts/update.sh`:

```bash
#!/bin/sh
set -eu

INSTALL_DIR="$HOME/.local/PROJECT_NAME"

echo "=== PROJECT_NAME updater ==="
echo

if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: PROJECT_NAME not found at $INSTALL_DIR"
    echo "Install first with:"
    echo "  curl -LsSf https://example.com/install.sh | sh"
    exit 1
fi

# Fetch latest
echo "Fetching updates..."
git -C "$INSTALL_DIR" fetch origin main

# Check if already up to date
LOCAL=$(git -C "$INSTALL_DIR" rev-parse HEAD)
REMOTE=$(git -C "$INSTALL_DIR" rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✓ Already up to date"
    exit 0
fi

# Show changes
echo
echo "Changes:"
git -C "$INSTALL_DIR" log --oneline HEAD..origin/main
echo

printf "Update now? (Y/n): "
read -r response < /dev/tty
case "$response" in
    [Nn]) echo "Cancelled."; exit 0 ;;
esac

# Pull updates
echo "Updating..."
git -C "$INSTALL_DIR" pull origin main

# Re-run any build/install steps if needed
# cd "$INSTALL_DIR" && make install

echo "✓ Updated successfully"
```

### Make it easy to run

Add to the main tool:

```bash
#!/bin/bash

case "${1:-}" in
    update)
        curl -fsSL https://example.com/update.sh | sh
        exit 0
        ;;
esac
```

Or tell users to run:

```bash
curl -LsSf https://example.com/update.sh | sh
```

## Pattern 3: Check on Startup

Best for: Tools run frequently, want passive notifications

### Implementation (Python)

```python
#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import urlopen, Request

VERSION = "1.0.0"
REPO = "USER/PROJECT"
CACHE_FILE = Path.home() / ".cache" / "PROJECT" / "version_check"

def check_for_updates():
    """Check for updates once per day, non-blocking."""
    # Rate limit: check once per day
    if CACHE_FILE.exists():
        mtime = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
        if datetime.now() - mtime < timedelta(days=1):
            return

    try:
        # Quick API call with timeout
        req = Request(
            f"https://api.github.com/repos/{REPO}/releases/latest",
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        with urlopen(req, timeout=2) as response:
            data = json.loads(response.read())
            latest = data["tag_name"].lstrip("v")

        # Cache result
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(latest)

        # Notify if outdated
        if latest != VERSION:
            print(f"⚠ New version available: {latest} (current: {VERSION})", file=sys.stderr)
            print(f"  Update with: PROJECT_NAME update", file=sys.stderr)
            print(file=sys.stderr)
    except Exception:
        pass  # Silently fail - don't interrupt the tool

def main():
    # Check for updates in background (non-blocking)
    check_for_updates()

    # ... rest of your tool
    pass

if __name__ == "__main__":
    main()
```

### Implementation (Bash)

```bash
#!/bin/bash

VERSION="1.0.0"
REPO="USER/PROJECT"
CACHE_FILE="$HOME/.cache/PROJECT/version_check"

check_updates() {
    # Rate limit: once per day
    if [ -f "$CACHE_FILE" ]; then
        if [ $(($(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE"))) -lt 86400 ]; then
            return
        fi
    fi

    # Quick check with timeout
    latest=$(curl -fsSL -m 2 \
        "https://api.github.com/repos/$REPO/releases/latest" \
        | grep -o '"tag_name": *"v[^"]*"' \
        | head -1 \
        | cut -d'"' -f4 \
        | sed 's/^v//' \
        2>/dev/null)

    if [ -n "$latest" ] && [ "$latest" != "$VERSION" ]; then
        mkdir -p "$(dirname "$CACHE_FILE")"
        echo "$latest" > "$CACHE_FILE"
        echo "⚠ New version available: $latest (current: $VERSION)" >&2
        echo "  Update with: $(basename "$0") update" >&2
        echo >&2
    fi
}

# Run check in background to not block startup
check_updates &

# ... rest of your tool
```

## Pattern 4: Re-run Installer

Best for: Simple tools, no special update logic needed

### Implementation

```bash
#!/bin/bash

case "${1:-}" in
    update)
        echo "Re-running installer..."
        curl -LsSf https://example.com/install.sh | sh
        exit 0
        ;;
esac
```

This literally just re-runs the install script, which:
- Re-downloads/re-clones the tool
- Overwrites the old version
- Preserves config (if installer checks for existing config)

**Pros:** Simplest possible approach
**Cons:** Might be slower than targeted update

## Pattern 5: Version File Checking

Best for: Tools with a published version file

### Setup

Create a `version.txt` in your repo:

```
1.0.0
```

Update it on each release.

### Implementation

```bash
#!/bin/bash

CURRENT_VERSION="1.0.0"
VERSION_URL="https://raw.githubusercontent.com/USER/PROJECT/main/version.txt"

check_version() {
    latest=$(curl -fsSL -m 2 "$VERSION_URL" 2>/dev/null | tr -d '[:space:]')

    if [ -n "$latest" ] && [ "$latest" != "$CURRENT_VERSION" ]; then
        echo "⚠ Update available: $latest (current: $CURRENT_VERSION)"
        echo "  Run: $(basename "$0") update"
        return 1
    fi
    return 0
}

update() {
    echo "Updating..."
    # Re-download script or re-run installer
    curl -LsSf https://example.com/install.sh | sh
}

case "${1:-}" in
    update) update; exit 0 ;;
    --check-version) check_version; exit $? ;;
esac

# Optional: check on every run
check_version || true
```

## Comparison

| Pattern | Pros | Cons | Best For |
|---------|------|------|----------|
| Built-in command | Clean UX, full control | Requires compiled tool or package manager | Binaries, Python tools |
| Separate script | Simple, works anywhere | Extra file to maintain | Git-cloned tools |
| Check on startup | Passive, reminds users | Can slow startup | Frequently-run tools |
| Re-run installer | Simplest implementation | Might be slow | Simple tools |
| Version file | Lightweight check | Need to maintain version file | Any tool |

## Best Practices

1. **Non-blocking checks**: Don't slow down tool startup
2. **Rate limiting**: Check at most once per day
3. **Graceful failures**: Silently fail if network unavailable
4. **Clear messages**: Tell users how to update
5. **Preserve config**: Don't overwrite user settings
6. **Atomic updates**: Use temp files + move, not in-place edits
7. **Rollback support**: Keep backup during update
8. **Test in CI**: Automate update testing

## Security Considerations

1. **HTTPS only**: Never update over HTTP
2. **Verify signatures**: For binary updates, check GPG/checksums
3. **Pin to tags**: Don't update from `main` in production
4. **User confirmation**: Ask before destructive operations
5. **Sandbox updates**: Test in temp dir before replacing

## Example: Complete Self-Update with Rollback

```bash
#!/bin/bash
set -eu

self_update() {
    SCRIPT_PATH="$(realpath "$0")"
    BACKUP="$SCRIPT_PATH.backup"
    TEMP="$SCRIPT_PATH.tmp"

    echo "Updating $(basename "$0")..."

    # Backup current version
    cp "$SCRIPT_PATH" "$BACKUP"

    # Download to temp file
    if curl -fsSL "$UPDATE_URL" -o "$TEMP"; then
        # Verify it's valid
        if bash -n "$TEMP" 2>/dev/null; then
            # Atomic replace
            mv "$TEMP" "$SCRIPT_PATH"
            chmod 755 "$SCRIPT_PATH"
            echo "✓ Updated successfully"
            rm -f "$BACKUP"
        else
            echo "✗ Downloaded file is invalid"
            rm -f "$TEMP"
            exit 1
        fi
    else
        echo "✗ Download failed"
        rm -f "$TEMP"
        exit 1
    fi
}

case "${1:-}" in
    update) self_update; exit 0 ;;
esac
```
