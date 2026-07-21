r"""Build the shareable public zip of the ngi-pptx skill — reproducibly.

Takes the private skill in this repo and produces `ngi-pptx-skill_pub.zip`:
  * strips internal references (personal email, machine paths, the Obsidian AI MOC
    step, the repo name, the miniconda note),
  * sets the author to the maintainer and records the version + last-updated date
    (both read from SKILL.md, the single source of truth) in the gallery .pptx,
  * ABORTS if any forbidden term survives the sanitisation (so it can never silently
    leak internal info),
  * excludes itself and __pycache__ from the output.

    python scripts/make_public_zip.py                 # -> ~/Downloads/ngi-pptx-skill_pub.zip
    python scripts/make_public_zip.py path\to\out.zip # -> custom output path

The template .pptx is deliberately left authorless: python-pptx makes decks inherit
their template's author, so stamping a name there would mis-attribute every deck built
from it. The author rides on SKILL.md and the gallery instead.
"""
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from pptx import Presentation

AUTHOR = "Dylan Mikesell"
SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_NAME = SKILL_DIR.name  # "ngi-pptx"
DEFAULT_OUT = Path.home() / "Downloads" / "ngi-pptx-skill_pub.zip"

# Substrings that must NOT appear in any shipped text file (checked case-insensitively).
# The maintainer's *name* is allowed (it is the author); the email and internal
# locations are not.
FORBIDDEN = [
    "dylan.mikesell@", "onedrive", "ngi.vault", "ai moc", "obsidian",
    "miniconda", "ai-configs", r"c:\users", "extras/moc",
]


def require_replace(text, old, new, label):
    """str.replace that fails loudly if the expected source text is missing."""
    if old not in text:
        raise SystemExit(
            f"[make_public_zip] sanitisation rule '{label}' did not match — the source "
            f"wording changed. Update this rule before shipping.")
    return text.replace(old, new)


def sanitise_skill(text, version, date):
    text = require_replace(
        text,
        "Maintainer: Dylan Mikesell (dylan.mikesell@ngi.no)",
        f"Author: {AUTHOR}",
        "provenance line")
    text = require_replace(
        text,
        "- Requires **python-pptx** (`pip install python-pptx`). Already installed in the\n"
        "  user's miniconda base env.",
        "- Requires **python-pptx**: `pip install python-pptx` into whatever Python "
        "environment\n  Claude runs in.",
        "dependencies note")
    text = require_replace(
        text,
        "import sys\n"
        "# In Claude Code the skill lives here; adjust if running elsewhere:\n"
        'sys.path.insert(0, r"C:\\Users\\DMi\\.claude\\skills\\ngi-pptx\\scripts")',
        "import sys, pathlib\n"
        "# Point this at this skill's scripts/ folder. In Claude Code it lives under ~/.claude:\n"
        'sys.path.insert(0, str(pathlib.Path.home() / ".claude" / "skills" / "ngi-pptx" / "scripts"))',
        "workflow import")
    text = require_replace(
        text,
        'set_text(cover, 1, "Dylan Mikesell · NGI · 2026")',
        'set_text(cover, 1, "Your name · NGI · 2026")',
        "example subtitle")
    text = require_replace(
        text,
        'prs.save(r"C:\\Users\\DMi\\Downloads\\deck.pptx")',
        'prs.save("deck.pptx")',
        "example save path")
    return text


def sanitise_rebuild(text):
    text = require_replace(
        text,
        "**Commit & push** to `ai-configs`",
        "**Commit & push** to wherever you keep this skill under version control",
        "rebuild commit target")
    # Drop the whole "Update the AI MOC" step (step 9). Regex dodges the exact emoji/dashes.
    new = re.sub(
        r"\n\n9\. \*\*Update the AI MOC\*\*.*?document new AI capabilities.*?rule\.",
        "", text, flags=re.S)
    if new == text:
        raise SystemExit("[make_public_zip] could not find the AI MOC step to remove.")
    return new


def parse_version_and_date(skill_text):
    m = re.search(r"\*\*Version\s+(\d+\.\d+\.\d+)\*\*.*?Last updated:\s*(\d{4}-\d{2}-\d{2})",
                  skill_text, flags=re.S)
    if not m:
        raise SystemExit("[make_public_zip] could not parse version/date from SKILL.md.")
    return m.group(1), m.group(2)


def leak_check(root):
    hits = []
    for path in list(root.rglob("*.md")) + list(root.rglob("*.py")):
        low = path.read_text(encoding="utf-8", errors="replace").lower()
        for term in FORBIDDEN:
            if term.lower() in low:
                hits.append((path.relative_to(root), term))
    if hits:
        lines = "\n".join(f"  {p} contains {t!r}" for p, t in hits)
        raise SystemExit(f"[make_public_zip] ABORT — internal terms leaked:\n{lines}")


def stamp_gallery(path, version, date):
    prs = Presentation(str(path))
    cp = prs.core_properties
    cp.author = AUTHOR
    cp.last_modified_by = AUTHOR
    cp.title = "NGI template - layout gallery"
    cp.keywords = "NGI, template, layout gallery, ngi-pptx"
    cp.category = "Template reference"
    cp.version = version
    cp.revision = 1
    stamp = datetime.strptime(date, "%Y-%m-%d")
    cp.created = stamp
    cp.modified = stamp
    prs.save(str(path))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    version, date = parse_version_and_date((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))

    tmp = Path(tempfile.mkdtemp(prefix="ngi-pptx-pub-"))
    staged = tmp / SKILL_NAME
    shutil.copytree(
        SKILL_DIR, staged,
        ignore=shutil.ignore_patterns("__pycache__", "make_public_zip.py"))

    skill_md = staged / "SKILL.md"
    skill_md.write_text(
        sanitise_skill(skill_md.read_text(encoding="utf-8"), version, date),
        encoding="utf-8")
    rebuild_md = staged / "REBUILD.md"
    rebuild_md.write_text(
        sanitise_rebuild(rebuild_md.read_text(encoding="utf-8")),
        encoding="utf-8")

    leak_check(staged)
    stamp_gallery(staged / "references" / "layout-gallery.pptx", version, date)

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    files = sorted(p for p in staged.rglob("*") if p.is_file())
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(tmp).as_posix())
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"Built {out}")
    print(f"  version {version} · author {AUTHOR} · last updated {date}")
    print(f"  {len(files)} files, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
