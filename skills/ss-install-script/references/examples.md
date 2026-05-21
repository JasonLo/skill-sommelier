# Install Script Examples

Real-world examples of production install scripts.

## Example 1: uw-s3 (Python Tool with Credentials)

From https://github.com/jasonlo/uw-s3

```bash
#!/bin/sh
set -eu

REPO="git+https://github.com/jasonlo/uw-s3.git"
CONFIG_DIR="$HOME/.config/uw-s3"
ENV_FILE="$CONFIG_DIR/.env"

echo "=== uw-s3 installer ==="
echo

# Install uw-s3 as a uv tool
echo "Installing uw-s3..."
uv tool install "$REPO" --python 3.14
echo

# Set up credentials
if [ -f "$ENV_FILE" ]; then
    echo "Credentials already configured at $ENV_FILE"
    printf "Overwrite? (y/N): "
    read -r overwrite < /dev/tty
    case "$overwrite" in
        [Yy]) ;;
        *)
            echo "Keeping existing credentials."
            echo
            echo "Done! Run 'uws3' to start."
            exit 0
            ;;
    esac
fi

echo "Enter your UW Research Object Storage credentials."
echo "Get them from https://storage.researchdata.wisc.edu"
echo

while true; do
    printf "Access Key ID: "
    read -r access_key < /dev/tty
    [ -n "$access_key" ] && break
    echo "Access key cannot be empty."
done

while true; do
    printf "Secret Access Key: "
    stty -echo < /dev/tty
    read -r secret_key < /dev/tty
    stty echo < /dev/tty
    echo
    [ -n "$secret_key" ] && break
    echo "Secret key cannot be empty."
done

mkdir -p "$CONFIG_DIR"
cat > "$ENV_FILE" <<EOF
S3_ACCESS_KEY_ID=$access_key
S3_SECRET_ACCESS_KEY=$secret_key
EOF
chmod 600 "$ENV_FILE"
echo
echo "Credentials saved to $ENV_FILE"

# Optional: install rclone for mount support
echo
if command -v rclone >/dev/null 2>&1; then
    echo "rclone found (mount support available)."
else
    printf "Install rclone for mount support? (y/N): "
    read -r install_rclone < /dev/tty
    case "$install_rclone" in
        [Yy])
            sudo -v
            rclone_install_script="$(mktemp)"
            curl -fsSL https://rclone.org/install.sh -o "$rclone_install_script"
            sudo bash "$rclone_install_script"
            rm -f "$rclone_install_script"
            ;;
        *) echo "Skipping rclone (mount feature will be unavailable)." ;;
    esac
fi

echo
echo "Done! Run 'uws3' to start."
```

**Key features:**
- Python tool via uv
- Credential setup with secure storage (chmod 600)
- Password input hidden with stty
- Optional dependency (rclone)
- Checks for existing config
- Clear user guidance

**Install command:**
```bash
curl -LsSf https://raw.githubusercontent.com/jasonlo/uw-s3/main/scripts/install.sh | sh
```

## Example 2: uv (Rust Binary with Self-Update)

From https://github.com/astral-sh/uv

```bash
#!/bin/sh
set -eu

# Detect platform
case "$(uname -s)" in
    Linux*) PLATFORM="unknown-linux-gnu" ;;
    Darwin*) PLATFORM="apple-darwin" ;;
    *) echo "Unsupported platform"; exit 1 ;;
esac

# Detect architecture
case "$(uname -m)" in
    x86_64) ARCH="x86_64" ;;
    aarch64|arm64) ARCH="aarch64" ;;
    *) echo "Unsupported architecture"; exit 1 ;;
esac

BINARY="uv-${ARCH}-${PLATFORM}"
URL="https://github.com/astral-sh/uv/releases/latest/download/${BINARY}.tar.gz"
INSTALL_DIR="$HOME/.local/bin"

echo "=== uv installer ==="
echo "Platform: ${ARCH}-${PLATFORM}"
echo

# Download and extract
mkdir -p "$INSTALL_DIR"
echo "Downloading uv..."
curl -LsSf "$URL" | tar xz -C "$INSTALL_DIR"

# Make executable
chmod 755 "$INSTALL_DIR/uv"

# Verify installation
if "$INSTALL_DIR/uv" --version >/dev/null 2>&1; then
    echo "✓ Installation successful"
    "$INSTALL_DIR/uv" --version
else
    echo "✗ Installation failed"
    exit 1
fi

# Check PATH
if echo "$PATH" | grep -q "$INSTALL_DIR"; then
    echo "✓ $INSTALL_DIR is in PATH"
else
    echo "⚠ Add to PATH:"
    echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
fi

echo
echo "Done! Run 'uv --help' to start."
echo "Update with: uv self update"
```

**Key features:**
- Platform/architecture detection
- Binary download from releases
- Verification step
- PATH checking
- Self-update support built into the tool

**Install command:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Example 3: rustup (Multi-Tool Installer)

Simplified version of https://rustup.rs

```bash
#!/bin/sh
set -eu

RUSTUP_HOME="${RUSTUP_HOME:-$HOME/.rustup}"
CARGO_HOME="${CARGO_HOME:-$HOME/.cargo}"

echo "=== Rust installer ==="
echo

# Check for existing installation
if [ -x "$CARGO_HOME/bin/rustup" ]; then
    echo "Rust is already installed:"
    "$CARGO_HOME/bin/rustup" --version
    printf "Reinstall? (y/N): "
    read -r reinstall < /dev/tty
    case "$reinstall" in
        [Yy]) ;;
        *) exit 0 ;;
    esac
fi

# Download and run rustup-init
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Downloading rustup-init..."
curl -fsSL https://sh.rustup.rs -o "$TEMP_DIR/rustup-init.sh"
chmod +x "$TEMP_DIR/rustup-init.sh"

echo
"$TEMP_DIR/rustup-init.sh" -y

# Source environment
if [ -f "$CARGO_HOME/env" ]; then
    . "$CARGO_HOME/env"
fi

echo
echo "Rust installed successfully!"
echo "Run 'rustup --help' for more information."
```

**Key features:**
- Checks for existing installation
- Uses temporary directory with cleanup trap
- Environment variable support
- Sources environment after install

## Example 4: Node Version Manager (nvm)

Simplified from https://github.com/nvm-sh/nvm

```bash
#!/bin/sh
set -eu

NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
REPO="https://github.com/nvm-sh/nvm.git"
VERSION="v0.39.0"

echo "=== nvm installer ==="
echo

# Clone or update
if [ -d "$NVM_DIR" ]; then
    echo "Updating nvm..."
    git -C "$NVM_DIR" fetch origin
    git -C "$NVM_DIR" checkout "$VERSION"
else
    echo "Installing nvm..."
    git clone "$REPO" "$NVM_DIR"
    git -C "$NVM_DIR" checkout "$VERSION"
fi

# Load nvm
. "$NVM_DIR/nvm.sh"

echo
echo "nvm installed successfully!"
echo
echo "Add to your shell profile (~/.bashrc, ~/.zshrc):"
echo "  export NVM_DIR=\"\$HOME/.nvm\""
echo "  [ -s \"\$NVM_DIR/nvm.sh\" ] && . \"\$NVM_DIR/nvm.sh\""
```

**Key features:**
- Git-based installation
- Version pinning
- Shell profile setup instructions
- Update support

## Example 5: Simple Script Installer

Minimal installer for a single script.

```bash
#!/bin/sh
set -eu

SCRIPT_URL="https://raw.githubusercontent.com/USER/REPO/main/script.sh"
INSTALL_DIR="$HOME/.local/bin"
SCRIPT_NAME="myscript"

echo "=== $SCRIPT_NAME installer ==="
echo

# Download script
mkdir -p "$INSTALL_DIR"
echo "Downloading $SCRIPT_NAME..."
curl -fsSL "$SCRIPT_URL" -o "$INSTALL_DIR/$SCRIPT_NAME"
chmod 755 "$INSTALL_DIR/$SCRIPT_NAME"

# Verify
if [ -x "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo "✓ Installed to $INSTALL_DIR/$SCRIPT_NAME"
else
    echo "✗ Installation failed"
    exit 1
fi

# Check PATH
if echo "$PATH" | grep -q "$INSTALL_DIR"; then
    echo "✓ Ready to use"
else
    echo "⚠ Add to PATH: export PATH=\"$INSTALL_DIR:\$PATH\""
fi

echo
echo "Done! Run '$SCRIPT_NAME' to start."
```

**Key features:**
- Minimal and fast
- Single file download
- Verification
- PATH guidance

## Self-Update Patterns

### Pattern 1: Git-based update (for scripts)

```bash
# In the script itself
update_self() {
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    SCRIPT_PATH="$SCRIPT_DIR/$(basename "$0")"
    BACKUP="$SCRIPT_PATH.backup"

    echo "Updating..."
    cp "$SCRIPT_PATH" "$BACKUP"

    if curl -fsSL "$SCRIPT_URL" -o "$SCRIPT_PATH"; then
        chmod 755 "$SCRIPT_PATH"
        echo "✓ Updated successfully"
        rm "$BACKUP"
    else
        echo "✗ Update failed, restoring backup"
        mv "$BACKUP" "$SCRIPT_PATH"
        exit 1
    fi
}

# Usage: script.sh --update
case "${1:-}" in
    --update) update_self; exit 0 ;;
esac
```

### Pattern 2: Re-run installer

```bash
# In update.sh or as a subcommand
update() {
    echo "Updating..."
    curl -LsSf https://example.com/install.sh | sh
}
```

### Pattern 3: Check version on startup

```python
# In Python tool
import requests
import sys

def check_for_updates():
    try:
        response = requests.get("https://api.github.com/repos/USER/REPO/releases/latest")
        latest = response.json()["tag_name"]
        current = "v1.0.0"  # Your current version

        if latest != current:
            print(f"⚠ New version available: {latest} (current: {current})")
            print(f"  Update with: <your-command> --update")
    except Exception:
        pass  # Silently fail

if __name__ == "__main__":
    check_for_updates()
    # ... rest of tool
```
