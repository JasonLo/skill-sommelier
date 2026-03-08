---
name: ss-modern-python
description: >-
  Configure Python projects with modern tooling: uv, ruff, ty. Use when creating new Python projects,
  setting up pyproject.toml, migrating from pip/Poetry/mypy/black, or writing standalone scripts.
  Triggers on new Python project, setup Python, pyproject.toml, migrate from pip, migrate from Poetry,
  replace mypy, replace black, uv init, ruff config.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Modern Python

Reference for modern Python tooling and project setup. Adapted from [trailofbits/modern-python](https://github.com/trailofbits/skills).

## When to Use
- Creating a new Python project or package
- Setting up or configuring pyproject.toml
- Migrating from legacy tools (pip, Poetry, mypy, black, isort)
- Writing standalone scripts with dependencies

## When NOT to Use
- User explicitly wants to keep legacy tooling
- Non-Python projects
- Python < 3.11 required

## Tool Stack

| Tool | Purpose | Replaces |
|------|---------|----------|
| **uv** | Package/dependency management | pip, virtualenv, pip-tools, pipx, pyenv, Poetry |
| **ruff** | Linting AND formatting | flake8, black, isort, pyupgrade |
| **ty** | Type checking | mypy, pyright |
| **pytest** | Testing | unittest |

## Anti-Patterns

| Avoid | Use Instead |
|-------|-------------|
| `uv pip install` | `uv add` and `uv sync` |
| Editing pyproject.toml to add deps | `uv add <pkg>` / `uv remove <pkg>` |
| Poetry | uv |
| requirements.txt for projects | pyproject.toml + uv.lock |
| requirements.txt for scripts | PEP 723 inline metadata |
| mypy / pyright | ty |
| `[project.optional-dependencies]` for dev tools | `[dependency-groups]` (PEP 735) |
| Manual virtualenv activation | `uv run <cmd>` |
| `serial` type aliases | `BIGINT GENERATED ALWAYS AS IDENTITY` |

## Quick Start: New Project

```bash
uv init myproject
cd myproject
uv add requests rich
uv add --group dev pytest ruff ty
uv run pytest
uv run ruff check .
uv run ty check src/
```

## Full Project Setup

### 1. Create structure

```bash
uv init --package myproject
cd myproject
```

### 2. Configure pyproject.toml

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []

[dependency-groups]
dev = [{include-group = "lint"}, {include-group = "test"}]
lint = ["ruff", "ty"]
test = ["pytest", "pytest-cov"]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "COM812", "ISC001"]

[tool.pytest.ini_options]
addopts = ["--cov=myproject"]

[tool.ty.environment]
python-version = "3.13"
```

### 3. Install and verify

```bash
uv sync --all-groups
uv run ruff check .
uv run ty check src/
uv run pytest
```

## PEP 723: Standalone Scripts

For single-file scripts with dependencies, use inline metadata instead of pyproject.toml:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = ["requests", "rich"]
# ///

import requests
from rich import print

data = requests.get("https://httpbin.org/ip").json()
print(data)
```

Run with: `uv run script.py` (uv auto-installs dependencies).

## Migration Guides

### From requirements.txt + pip

```bash
uv init --bare
# Add each dependency
uv add requests rich pandas
# Add dev deps
uv add --group dev pytest ruff ty
uv sync
```

Then delete `requirements.txt`, `requirements-dev.txt`, and any virtualenv directories.

### From Poetry

```bash
uv init --bare
# Transfer deps from [tool.poetry.dependencies]
uv add requests rich
# Transfer dev deps from [tool.poetry.group.dev.dependencies]
uv add --group dev pytest ruff
uv sync
```

Then delete `poetry.lock` and `[tool.poetry]` sections.

### From flake8 + black + isort to ruff

1. `uv remove flake8 black isort` (if installed)
2. Delete `.flake8`, `[tool.black]`, `[tool.isort]` configs
3. `uv add --group dev ruff`
4. `uv run ruff check --fix . && uv run ruff format .`

### From mypy to ty

1. `uv remove mypy` (if installed)
2. Delete `mypy.ini` or `[tool.mypy]` section
3. `uv add --group dev ty`
4. `uv run ty check src/`

## uv Commands Reference

| Command | Description |
|---------|-------------|
| `uv init` | Create new project |
| `uv init --package` | Create distributable package |
| `uv add <pkg>` | Add dependency |
| `uv add --group dev <pkg>` | Add to dev group |
| `uv remove <pkg>` | Remove dependency |
| `uv sync` | Install dependencies |
| `uv sync --all-groups` | Install all groups |
| `uv run <cmd>` | Run in project venv |
| `uv run --with <pkg> <cmd>` | Run with temporary dep |
| `uv build` | Build package |
| `uv publish` | Publish to PyPI |
