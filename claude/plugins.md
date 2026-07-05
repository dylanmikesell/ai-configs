# Claude Code plugins

Plugins are installed and versioned by their upstream authors via the Claude Code plugin
marketplace, so their code does **not** live in this repo. This file records which
plugins I rely on and the commands to reinstall them on a fresh machine.

Marketplace/plugin state itself lives under `~/.claude/plugins/`
(`installed_plugins.json`, `known_marketplaces.json`) — managed by Claude Code, not tracked here.

## Installed

### `claude-scientific-writer`

- **Marketplace:** `claude-scientific-writer` — https://github.com/K-Dense-AI/claude-scientific-writer
- **Plugin:** `claude-scientific-writer@claude-scientific-writer`
- **Installed:** 2026-07-03
- **Purpose:** skills for research writing, literature review, peer review, and
  document/slide/poster production.
- **Local pruning:** the three clinical/medical skills (`clinical-decision-support`,
  `clinical-reports`, `treatment-plans`) are removed to save context tokens — irrelevant
  to geophysics work. See "Pruning" below.

Reinstall:

```
/plugin marketplace add https://github.com/K-Dense-AI/claude-scientific-writer
/plugin install claude-scientific-writer@claude-scientific-writer
```

Skills it provides (namespaced `claude-scientific-writer:<skill>`):

| Group | Skills |
|---|---|
| Writing & manuscripts | `scientific-writing`, `scientific-writer-init`, `venue-templates`, `research-grants` |
| Literature & citations | `literature-review`, `citation-management`, `research-lookup` |
| Review & reasoning | `peer-review`, `scientific-critical-thinking`, `hypothesis-generation` |
| Slides, posters, figures | `scientific-slides`, `latex-posters`, `paper-2-web`, `scientific-schematics` |
| Document toolkits | `docx`, `pdf`, `pptx`, `xlsx`, `markitdown` |
| ~~Clinical/medical~~ (removed) | ~~`clinical-decision-support`, `clinical-reports`, `treatment-plans`~~ |

#### Pruning (removing skills to save tokens)

Registered skills cost context tokens every session, so unused ones are worth removing.
The plugin lives under `~/.claude/plugins/` — **not** in this repo, so pruning is a manual
local edit, not a git change here.

To remove a skill:

1. Delete its entry from the `skills` array in the plugin manifest:
   - Active install: `~/.claude/plugins/cache/claude-scientific-writer/claude-scientific-writer/<sha>/.claude-plugin/marketplace.json`
   - Marketplace copy (keeps reinstall consistent): `~/.claude/plugins/marketplaces/claude-scientific-writer/.claude-plugin/marketplace.json`
2. Delete the skill's folders (they appear under `skills/`, `.claude/skills/`, and
   `scientific_writer/.claude/skills/` within each of the two locations above).

Removed so far: `clinical-decision-support`, `clinical-reports`, `treatment-plans` (2026-07-05).

> ⚠️ **`/plugin update` restores upstream state**, re-adding pruned skills. Re-prune after updating.

Documented for future-me in the Obsidian vault: `Extras/MOC/🤖 AI + Claude MOC.md`.
