---
name: ss-make-slides
description: Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presentation, convert a PPT/PPTX to web, or create slides for a talk/pitch. Helps non-designers discover their aesthetic through visual exploration rather than abstract choices.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
---

# Frontend Slides Skill

Create zero-dependency, animation-rich HTML presentations that run entirely in the browser.

## When to Use
- Building a presentation from scratch
- Converting PowerPoint/PPTX to a web-based format
- Creating slides for a talk, pitch, or lecture

## When NOT to Use
- Slidev/reveal.js projects — use those tools directly
- Documents or reports — this is for slide decks only

## Core Philosophy

1. **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no build tools.
2. **Show, Don't Tell** — Generate visual previews, not abstract choices.
3. **Distinctive Design** — Avoid generic "AI slop" aesthetics.
4. **Production Quality** — Well-commented, accessible, performant.
5. **Viewport Fitting (CRITICAL)** — Every slide MUST fit exactly within the viewport. No scrolling. See `references/viewport-css.md`.

## CRITICAL: Viewport Fitting

**Every slide must be fully visible without scrolling on any screen size.**

- Each slide = exactly `100vh`/`100dvh`, `overflow: hidden`
- All typography uses `clamp()` for responsive scaling
- Content per slide respects density limits (max 4-6 bullets, max 6 cards)
- Breakpoints for heights: 700px, 600px, 500px

Full CSS architecture and checklist: **`references/viewport-css.md`**

---

## Phase 0: Detect Mode

- **Mode A: New Presentation** → Phase 1
- **Mode B: PPT Conversion** → Phase 4
- **Mode C: Enhancement** → Read existing file, then enhance

---

## Phase 1: Content Discovery (New Presentations)

Ask via AskUserQuestion:

1. **Purpose** — Pitch deck / Teaching / Conference talk / Internal presentation
2. **Length** — Short (5-10) / Medium (10-20) / Long (20+)
3. **Content readiness** — All ready / Rough notes / Topic only

If user has content, ask them to share it.

---

## Phase 2: Style Discovery

**Two paths:**

**Option A: Guided Discovery (Default)**
1. Ask mood: Impressed/Confident, Excited/Energized, Calm/Focused, Inspired/Moved (multiSelect, up to 2)
2. Generate 3 mini HTML previews in `.claude-design/slide-previews/` based on mood
3. User picks favorite or mixes elements

**Option B: Direct Selection** — User picks from preset list, skip to Phase 3.

### Available Presets

| Preset | Vibe | Best For |
|--------|------|----------|
| Bold Signal | Confident, high-impact | Pitch decks, keynotes |
| Electric Studio | Clean, professional | Agency presentations |
| Creative Voltage | Energetic, retro-modern | Creative pitches |
| Dark Botanical | Elegant, sophisticated | Premium brands |
| Notebook Tabs | Editorial, organized | Reports, reviews |
| Pastel Geometry | Friendly, approachable | Product overviews |
| Split Pastel | Playful, modern | Creative agencies |
| Vintage Editorial | Witty, personality-driven | Personal brands |
| Neon Cyber | Futuristic, techy | Tech startups |
| Terminal Green | Developer-focused | Dev tools, APIs |
| Swiss Modern | Minimal, precise | Corporate, data |
| Paper & Ink | Literary, thoughtful | Storytelling |

### Mood → Preset Mapping

| Mood | Options |
|------|---------|
| Impressed/Confident | Bold Signal, Electric Studio, Dark Botanical |
| Excited/Energized | Creative Voltage, Neon Cyber, Split Pastel |
| Calm/Focused | Notebook Tabs, Paper & Ink, Swiss Modern |
| Inspired/Moved | Dark Botanical, Vintage Editorial, Pastel Geometry |

### Preview Requirements

Each preview: self-contained HTML, single title slide, animated, ~50-100 lines.

**Never use:** Purple gradients on white, Inter/Roboto/system fonts, standard blue primary, predictable hero layouts.

**Instead use:** Unique font pairings (Clash Display, Satoshi, Cormorant Garamond, DM Sans), cohesive color themes, atmospheric backgrounds, signature animations.

---

## Phase 3: Generate Presentation

### HTML Architecture

Single self-contained HTML file with:

1. **CSS Custom Properties** — All theme values in `:root` for easy customization
2. **Mandatory viewport fitting CSS** — See `references/viewport-css.md`
3. **SlidePresentation JS class** — Keyboard nav, touch/swipe, mouse wheel, progress bar, nav dots
4. **Intersection Observer** — Scroll-triggered `.visible` class for animations
5. **Accessibility** — Semantic HTML, ARIA labels, reduced motion support

Animation patterns and effects: **`references/animation-patterns.md`**

### Code Quality

- Every CSS/JS section has clear comments
- Semantic HTML (`<section>`, `<nav>`, `<main>`)
- Keyboard navigation works
- `@media (prefers-reduced-motion: reduce)` support

---

## Phase 4: PPT Conversion

1. **Extract** — Use `python-pptx` to extract text, images, notes
2. **Confirm** — Present extracted content structure to user
3. **Style** — Proceed to Phase 2 for style selection
4. **Generate** — Convert to chosen style, preserving all content and images

---

## Phase 5: Delivery

1. Clean up `.claude-design/slide-previews/` if it exists
2. Open presentation with `open [filename].html`
3. Provide summary with navigation instructions and customization tips

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Fonts not loading | Check Fontshare/Google Fonts URL and CSS font names |
| Animations not triggering | Verify Intersection Observer and `.visible` class |
| Scroll snap broken | Check `scroll-snap-type` on html and `scroll-snap-align` on slides |
| Mobile issues | Disable heavy effects at 768px, test touch events |
| Performance | Use `will-change` sparingly, prefer `transform`/`opacity` animations |
