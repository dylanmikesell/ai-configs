r"""Sanity-check a generated .pptx: no duplicate parts + it re-opens cleanly.

This is the automated version of "does it open in PowerPoint without the repair
prompt?". Duplicate zip parts are the classic corruption that triggers that prompt
(see blank_deck() in pptx_helpers.py). Run it on any deck you produce, and after a
template rebuild.

    python scripts/check_integrity.py path\to\deck.pptx

Exits non-zero and lists the problems if any are found.
"""
import collections
import sys
import zipfile

from pptx import Presentation


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python check_integrity.py <deck.pptx>")
    path = sys.argv[1]

    names = zipfile.ZipFile(path).namelist()
    dupes = [n for n, c in collections.Counter(names).items() if c > 1]

    problems = []
    if dupes:
        problems.append(f"duplicate parts (will trigger PowerPoint repair): {dupes}")

    try:
        prs = Presentation(path)
        n_slides = len(list(prs.slides))
        w, h = prs.slide_width, prs.slide_height
        print(f"opened OK: {n_slides} slides, size {w}x{h} EMU, {len(names)} parts")
    except Exception as e:  # noqa: BLE001 - report any open failure
        problems.append(f"python-pptx could not open the file: {e!r}")

    if problems:
        print("INTEGRITY PROBLEMS:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("OK: no duplicate parts, opens cleanly.")


if __name__ == "__main__":
    main()
