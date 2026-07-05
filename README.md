# Presenty Skill

Give your AI agent the power to create stunning presentations.

**[Presenty](https://www.presenty.dev)** is a free, web-based presentation tool: Markdown in, beautiful Reveal.js slides out — with animated step-by-step mermaid diagrams, interactive Chart.js charts, auto-animated slides, backgrounds, transitions, themes, and inline drawing.

This skill teaches your agent Presenty's special Markdown syntax and publishes presentations directly, handing you back a live edit URL. Just say:

> *"Create me a presentation about \<anything\> using presenty"*

…and open the link it returns. Update it the same way: paste your presenty.dev link and describe the change.

## Install

Works with Claude Code, Cursor, Codex, GitHub Copilot, OpenClaw, Gemini CLI, and [70+ other agents](https://skills.sh):

```bash
npx skills add salman497/presenty-skill
```

Get the latest version anytime:

```bash
npx skills update
```

**Claude.ai (web/desktop):** download [`presenty.zip`](https://github.com/salman497/presenty-skill/releases/latest/download/presenty.zip) and upload it in *Settings → Capabilities → Skills* (requires Code execution enabled).

**Manual:** copy `skills/presenty/` into your agent's skills folder (e.g. `~/.claude/skills/`, `~/.agents/skills/`, or your repo's `.claude/skills/`).

## What's inside

```
skills/presenty/
├── SKILL.md               # the workflow the agent follows
├── references/syntax.md   # full Presenty Markdown syntax guide
└── scripts/presenty.py    # zero-dependency publisher (Python 3 stdlib)
```

No API keys, no signup, no dependencies — the script publishes anonymously through Presenty's public backend and returns your edit/view URLs.

## Example

Ask your agent: *"i need a quick pitch deck for my coffee startup using presenty"* → you get a link like:

```
https://www.presenty.dev/published/edit/439223/beandrop-pitch-deck
```

Open it to present, edit live, draw on slides, switch themes, or share the view link.

## License

MIT
