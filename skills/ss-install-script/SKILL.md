---
name: ss-install-script
description: >-
  Create a single-line install script with auto-update capability for CLI tools,
  Python packages, or applications. Generates shell scripts similar to uv or
  uw-s3 installers that handle installation, configuration, and optional
  dependencies. Use when users want to "create an install script", "make a
  single-line installer", "add auto-update", or "build an installer like uv".
  Triggers on "install script", "single-line installer", "curl installer",
  "auto-update script", "installer like uv", "install.sh".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
---

# Install Script Generator

Create production-ready single-line install scripts with auto-update capabilities.

## When to Use

- Creating a curl-pipeable install script for a CLI tool or Python package
- Adding auto-update functionality to an existing project
- Building an installer similar to uv, rustup, or uw-s3
- Need to handle credential setup, optional dependencies, or configuration
- Want users to install with `curl -LsSf URL | sh`

## When NOT to Use

- Simple pip/npm install suffices — use standard package managers instead
- Distributing to package registries (PyPI, npm) — use their native installers
- Desktop GUI applications — use platform-specific installers (DMG, MSI, AppImage)
- The project doesn't need automatic updates or complex setup

## Phase 1 — Gather Context

Understand what needs to be installed and how.

1. Ask the user or infer from context:
   - What type of project? (Python package, Rust binary, shell tool, etc.)
   - What's the installation command? (e.g., `uv tool install`, `cargo install`, `pip install`)
   - Does it need configuration files? (credentials, env files, etc.)
   - Are there optional dependencies? (e.g., rclone for mount support)
   - What's the repository URL?
   - What command should users run after install?

2. Read the project's README if available to understand existing install instructions

**Exit:** Clear understanding of installation requirements.

## Phase 2 — Choose Template

Select the appropriate template based on project type.

| Project Type | Template | Features |
|--------------|----------|----------|
| Python package (uv) | `uv-tool` | uv tool install, config files, optional deps |
| Rust binary | `cargo` | cargo install, binary placement, config |
| Shell script | `script` | Download script, make executable, PATH setup |
| Generic | `generic` | Flexible installer with auto-update |

**Exit:** Template selected.

## Phase 3 — Generate Install Script

Create `scripts/install.sh` based on the chosen template.

1. Use the template from `references/templates.md`
2. Customize these sections:
   - **Variables**: REPO, BINARY_NAME, CONFIG_DIR
   - **Install command**: The actual installation step
   - **Configuration**: Create config files if needed
   - **Optional dependencies**: Prompt for additional tools
   - **Verification**: Test that installation succeeded

3. Ensure the script:
   - Uses `set -eu` for error handling
   - Reads from `/dev/tty` for interactive prompts
   - Sets proper permissions (600 for secrets, 755 for executables)
   - Provides clear success/error messages
   - Includes a "Done! Run '<command>' to start." message

**Exit:** `scripts/install.sh` created and tested.

## Phase 4 — Add Auto-Update Support

Create an update mechanism (optional but recommended).

Choose one approach:

**Option A: Self-update subcommand** (for compiled binaries or Python tools)
1. Add a `--self-update` or `update` subcommand to the tool itself
2. Use git to check for updates and pull latest version
3. See `references/self-update-patterns.md` for examples

**Option B: Separate update script** (for simpler tools)
1. Create `scripts/update.sh` that re-runs the installer
2. Or fetches latest version and replaces existing install

**Option C: Check on startup** (for Python/Node tools)
1. Add version check on tool startup
2. Notify user if newer version available

**Exit:** Auto-update mechanism implemented or explicitly skipped.

## Phase 5 — Update Documentation

Add installation instructions to README.

1. Add an "Install" section with the curl one-liner:
   ````markdown
   ## Install

   ```bash
   curl -LsSf https://raw.githubusercontent.com/USER/REPO/main/scripts/install.sh | sh
   ```

   The installer will set up `<command>`, prompt for configuration, and handle dependencies.
   ````

2. Document what the installer does:
   - What gets installed
   - Where files are placed
   - What prompts to expect
   - How to update

3. Add manual install instructions as fallback

**Exit:** README updated with clear install instructions.

## Phase 6 — Test the Installer

Verify the script works in a clean environment.

1. Test in a fresh shell or container:
   ```bash
   docker run -it --rm ubuntu:22.04 bash
   # Then run the curl installer
   ```

2. Verify:
   - Installation completes without errors
   - Configuration prompts work correctly
   - The installed command runs successfully
   - File permissions are correct
   - Update mechanism works (if implemented)

3. Test edge cases:
   - Already installed (should handle gracefully)
   - Missing dependencies (should error clearly)
   - User cancels during prompts (should cleanup)

**Exit:** Installer tested and working.

## Security Notes

- Never pipe arbitrary URLs to shell without reviewing the script first
- Use HTTPS URLs only
- Pin to specific git refs/tags for production use
- Validate checksums for binary downloads
- Set restrictive permissions on credential files (600)
- Avoid storing secrets in the install script itself

## Examples

See `references/examples.md` for complete examples:
- uw-s3 style Python tool installer with credentials
- uv style binary installer with self-update
- Simple shell script installer
