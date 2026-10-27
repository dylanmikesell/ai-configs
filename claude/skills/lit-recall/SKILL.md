---
name: lit-recall
description: >-
  Recall papers that Claude has already read for the user through the lit-inbox pipeline,
  cheaply and without re-reading PDFs. Searches the Zotero semantic index and the frontmatter
  of the Obsidian literature notes, reads only the short digest at the top of the best-matching
  notes, and reports each paper's tier (triaged, skimmed or fully read) so claims are never
  overstated. Use this skill whenever the user asks what they or Claude have read, what the
  literature says about a topic, which papers support a statement, for citations or numbers
  from previously processed papers, to write or revise an introduction, discussion or
  proposal section from the literature notes, to prepare a review that draws on read papers,
  or mentions "my lit notes", "papers we read", "from the inbox", "@citekey", or asks "what
  did we conclude about ...". Use it before answering any such question from general memory.
  Read-only: it never writes to the vault.
---

# lit-recall: retrieve what the lit-inbox pipeline already produced

Claude does not remember papers between sessions. The pipeline therefore stored each paper as
an Obsidian note whose first ~60 lines form a compact **digest**, and as a Zotero item with a
"Claude takeaways" child note. This skill retrieves from those artifacts in an order that
spends the fewest tokens, and states how deeply each paper was actually read.

This skill is read-only. Creating or deepening notes belongs to `lit-inbox`.

## Locations (must match the lit-inbox Section 0 table)

| What | Where |
|---|---|
| Lit notes | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Literature-notes\` (`@{citekey}.md`) |
| Idea notes | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Ideas\` (`idea-{slug}.md`) |
| Schema | `lit-inbox/references/templates.md` §1 (fields: `title`, `title_norm`, `summary`, `tier`, `pages_read`, `zotero_key`, `attachment_key`, `date_processed`) |

If a path has changed, update this table and the lit-inbox table together.

## What the digest is

For a lit note, the digest is the frontmatter plus the callouts down to `> [!Check]`
(Cite, Metadata, Synth with Contribution / Numbers / Methods / Relevance / Limitations /
Related / Ideas, Critical appraisal, Reproducibility). It sits at the top of the file, so
`Read` with `limit=60` returns it without the rest of the note. `Numbers::` carries each
key result with a page anchor `(p. n)`. The `tier` field says how much was read:

| tier | Meaning | What may be claimed from it |
|---|---|---|
| 0 | Triaged on abstract and outline only (`status: triaged`) | Existence, topic, one-line claim. Say "triaged, not read". |
| 1 | Skimmed: intro end, conclusions, captions (max 4 pages) | The paper's stated contribution and headline numbers. No appraisal, no methods detail. |
| 2 | Read in full (methods, results, discussion) | Everything in the digest, including appraisal and reuse verdict. |

Legacy v1 notes (`legacy: v1`) were read in full and count as tier 2, but may lack `Numbers`.

---

## Retrieval ladder (stop as soon as the question is answered)

**Step 1: pick the cheapest probe.**

- *Topic or concept question* ("what do we know about regolith segregation?"): start with
  Step 2 and Step 3 together.
- *Specific paper* (`@citekey`, a DOI, or a title): `Read` the note at
  `Literature-notes\@{citekey}.md` with `limit=60`. If the filename is unknown, Grep
  `^title_norm: <normalized title>$`, `^doi: <doi>$` or `^citekey: <key>$` (rule for
  `title_norm`: lowercase, delete everything except `a-z0-9`).
- *"What did I ask you to read?" / recent activity*: Grep `^date_processed: 2026-10` (adjust
  the prefix), `output_mode="content"`, to list matching files with their frontmatter lines;
  then Grep `^summary:` restricted to those files if one-line claims are wanted. Never open
  the notes for this.
- *Coverage by tier*: Grep `^tier: 0$`, `^tier: 1$`, `^tier: 2$` with `output_mode="count"`
  or `files_with_matches`.

**Step 2: Zotero semantic search** for concepts and synonyms the notes may not spell the same
way. Call `zotero_semantic_search(query, limit=8)`. If it errors or returns nothing, run
`zotero_get_search_database_status`; if the database is empty, say so and continue with Step 3
only (do not rebuild it from this skill). Each result carries an item key. Map keys to notes
with Grep `^zotero_key: <KEY>$` in the lit-notes folder. A result with no matching note is a
library paper that Claude has **not** processed: report it as "in the library, not read" and
never describe its content from memory.

**Step 3: frontmatter keyword search** (cheap index over every processed paper). Grep the
lit-notes folder, case-insensitive, `output_mode="content"`, `head_limit=30`:

```
pattern: ^(summary|tags|title):.*(regolith|segregat)
```

Each hit returns one line of frontmatter, so 30 hits cost a fraction of one digest. Combine
terms with `|`; tighten the pattern if there are more than 30 hits. Idea notes: same pattern
against `^summary:` in the ideas folder.

**Step 4: read digests, at most 8 per query.** Rank candidates from Steps 2 and 3 (tier 2
before tier 1, recent before old, direct summary match first) and `Read` each note with
`limit=60`. Read more than 8 only if the user asks. Never read an entire note unless the user
asks for the full text of one.

**Step 5: go deeper only when the digest cannot answer.** For example, the user needs the
experimental conditions behind a number, or a methods detail on a tier 1 paper. Use the
`attachment_key` from the frontmatter and the page anchor in `Numbers::` or `Key findings`
with the page-range tool (`zotero_read_pdf_pages`) to read just those pages, and answer from
them. This does not modify the note. If the user wants a lasting upgrade of a tier 0 or 1
paper, tell them to add the tag `claude/deepen` in Zotero and run lit-inbox, or to ask
"upgrade @citekey".

---

## Rules for using what is retrieved

1. **State the tier whenever it limits the claim.** A tier 1 paper supports "the authors
   report X"; it does not support "the study is sound" or "the method is reproducible".
   A tier 0 paper is mentioned only as triaged.
2. **Numbers come from `Numbers::` or `Key findings` with their page anchors**, or from the
   pages read in Step 5. Never restate a number from memory or round it differently.
3. **Separate the author's claim from the appraisal.** Quote the note's Critical appraisal
   as Claude's earlier assessment, with its date, not as established fact.
4. **Cite with the citekey** (`[[@citekey]]` in Obsidian drafts, or the plain citekey for
   Better BibTeX workflows) so each statement stays traceable.
5. **Say what was not found.** If no processed note matches, say so and offer to search the
   Zotero library or process the paper through lit-inbox; do not fall back to unverified
   general knowledge presented as if it came from the notes.
6. **Idea notes are the user's.** When asked for ideas, list matching `idea-*.md` summaries
   and their `seeds`; do not rewrite or extend them.
7. **No manuscripts under review.** They are never in this vault; do not look for them here.

## Task patterns

- **Writing an introduction or discussion section.** Run Steps 2 to 4 for each distinct
  sub-claim, collect at most 8 digests per sub-claim, then draft with citekeys and page-anchored
  numbers. Flag every statement supported only by a tier 0 or tier 1 paper.
- **Preparing a review or critique.** Prefer tier 2 papers and quote their appraisal flags and
  reuse verdicts; for any tier 1 paper that matters to the argument, offer the upgrade.
- **Finding gaps or ideas.** Combine Step 3 over `Limitations::` (Grep
  `^> \*\*Limitations\*\*::.*<topic>`) with the idea notes' `summary` lines.
- **"What have we read on X?"** Return a short list: citekey, year, tier, one-line summary
  from frontmatter. Offer to open digests for the ones that matter.

## When the vault is not reachable

In a claude.ai session with only the Zotero connector, the Obsidian notes cannot be read.
Fall back to `zotero_semantic_search`, then `zotero_get_item_children` and `zotero_get_notes`
on the best hits to read the "Claude takeaways" child note (it states tier, contribution,
numbers with page anchors, appraisal and reuse verdicts). Make clear to the user that the
answer rests on the child note only.
