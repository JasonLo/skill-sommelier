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
   - **Configuration**: Create config files if needed (or defer to first run — see below)
   - **Optional dependencies**: Prompt for additional tools
   - **Verification**: Test that installation succeeded

3. Ensure the script:
   - Uses `set -eu` for error handling (or `set -euo pipefail` if `#!/bin/bash`)
   - Reads from `/dev/tty` for interactive prompts, **gated by a TTY check** so CI installs don't hang
   - Honors `--yes` / `INSTALLER_ASSUME_YES=1` for unattended installs (see "Non-Interactive Mode" in `references/templates.md`)
   - Sets proper permissions (600 for secrets, 755 for executables)
   - Provides clear success/error messages
   - Includes a "Done! Run '<command>' to start." message

4. For binary downloads, **verify a checksum before extracting/installing**. See "Checksum Verification" in `references/templates.md`. `tar tzf` only detects corruption, not tampering.

5. Prefer **deferring credential prompts to first run** rather than asking during `curl | sh`. Install-time prompts break unattended installs, can end up in shell history, and put secrets through a piped subshell. Inline credential prompts are only appropriate when the tool is unusable without them and no first-run UX exists.

**Exit:** `scripts/install.sh` created and tested.

## Phase 3.5 — Generate Uninstaller

Create `scripts/uninstall.sh` as a standard companion artifact. Every mature installer (uv, rustup, rclone, brew) ships one — without it, users can't cleanly remove your tool.

Use the "Uninstall Template" in `references/templates.md`. It should:
- Remove the binary / `uv tool uninstall` / `cargo uninstall`
- Optionally remove config (`$XDG_CONFIG_HOME/PROJECT`) — prompt unless `--purge` is passed
- Leave user data untouched by default
- Print exactly what was removed

**Exit:** `scripts/uninstall.sh` created.

## Phase 4 — Add Auto-Update Support

Create an update mechanism. **Default: built-in self-update subcommand.**

### Default: Self-update subcommand

For any tool you control the source of (Python via `uv tool`, Rust via `cargo`, compiled binary with a release pipeline), add a `<tool> update` or `<tool> self-update` subcommand. This is what `uv`, `rustup`, and `gh` all do.

1. Add the subcommand to the tool itself
2. Inside it, run the package manager's upgrade command or re-fetch the release asset
3. See "Pattern 1: Built-in Self-Update Command" in `references/self-update-patterns.md`

Why this is the default: discoverable via `--help`, no second file to maintain, no shell pipe required at update time, lives in the codebase under version control.

### Alternatives (use only if the default doesn't fit)

- **Separate `scripts/update.sh`** — use when the tool is a pure shell script with no "source code" to add a subcommand to, or when the install is git-clone-based and `git pull` is the natural update path. See Pattern 2.
- **Background version check on startup** — add *in addition* to the default for frequently-run tools that need a passive nudge. Never use as the only mechanism. See Pattern 3.
- **Re-run the installer** — only for trivial single-file installs. Slower and racier than a real upgrade. See Pattern 4.

**Exit:** A built-in `update` subcommand exists, or an explicit reason was recorded for choosing an alternative.

## Phase 5 — Update Documentation

Add installation instructions to README.

1. Add an "Install" section with **two one-liners** — a pinned production install and a tracking install:

   ````markdown
   ## Install

   Pinned to the latest release (recommended):

   ```bash
   curl -LsSf https://raw.githubusercontent.com/USER/REPO/v1.0.0/scripts/install.sh | sh
   ```

   Tracking `main` (for contributors / bleeding edge):

   ```bash
   curl -LsSf https://raw.githubusercontent.com/USER/REPO/main/scripts/install.sh | sh
   ```

   The installer will set up `<command>`, prompt for configuration, and handle dependencies.
   ````

   **Why two:** the `main` URL re-fetches whatever the latest commit is at the time the user runs it — that means a compromised or accidentally-broken commit on `main` ships to everyone who runs `curl | sh` until you notice. Pinning to a tag (or commit SHA) freezes what users execute. README copy should default to the pinned URL and only mention `main` as a contributor option.

   Bump the pinned version in the README on every release. The `ssm-repo-release` skill is a good place to wire this in.

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

Listed roughly in order of impact:

- **Pin the install URL to a git tag or commit SHA in your README.** `raw.githubusercontent.com/.../main/install.sh` is mutable — anyone with push access (or a compromised dependency that touches the repo) can change what `curl | sh` users execute. See Phase 5 for the two-URL pattern.
- **Verify a checksum before extracting binary downloads.** `tar tzf` only catches corruption. Publish a `.sha256` next to each release asset and check it in the installer. See the "Checksum Verification" template.
- **Use HTTPS URLs only** — never HTTP, never plain git://.
- **Set restrictive permissions on credential files** (`chmod 600`).
- **Avoid storing secrets in the install script itself.** Prefer first-run prompts (Phase 3 note) so secrets never go through `curl | sh`.
- **Never pipe arbitrary third-party URLs to shell without reviewing the script first** — applies to dependencies the installer pulls in (e.g. `rclone.org/install.sh`). Download to a temp file and `bash <file>` rather than piping.

## Examples

See `references/examples.md` for complete examples:
- uw-s3 style Python tool installer with credentials
- uv style binary installer with self-update
- Simple shell script installer
