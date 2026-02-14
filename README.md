# prompt-sync

A lightweight CLI for managing reusable LLM prompts and Claude skills from a single repository. It lets you browse, inject, and refresh registry entries directly inside any project that follows the Claude workspace layout.

## Overview

1. A curated registry stores prompts and skills as Markdown files inside a Git-tracked repository.
2. `prompt-sync` clones that registry, surfaces the available artifacts, and pushes selected content into the local project files a developer already uses (e.g., `CLAUDE.md` and `.claude/skills`).
3. The CLI is designed to be installed as a global `uv` tool so teammates can run it from any directory and stay in sync with the shared registry.

## Repository Layout (Registry)

```text
prompt_sync/
├── registry.json          # Typed index that maps names to paths, descriptions, tags, and hashes
├── claude_skills/
│   ├── skill_1/
│   │   └── SKILL.md      # Full Claude skill definition folder
│   └── skill_2/
│       └── SKILL.md
└── claude_prompts/
    └── prompt_1/<name>.md # Sections that can be injected into CLAUDE.md
```

## Features

- **Prompt injection**: The tool discovers the local `CLAUDE.md`, prompts you to pick sections via `questionary`, and appends the selected segments into clearly marked regions so they are always available in your project.
- **Skill injection**: Available skills are listed with their descriptions; once you choose one, the CLI mirrors the Markdown into `.claude/skills/<name>/SKILL.md` and wraps registry-owned content in markers so updates can apply cleanly.
- **Registry syncing**: `psync update` refreshes installed content by re-reading the markers, grabbing the latest Markdown from the registry cache, and overwriting only the psync-owned regions.
- **Info & discovery**: `psync list` and `psync info` provide quick access to metadata, tags, and previews directly in the terminal.
- **Installed set management**: optional `psync list-installed` and `psync remove <name>` operate over whatever the CLI has previously injected into the current project.

## CLI Commands

| Command | Description |
| --- | --- |
| `psync list` | Fetch `registry.json` from the configured registry cache and show available prompts/skills with versions and tags. |
| `psync info <name>` | Display the registry record for a prompt or skill, including description, tags, and a Markdown preview. |
| `psync add <name>` | Inject the selected prompt sections or skill into the current project (`CLAUDE.md` and/or `.claude/skills`). |
| `psync list-installed` | Inspect local files for psync markers and list what is currently installed in this project. |
| `psync remove <name>` | Remove psync-managed regions for a given name from `CLAUDE.md` and/or `.claude/skills`. |
| `psync update` | Scan local files for psync markers and pull fresh content for all installed prompts/skills; supports `--dry-run` to show diffs only. |

## Markers and Update Semantics

Psync never edits user content outside of its own marker blocks. Injected regions are wrapped in comments like:

```markdown
<!-- psync:begin name=<name> type=<prompt|skill> hash=<hash> -->
...registry-managed Markdown...
<!-- psync:end name=<name> -->
```

- `psync add` creates these blocks; `psync update` replaces only the content between matching `begin` / `end` markers.
- Edits inside psync regions are treated as ephemeral and may be overwritten on update; project-specific notes should be kept outside the markers.
- If markers are malformed or missing, psync will skip that region and surface a warning instead of guessing.

## Implementation Notes

- `typer` powers the CLI interface and handles argument parsing plus rich help text.
- `questionary` renders the interactive checkboxes used during injection steps.
- The first bootstrap clones the registry repo; future improvements might swap to the GitHub Contents API when cloning becomes slow or bandwidth-heavy.

## Data Models (Static Typing)

```python
from typing import Literal, TypedDict

class Record(TypedDict):
    name: str
    path: str
    description: str
    tags: list[str]
    version: str  # semVer; bump when `_hash` changes
    _hash: str    # generated checksum for change detection
    _type: Literal["prompt", "skill"]

class Registry(TypedDict):
    version: str
    skills: dict[str, Record]
    prompts: dict[str, Record]
```

## Project Rules

- Install dependencies with `uv add` so the virtual environment stays aligned with the project policy.
- Run scripts via `uv run` to always pick up the right interpreter and locked dependencies.
- Prefer single-line docstrings for simple helper functions, and reserve multiline docs for complex behaviors.
- Reach for `pydantic` models when objects have seven or more attributes to stay consistent with the broader codebase.
- Static typing is mandatory (Python 3.13+); leverage `typing` annotations liberally.
- Reference the official docs when using newer language or library syntax to ensure correctness.
- Keep comments rare and meaningful; don’t spell out what the code already expresses clearly.
