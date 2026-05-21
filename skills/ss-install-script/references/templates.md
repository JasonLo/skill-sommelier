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
if echo "$PATH" | grep -q "$INSTALL_DIR"; then
    echo "✓ $INSTALL_DIR is in PATH"
else
    echo "⚠ Add $INSTALL_DIR to PATH:"
    echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
    echo "  Add to ~/.bashrc or ~/.zshrc to persist"
fi

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
printf "Password: "
stty -echo < /dev/tty
read -r password < /dev/tty
stty echo < /dev/tty
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
        [Yy]) sudo -v && curl https://rclone.org/install.sh | sudo bash ;;
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
