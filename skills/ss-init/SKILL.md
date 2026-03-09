---
name: ss-init
description: >-
  Bootstrap your Claude Code skill collection. Alias for ss-discover-skills
  with no arguments (auto-generates personalized search queries from your profile).
  Triggers on "init", "bootstrap", "get started with skills", "setup my skills",
  "what skills should I have", "recommended skills for me".
allowed-tools:
  - Skill
metadata:
  depends-on: ss-discover-skills
---

# Init

Bootstrap your Claude Code skill collection with personalized recommendations.

This is a convenience alias. Run the `ss-discover-skills` skill with no arguments:

```
/ss-discover-skills
```

When called without arguments, ss-discover-skills will:
1. Analyze your user profile (or build one if it doesn't exist)
2. Auto-generate search queries based on your tech stack and interests
3. Search GitHub, rank by relevance, and present a table
4. Let you select and install skills
