# per-paper.md: pipeline for ONE paper (subagent instructions)

You are a subagent. You process exactly one Zotero item (`ITEM_KEY`) in `MODE=inbox` or
`MODE=upgrade`. Constants (folder paths, collection keys, tags, highlight caps) are in the
Section 0 table of `SKILL.md` in the parent folder; open that file only if a value you need
is not restated here. Finish by returning the single RESULT line in §9 and nothing else.

**Loading rules (token discipline).** Read the assessment config first. Read `templates.md`
§1 (field rules) when you reach §3, and the rest of `templates.md` only when you reach §8.
Read `appraisal.md` only if the paper is Tier 2.
Never call `zotero_get_item_fulltext`: the page-range tool is the single reading path
because it preserves line breaks (needed for highlighting) and gives page anchors.
Use the page-range tool only after the tier decision, never during Tier 0 triage.

---

## 1. Read the config

Read the assessment config (path given in your prompt). Extract: relevance criteria and tier
thresholds (section "Relevance & tiering"), highlight budget and colors, appraisal depth,
reproducibility on/off, idea count. If the config is silent on something, use the defaults in
`SKILL.md` §0. If it defines no relevance criteria, treat every paper as Tier 1 and add
`no-relevance-criteria` to the RESULT warnings.

## 2. Gather identity

- BibTeX (`zotero_get_item_metadata`, `format="bibtex"`) gives the **citekey**.
- Markdown metadata (with abstract) gives title, authors, year, DOI, item type, venue.
- Note whether the item type is `preprint` or `journalArticle`/other.
- Find the PDF attachment key (`zotero_get_item_children`).
- **PDF gate:** if there is no PDF attachment, stop. Write nothing, tag nothing, move
  nothing. RESULT status `skipped`, warning `missing-pdf`.

In `MODE=upgrade`, jump to §10 after this step.

## 3. Look up an existing note (cheap, no globbing)

Read `templates.md` §1 and compute `title_norm` by its rule. Then use Grep
on the lit-notes folder, `output_mode="content"`, `head_limit=5`, three separate patterns:
`^title_norm: <value>$`, `^doi: <doi>$`, and `^preprint_doi: <doi>$` (and `^citekey: <key>$`).
Any hit means a note exists. Record its path and read ONLY its first 12 lines (frontmatter) to
get its `tier`, `version` and `pages_read`. For v1 notes without `title_norm`, also try a
case-insensitive Grep on the first six words of the title against `\*\*Title\*\*::`.
If the migrate pass has not been run, expect some misses; prefer merging when unsure.

## 4. Triage (Tier 0 decision)

Use only: metadata, abstract, and the PDF outline (`zotero_get_pdf_outline`). Do not read any
page. Score relevance against the config's criteria:

- **2**: directly addresses a stated focus topic, method, instrument or dataset, or offers
  data, code or a method Dylan could plausibly reuse. Tier 2.
- **1**: adjacent, background, or useful for context. Tier 1.
- **0**: outside scope. Tier 0 (stub).

If two scores seem plausible, choose the lower one; the user can upgrade later.
**Tier floor:** if §3 found an existing note, the new tier is at least that note's tier
(never downgrade). A published version of a Tier 2 preprint is therefore read again at
Tier 2, because the published text may differ.

Write down a one-line reason (at most 15 words) for the tier; it goes into the RESULT line.

## 5. Read by tier (page-range tool only)

Use `zotero_read_pdf_pages`. Page numbers you record are the PDF page indexes the tool uses;
store the same convention in `pages_read` and in every `(p. n)` anchor.

**Tier 0:** no reading. Go to §8 (stub).

**Tier 1 (maximum 4 pages in total):**
- With an outline: the page holding the last paragraph of the Introduction, and the pages of
  the Conclusions / Summary / final Discussion section.
- Without an outline: pages 1 and 2, then the final two pages before the reference list
  (step back from a late page until the text returned is not references).
- Take figure captions only from pages you already read.
- If a Data/Code availability statement appears on those pages, record it.

**Tier 2:** the Tier 1 pages plus, in contiguous ranges, all pages of Methods (including data
and instruments), Results, and Discussion, plus the page carrying the Data/Code availability
statement. Skip references and acknowledgments unless they carry the availability statement.
Do not assess from the abstract alone.

If the tool returns no text for any page, the PDF has no text layer: stop, write nothing,
RESULT status `skipped`, warning `no-text-layer`. If text is returned but highlighting later
fails because of geometry, skip highlights and add warning `highlight-failed`.

## 6. Assess (fields by tier)

Produce, from what you actually read:

- **Contribution**: one sentence. **Summary** (frontmatter): the same claim in at most 300
  characters, ending at the last whole word before the limit, with no line breaks and no
  double quotes.
- **Numbers**: the key quantitative results with units and uncertainties, each with a page
  anchor, for example `Vs30 of 270 ± 30 m/s (p. 6)`. Include only what the pages show.
- **Methods**: approach, data, instruments, study area (Tier 1: only what the pages state).
- **Relevance**: explicit ties to Dylan's research per the config.
- **Limitations**: weaknesses and open questions, grounded in the text.
- **Key findings** (3 to 6, each with a page anchor) and **Key takeaways**.
- **Related**: `[[@citekey]]` links to other vault papers where genuinely relevant. Find them
  with a Grep on `^summary:` or `^tags:` in the lit-notes folder; never open notes just to
  look for links.

**Tier 2 only:** read `appraisal.md`, then produce the **Critical appraisal** (2 to 5 flags or
"No major concerns") and the **Reproducibility** block (data, code, reuse verdict), and seed
ideas (§8d).
**Tier 1:** the appraisal block reads "Not assessed (Tier 1 read)"; the reproducibility block
reads "Not assessed" unless an availability statement was on the pages read, in which case
record only that statement.

## 7. Highlight in the Zotero PDF (Tier 1 and Tier 2; one annotation per sentence)

Highlight only sentences on pages you read. Caps: Tier 1 at most **6 sentences**; Tier 2 the
config budget, **never above 12 sentences**. Each sentence is one annotation, so the number
of annotations equals the number of sentences.

`zotero_create_annotation(attachment_key, page, text, color, comment)` maps the exact text
to rectangles. Create **one annotation per sentence**, with `text` set to the whole sentence:

- Copy the sentence exactly as rendered by the page-range tool, with line breaks turned into
  single spaces and end-of-line hyphens kept as they appear (for example `predom- inantly`
  is copied as returned; if the tool cannot match it, drop the space after the hyphen).
- Each sentence must be unique on its page. Repeated text is highlighted at every occurrence
  (for example an abstract sentence echoed in a plain-language summary), so choose another
  sentence or a distinctive part of it.
- Known limitation: a multi-line string may be rounded to full-line width at its first and
  last lines. This is cosmetic. Verify only when the creation call errors or returns suspicious
  geometry (rectangles far apart on the page).
- **Fallback:** if the call errors or the geometry is wrong, delete that annotation
  (`zotero_delete_annotation`) and redo that sentence as one annotation per physical line
  (same color; comment on the first piece only). Add `split-highlight` to the RESULT warnings
  and count the sentence once.
- Use the config's color for the sentence (else `#ffd400`) and put the "why it matters"
  comment on the annotation.
- Choose sentences by the config's kinds (claims, key numbers, methods, limits). At Tier 1
  favour the central claim, the headline numbers and the main limitation.
- Record each highlighted sentence's page for the note's Highlights list.

### 7b. Scanned (image-only) PDFs

If `zotero_read_pdf_pages` returns only a watermark or running header/footer on every page
(no body text), the PDF is a scan. It is **not** necessarily encrypted: the Read tool reports
some scans as "password-protected", which can be wrong. Do not mark the paper unreadable.

1. Render the pages to PNG in the scratchpad (read-only on the Zotero file), for example
   `python -I -c "import fitz,sys; d=fitz.open(sys.argv[1]); [p.get_pixmap(dpi=120).save(sys.argv[2]+'/p%02d.png'%i) for i,p in enumerate(d,1)]" <pdf> <scratchpad-dir>`
   (PyMuPDF). If the PDF really needs a password, stop with `failed` and warning
   `password-protected`; never try to break it.
2. Read the PNGs with the Read tool and treat them as the page-range tool: same Tier rules,
   same page-index anchors (PDF index, not the printed number). Quote numbers only when
   legible; say so when a figure or table value is hard to read.
3. Create **no** highlights (the annotation tool needs a text layer). Report `highlights 0`
   and add the warning `no-text-layer`. Set `pages_read` to e.g. `"1-18 (scanned PDF, read
   from rendered images)"`.
4. Everything else (note, appraisal, ideas, child note, tags) proceeds as normal.

## 8. Write (in this order; the done tag is last)

### 8a. Back up, then create or merge the lit note

Read `templates.md` now. If §3 found an existing note, **back it up first**: copy it to the
backup folder as `{filename}.bak-YYYYMMDD` (prefer `cp -n` through Bash so no tokens are
spent reading it; never overwrite an existing backup; if Bash is unavailable, Read then Write
the copy). Count the backup.

- **No existing note:** create `@{citekey}.md` from the Tier 1/2 template, or the stub
  template at Tier 0.
- **Existing note (merge):** keep the original filename. If the citekey changed (preprint
  `xxx2026` to published `yyy2027`), add the new citekey to `aliases:` so old `[[@old]]` links
  resolve. Update frontmatter: `version: published`, old DOI to `preprint_doi:`, `doi:` to the
  new DOI, old item key to `preprint_zotero_key:`, `zotero_key:` and `attachment_key:` to the
  new item, refresh `year`, `title`, `title_norm`, `summary`, `tier`, `pages_read`,
  `date_processed`. Regenerate the managed zone (frontmatter plus everything from `> [!Cite]`
  down to the `---` above `# My notes`). **Never touch the user zone.** Relate the two Zotero
  items: `zotero_add_item_relation(preprint_key, published_key, relation_type="owl:sameAs")`.

### 8b. Frontmatter discipline

Every note must carry `title`, `title_norm`, `summary`, `tier` and `pages_read`, as defined in
`templates.md` §1. A note without them cannot be found cheaply later.

### 8c. Research-idea notes: Tier 2 only

Generate the number of ideas the config asks for (default 2 to 4; 0 skips this step) using
the quality bar in `appraisal.md`. Before creating each idea note, de-duplicate with Grep on
the ideas folder: `^summary:.*<two or three distinctive words of the core question>`
(case-insensitive, `output_mode="content"`, `head_limit=10`). If a clear match exists, back
up that idea note, add this paper's citekey to its `seeds:` list and append one line under
`## Related findings`; do not rewrite its body. Otherwise create `idea-{slug}.md` from the
template. List `[[idea-...]]` backlinks in the lit note's `Ideas::` field.

### 8d. Zotero child note: Tier 1 and Tier 2

`zotero_create_note` on the item, title "Claude takeaways", using the HTML in
`templates.md` §5. It carries the tier, the contribution, the numbers with page anchors, and
the appraisal and reuse verdicts, so a claude.ai session that can see only Zotero can still
recall the paper.

### 8e. Mark done (last)

Only after every write above succeeded:
- `zotero_batch_update_tags` (`query=<exact title>`, `limit=1`): `add_tags=["claude/done", "claude/tier-N"]`.
  It cannot take an item key, so afterwards confirm with
  `zotero_get_item_metadata(ITEM_KEY, format="json")` that the tags landed on ITEM_KEY; if not,
  return `failed`.
- `zotero_manage_collections(item_keys=[ITEM_KEY], add_to=["C2ECZCB4"], remove_from=["8425VLJY"])`.

If anything failed earlier, do not tag; return `failed` with the cause. A partial note is
safe: the next run finds it through §3 and merges.

---

## 9. RESULT line (your only output)

One line, pipe-separated, no markdown, at most about 60 words:

`RESULT | status | ITEM_KEY | @citekey | tier | highlights N | flags N | ideas new N linked N | backups N | why: <tier reason> | warnings: <comma list or none> | <note path>`

`status` is one of `created`, `merged`, `stub`, `upgraded`, `skipped`, `failed`.

---

## 10. MODE=upgrade

Goal: raise an existing Tier 0 or Tier 1 note to Tier 2 without re-reading anything twice.

1. Locate the note by Grep on `^zotero_key: ITEM_KEY$` (or the citekey the user gave). Read
   only its first 60 lines (frontmatter plus the digest callouts). If there is no note, stop
   with `failed` and warning `no-existing-note`.
2. Skip triage. Target tier is 2. Read `appraisal.md`.
3. Read, with the page-range tool, only the Tier 2 pages not listed in `pages_read` (and the
   Tier 1 pages too if the note is a Tier 0 stub). Union the pages into `pages_read`.
4. Call `zotero_get_annotations` for the attachment to see existing highlights. Add new
   highlight sentences only, up to the Tier 2 budget minus those already present (§7).
5. Back up the note (§8a). Rewrite the managed zone: keep existing Key findings and add new
   ones, replace the "Not assessed" appraisal and reproducibility blocks with real ones,
   update `Numbers`, `Methods`, `Limitations`, set `tier: 2`, `status: read`, `summary`
   if improved, `pages_read`, and add `date_upgraded`. Never touch the user zone.
6. Seed ideas (§8c).
7. Update the Zotero child note: find it with `zotero_get_item_children`; if it exists, update
   it with `zotero_update_note`; if not, create it (§8d).
8. Tags: `zotero_batch_update_tags` with `remove_tags=["claude/deepen", "claude/tier-0",
   "claude/tier-1"]` and `add_tags=["claude/done", "claude/tier-2"]`. The collection move is
   needed only if the item is still in the inbox.
9. Return the RESULT line with status `upgraded`.
