---
name: lit-inbox
description: >-
  Process new papers dropped into the Zotero "_Claude-Inbox" collection. For each
  new paper: read and assess the PDF against the user's editable assessment config,
  create highlight annotations on the PDF inside Zotero, and write (or merge) an
  Obsidian literature note. Handles preprint -> published de-duplication so a paper
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

The assessment config is the user's control panel. **Always read it fresh at the start
of every run** — the user edits it between runs to steer what you extract and highlight.
Never cache your memory of it.

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
- Find the PDF attachment key (`zotero_get_item_children`). If there is no PDF, note
  that in the report, write the note from metadata/abstract only, skip highlighting.

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
- **Key takeaways** — bulleted, skimmable.
- **Related** — `[[@citekey]]` links to other papers in the vault where relevant.

### 2d. Highlight in the Zotero PDF
Follow the config's highlighting guidance (how many, what kinds). Default: 6–12 of the
most important sentences (claims, key results, definitions, method choices, limitations).
For each, call `zotero_create_annotation(attachment_key, page, text, color, comment)`:
- `text` MUST be the **exact** substring from that page's text layer (verify by reading
  the page). Ligatures (ﬀ, ﬁ) and hyphenation break matches — pick clean, contiguous
  phrases; shorten rather than risk a miss.
- Use color to encode meaning if the config defines a scheme; otherwise yellow `#ffd400`.
- Put a short "why this matters" in `comment`.
- If a highlight fails to match, adjust the text and retry once; then move on and log it.
Scanned/image-only PDFs have no text layer — skip highlighting and note it.

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

### 2g. Optional Zotero child note
If enabled (Section 0), create a short takeaways note on the item
(`zotero_create_note`, title "Claude takeaways", concise HTML: contribution + 3–5
bullets). This keeps the gist visible inside Zotero too.

### 2h. Mark done
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

## 4. Report

End with a compact summary: papers processed, notes created vs merged, highlights added
per paper, any skips (no PDF / scanned / failed highlight), and the note file paths.

## 5. Guardrails
- Idempotent: the `claude/done` tag prevents reprocessing; a title match prevents
  duplicate notes. When unsure whether two items are the same paper, prefer merging and
  say so in the report rather than creating a duplicate.
- Never invent findings. If the PDF is unreadable, say so; don't fabricate an assessment.
- Never edit the user zone of a note.
- The assessment config governs judgement calls (focus, tone, highlight budget). Re-read
  it every run.
