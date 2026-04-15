---
name: ss-cli2task
description: >-
  Generate VS Code tasks.json from Python CLI commands discovered in a repo
  (typer, click, argparse, or plain functions). Parses CLI modules to find
  commands, asks the user which to include, and writes .vscode/tasks.json.
  Use when the user wants to create VS Code tasks from their CLI, generate
  tasks.json, or convert CLI commands to VS Code tasks. Triggers on
  "generate tasks", "vscode tasks", "tasks.json", "cli to tasks",
  "cli2task", "create tasks from cli".
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# CLI to VS Code Tasks Generator

Generate `.vscode/tasks.json` entries from Python CLI commands defined in a repository.

## Instructions

Follow these steps exactly:

### Step 1 — Discover the CLI module

Find the CLI entry point in the repo. Search for files that define CLI commands:

1. Look for `cli.py` files anywhere in the repo (`**/cli.py`).
2. If none found, look for `__main__.py`, `main.py`, or files importing `typer`, `click`, or `argparse`.
3. If multiple candidates exist, ask the user which file to use.

### Step 2 — Parse commands

Read the CLI module and extract all commands. Identify:

- **Framework**: `typer`, `click`, `argparse`, or plain functions.
- **Command names**: function names or explicit name overrides (e.g., `@app.command("list")`).
- **Arguments**: required positional args with their types and help text.
- **Options**: optional flags with defaults and help text.
- **Docstrings**: the one-line description of each command.

Also determine the **invocation prefix** — how the CLI is run:

1. Check `pyproject.toml` for `[project.scripts]` entries (e.g., `raven = "raven.main:app"` means the prefix is `uv run raven`).
2. If no script entry, check if there is a `__main__.py` (prefix: `uv run python -m <package>`).
3. If neither, fall back to `uv run python <path/to/cli.py>`.

### Step 3 — Ask the user

Present all discovered commands using `AskUserQuestion` with `multiSelect: true`. For each command show:

- **label**: the command name
- **description**: the docstring or a summary of what it does

Let the user select which commands to generate tasks for.

### Step 4 — Generate tasks.json

For each selected command, create a VS Code task object:

```json
{
  "label": "<prefix> <command>",
  "type": "shell",
  "command": "<full invocation>",
  "group": "build",
  "problemMatcher": []
}
```

Rules for generating tasks:

- **Required arguments** (positional args without defaults): add `"${input:<argName>}"` placeholder and a corresponding entry in the top-level `"inputs"` array with `"type": "promptString"` and `"description"` from the arg's help text.
- **Optional flags with no default or with a meaningful default**: do NOT include them in the base command. Instead, if a command has options, create a second task variant suffixed with `(with options)` that includes all options as `${input:...}` placeholders.
- **Boolean flags** (like `--dry-run`): use `"type": "pickString"` input with choices `["", "--flag-name"]`.
- If `.vscode/tasks.json` already exists, read it first and merge — do not overwrite existing tasks. Append new tasks and inputs, skipping duplicates by label.
- If `.vscode/tasks.json` does not exist, create it with `"version": "2.0.0"`.

### Step 5 — Confirm and write

Show the user the generated tasks.json content, then write it to `.vscode/tasks.json`.

## Example output

For a typer CLI with `pyproject.toml` entry `raven = "raven.main:app"` and commands `list`, `run --dry-run --output FILE`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "raven list",
      "type": "shell",
      "command": "uv run raven list",
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "raven run",
      "type": "shell",
      "command": "uv run raven run",
      "group": "build",
      "problemMatcher": []
    },
    {
      "label": "raven run (with options)",
      "type": "shell",
      "command": "uv run raven run ${input:runDryRun} ${input:runOutput}",
      "group": "build",
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "runDryRun",
      "description": "Include --dry-run flag?",
      "type": "pickString",
      "options": ["", "--dry-run"]
    },
    {
      "id": "runOutput",
      "description": "Save digests to JSON file (leave empty to skip)",
      "type": "promptString",
      "default": ""
    }
  ]
}
```
