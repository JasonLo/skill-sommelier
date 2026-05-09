# skill-sommelier

A self-improving [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) plugin. It discovers skills from GitHub, ranks them against a profile built from your local Claude Code history, installs them, and uses its own skills to validate and evolve the collection.

Everything is `SKILL.md` files — no build system, no scripts.

## Install

```
/plugin marketplace add JasonLo/skill-sommelier
/plugin install skill-sommelier@skill-sommelier
```

Skills are namespaced as `/skill-sommelier:<name>`. Update with `/plugin marketplace update`.

## Quickstart

```
/skill-sommelier:ss-skill-discover
```

On first run it builds your developer profile from local Claude Code history, then finds and installs skills tailored to your stack. Pass `my profile` to refresh the profile alone.

## Skills

Public skills (distributed):

| Skill | Description |
|-------|-------------|
| [ss-skill-discover](skills/ss-skill-discover/SKILL.md) | Build a developer profile from local history, then search GitHub and install ranked picks |
| [ss-skill-craft](skills/ss-skill-craft/SKILL.md) | Create, improve, or design Claude Code skills |
| [ss-repo-update](skills/ss-repo-update/SKILL.md) | Check for plugin updates, show changelog, apply them |
| [ss-modern-python](skills/ss-modern-python/SKILL.md) | Set up Python projects with `uv`, `ruff`, `ty` |
| [ss-python-to-chtc](skills/ss-python-to-chtc/SKILL.md) | Containerize Python apps for Docker / Apptainer / HPC |
| [ss-diagnose](skills/ss-diagnose/SKILL.md) | Disciplined diagnosis loop for hard bugs and perf regressions |
| [ss-tdd](skills/ss-tdd/SKILL.md) | Test-driven development with red-green-refactor and tracer-bullet vertical slices |
| [ss-grill](skills/ss-grill/SKILL.md) | Stress-test a plan — Q&A only, or with-docs that updates `CONTEXT.md`/ADRs inline |
| [ss-spec-new](skills/ss-spec-new/SKILL.md) | Draft an RFC-style `SPEC.md` (RFC 2119, scope, domain model, conformance) |
| [ss-autoresearch](skills/ss-autoresearch/SKILL.md) | Two-loop autonomous AI research: rapid experiments inside, synthesis outside |

Maintainer-only skills under `maintainer-skills/` are not distributed via the marketplace — only contributors with a clone see them. They cover release automation, frontmatter validation, weekly discovery, evolution, and consolidation.

## Development

```bash
git clone https://github.com/JasonLo/skill-sommelier.git
cd skill-sommelier
# Project-level skills work via the .claude/skills/ symlink farm
# (see CLAUDE.md for the rebuild command after adding/removing a skill)
```

## Credits

Several skills are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the full list and licence text.
