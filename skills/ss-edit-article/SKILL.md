---
name: ss-edit-article
description: >-
  Edit and improve articles by restructuring sections, improving clarity,
  and tightening prose. Treats information as a directed acyclic graph so
  prerequisites come first. Use when the user wants to edit, revise, or
  improve an article draft, blog post, or essay.
  Triggers on "edit article", "improve article", "revise draft", "tighten
  prose", "edit my blog post", "edit essay".
allowed-tools:
  - Read
  - Edit
  - Write
---

# Edit Article

1. First, divide the article into sections based on its headings. Think about the main points you want to make during those sections.

   Consider that information is a directed acyclic graph, and that pieces of information can depend on other pieces of information. Make sure that the order of the sections and their contents respects these dependencies — prerequisites come before what depends on them.

   Confirm the sections with the user.

2. For each section:

   2a. Rewrite the section to improve clarity, coherence, and flow. Use a maximum of 240 characters per paragraph.

   2b. Cut filler, weasel words, and redundant transitions. Prefer concrete nouns and active verbs.

   2c. Show the user the rewritten section and incorporate their feedback before moving on.

3. After all sections are rewritten, do one final pass for cross-section flow:
   - Does each section's opening sentence pick up where the previous section left off?
   - Are any terms used before they're defined?
   - Are there any duplicate explanations across sections that can collapse into one?
