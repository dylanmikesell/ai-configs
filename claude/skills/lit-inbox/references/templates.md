# templates.md: frontmatter rules and note templates

Contents: §1 field rules · §2 lit note (Tier 1 and 2) · §3 stub (Tier 0) · §4 idea note ·
§5 Zotero child note. The `lit-recall` skill depends on §1 and on the layout of §2: the
first ~60 lines of a lit note are the "digest" that recall reads. Do not reorder the
callouts.

---

## 1. Field rules (the schema both skills depend on)

| Field | Rule |
|---|---|
| `title` | Original title, in double quotes, with any inner double quote escaped as `\"`. |
| `title_norm` | Lowercase the title, then delete every character except `a-z` and `0-9` (no spaces). Same value for a preprint and its published version, so it is the de-duplication key. Example: "Lunar Regolith: A Review" becomes `lunarregolithareview`. Apply the rule mechanically, never by eye. |
| `summary` | The paper's central claim in at most 300 characters, ending at the last whole word before the limit (never mid-word), one line, no double quotes. Searchable by Grep. |
| `tier` | `0`, `1` or `2`. Never lower an existing value. |
| `status` | `triaged` for Tier 0; `read` for Tier 1 and 2. |
| `pages_read` | Quoted string of PDF page ranges actually read, for example `"1-2, 9-11"`. Tier 0: `"none"`. Legacy notes: `"all (v1)"`. |
| `version` | `preprint` or `published`. |
| `date_processed` | `YYYY-MM-DD` of the run that created or last merged the note. `date_upgraded` is added only by an upgrade. |
| `zotero_key`, `attachment_key` | The current item and its PDF. After a merge, the previous ones move to `preprint_zotero_key`. |
| `doi`, `preprint_doi` | Current DOI; the old DOI after a merge. |
| `legacy` | `v1` only on notes touched by the migrate pass. |

Keep the vault's dataview inline-field style (`Field:: value`) inside the callouts and keep
`category: literaturenote` so existing dataview queries keep working.

---

## 2. Lit note (Tier 1 and Tier 2)

Keep the exact `# My notes` marker line so merges can find the user zone. Fill every `{{...}}`.

```markdown
---
category: literaturenote
tags: [{{topic-tags, kebab-case}}]
citekey: {{citekey}}
aliases: ["@{{citekey}}"]
title: "{{title}}"
title_norm: {{title_norm}}
summary: "{{claim, at most 300 characters, whole words}}"
zotero_key: {{ITEM_KEY}}
attachment_key: {{PDF_KEY}}
doi: {{doi}}
year: {{year}}
version: {{preprint|published}}
status: read
tier: {{1|2}}
pages_read: "{{page ranges}}"
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

> [!Synth] Claude assessment ({{version}} · tier {{tier}} · assessed {{YYYY-MM-DD}})
> **Contribution**:: {{one sentence}}
> **Numbers**:: {{key results with units and uncertainties, each with a page anchor, separated by semicolons}}
> **Methods**:: {{approach / data / study area}}
> **Relevance**:: {{ties to the user's research}}
> **Limitations**:: {{weaknesses / open questions}}
> **Related**:: {{[[@citekey]], ... or "—"}}
> **Ideas**:: {{[[idea-slug]], ... (Tier 2) or "—"}}

> [!Warning] Critical appraisal
> {{Tier 2: 2 to 5 rigor/bias/stats/claim-vs-data flags, or "No major concerns — sound within its scope."}}
> {{Tier 1: "Not assessed (Tier 1 read: intro end, conclusions, captions). Add the tag claude/deepen in Zotero to upgrade."}}

> [!Check] Reproducibility
> **Data**:: {{repository / DOI / on request / not available; Tier 1: statement if seen, else "not assessed"}}
> **Code**:: {{shared where / not shared; Tier 1: statement if seen, else "not assessed"}}
> **Reuse**:: {{Tier 2: one-line could-I-reuse-this verdict; Tier 1: "not assessed"}}

## Key findings
- {{finding with numbers}} (p. {{n}})

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

On a merge or upgrade, rewrite only the frontmatter and everything from `> [!Cite]` down to
the `---` above `# My notes`. Leave the user zone byte-for-byte unchanged.

---

## 3. Stub (Tier 0)

Short on purpose: it exists so the paper is never triaged twice and so recall can say "triaged,
not read".

```markdown
---
category: literaturenote
tags: [{{topic-tags}}]
citekey: {{citekey}}
aliases: ["@{{citekey}}"]
title: "{{title}}"
title_norm: {{title_norm}}
summary: "{{one-line claim from the abstract, at most 300 characters, whole words}}"
zotero_key: {{ITEM_KEY}}
attachment_key: {{PDF_KEY}}
doi: {{doi}}
year: {{year}}
version: {{preprint|published}}
status: triaged
tier: 0
pages_read: "none"
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

> [!Synth] Triage only (tier 0 · {{YYYY-MM-DD}})
> **Contribution**:: {{one sentence from the abstract}}
> **Relevance**:: Triage score 0: {{reason, at most 15 words}}. Not read beyond abstract and outline.

> [!Abstract]
> {{abstract}}

> [!LINK] PDF
> [Open in Zotero](zotero://select/library/items/{{ITEM_KEY}})

---
# My notes
<!-- USER ZONE — Claude never edits below this line. -->
```

---

## 4. Idea note (Tier 2 papers only)

One note per idea, in the ideas folder. The title is the idea phrased as a question.
Everything below `# Develop` belongs to the user; Claude only ever appends a `seeds:` entry
and a `## Related findings` line (after backing the note up).

```markdown
---
type: research-idea
status: seed
summary: {{idea as a one-line question; this is what the Ideas MOC table shows}}
seeds: ["[[@{{citekey}}]]"]
created: {{YYYY-MM-DD}}
tags: [research-idea, {{topic-tags}}]
---
tags:: [[💡 Ideas MOC]]

# {{idea as a one-line question}}

**Extends**:: [[@{{citekey}}]]
**Why**:: {{what in the paper makes this plausible: the mechanistic hook}}
**Prediction**:: {{concrete, falsifiable: what we would expect to see if the idea holds}}
**Test**:: {{how Dylan could actually test it: data, instrument, site, method}}
**Ties to my work**:: {{link to the NGI/geophysics angle, other [[@citekey]] or [[notes]]}}

## Related findings
- [[@{{citekey}}]] ({{YYYY}}) — {{one line on how this paper feeds the idea}}

# Develop
<!-- USER ZONE — Claude never edits below this line. Grow the idea here. -->
```

Fields the Ideas MOC table depends on, always filled: `summary`, `status` (one of `seed`,
`exploring`, `active`, `parked`, `done`; start at `seed`), `seeds` (YAML list of
`"[[@citekey]]"` strings, one added per merge), `created`.

---

## 5. Zotero child note (Tier 1 and Tier 2)

Title "Claude takeaways". Concise HTML:

```html
<p><b>Claude takeaways</b> — tier {{N}} · {{YYYY-MM-DD}} · Obsidian: [[@{{citekey}}]]</p>
<p><b>Contribution:</b> {{one sentence}}</p>
<ul>
  <li>{{result with numbers}} (p. {{n}})</li>
  <li>{{3 to 5 items in total}}</li>
</ul>
<p><b>Appraisal:</b> {{Tier 2 verdict in one line, or "not assessed (tier 1)"}}
<b>Reuse:</b> {{one-line verdict or "not assessed"}}</p>
```
