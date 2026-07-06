---
name: lit-inbox
description: >-
  Process new papers dropped into the Zotero "_Claude-Inbox" collection. For each
  new paper: read and assess the PDF against the user's editable assessment config,
  create highlight annotations on the PDF inside Zotero, and write (or merge) an
  Obsidian literature note that includes a critical appraisal (rigor/bias/stats) and
  a reproducibility check, then seed linked "research-idea" notes that extend the
  paper toward the user's work. Handles preprint -> published de-duplication so a paper
  is never noted twice. Trigger with the slash command /lit-inbox or phrases like
  "process my inbox", "process my papers", "read my new papers", "run lit-inbox".
---

# lit-inbox — Zotero → Obsidian literature pipeline

This skill turns "I dropped a paper in my Zotero inbox" into "the PDF is highlighted
in Zotero and there is a rich, linkable literature note in Obsidian" — with the human
staying in control of *what* gets assessed via an external, editable config file.

Owner: Dylan Mikesell (dylan.mikesell@ngi.no). Manual trigger for now (a cron job may
be added later; the pipeline below is written to run identically either way).

---

## 0. Configuration (single source of truth)

All machine-specific values live here. If any path/key changes, edit only this block.

| Setting | Value |
|---|---|
| Zotero library | My Library (libraryID = 1) — the default active library |
| Inbox collection | `_Claude-Inbox` — key `8425VLJY` |
| Done/read collection | `_Claude-Read` — key `C2ECZCB4` |
| Processed marker tag | `claude/done` |
| Assessment config (read EVERY run) | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Extras\Claude\literature-assessment.md` |
| Obsidian lit-notes folder | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Literature-notes\` |
| Note filename | `@{citekey}.md` (matches the vault's `[[@citekey]]` wikilink convention) |
| Zotero child note | ON — also write a short takeaways note onto the Zotero item |
| Obsidian ideas folder | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Ideas\` |
| Idea note filename | `idea-{slug}.md` (kebab-case slug of the idea's core question) |
| Critical appraisal | ON — rigor / bias / stats / claim-vs-data flags in the assessment (framework in §2c) |
| Reproducibility check | ON — note data & code availability and reuse potential (§2c) |
| Research-idea notes | ON — seed 2–4 linked idea notes per paper (§2g) |

The assessment config is the user's control panel. **Always read it fresh at the start
of every run** — the user edits it between runs to steer what you extract and highlight.
It also governs the newer features: how hard to push the critical appraisal, whether to
run the reproducibility check, and how many research-idea notes to seed (0 turns the idea
step off). Honor those settings; the table values above are only defaults when the config
is silent. Never cache your memory of it.

---

## 1. Find the work

1. Read the assessment config file (Section 0 path). Treat its contents as
   authoritative instructions for *what to assess and highlight*.
2. List items in the inbox collection (`zotero_get_collection_items`, key `8425VLJY`,
   `detail="full"`).
3. For each item, fetch metadata as JSON (`zotero_get_item_metadata`, `format="json"`)
   and check its tags. **Skip any item already tagged `claude/done`** (idempotency —
   safe to re-run any time). Attachments are not papers; ignore them.
4. If nothing is unprocessed, report "Inbox clear" and stop.
5. Process the remaining items one at a time, oldest first.

---

## 2. Per-paper pipeline

For each unprocessed item (`ITEM_KEY`):

### 2a. Gather identity
- BibTeX (`zotero_get_item_metadata`, `format="bibtex"`) → the **citekey** and clean fields.
- Markdown metadata (with abstract) for title, authors, year, DOI, item type, venue.
- Record the **item type** — note whether it is a `preprint` vs `journalArticle`/etc.
- Find the PDF attachment key (`zotero_get_item_children`; also confirm `numChildren` in
  the item metadata). **PDF-required gate — if there is NO PDF attachment, STOP processing
  this item:** do not write/merge an Obsidian note, do not seed ideas, do not create a
  Zotero child note, and do **NOT** tag `claude/done` or move it out of the inbox. Leave it
  in `_Claude-Inbox` untouched and add it to the report's **"⚠️ Missing PDF"** list so the
  user can attach the PDF and re-run. Then continue to the next item.
  (A PDF that *exists* but is scanned/image-only is a different case — see §2d: process it
  from text where possible and skip only the highlighting.)

### 2b. Read the paper
- Get the PDF outline if available (`zotero_get_pdf_outline`) to map sections.
- Read the full text (`zotero_get_item_fulltext`) OR read page ranges
  (`zotero_read_pdf_pages`) covering intro, methods, results, and conclusions.
- Read enough to genuinely assess the paper — do not assess from the abstract alone.

### 2c. Assess (follow the assessment config)
Produce the fields the config asks for. Default set if the config is silent:
- **Contribution** — the one-sentence "what's new / why it matters".
- **Key findings** — 3–6 concrete results (numbers where available).
- **Methods / data** — approach, dataset, instruments, study area.
- **Relevance to my work** — explicit ties to the user's research (see config).
- **Limitations / open questions** — what's weak, unresolved, or worth following up.
- **Critical appraisal** — rigor flags (framework below). 2–5 bullets, not an essay.
- **Reproducibility** — data & code availability + could-I-reuse-this verdict (framework below).
- **Key takeaways** — bulleted, skimmable.
- **Related** — `[[@citekey]]` links to other papers in the vault where relevant.

**Critical-appraisal framework** (adapted from `scientific-critical-thinking`). Skim these
lenses and surface only the flags that genuinely apply — say "no major concerns" when it's
sound. Ground every flag in the actual text; never invent a weakness to fill the section.
- **Design/validity** — does the design support the causal claims made? Confounders controlled?
- **Statistics** — sample size / power; correlation used as causation; multiple comparisons
  uncorrected; effect sizes & uncertainty reported (error bars, CIs) or just p-values?
- **Bias** — selection/sampling, p-hacking or HARKing (post-hoc hypotheses), cherry-picked
  evidence, ignored contradictory findings.
- **Claim vs. data** — do the conclusions follow from what was actually shown, or overreach
  (overgeneralized, extrapolated beyond the data, mechanism claimed without mechanistic evidence)?
Where useful, name the issue precisely (e.g. "causal claim from correlational field data").

**Reproducibility framework** (from `peer-review`, reuse-focused — NOT an accept/reject verdict).
- Is the **data** deposited/available (repository, DOI, accession numbers) or on request/absent?
- Is **code** shared (GitHub/Zenodo/supplement) and are software/versions/parameters stated?
- Are methods detailed enough that you could re-run or adapt the workflow?
- One-line **reuse verdict**: could Dylan reuse the data/code/method in his work, and how?

### 2d. Highlight in the Zotero PDF (PER-LINE, full sentences)
`zotero_create_annotation(attachment_key, page, text, color, comment)` takes only
`(page, exact text)` and maps the text to rectangles itself. That mapping is reliable
ONLY for a single physical line of text that is unique on the page. Multi-line strings
get rounded to full-line width (over-painting adjacent words), and text that repeats on
the page is highlighted at EVERY occurrence. So highlight the full sentence by creating
**one annotation per physical line** it spans:

- Get exact line breaks from `zotero_read_pdf_pages` (it preserves them). Follow the
  config for how many sentences and which kinds (claims, key numbers, methods, limits).
- Split the target sentence at the PDF's physical line boundaries. For each line the
  annotation `text` is the exact on-page substring of the sentence on that line:
  - first line: sentence's start word → end of that line (KEEP a trailing hyphen if the
    word is split at the line end, e.g. `"... causes predom-"`);
  - middle lines: the whole line, verbatim;
  - last line: line start → the sentence's final word/punctuation.
- Copy each substring EXACTLY as rendered (including end-of-line hyphens). Each piece is
  then a clean single-line match = one rectangle.
- Make each piece UNIQUE on the page. If a line's text also appears elsewhere on the same
  page (classic case: an abstract sentence echoed in a Plain-Language Summary), extend the
  snippet by one adjacent word to disambiguate, or pick a different sentence. Don't cross
  a line break to gain uniqueness.
- Same color for all pieces of one sentence (config scheme, else `#ffd400`). Put the
  "why it matters" comment on the FIRST piece only; leave later pieces' comment empty.
- The config's highlight budget counts SENTENCES, not pieces (default 6–12 sentences).
- Optional verify: re-read a sentence's pieces; if one produced rectangles far apart on
  the page it matched a duplicate — delete it and redo with a unique snippet.
- Scanned/image-only PDFs have no text layer — skip highlighting and note it.

### 2e. De-duplicate (preprint → published merge) — CRITICAL
A paper must have **exactly one** Obsidian note across its whole life (preprint, then
published). Before writing, look for an existing note for this paper:
1. Glob `Literature-notes/*.md` and compare against a **normalized title** (lowercase,
   strip punctuation/whitespace). Also compare DOI and citekey. Title match is the
   reliable cross-version signal, because a preprint and its published version have
   **different DOIs** but (almost always) the **same title**.
2. **No match →** create a new note `@{citekey}.md` (Section 3).
3. **Match found →** MERGE into the existing note, do NOT create a second file:
   - Keep the original filename. If the citekey changed (e.g. preprint `xxx2026` →
     published `yyy2027`), add the new citekey to the note's `aliases:` so old
     `[[@oldcitekey]]` links still resolve.
   - Update frontmatter: set `version: published`, move the old DOI to `preprint_doi:`,
     set `doi:` to the published DOI, update `year`/venue, append the new `zotero_key`.
   - Regenerate the Claude-managed assessment zone from the newer version.
   - **Never touch the user zone** (everything below the `# My notes` marker).
   - Relate the two Zotero items: `zotero_add_item_relation(preprint_key,
     published_key, relation_type="owl:sameAs")`.

### 2f. Write / update the Obsidian note
Write the note per the template in Section 3. Managed zone above the marker is yours to
(re)generate; the user zone below is sacrosanct.

### 2g. Seed research-idea notes (Obsidian)
Turn the reading into *your own next moves*. Using the hypothesis-quality bar (below),
generate the number of ideas the config asks for (default 2–4; `0` = skip this step) that
**extend** the paper toward Dylan's work — not a summary of the paper's own future-work
section. Each idea becomes its **own note** in the ideas folder (Section 0), so it's a
first-class graph node he can grow and link to other papers later.

**What makes an idea worth a note** (adapted from `hypothesis-generation`):
- **Mechanistic** — proposes *how/why*, not just "someone should study X".
- **Testable & falsifiable** — a concrete prediction that could come out either way.
- **Distinguishable** — doesn't just restate the paper; adds a new angle, scale, method,
  or application (ideally tied to Dylan's geophysics/NGI context).
- **Grounded** — traces back to something specific the paper showed.

For each idea, write a note from the template in **Section 3b**. Before creating it, do a
**light de-dup**: glob the ideas folder and compare the idea's core question (normalized)
against existing `idea-*.md`. If one clearly already exists, DON'T duplicate — add this
paper's citekey to that note's `seeds:` list and append a one-line note under a
`## Related findings` heading instead. Otherwise create `idea-{slug}.md`.

Idea notes are **user-owned once created**: on later runs (including preprint→published
merges) never rewrite an existing idea note's body — only append a new `seeds:` entry / a
`## Related findings` line. In the lit note's managed zone, list `[[idea-...]]` backlinks
for every idea seeded from this paper (so the graph connects both ways).

### 2h. Optional Zotero child note
If enabled (Section 0), create a short takeaways note on the item
(`zotero_create_note`, title "Claude takeaways", concise HTML: contribution + 3–5
bullets). This keeps the gist visible inside Zotero too.

### 2i. Mark done
- Tag the item `claude/done` (`zotero_batch_update_tags`, select by exact title,
  `add_tags=["claude/done"]`). This tag is the authoritative "processed" marker.
- Move it inbox → read with a single call:
  `zotero_manage_collections(item_keys=[ITEM_KEY], add_to=["C2ECZCB4"],
  remove_from=["8425VLJY"])` so the inbox reflects only unprocessed papers. (The
  `claude/done` tag remains the authoritative processed marker regardless.)

---

## 3. Obsidian note template (rendered, static — no plugin required)

Write plain Markdown. Preserve the vault's dataview inline-field style (`Field:: value`)
and `category: literaturenote` so existing dataview queries keep working. Fill every
`{{...}}`. Keep the exact `# My notes` marker line so merges can find the user zone.

```markdown
---
category: literaturenote
tags: [{{topic-tags, kebab-case}}]
citekey: {{citekey}}
aliases: ["@{{citekey}}"]
zotero_key: {{ITEM_KEY}}
attachment_key: {{PDF_KEY}}
doi: {{doi}}
year: {{year}}
version: {{preprint|published}}
status: read
date_processed: {{YYYY-MM-DD}}
---

> [!Cite]
> {{full formatted citation}}

> [!md] Metadata
> **Title**:: {{title}}
> **FirstAuthor**:: {{first author "Last, First"}}
> **Year**:: {{year}}
> **itemType**:: {{itemType}}
> **Citekey**:: {{citekey}}

> [!Synth] Claude assessment ({{version}} · assessed {{YYYY-MM-DD}})
> **Contribution**:: {{one sentence}}
> **Methods**:: {{approach / data / study area}}
> **Relevance**:: {{ties to the user's research}}
> **Limitations**:: {{weaknesses / open questions}}
> **Related**:: {{[[@citekey]], ...}}
> **Ideas**:: {{[[idea-slug]], ... — backlinks to notes seeded in §2g, or "—"}}

> [!Warning] Critical appraisal
> {{2–5 rigor/bias/stats/claim-vs-data flags, or "No major concerns — sound within its scope."}}

> [!Check] Reproducibility
> **Data**:: {{repository / DOI / on request / not available}}
> **Code**:: {{shared where / not shared}}
> **Reuse**:: {{one-line could-I-reuse-this verdict}}

## Key findings
- {{finding with numbers}}

## Key takeaways
- {{skimmable takeaway}}

> [!Abstract]
> {{abstract}}

> [!LINK] PDF
> [Open in Zotero](zotero://select/library/items/{{ITEM_KEY}}) · [PDF]({{file:// path}})

## Highlights (from Zotero)
- p.{{n}} "{{highlighted text}}" — {{why}}

---
# My notes
<!-- USER ZONE — Claude never edits below this line. Add your own thoughts and [[links]] here. -->
```

On a **merge/update**, rewrite only the frontmatter + everything from `> [!Cite]` down to
the `---` above `# My notes`. Leave the user zone byte-for-byte unchanged.

---

## 3b. Research-idea note template (Section 2g)

One note per idea, in the ideas folder. The title is the idea phrased as a **question**.
Everything below `# Develop` is the user's — Claude only ever appends a new `seeds:` entry
and, if this paper is a fresh seed for an existing idea, a `## Related findings` line.

```markdown
---
type: research-idea
status: seed
summary: {{idea as a one-line question — this is what the Ideas MOC table shows}}
seeds: ["[[@{{citekey}}]]"]
created: {{YYYY-MM-DD}}
tags: [research-idea, {{topic-tags}}]
---
tags:: [[💡 Ideas MOC]]

# {{idea as a one-line question}}

**Extends**:: [[@{{citekey}}]]
**Why**:: {{what in the paper makes this plausible — the mechanistic hook}}
**Prediction**:: {{concrete, falsifiable — what we'd expect to see if the idea holds}}
**Test**:: {{how Dylan could actually test it — data, instrument, site, method}}
**Ties to my work**:: {{link to the NGI/geophysics angle, other [[@citekey]] or [[notes]]}}

## Related findings
- [[@{{citekey}}]] ({{YYYY}}) — {{one line on how this paper feeds the idea}}

# Develop
<!-- USER ZONE — Claude never edits below this line. Grow the idea here. -->
```

**Fields the [[💡 Ideas MOC]] table depends on** — always fill them:
- `summary` — the readable one-line question (the table's main column).
- `status` — one of `seed` · `exploring` · `active` · `parked` · `done` (start at `seed`).
- `seeds` — YAML list of `"[[@citekey]]"` wikilink strings (add one per de-dup merge; §2g).
- `created` — the run date.

---

## 4. Report

End with a compact summary: papers processed, notes created vs merged, highlights added
per paper, **critical-appraisal flags raised** and **research-idea notes seeded** (new vs.
linked-to-existing) per paper, and the file paths for both the lit notes and the idea notes.
Call out a separate **"⚠️ Missing PDF (left in inbox, not processed)"** list naming every
item skipped by the §2a PDF-required gate, plus any other skips (scanned/image-only,
failed highlight).

## 5. Guardrails
- Idempotent: the `claude/done` tag prevents reprocessing; a title match prevents
  duplicate notes. When unsure whether two items are the same paper, prefer merging and
  say so in the report rather than creating a duplicate.
- **A PDF is required to process an item.** No PDF attachment → skip it entirely and report
  it as missing (§2a); never write a metadata/abstract-only note and never mark it done. The
  item must stay in the inbox so re-running after the PDF is attached picks it up cleanly.
- Never invent findings. If the PDF is unreadable, say so; don't fabricate an assessment.
- **Never fabricate rigor.** Critical-appraisal flags must trace to the actual text —
  "no major concerns" is a valid, honest result. Don't manufacture weaknesses to fill the
  section, and don't soft-pedal a real one.
- **Ideas extend, they don't summarize.** An idea note must add a new angle Dylan could
  act on — if the only "idea" is restating the paper's own future work, seed fewer notes.
- Never edit the user zone of a lit note, and never rewrite an existing idea note's body —
  only append a `seeds:` entry / a `## Related findings` line (idea notes are user-owned
  once created).
- The assessment config governs judgement calls (focus, tone, highlight budget, appraisal
  depth, idea count). Re-read it every run.
