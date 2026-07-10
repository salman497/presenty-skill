---
name: presenty
description: Create and update Presenty presentations (presenty.dev) — visually rich Reveal.js slide decks written in Markdown with animated mermaid diagrams, Chart.js charts, auto-animated slides, backgrounds, and transitions. Use this whenever the user asks to create, make, build, or update a presentation, slide deck, slideshow, or pitch deck, mentions Presenty, or shares a presenty.dev URL — even if they don't say "Presenty" explicitly, a request for a presentation should use this skill. Publishes directly and returns a live edit URL.
---

# Presenty Presentation Creator

Presenty (https://www.presenty.dev) turns special-syntax Markdown into stunning
Reveal.js presentations with real-time editing, animated step-by-step diagrams,
interactive charts, inline drawing, slide animations, and themes. This skill
authors that Markdown, publishes it, and hands the user a live URL.

## Workflow

### 1. Understand the request

Figure out: the topic, the audience/tone, roughly how many slides (default
8–12), and whether this is a **new** presentation or an **update** to an
existing one (the user gives a presenty.dev URL or an id → it's an update).
If the topic needs current facts (recent events, prices, versions), do a quick
web search first so the content is accurate.

### 2. Author the Markdown

**Read `references/syntax.md` before writing** — it contains the exact syntax,
working examples, and the common mistakes that silently break slides.

**It's a PowerPoint-style deck, not a book: less words, more visual.** Hard
rules:

- **Never put large text on one slide.** Any slide that would carry more than
  a heading plus ~2 short lines must become a **progressive-disclosure
  build-up**: consecutive slides with `<!-- .slide: data-auto-animate -->`,
  repeating the previous slide's content verbatim and adding **one** new line
  each slide. Use a descending heading hierarchy so the new line lands
  smaller than what's above it (`##` title → `####` point → `#####` detail):

  ```markdown
  <!-- .slide: data-auto-animate -->

  ## Why Solar Energy?

  ***

  <!-- .slide: data-auto-animate -->

  ## Why Solar Energy?

  #### ☀️ Clean and renewable

  ***

  <!-- .slide: data-auto-animate -->

  ## Why Solar Energy?

  #### ☀️ Clean and renewable

  #### 📉 Cost fell 90% in a decade
  ```

  This is the pattern the official starter template uses throughout — the
  audience sees points appear step by step instead of a wall of text.
- **Max ~20 words per slide** (headings included, diagrams/charts excluded).
  Phrases, not sentences. Never paragraphs, never long bullet lists.
- **Use emoji icons** (🚀 ✅ 📈 💡 👍 ⚠️ …) at the start of points, in
  headings, and in mermaid/flowchart node labels (or `fa:fa-*` FontAwesome in
  flowcharts) — they read as professional visual anchors. **Do not use random
  stock/background images**: no `data-background-image`, no decorative
  `<img>` from picsum/unsplash. Only embed an image if it's a real, verified,
  topic-specific URL (a product screenshot, a logo the user gave you). For
  visual variety use `data-background-color` section-break slides instead.
- Title slide with the topic as the main heading, then `***`-separated slides.
- Each slide is **one idea**: a heading plus a diagram, a chart, or 1–3 short
  icon-prefixed lines.
- Must include, somewhere in the deck:
  - at least one ` ```mermaid-steps ` diagram (flowchart, sequenceDiagram, or
    mindmap) — this is Presenty's signature animated-diagram feature
  - at least one plain ` ```mermaid ` diagram of a different type
  - a ` ```chartjs ` chart whenever the topic has anything quantifiable
  - at least two progressive-disclosure build-up sequences (see above)
  - at least one `data-background-color` section-break slide
  - at least one slide with `<!-- .slide: data-transition="zoom" -->`
    (the big-reveal slide — use it once, not everywhere)
- For mindmaps, add `%%URL%%` after node text to make nodes clickable when
  there's a genuinely useful link.

**Pick theme, animation, and mermaid style for the topic — then keep them
consistent** (one theme, one base animation for the whole deck; per-slide
`data-transition` only for the single big reveal). Supported values (from the
app's settings):

- Themes: `Black`, `White`, `League`, `Sky`, `Beige`, `Simple`, `Serif`,
  `Blood`, `Night`, `Moon`, `Dracula`, `Solarized`. Guide: `Black` = default
  all-rounder / tech; `White` or `Simple` = corporate, clean; `Sky` or
  `Beige` = friendly, light; `Night` / `Moon` / `Dracula` = developer-flavored
  dark; `Serif` = formal/academic; `League` = stylish gray; `Blood` = bold.
- Animations: `None`, `Fade`, `Slide`, `Convex`, `Concave`, `Zoom` —
  `Slide` is the safe default; `Fade` for calm/corporate; `Zoom` for punchy.
- Mermaid styles: `dark`, `neutral`, `default`, `base` — **omit it** unless
  you have a reason: Presenty auto-picks a mermaid theme that matches the
  Reveal theme (e.g. Black→dark, White→neutral).

Write the markdown to a local file (e.g. `slides.md` in a temp/working dir).

### 3. Validate before publishing (mandatory)

Re-read the finished file top to bottom and run **both** checklists. Fix and
re-check until everything passes — do not publish a deck that fails a line.

**Syntax check** (against `references/syntax.md` "Common mistakes"):

- [ ] every `***` alone on its own line, blank line before and after, never
      inside a code fence
- [ ] every ` ``` ` fence is closed
- [ ] chartjs bodies are strict JSON — mentally `JSON.parse` each one
      (double quotes, no trailing commas, no comments)
- [ ] `mermaid-steps` only wraps flowchart / sequenceDiagram / mindmap
- [ ] mermaid node labels have no `(`, `)`, or `"` inside the text
- [ ] auto-animate slides repeat the previous slide's content **verbatim**
- [ ] any image URL is absolute, verified real, and not presenty.dev-hosted

**Professional-quality check:**

- [ ] no slide exceeds ~20 words — anything bigger is split into an
      auto-animate build-up
- [ ] heading hierarchy is consistent (`##` titles, `####`/`#####` points)
- [ ] points carry emoji icons; no random background/stock images anywhere
- [ ] one theme + one animation feel, `zoom` transition used at most once
- [ ] deck flows: title → agenda/hook → body (visuals + build-ups) →
      close/summary
- [ ] every diagram/chart genuinely supports the slide's one idea

### 4. Publish with the script

The script is fully self-contained (Python 3 stdlib, no install needed).

New presentation:

```bash
python3 scripts/presenty.py create --name "Presentation Name" --file slides.md
```

Pass the theme/animation you chose in step 2: `--theme <Theme>` and
`--animation Slide|Zoom|Fade|Concave|Convex|None` (defaults: `Black`,
`Slide`). Optionally `--mermaid-style dark|neutral|default|base` — omit to
let Presenty auto-match the theme. When in doubt, stay with `Black`/`Slide`.

It prints the id plus `edit_url` and `view_url`.

### 5. Updates to an existing presentation

When the user wants changes to an existing deck:

```bash
# 1. Pull the current markdown (accepts the URL they pasted, or --id)
python3 scripts/presenty.py get --url "<presenty url>" --out existing.md

# 2. Edit existing.md — modify what they asked for, keep the rest intact

# 3. Push it back (theme/settings are preserved automatically)
python3 scripts/presenty.py update --url "<presenty url>" --file existing.md
```

Only rewrite from scratch if the user asks for a rewrite; otherwise make
targeted edits to the fetched markdown.

### 6. Reply to the user

Give them the **edit URL** as the main deliverable (view URL as a bonus), in a
friendly tone. Always tell them: **everything is changeable via the burger
menu (☰) in the Presenty editor** — the Markdown itself (real-time editing),
settings, theme, colors, animations, and mermaid style, plus 100+ insertable
samples and drawing on top of slides. For new presentations, also mention they
can keep refining it just by chatting here.
