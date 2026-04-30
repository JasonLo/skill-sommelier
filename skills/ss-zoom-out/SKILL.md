---
name: ss-zoom-out
description: >-
  Zoom out and give broader context — a higher-level map of relevant modules
  and callers — when you're unfamiliar with a section of code or need to
  understand how it fits into the bigger picture. Triggers on "zoom out",
  "give me the big picture", "higher level view", "explain this area",
  "map the modules".
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
---

# Zoom Out

I don't know this area of code well. Go up a layer of abstraction. Give me a map of all the relevant modules and callers, using the project's domain glossary vocabulary (read `CONTEXT.md` if it exists).

Cover:

- The boundary of the area being zoomed out from (which folder/module/file).
- The modules **inside** the area and how they relate to each other.
- The callers **outside** the area that depend on it, and the entry points used.
- The dependencies the area pulls in (libraries, services, schemas).
- Any obvious seams (places where behaviour can change without editing in place).

Keep it concise — the goal is to orient, not to document every detail.
