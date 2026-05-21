# Install Script Templates

Production-ready templates for different project types.

## Template: uv-tool (Python Package)

For Python packages installed via `uv tool install`.

```bash
#!/bin/sh
set -eu

REPO="git+https://github.com/USER/PROJECT.git"
CONFIG_DIR="$HOME/.config/PROJECT_NAME"
ENV_FILE="$CONFIG_DIR/.env"
PYTHON_VERSION="3.13"

echo "=== PROJECT_NAME installer ==="
echo

# Install as a uv tool
echo "Installing PROJECT_NAME..."
uv tool install "$REPO" --python "$PYTHON_VERSION"
echo

# Set up configuration (if needed)
if [ -f "$ENV_FILE" ]; then
    echo "Configuration already exists at $ENV_FILE"
    printf "Overwrite? (y/N): "
    read -r overwrite < /dev/tty
    case "$overwrite" in
        [Yy]) ;;
        *)
            echo "Keeping existing configuration."
            echo
            echo "Done! Run 'COMMAND_NAME' to start."
            exit 0
            ;;
    esac
fi

# Prompt for configuration
echo "Enter configuration values:"
echo

while true; do
    printf "API Key: "
    read -r api_key < /dev/tty
    [ -n "$api_key" ] && break
    echo "API key cannot be empty."
done

while true; do
    old_stty=$(stty -g < /dev/tty)
    trap 'stty "$old_stty" < /dev/tty' EXIT HUP INT TERM
    printf "Secret: "
    stty -echo < /dev/tty
    read -r secret < /dev/tty
    stty "$old_stty" < /dev/tty
    trap - EXIT HUP INT TERM
    echo
    [ -n "$secret" ] && break
    echo "Secret cannot be empty."
done

mkdir -p "$CONFIG_DIR"
cat > "$ENV_FILE" <<EOF
API_KEY=$api_key
SECRET=$secret
EOF
chmod 600 "$ENV_FILE"
echo
echo "Configuration saved to $ENV_FILE"

# Optional dependencies
echo
if command -v optional_dep >/dev/null 2>&1; then
    echo "optional_dep found."
else
    printf "Install optional_dep for extra features? (y/N): "
    read -r install_dep < /dev/tty
    case "$install_dep" in
        [Yy])
            sudo -v
            tmp_install_script="$(mktemp)"
            curl -fsSL https://example.com/install.sh -o "$tmp_install_script"
            sudo bash "$tmp_install_script"
            rm -f "$tmp_install_script"
            ;;
        *) echo "Skipping optional_dep." ;;
    esac
fi

echo
echo "Done! Run 'COMMAND_NAME' to start."
```

## Template: cargo (Rust Binary)

For Rust binaries installed via `cargo install`.

```bash
#!/bin/sh
set -eu

REPO="https://github.com/USER/PROJECT"
BINARY_NAME="project"
CONFIG_DIR="$HOME/.config/$BINARY_NAME"

echo "=== $BINARY_NAME installer ==="
echo

# Check for cargo
if ! command -v cargo >/dev/null 2>&1; then
    echo "Error: cargo not found. Install Rust from https://rustup.rs"
    exit 1
fi

# Install binary
echo "Installing $BINARY_NAME..."
cargo install --git "$REPO" --locked
echo

# Create default config
mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
    cat > "$CONFIG_DIR/config.toml" <<EOF
# Default configuration
[settings]
option = "value"
EOF
    echo "Default config created at $CONFIG_DIR/config.toml"
fi

echo
echo "Done! Run '$BINARY_NAME --help' to start."
```

## Template: script (Shell Script)

For standalone shell scripts.

```bash
#!/bin/sh
set -eu

REPO="https://github.com/USER/PROJECT"
SCRIPT_NAME="script.sh"
INSTALL_DIR="$HOME/.local/bin"

echo "=== $SCRIPT_NAME installer ==="
echo

# Download script
mkdir -p "$INSTALL_DIR"
echo "Downloading $SCRIPT_NAME..."
curl -fsSL "$REPO/raw/main/$SCRIPT_NAME" -o "$INSTALL_DIR/$SCRIPT_NAME"
chmod 755 "$INSTALL_DIR/$SCRIPT_NAME"

# Check if in PATH
case ":$PATH:" in
    *":$INSTALL_DIR:"*)
        echo "✓ $INSTALL_DIR is in PATH" ;;
    *)
        echo "⚠ Add $INSTALL_DIR to PATH:"
        echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
        echo "  Add to ~/.bashrc or ~/.zshrc to persist" ;;
esac

echo
echo "Done! Run '$SCRIPT_NAME' to start."
```

## Template: generic (Flexible)

Generic template for any installation method.

```bash
#!/bin/sh
set -eu

PROJECT_NAME="myproject"
INSTALL_DIR="$HOME/.local/$PROJECT_NAME"
BIN_DIR="$HOME/.local/bin"

echo "=== $PROJECT_NAME installer ==="
echo

# Check dependencies
if ! command -v git >/dev/null 2>&1; then
    echo "Error: git is required but not installed." >&2
    exit 1
fi

# Clone or download
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation..."
    git -C "$INSTALL_DIR" pull origin main
else
    echo "Installing $PROJECT_NAME..."
    git clone https://github.com/USER/PROJECT "$INSTALL_DIR"
fi

# Install/build
cd "$INSTALL_DIR"
# Add project-specific install commands here
# Examples:
# - make install
# - python setup.py install
# - npm install -g .

# Command/binary name
COMMAND_NAME="command"

# Create symlink in PATH
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/bin/$COMMAND_NAME" "$BIN_DIR/$COMMAND_NAME"

echo
echo "Done! Run '$COMMAND_NAME' to start."
```

## Common Patterns

### Error Handling

```bash
set -eu  # Exit on error, undefined variables

# Check for required commands
if ! command -v git >/dev/null 2>&1; then
    echo "Error: git not found. Please install git first."
    exit 1
fi
```

### Interactive Prompts

```bash
# Read from /dev/tty (works when piped from curl)
printf "Continue? (y/N): "
read -r response < /dev/tty
case "$response" in
    [Yy]) echo "Continuing..." ;;
    *) echo "Aborted."; exit 1 ;;
esac
```

### Hide Password Input

```bash
old_stty=$(stty -g < /dev/tty)
trap 'stty "$old_stty" < /dev/tty' EXIT HUP INT TERM
printf "Password: "
stty -echo < /dev/tty
read -r password < /dev/tty
stty "$old_stty" < /dev/tty
trap - EXIT HUP INT TERM
echo
```

### Optional Dependencies

```bash
if command -v rclone >/dev/null 2>&1; then
    echo "✓ rclone found"
else
    printf "Install rclone? (y/N): "
    read -r install_rclone < /dev/tty
    case "$install_rclone" in
        [Yy])
            sudo -v
            _tmp_script="$(mktemp)"
            curl -fsSL https://rclone.org/install.sh -o "$_tmp_script"
            sudo bash "$_tmp_script"
            rm -f "$_tmp_script"
            ;;
        *) echo "Skipped." ;;
    esac
fi
```

### Check if Already Installed

```bash
if command -v mycommand >/dev/null 2>&1; then
    echo "mycommand is already installed:"
    mycommand --version
    printf "Reinstall? (y/N): "
    read -r reinstall < /dev/tty
    case "$reinstall" in
        [Yy]) ;;
        *) echo "Keeping existing installation."; exit 0 ;;
    esac
fi
```

### File Permissions

```bash
# Secrets: owner read/write only
chmod 600 "$ENV_FILE"

# Executables: owner rwx, group/other rx
chmod 755 "$BINARY"

# Config: owner rw, group/other r
chmod 644 "$CONFIG"
```

### Checksum Verification

For any binary or archive download, verify a checksum **before** extracting or executing. `tar tzf` only detects corruption, not tampering. Publish a `.sha256` file next to each release asset.

```sh
URL="https://github.com/USER/PROJECT/releases/download/v1.0.0/project-x86_64-linux.tar.gz"
SHA_URL="${URL}.sha256"
TMP_ARCHIVE="$(mktemp "${TMPDIR:-/tmp}/project.XXXXXX.tar.gz")"
TMP_SHA="$(mktemp "${TMPDIR:-/tmp}/project.XXXXXX.sha256")"
trap 'rm -f "$TMP_ARCHIVE" "$TMP_SHA"' EXIT HUP INT TERM

echo "Downloading..."
curl -fsSL -o "$TMP_ARCHIVE" "$URL"
curl -fsSL -o "$TMP_SHA" "$SHA_URL"

# The .sha256 file should contain: "<hex>  <filename>"
# Rewrite the filename column so sha256sum -c finds our temp file.
expected=$(awk '{print $1}' "$TMP_SHA")
echo "${expected}  $TMP_ARCHIVE" | sha256sum -c - || {
    echo "✗ Checksum mismatch — refusing to install" >&2
    exit 1
}
echo "✓ Checksum verified"

# Safe to extract now
tar xzf "$TMP_ARCHIVE" -C "$INSTALL_DIR"
```

On macOS use `shasum -a 256 -c -` instead of `sha256sum -c -` (or detect: `command -v sha256sum || alias sha256sum='shasum -a 256'`).

For stronger guarantees, use signature verification (minisign, cosign, GPG) — checksums protect against a corrupt CDN but not a compromised release pipeline.

### Non-Interactive Mode

Installers piped through `curl | sh` from a CI job, Dockerfile `RUN`, or devcontainer have no TTY. If your script blocks on `read < /dev/tty`, the install hangs forever. Always provide an unattended path.

```sh
#!/bin/sh
set -eu

ASSUME_YES="${INSTALLER_ASSUME_YES:-0}"

# Parse flags
while [ $# -gt 0 ]; do
    case "$1" in
        -y|--yes) ASSUME_YES=1; shift ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

# Auto-enable if stdin is not a TTY (curl | sh in CI, Docker RUN, etc.)
if [ ! -t 0 ] && [ ! -r /dev/tty ]; then
    ASSUME_YES=1
fi

# Wrapper for any y/N prompt
confirm() {
    prompt="$1"
    default="${2:-N}"   # "Y" or "N"
    if [ "$ASSUME_YES" = "1" ]; then
        [ "$default" = "Y" ]
        return
    fi
    printf "%s " "$prompt"
    read -r reply < /dev/tty
    case "$reply" in
        [Yy]) return 0 ;;
        [Nn]) return 1 ;;
        "")   [ "$default" = "Y" ] ;;
        *)    return 1 ;;
    esac
}

# Usage
if confirm "Install optional rclone? (y/N)"; then
    echo "Installing rclone..."
fi
```

Document both invocations in the README:

```bash
# Interactive (default)
curl -LsSf https://.../install.sh | sh

# Unattended (CI, Docker, devcontainers)
curl -LsSf https://.../install.sh | sh -s -- --yes
# or
INSTALLER_ASSUME_YES=1 curl -LsSf https://.../install.sh | sh
```

Note the `sh -s --` is required to pass flags through a pipe.

### Pinning the Install URL

In the README, default to a tagged URL — never `main` — for production users:

```bash
# Pinned (recommended in README)
curl -LsSf https://raw.githubusercontent.com/USER/PROJECT/v1.0.0/scripts/install.sh | sh

# Tracking main (contributors only)
curl -LsSf https://raw.githubusercontent.com/USER/PROJECT/main/scripts/install.sh | sh
```

A commit SHA is even stronger than a tag (tags can be moved):

```bash
curl -LsSf https://raw.githubusercontent.com/USER/PROJECT/a1b2c3d/scripts/install.sh | sh
```

Bump the pinned tag in the README on every release.

## Template: uninstall (Companion)

Every installer needs an uninstaller. This template covers the common cases.

```sh
#!/bin/sh
set -eu

PROJECT_NAME="myproject"
COMMAND_NAME="mytool"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/$PROJECT_NAME"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$PROJECT_NAME"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/$PROJECT_NAME"

PURGE=0
ASSUME_YES="${INSTALLER_ASSUME_YES:-0}"

while [ $# -gt 0 ]; do
    case "$1" in
        --purge) PURGE=1; shift ;;
        -y|--yes) ASSUME_YES=1; shift ;;
        -h|--help)
            cat <<EOF
Usage: uninstall.sh [--purge] [--yes]

  --purge   Also remove config, data, and cache directories
  --yes     Skip confirmation prompts
EOF
            exit 0 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

if [ ! -t 0 ] && [ ! -r /dev/tty ]; then
    ASSUME_YES=1
fi

confirm() {
    [ "$ASSUME_YES" = "1" ] && return 0
    printf "%s (y/N): " "$1"
    read -r reply < /dev/tty
    case "$reply" in [Yy]) return 0 ;; *) return 1 ;; esac
}

echo "=== $PROJECT_NAME uninstaller ==="
echo

REMOVED=""

# Remove the binary / package
# Pick the line(s) that match how you installed:
if command -v uv >/dev/null 2>&1 && uv tool list 2>/dev/null | grep -q "^$PROJECT_NAME"; then
    confirm "Uninstall $PROJECT_NAME via uv tool?" && {
        uv tool uninstall "$PROJECT_NAME"
        REMOVED="$REMOVED\n  - uv tool: $PROJECT_NAME"
    }
elif command -v cargo >/dev/null 2>&1 && cargo install --list 2>/dev/null | grep -q "^$PROJECT_NAME "; then
    confirm "Uninstall $PROJECT_NAME via cargo?" && {
        cargo uninstall "$PROJECT_NAME"
        REMOVED="$REMOVED\n  - cargo: $PROJECT_NAME"
    }
elif [ -f "$HOME/.local/bin/$COMMAND_NAME" ]; then
    confirm "Remove $HOME/.local/bin/$COMMAND_NAME?" && {
        rm -f "$HOME/.local/bin/$COMMAND_NAME"
        REMOVED="$REMOVED\n  - binary: $HOME/.local/bin/$COMMAND_NAME"
    }
else
    echo "No installation found — nothing to remove."
fi

# Config / data / cache are kept by default (user data principle).
# --purge opts in to wiping them.
if [ "$PURGE" = "1" ]; then
    for dir in "$CONFIG_DIR" "$DATA_DIR" "$CACHE_DIR"; do
        [ -d "$dir" ] || continue
        confirm "Delete $dir?" && {
            rm -rf "$dir"
            REMOVED="$REMOVED\n  - directory: $dir"
        }
    done
else
    echo
    echo "Config, data, and cache directories were preserved."
    echo "Run with --purge to remove them as well."
fi

echo
if [ -n "$REMOVED" ]; then
    printf "Removed:%b\n" "$REMOVED"
else
    echo "Nothing was removed."
fi
echo "Done."
```

Document in the README:

```bash
# Remove the tool, keep config
curl -LsSf https://raw.githubusercontent.com/USER/PROJECT/v1.0.0/scripts/uninstall.sh | sh

# Remove the tool and wipe config/data
curl -LsSf https://raw.githubusercontent.com/USER/PROJECT/v1.0.0/scripts/uninstall.sh | sh -s -- --purge
```
