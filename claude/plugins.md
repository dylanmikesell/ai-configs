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

## Vendored skills (copied into this repo)

### Co-Scientist toolkit skills (2026-10-27)

- **Source:** https://github.com/shocklab/co-scientist-toolkit (Shocklab, Univ. of Cape Town). Code MIT, docs CC BY 4.0.
  Licence copy: `claude/skills/THIRD-PARTY-LICENSE-co-scientist-toolkit.txt`.
- **Why vendored, not installed as a plugin:** the `papers` plugin bundles a licence-check hook
  (bash, needs `jq`/poppler, Mac-oriented) that I have not adopted. Installing the plugin would
  register it. The toolkit is young and Mac-first, so I copied only the skills I want.
- **Copied:** `reference-verifier` (with `scripts/verify_references.py`), `pre-register`,
  `convergence-check` under `claude/skills/`.
- **Local edits:** a provenance line under each title; in `reference-verifier`, the sentence about the
  licence hook was replaced by a Windows note about `pdftotext`/`pandoc`.
- **Not yet adapted:** `pre-register` is worded for RL/ML ("cheap pilot", compute); reword for
  geophysics (synthetic test, small forward model) after first use.
- **Script patch:** `verify_references.py` wrote its report and cache with the Windows default
  encoding (cp1252) and crashed on the status symbols. Added `encoding="utf-8"` to the four
  `read_text`/`write_text` calls (lines 137, 165, 1195, 1200). Re-apply if the script is re-vendored.
- **Status:** smoke-tested 2026-10-27 on a two-entry `.bib` (one real, one invented). It runs on Windows.
  Needs `uv` and `REFVERIFY_CONTACT_EMAIL`; optional `SEMANTIC_SCHOLAR_API_KEY`. Results: the invented
  entry came back `low_confidence` (nearest unrelated paper shown), not `not_found`. The real entry
  came back `metadata_mismatch` because Crossref's best match was a 2025 re-registration of the
  same title (year 2017 vs 2025). So entries without a DOI need a human look; add DOIs to the `.bib`
  for clean results.
- **Considered, not adopted (yet):** `paper-review`, `claim-fact-checker`, `academic-pdf-to-mkd`,
  `arxiv-fetcher`, the licence-check hook, `decision-page`, and the meetings/audio/documents plugins.
  The `guidance/` templates (decision log, facts registry, handoff, paper `CLAUDE.md`) are queued for
  `project-templates/`.

Documented for future-me in the Obsidian vault: `Extras/MOC/🤖 AI + Claude MOC.md`.
