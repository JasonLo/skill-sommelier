# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this repo is

**skill-sommelier** is a Claude Code plugin that discovers, curates, and manages [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) from GitHub. Distributed via the plugin marketplace (`/plugin marketplace add`).

The plugin has no build system, test suite, or application code — just `SKILL.md` files with YAML frontmatter and procedural instructions. **No standalone scripts.** All capabilities ship as skills; supporting scripts inside a skill directory (`scripts/`) are fine, top-level scripts are not.

Exception: **skill-cellar**, a terminal UI (OpenTUI on Bun, TypeScript) for managing skills, lives at the repo root (`src/`, `specs/`, `package.json`, `bun.lock`, `biome.json`, `tsconfig.json`, `vitest.config.ts`). It is not part of the plugin's skills. See [skill-cellar](#skill-cellar-terminal-ui) below.

Narrow exception: `scripts/install.sh` and `scripts/uninstall.sh` at the repo root are distribution infrastructure, not capabilities — curl-pipeable installers need stable repo-root URLs. Don't add other top-level scripts under this exception; new capabilities still go in `skills/` or `maintainer-skills/`.

```
skills/                # public — distributed
maintainer-skills/     # local-only — repo upkeep, NOT distributed
.claude/skills/        # symlink farm so project-level discovery picks up both
scripts/               # carve-out: install.sh / uninstall.sh only
src/                   # skill-cellar TUI (TypeScript, Bun)
specs/                 # skill-cellar lite-spec: CONSTITUTION.md + INTENT/
```

## Public vs maintainer-only

Claude Code only auto-loads skills under a plugin's `skills/`. Anything in `maintainer-skills/` is invisible to end users.

- Useful to anyone authoring skills or working with arbitrary repos? → `skills/` with `ss-` prefix.
- Only meaningful when run against this repo? → `maintainer-skills/` with `ssm-` prefix.

## Local dev — rebuild the symlink farm

After adding, removing, or moving a skill, run:

```bash
bash maintainer-skills/ssm-skill-validate/scripts/sync-skills.sh
```

The script is idempotent and rebuilds `.claude/skills/` from `skills/` + `maintainer-skills/`. Commit the resulting symlink changes.

To auto-sync on every commit that touches `skills/` or `maintainer-skills/`, opt in once per clone:

```bash
git config core.hooksPath .githooks
```

The `.githooks/pre-commit` hook then runs the sync script and stages any farm changes automatically.

## SKILL.md conventions

Follows the [Agent Skills spec](https://agentskills.io/specification). Required frontmatter:

- `name` — lowercase + hyphens, must match directory name. `ss-` for public, `ssm-` for maintainer-only.
- `description` — what the skill does AND when it should trigger.
- `allowed-tools` (recommended) — tools the skill uses.
- `metadata.depends-on` (recommended) — space-delimited list of skills it invokes or delegates to.

Keep SKILL.md under 500 lines; move long content to `references/` inside the skill directory. Skills must be self-contained.

## skill-cellar (terminal UI)

A librarian, not an agent runner: shop, install (project or global), usage analytics, and crafting, all conformant to the agentskills.io spec. Bun only (constitution P-9) — never npm, yarn, or pnpm.

```bash
bun install && bun run test && bun run build && bun run lint
```

The rules below apply to skill-cellar work (`src/`, `specs/`), not to the plugin skills.

<!-- lite-spec:pointer-block:start -->

### Read before non-trivial work

Before generating output that touches design, architecture, scope, or behavior, load the spec files lazily — they override CLAUDE.md on conflict.

- **`specs/CONSTITUTION.md`** — non-negotiable principles. Every change to principles MUST go through `spec-constitution`; never edit silently.
- **`specs/INTENT/`** — one folder per intent (`I-N-<slug>/intent.md`), with experiments nested inside. Open intents have `status: draft` or `in_progress`; finished ones have `status: complete` or `superseded`. Outcomes use EARS (`WHEN <trigger> THE SYSTEM SHALL <response>`). Load only the intents whose scope intersects your task. Create/refine/supersede via `spec-intent`; `spec-check` derives `status` from outcome pass-counts.

### Spec file ownership

`specs/CONSTITUTION.md` (governance) and `specs/INTENT/` (product/scope — the whole tree, every `I-N-<slug>/intent.md`) are **human-owned**. AI agents MUST modify these only via `/spec-constitution` and `/spec-intent` respectively. Never with direct Edit/Write/sed, not even for a "trivial sync" like fixing a stale count. The exception is the skill-managed frontmatter fields on each `intent.md` (`status`, `closed`, `verdict_*`), which `spec-check` writes.

Files outside `specs/` (README, this file, source, `SKILL.md` bodies, scripts) are fair game for normal edits.

### Spec workflow

This repo uses **lite-spec** — invoke the skills by name:

- `/spec-init` — bootstrap or repair the lite-spec setup
- `/spec-constitution` — ratify or amend principles (`specs/CONSTITUTION.md`)
- `/spec-intent` — draft, refine, or supersede an intent (`specs/INTENT/I-N-<slug>/intent.md`)
- `/spec-check` — drift report + status derivation across open intents

<!-- lite-spec:pointer-block:end -->

## Workflow

- Commit + push when a feature is complete — ask the user first.
- After every commit, verify related docs are still accurate (CLAUDE.md, README, frontmatter of changed skills) and offer to fix anything stale.
- When the user mentions updates, new skills, or staying current, suggest the `ss-update` skill.
- The `claude.yml` workflow handles `@claude` mentions on issues/PRs.
