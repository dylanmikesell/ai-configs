# Claude configs

Configuration for [Claude Code](https://claude.com/claude-code), kept under version
control here and linked into `~/.claude` so edits made while working flow straight back
into git.

## Structure

- **skills/** — user-level Claude Code skills (available in every session).
  - **lit-inbox/** — Zotero → Obsidian literature pipeline. Drop a paper into the Zotero
    `_Claude-Inbox` collection, then tell Claude "process my inbox": it reads and
    assesses the PDF, highlights it inside Zotero, and writes/merges an Obsidian
    literature note. See `skills/lit-inbox/SKILL.md`.
  - **spec-first-phoenix/** — spec-first ("Phoenix") development methodology. Structure a
    project around durable specs + language-agnostic test contracts so implementations are
    regenerable and pass the deletion test (delete the code, regenerate it from spec +
    contract alone). Distils Chad Fowler, Drew Breunig, and Bergel in `references/`. See
    `skills/spec-first-phoenix/SKILL.md`.

## Plugins

Marketplace plugins (installed via Claude Code, versioned upstream — not stored in this
repo) are catalogued in [`plugins.md`](plugins.md), with reinstall commands. Currently:
`claude-scientific-writer` (research writing / literature / document production).

## Install (Windows)

```powershell
# from the repo root
pwsh -File claude/install.ps1
```

This creates a directory **junction** `~/.claude/skills` → `claude/skills` (junctions
work without admin rights and write through, so refining a skill edits the repo files).

## Install (Linux/Mac)

```bash
# from the repo root
bash claude/install.sh
```

This creates a **symlink** `~/.claude/skills` → `claude/skills` (write-through, same as
the Windows junction).

## Notes

- The `lit-inbox` skill references machine-specific paths (the Obsidian vault) and Zotero
  collection keys in its Section 0 config block — update those if they change.
- The user-editable assessment config for `lit-inbox` lives in the Obsidian vault
  (`Extras/Claude/literature-assessment.md`), not in this repo, so it can be edited in
  Obsidian alongside the notes it governs.
