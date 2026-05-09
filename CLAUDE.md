# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this repo is

**skill-sommelier** is a Claude Code plugin that discovers, curates, and manages [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) from GitHub. Distributed via the plugin marketplace (`/plugin marketplace add`).

There is no build system, test suite, or application code — just `SKILL.md` files with YAML frontmatter and procedural instructions. **No standalone scripts.** All capabilities ship as skills; supporting scripts inside a skill directory (`scripts/`) are fine, top-level scripts are not.

```
skills/                # public — distributed
maintainer-skills/     # local-only — repo upkeep, NOT distributed
.claude/skills/        # symlink farm so project-level discovery picks up both
```

## Public vs maintainer-only

Claude Code only auto-loads skills under a plugin's `skills/`. Anything in `maintainer-skills/` is invisible to end users.

- Useful to anyone authoring skills or working with arbitrary repos? → `skills/` with `ss-` prefix.
- Only meaningful when run against this repo? → `maintainer-skills/` with `ssm-` prefix.

## Local dev — rebuild the symlink farm

After adding, removing, or moving a skill:

```bash
rm -rf .claude/skills && mkdir -p .claude/skills
for d in skills/*/ maintainer-skills/*/; do
  ln -s "../../$d" ".claude/skills/$(basename "$d")"
done
```

## SKILL.md conventions

Follows the [Agent Skills spec](https://agentskills.io/specification). Required frontmatter:

- `name` — lowercase + hyphens, must match directory name. `ss-` for public, `ssm-` for maintainer-only.
- `description` — what the skill does AND when it should trigger.
- `allowed-tools` (recommended) — tools the skill uses.
- `metadata.depends-on` (recommended) — space-delimited list of skills it invokes or delegates to.

Keep SKILL.md under 500 lines; move long content to `references/` inside the skill directory. Skills must be self-contained.

## Workflow

- Commit + push when a feature is complete — ask the user first.
- After every commit, verify related docs are still accurate (CLAUDE.md, README, frontmatter of changed skills) and offer to fix anything stale.
- When the user mentions updates, new skills, or staying current, suggest the `ss-update` skill.
- The `claude.yml` workflow handles `@claude` mentions on issues/PRs.
