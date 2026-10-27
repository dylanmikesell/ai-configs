---
name: lit-inbox
description: >-
  Process papers dropped into the Zotero "_Claude-Inbox" collection with a tiered,
  token-efficient pipeline. Each paper is handled by its own subagent: triage from
  metadata/abstract/outline (Tier 0), a targeted read of intro/conclusions (Tier 1), or a
  full methods-and-results read with critical appraisal, reproducibility check and
  research-idea seeding (Tier 2). Writes Zotero highlights, an Obsidian literature note with
  recall-ready frontmatter (tier, summary, page anchors), and a Zotero child note, then
  refreshes the Zotero semantic index. Also supports upgrading a Tier 0/1 paper to Tier 2
  (tag `claude/deepen`, or "upgrade @citekey") and a one-time migration of v1 notes. Use this
  skill for "/lit-inbox", "process my inbox", "process my papers", "read my new papers",
  "run lit-inbox", "upgrade @citekey", "deepen this paper", or "migrate my lit notes".
  Never use it for manuscripts under peer review.
---

# lit-inbox v2: Zotero to Obsidian literature pipeline

This skill converts "I dropped a paper in my Zotero inbox" into a highlighted PDF in Zotero
and a linkable, recall-ready literature note in Obsidian, while spending tokens in proportion
to how relevant each paper is. The companion skill `lit-recall` retrieves what this skill
wrote. Both skills depend on the frontmatter schema in `references/templates.md`; change the
schema in one place only and update both.

Owner: Dylan Mikesell (dylan.mikesell@ngi.no). Manual trigger; the logic is written to run
identically if a scheduled job is added later.

## How the files are organised

| File | Loaded by | When |
|---|---|---|
| `SKILL.md` (this file) | main session | always |
| `references/per-paper.md` | each subagent | always, first |
| `references/templates.md` | each subagent | when writing notes; migrate subagents read its §1 |
| `references/appraisal.md` | subagent | Tier 2 only (and upgrades to Tier 2) |

The main session never reads the three reference files. This keeps the orchestrating
context small, and keeps appraisal instructions out of Tier 0 and Tier 1 runs.

---

## 0. Configuration (single source of truth)

All machine-specific values live in this table. If a path or key changes, edit only here.

| Setting | Value |
|---|---|
| Zotero library | My Library (libraryID = 1), the default active library |
| Inbox collection | `_Claude-Inbox`, key `8425VLJY` |
| Done/read collection | `_Claude-Read`, key `C2ECZCB4` |
| Processed marker tag | `claude/done` |
| Tier tags | `claude/tier-0`, `claude/tier-1`, `claude/tier-2` (exactly one per processed item) |
| Upgrade request tag | `claude/deepen` (added by the user to an item in `_Claude-Read`) |
| Skill folder | `C:\Users\DMi\.claude\skills\lit-inbox\` (edit if installed elsewhere) |
| Assessment config (read by every subagent, every run) | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Extras\Claude\literature-assessment.md` |
| Obsidian lit-notes folder | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Literature-notes\` |
| Note filename | `@{citekey}.md` |
| Obsidian ideas folder | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Ideas\` |
| Idea note filename | `idea-{slug}.md` |
| Backup folder | `C:\Users\DMi\OneDrive - NGI\Documents\NGI.Vault\Extras\Claude\backups\` |
| Zotero child note | ON for Tier 1 and Tier 2 (title "Claude takeaways") |
| Highlight cap, Tier 1 | 6 sentences |
| Highlight cap, Tier 2 | the config's budget, never more than 12 sentences |
| Papers per run | 10 (oldest first; the rest wait for the next run) |

### What each tier does

| | Tier 0 (triage) | Tier 1 (skim) | Tier 2 (full) |
|---|---|---|---|
| Reads | metadata, abstract, PDF outline only | intro end, conclusions, captions on those pages (max 4 pages) | Tier 1 pages plus methods, results, discussion, availability statements |
| Obsidian note | stub (`status: triaged`) | full template, appraisal and reproducibility marked "not assessed" | full template |
| Highlights | none | up to 6 sentences | up to the budget (max 12) |
| Appraisal and reproducibility | no | no | yes |
| Idea notes | no | no | yes (count from config) |
| Zotero child note | no | yes | yes |

### The assessment config

Each subagent reads the config fresh at the start of its paper; never rely on remembered
content. The config governs relevance criteria and tier thresholds (section "Relevance &
tiering"), highlight budget and colors, appraisal depth, and idea count (0 turns idea
seeding off). The values in this file are defaults used only when the config is silent.

---

## 1. Modes

**Inbox run (default).** Triggered by `/lit-inbox` or "process my inbox". Section 2.

**Upgrade.** Triggered by "upgrade @citekey" / "deepen @citekey", or automatically for every
item in `_Claude-Read` that carries the tag `claude/deepen`. Section 3.

**Migrate.** Triggered by "migrate my lit notes". One-time pass that adds the v2 frontmatter
fields to notes written by v1. Section 4.

---

## 2. Inbox run (main session)

The main session only orchestrates. It does not read PDFs, notes or the config.

1. **Check the config exists.** Use Glob on the assessment config path. If it is missing,
   stop and tell the user; do not guess at criteria.
2. **List the work.** `zotero_get_collection_items` (`collection_key="8425VLJY"`, `detail="full"`, `limit=100`). If the
   listing does not include tags, fetch tags per item with `zotero_get_item_metadata`
   (`format="json"`). Skip attachments and skip any item tagged `claude/done`. If nothing is
   left, report "Inbox clear" and go to step 5 only if an upgrade is pending (Section 3).
3. **Order and cap.** Oldest first. Keep the first 10 (Section 0). Mention the remainder
   in the report.
4. **One subagent per paper, strictly sequential.** Use the Agent (subagent) tool with a
   general-purpose agent. Wait for each result before launching the next. Do not run
   subagents in parallel: a preprint and its published version may both be in the inbox,
   and parallel runs would race on duplicate detection and on idea de-duplication.
   Prompt template (fill the braces; do not add anything else):

   > You are processing one paper for the lit-inbox skill. First read
   > `{SKILL_DIR}\references\per-paper.md` and follow it exactly. ITEM_KEY={key}.
   > MODE=inbox. Assessment config: `{CONFIG_PATH}`. Never delete files. When finished,
   > reply with ONLY the single RESULT line defined in per-paper.md §9, with no other prose.

   Record each RESULT line. If a subagent returns anything else, or reports `failed`, note
   it and continue with the next paper; never retry within the same run.
5. **Refresh the semantic index** (once, after the last paper, only if at least one paper
   was created, merged, stubbed or upgraded):
   - Call `zotero_get_search_database_status`. If it reports the semantic extras are not
     installed, skip the update and say so in the report.
   - If the database is empty or has never been built, tell the user that a first full
     build can take minutes and run `zotero_update_search_database()` once anyway.
   - Otherwise run `zotero_update_search_database()` (incremental; only new or changed items
     are embedded, so it is cheap). Never use `force_rebuild` unless the user asks.
6. **Report** (Section 5).

---

## 3. Upgrade mode

1. Collect targets: items named by the user, plus `_Claude-Read` items tagged
   `claude/deepen` (use `zotero_search_by_tag`; load its schema with tool_search if needed).
2. For each target, launch one subagent exactly as in Section 2 step 4, but with
   `MODE=upgrade`. Sequential, one at a time.
3. Run the semantic index refresh (Section 2, step 5) once at the end.
4. Report as in Section 5.

An upgrade never re-reads pages already recorded in the note's `pages_read` field, never
re-creates highlights that already exist, and never touches the user zone of the note.

---

## 4. Migrate mode (one time, for v1 notes)

v1 notes lack `title_norm`, `summary`, `tier` and `pages_read`, so de-duplication and recall
cannot find them cheaply. This mode adds those fields to existing notes without touching
anything else.

1. Run `rg -L --files-without-match -g "*.md" "^title_norm:" "<lit-notes folder>"` through
   Bash (the Grep tool has no files-without-match mode). Report the count before proceeding.
2. Split the list into batches of 15. For each batch launch one subagent (sequential):

   > You are migrating v1 literature notes for the lit-inbox skill. Read
   > `{SKILL_DIR}\references\templates.md` §1 (field rules) only. For each note path below:
   > Read only its first 45 lines; compute `title` (from the `**Title**::` field),
   > `title_norm`, and `summary` (from `**Contribution**::`, at most 300 characters, ending at the last whole word before the limit);
   > set `tier: 2`, `pages_read: "all (v1)"`, and `legacy: v1`. Fill only fields that are
   > missing or empty; never overwrite an existing value. Back up the note first
   > (copy to the backup folder as `{filename}.bak-YYYYMMDD`, never overwrite an existing
   > backup), then insert the new fields into the frontmatter and change nothing else.
   > Skip any note whose first 45 lines do not contain a recognisable `**Title**::` line,
   > and any note with `status: unread` (never read, so no tier), and list them. Never delete
   > files. Reply with one line: migrated N, skipped N, paths of skipped notes. Notes: {paths}

3. Report totals and the skipped notes. v1 notes were read in full, so tier 2 is the correct
   assumption; their Synth callouts will lack a `Numbers` line, which is acceptable.
4. **Gap-fill identity fields** (for notes missing `citekey`, `zotero_key`, `attachment_key`
   or `date_processed`; list them with `rg` on each `^field:\s*\S` pattern). Fill only what is
   missing, after a backup:
   - `citekey`: the filename without the leading `@` and the `.md`.
   - `date_processed`: the file's creation date as `YYYY-MM-DD` (PowerShell
     `(Get-Item -LiteralPath <path>).CreationTime`).
   - `zotero_key`: find the item with `zotero_search_by_citation_key`, else
     `zotero_search_items` on the title. Accept only if title and year agree.
   - `attachment_key`: the PDF child from `zotero_get_item_children`.
   If there is no confident match or no PDF, leave the field blank and list the note for the
   user. Never guess a key.

---

## 5. Report

Compile from the RESULT lines. Keep it compact:

- Papers processed, split by action (created, merged, stubbed, upgraded) and by tier.
- **Triage decisions with the one-line reason for every Tier 0 and Tier 1 paper**, so that a
  wrongly demoted paper can be rescued by adding the tag `claude/deepen`.
- Per Tier 2 paper: highlights added, critical-appraisal flags raised, idea notes seeded
  (new vs linked to existing).
- Backups created (count and folder).
- **"Missing PDF (left in inbox, not processed)"** list, plus any other skips (no text layer,
  failed subagent, failed highlight).
- Papers left over because of the per-run cap.
- Whether the semantic index was refreshed.
- File paths of lit notes and idea notes.

---

## 6. Guardrails

- **Published literature only.** Manuscripts under peer review must not enter this pipeline
  (no indexing, no idea seeding, no shared vault writes). Refuse and point to a separate
  review workflow.
- **Never delete anything**: no files, no notes, no folders, no `rm`, no recursive deletes.
  The only permitted removals are Zotero tags and collection membership as written in
  `per-paper.md`, and a mistaken highlight annotation (which goes to the Zotero trash).
- **Back up before editing any existing file** (note merges, upgrades, idea-note appends,
  migration): copy to the backup folder as `{filename}.bak-YYYYMMDD`, never overwriting an
  existing backup, and count it in the report. New files need no backup.
- **Stay in scope**: only the vault folders and backup folder in Section 0, the skill
  folder (read only), and the Zotero MCP. Touch no other path.
- Idempotent: the `claude/done` tag prevents reprocessing, and the title-norm / DOI lookup
  prevents duplicate notes. When unsure whether two items are the same paper, prefer merging
  and say so.
- **A PDF is required.** No PDF attachment: skip, leave in the inbox, no tag, no note.
- Never invent findings or rigor flags. "No major concerns" and "not assessed" are valid,
  honest results.
- Never edit below `# My notes` in a lit note or below `# Develop` in an idea note.
- Each subagent returns a single RESULT line. Long prose from a subagent defeats the
  purpose of delegating.

---

## 7. Permissions (hands-off runs)

Prompts are enforced by the Claude Code harness, not by this text. Configure once in
`~/.claude/settings.local.json` (`permissions.allow`):

- `mcp__zotero` for the whole Zotero MCP server.
- `Read`, `Write` and `Edit` on `C:/Users/DMi/OneDrive - NGI/Documents/NGI.Vault/**`.
- A narrowly scoped copy rule for backups (`Bash(cp -n:*)`); without it, subagents
  fall back to reading and rewriting each note to back it up, which costs tokens.
- `Read` on the skill folder.

Subagents are expected to inherit these rules. If a permission prompt appears inside a
subagent, add the matching rule rather than editing this file.
