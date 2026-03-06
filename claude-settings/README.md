# Claude Settings - Stow Package

This directory is structured as a [GNU Stow](https://www.gnu.org/software/stow/) package for managing Claude Code settings via symlinks.

## Directory Structure

```
claude-settings/          # Stow package directory
└── .claude/             # Files that will be stowed to ~/.claude/
    ├── settings.json
    ├── statusline-command.sh
    └── skills/
```

## How It Works

When you run the `sync-claude-settings` skill with "push" or "pull":

1. The skill uses `stow claude-settings -t ~` to create symlinks
2. This creates: `~/.claude/` → `<repo>/claude-settings/.claude/`
3. All files in `~/.claude/` become symlinks to files in this repo
4. Changes in either location are automatically reflected in the other

## Benefits Over Copying

- **No manual syncing**: Changes are immediately reflected in both locations
- **Version control**: Settings are always in sync with the git repo
- **Easy restore**: Just run `stow` to restore all settings on a new machine
- **Clean removal**: `stow -D` removes all symlinks cleanly

## Requirements

You need GNU Stow installed:
- macOS: `brew install stow`
- Ubuntu/Debian: `sudo apt install stow`
- Arch: `sudo pacman -S stow`
