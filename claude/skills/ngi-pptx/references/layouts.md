# NGI template — layout map

Extracted from `assets/ngi-template.pptx` (theme **"Agenda old"**, company **NGI**).
This is the authoritative list of layout names and placeholder indices. Match
layouts by **exact name** — names are Norwegian and a couple have quirks.

- **Slide size:** 11879263 × 6840538 EMU = **33 × 19 cm** (≈ 12.99″ × 7.48″).
  This is a *custom* size, not standard 16:9 — it is inherited automatically when
  you build on the template, and would be wrong if you started from a default deck.
- **Fonts (theme):** headings **Aptos SemiBold**, body **Aptos Display**.
- **Palette (theme):** red `#AB2325` (brand/accent1), blue `#00457C`, green
  `#115B14`, brown `#8E3B16`, gold `#F0B544`, near-black `#060606`, white
  `#FFFFFF`, dark-red heading `#AB2328`, link `#40749C`.

The title on every layout is a **centered-title (`ctrTitle`) placeholder at idx 0**
(not a plain `title`) — `set_title()` handles this. Fill other placeholders by the
idx listed below. Picture placeholders take `add_picture()`; text/body/content
placeholders take `set_text()` / `set_bullets()`.

| # | Layout name (exact) | English gloss | Use for | Placeholders (idx · kind) |
|---|---|---|---|---|
| 0 | `Forside #1` | Front page 1 | Cover / title slide | 0 title · 1 subtitle · 10 picture |
| 1 | `Forside #2` | Front page 2 | Alt cover / title slide | 0 title · 1 subtitle · 10 picture |
| 2 | `Agenda` | Agenda | Agenda / table of contents | 0 title · body 14,15,18,19,21,22,24,25,27,28 · picture 17,20,23,26,29 |
| 3 | `Seksjon` | Section | Section divider | 0 title · picture 10,17 |
| 4 | `Overskrift og tekstboks` | Heading + text box | One block of text | 0 title · 12 body |
| 5 | `Overskrift og to tekstbokser` | Heading + two text boxes | **Two-column** text | 0 title · 14 body (left) · 15 body (right) |
| 6 | `Overskrift, tekst og bilde` | Heading, text + image | Text beside one image | 0 title · 11 picture · 13 body |
| 7 | `Overskrift, tekst og to bilder` | Heading, text + two images | Text + two images | 0 title · 11 picture · 12 picture · 13 body |
| 8 | `Tittel og innhold` | Title + content | Generic title + content (bullets/object) | 0 title · 10 content/object |
| 9 | `Overskrift og heldekkende bilde` | Heading + full-cover image | Full-bleed image with heading | 0 title · 11 picture |
| 10 | `Overskrift og tre bilder` | Heading + three images | Three images with captions | 0 title · picture 11,16,18 · body 14,15,17 |
| 11 | `Overskrift og fire bokser` | Heading + four boxes | Four boxes / quadrants | 0 title · body 13,22,24,26,28,29,30,31 |
| 12 | `Tidslinje1` | Timeline 1 | Timeline (title only; build shapes onto it) | 0 title |
| 13 | `​ Tidslinje2` | Timeline 2 | Timeline variant | 0 title |
| 14 | `End_On safe ground` | Closing (English) | Closing slide, English tagline | 11 picture |
| 15 | `Slutt_På sikker grunn` | Closing (Norwegian) | Closing slide, Norwegian tagline | 11 picture |

> ⚠️ **Quirk:** layout 13 is `" Tidslinje2"` — it has a **leading space** in its
> name. Copy it verbatim (or look it up with `describe()`) or `get_layout()` will
> raise `KeyError`.

> Layouts 14 & 15 (closers) have **no title placeholder** — only a picture. Don't
> call `set_title()` on them.

To regenerate this data if the template changes, run in a session:

```python
from pptx_helpers import open_template, describe
describe(open_template())
```
