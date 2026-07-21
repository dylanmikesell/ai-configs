---
name: ngi-pptx
description: >-
  Create NGI-branded PowerPoint presentations (.pptx) from the official corporate
  template. Use whenever the user wants to build, draft, generate, or edit a slide
  deck / presentation / PowerPoint / pptx for NGI — a cover/title slide, agenda,
  section divider, one- or two-column content, image slides, four-box layout,
  timeline, or an "On safe ground" closing slide. Guarantees the deck keeps NGI
  branding (custom 33x19 cm slide size, Aptos fonts, NGI red/blue palette, master
  graphics, footer/logo) by building on the template's own layouts instead of
  generic python-pptx output. Trigger with phrases like "make an NGI presentation",
  "build a slide deck", "company PowerPoint", "use our template", "NGI slides".
---

# NGI presentations — build on the corporate template

**The premise:** a deck only looks like NGI's if it is built *from* NGI's template.
The one reliable way to get branded output is to **open the template file and use
its own layouts** — never assemble slides from python-pptx defaults. Start from the
template and everything branded is inherited for free: the **custom 33 × 19 cm page**
(not standard 16:9 — a generic deck gets this wrong), the **Aptos** fonts, the **NGI
palette**, and the master graphics / footer / logo. Rebuilding those by hand from a
style spec is exactly the fragile path that produces off-brand slides — don't.

Owner: Dylan Mikesell (dylan.mikesell@ngi.no). Template theme: "Agenda old".

## What ships in this skill

- `assets/ngi-template.pptx` — the corporate template. **This is the branding
  source.** Do not recreate its fonts/colours/sizes in code.
- `scripts/pptx_helpers.py` — the helper API. Use it rather than raw python-pptx:
  `open_template`, `blank_deck`, `add_slide`, `set_title`, `set_text`,
  `set_bullets`, `add_picture`, `describe`.
- `references/layouts.md` — the layout map: every layout's **exact name** and
  placeholder indices. **Read it before choosing layouts.**
- `references/layout-gallery.pptx` — one slide per layout; open in PowerPoint to
  see each branded layout visually.

## Dependencies

- Requires **python-pptx** (`pip install python-pptx`). Already installed in the
  user's miniconda base env.
- `pptx_helpers.py` resolves the template path relative to this skill folder, so it
  works both in **Claude Code** (folder is junctioned into `~/.claude/skills`) and
  in the **desktop app / claude.ai** (the whole folder is uploaded).

## The golden rules

1. **Always start from the template.** `blank_deck()` returns the template with its
   5 example slides removed but *all* branding intact. Use `open_template()` instead
   if the user wants to edit the existing example slides.
2. **Add slides from named layouts.** Match by **exact name** (`references/layouts.md`).
   Names are Norwegian; layout `" Tidslinje2"` has a **leading space**.
3. **Fill placeholders, don't float text boxes.** Every layout's slots are
   placeholders with fixed indices (title = idx 0; others vary — see the map).
   Adding free-floating text boxes where a placeholder exists is what breaks
   branding and alignment.
4. **Don't set slide size, fonts, or theme colours** — they're inherited. Only set an
   explicit colour when deliberately deviating, using the palette hexes below.
5. **Never fabricate content.** If the user hasn't supplied the text, ask or leave a
   clear `[placeholder]` — don't invent facts, figures, or quotes on branded slides.

## Canonical workflow

```python
import sys
# In Claude Code the skill lives here; adjust if running elsewhere:
sys.path.insert(0, r"C:\Users\DMi\.claude\skills\ngi-pptx\scripts")
from pptx_helpers import blank_deck, add_slide, set_title, set_text, set_bullets, add_picture

prs = blank_deck()                                       # branded, empty

cover = add_slide(prs, "Forside #1")                     # cover
set_title(cover, "Ground investigation summary")
set_text(cover, 1, "Dylan Mikesell · NGI · 2026")        # subtitle = idx 1

agenda = add_slide(prs, "Agenda")
set_title(agenda, "Agenda")
set_bullets(agenda, 14, ["Background", "Method", "Results", "Recommendations"])

body = add_slide(prs, "Overskrift og to tekstbokser")    # two-column
set_title(body, "Findings")
set_bullets(body, 14, ["Settlement within tolerance", ("< 15 mm measured", 1)])
set_bullets(body, 15, ["No anomalies in CPTu", "Groundwater as expected"])

fig = add_slide(prs, "Overskrift, tekst og bilde")       # text + image
set_title(fig, "Site overview")
set_text(fig, 13, "Aerial extent of the investigated area.")
add_picture(fig, 11, r"C:\path\to\figure.png")

add_slide(prs, "Slutt_På sikker grunn")                  # closing slide (no title)

prs.save(r"C:\Users\DMi\Downloads\deck.pptx")
```

Use `describe(open_template())` any time to print every layout and its placeholder
indices live, if the map and reality ever disagree.

## Choosing a layout (intent → exact name)

| The user wants… | Layout name |
|---|---|
| Cover / title slide | `Forside #1` (or `Forside #2`) |
| Agenda / contents | `Agenda` |
| Section divider | `Seksjon` |
| One block of text | `Overskrift og tekstboks` |
| Two columns of text | `Overskrift og to tekstbokser` |
| Text + one image | `Overskrift, tekst og bilde` |
| Text + two images | `Overskrift, tekst og to bilder` |
| Generic title + bullets | `Tittel og innhold` |
| Full-bleed image + heading | `Overskrift og heldekkende bilde` |
| Three images + captions | `Overskrift og tre bilder` |
| Four boxes / quadrants | `Overskrift og fire bokser` |
| Timeline | `Tidslinje1` / `​ Tidslinje2` |
| Closing slide | `End_On safe ground` (EN) / `Slutt_På sikker grunn` (NO) |

Full placeholder indices for each are in `references/layouts.md`.

## Fonts & colours (inherited — reference only)

- Headings **Aptos SemiBold**, body **Aptos Display** — do not set these; they come
  from the layout.
- NGI palette, for the rare case you deliberately colour a run or shape:
  red `#AB2325`, blue `#00457C`, green `#115B14`, brown `#8E3B16`, gold `#F0B544`,
  near-black `#060606`, link blue `#40749C`. Otherwise leave theme defaults.

## Verify before handing over

python-pptx can't render, so it can't tell you the deck *looks* right — check it:

- Confirm the file opens **without PowerPoint's "repair" prompt**. The helpers avoid
  the orphaned-slide-part bug that causes it; if you drop `blank_deck()` and delete
  slides yourself, drop each slide's relationship too or you'll reintroduce it.
- To eyeball it headless, if LibreOffice is present:
  `soffice --headless --convert-to pdf deck.pptx`.
- Re-open with python-pptx and check the slide count and titles are what you intended.

## Enabling this skill

- **Claude Code:** automatic — this folder is junctioned into `~/.claude/skills` by
  the repo's `claude/install.ps1`.
- **Desktop app / claude.ai:** zip the `ngi-pptx` folder and upload it under
  **Settings → Capabilities → Skills**, then enable it; re-upload after edits. (That
  environment also ships a generic built-in `pptx` skill — this one supersedes it for
  NGI decks because it carries the template and layout map.)

## Maintenance

If the template is updated: replace `assets/ngi-template.pptx`, then
`python scripts/make_gallery.py` to refresh the gallery, and reconcile
`references/layouts.md` against `describe(open_template())` (names or placeholder
indices may have changed).
