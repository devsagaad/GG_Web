#!/usr/bin/env python3
"""
One-time migration: lift the inline stylesheet out of index.html into
assets/glint.css, so the reference page and the Webflow build share one copy.

Same reasoning as the hero bundle: two consumers, one source, no drift.
The cost is one render-blocking request on the static page in exchange for the
stylesheet being addressable from Webflow at all.

    python3 tools/extract-css.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "grid-and-glint-website"
SRC = SITE / "index.html"
OUT = SITE / "assets" / "glint.css"

STYLE_OPEN, STYLE_CLOSE = 71, 434  # 1-based, inclusive of the tags


def fail(m):
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


lines = SRC.read_text().split("\n")

if lines[STYLE_OPEN - 1].strip() != "<style>":
    fail(f"line {STYLE_OPEN} is not <style>")
if lines[STYLE_CLOSE - 1].strip() != "</style>":
    fail(f"line {STYLE_CLOSE} is not </style>")

css = "\n".join(lines[STYLE_OPEN:STYLE_CLOSE - 1])

for marker in ("--mint:", ".glint-stage" if False else ".stage {", "@media (prefers-color-scheme: light)"):
    if marker not in css:
        fail(f"extracted CSS is missing {marker!r}; boundaries have shifted")

header = """/* Grid and Glint - the studio's stylesheet.
 *
 * Lifted out of index.html so the reference page and the Webflow build share
 * one copy. Pair it with the Google Fonts link:
 *
 *   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400&family=Big+Shoulders+Display:wght@700;900&display=swap">
 *
 * Thunder, the brand display face, is not licensed for web use yet; headings
 * fall back to Big Shoulders Display until its font files are added.
 */

"""

OUT.write_text(header + css + "\n")

replacement = '<link rel="stylesheet" href="assets/glint.css">'
lines = lines[: STYLE_OPEN - 1] + [replacement] + lines[STYLE_CLOSE:]
text = "\n".join(lines)

if "<style>" in text:
    fail("an inline <style> block still remains in index.html")
if text.count(replacement) != 1:
    fail("the stylesheet link was not written exactly once")

SRC.write_text(text)
print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size:,} bytes)")
print(f"index.html is now {len(text):,} bytes ({len(lines)} lines)")
