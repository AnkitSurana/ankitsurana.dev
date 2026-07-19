#!/usr/bin/env python3
"""
Generate cover.svg and header.svg for every post and project.

    python3 tools/make-covers.py            # regenerate everything
    python3 tools/make-covers.py my-slug    # just one item

Reads posts/posts.json and projects/projects.json, fills the two templates in
this folder, and writes the result into each item's own folder. Title, tags and
date come from the manifest, so changing a date there updates the artwork on the
next run. Nothing is hand-edited per item.

An item is skipped if its manifest entry sets "cover": "" (it then falls back to
the generated canvas mesh in the browser).
"""

import hashlib
import json
import os
import sys
import time
from xml.sax.saxutils import escape


def attr(text):
    """Escape for use inside a double-quoted XML attribute.

    Not quoteattr(): that switches to single-quote delimiters when the value
    contains a double quote, so stripping its outer characters leaves an
    unescaped quote behind and the file stops being well-formed. Titles here
    really do contain quotes.
    """
    return escape(text, {'"': "&quot;"})

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

COVER_W = 1070      # 1200 canvas, 70 left margin, 60 right
HEADER_W = 1432     # 1600 canvas, 88 left margin, 80 right

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def pretty_date(iso):
    """2026-07-18 -> 18 July 2026. Anything unparseable is passed through."""
    try:
        y, m, d = (int(p) for p in iso.split("-"))
        return f"{d} {MONTHS[m - 1]} {y}"
    except Exception:
        return iso or ""


def hue(slug):
    return int(hashlib.md5(slug.encode()).hexdigest()[:4], 16) % 360


def wrap(text, max_chars, limit):
    """Greedy wrap. Returns at most `limit` lines, last one ellipsised."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    if len(lines) > limit:
        lines = lines[:limit]
        lines[-1] = lines[-1].rstrip(" ,.;:") + "…"
    return lines


# Average glyph advance as a fraction of font size, measured in a browser for
# the stacks these templates use.
EM_SANS_BOLD = 0.44
EM_SANS      = 0.50
EM_MONO      = 0.62


def tspans(lines, x, leading, size, em, limit):
    """Emit tspans with an explicit textLength.

    A standalone SVG cannot resolve -apple-system, so whichever font the
    renderer falls back to decides the real width. That is how the title
    ended up running off the edge. Pinning textLength makes the line occupy
    a known width whatever font is substituted, and the width is clamped to
    the usable area so a long line can never overflow the canvas.
    """
    out = []
    for i, l in enumerate(lines):
        width = min(round(len(l) * size * em), limit)
        out.append(
            f'<tspan x="{x}" dy="{0 if i == 0 else leading}" '
            f'textLength="{width}" lengthAdjust="spacingAndGlyphs">{escape(l)}</tspan>'
        )
    return "".join(out)


def fixed(text, x, y, size, em, limit):
    """Same idea for a single-line label."""
    width = min(round(len(text) * size * em), limit)
    return f'textLength="{width}" lengthAdjust="spacingAndGlyphs"'



def strip_comment(svg):
    """Drop the leading explanatory comment so output files stay lean."""
    if svg.lstrip().startswith("<!--"):
        return svg[svg.index("-->") + 3:].lstrip()
    return svg


def fit(text, widths, sizes, max_lines=3):
    """Pick the largest size at which the text fits inside max_lines.

    widths maps a font size to how many characters fit on one line at that
    size. Bigger sizes are tried first, so a short title stays large and a
    long one steps down instead of colliding with the line beneath it.
    """
    for size in sizes:
        lines = wrap(text, widths[size], max_lines)
        if len(lines) <= max_lines and not lines[-1].endswith("\u2026"):
            return size, lines
    size = sizes[-1]
    return size, wrap(text, widths[size], max_lines)


# Conservative advance width. Real stacks sit nearer 0.50em at this weight, so
# budgeting 0.60 leaves slack for a wider fallback font. No textLength is used,
# because forcing a width is what distorted the glyphs before.
EM_BUDGET = 0.60


def render(template, item, kind):
    h = hue(item["slug"])
    out = template
    out = out.replace("{{HUE2}}", str((h + 48) % 360))
    out = out.replace("{{HUE3}}", str((h + 300) % 360))
    out = out.replace("{{HUE}}", str(h))

    if kind != "cover":
        return out                      # the banner's text is live HTML

    title = item.get("title") or item.get("name") or ""
    tags = item.get("tags") or item.get("status") or ""
    tags = " / ".join(tags) if isinstance(tags, list) else tags

    # step the size down until the title fits three lines inside the safe width
    for size in (58, 50, 44):
        per_line = max(12, int(COVER_W / (size * EM_BUDGET)))
        lines = wrap(title, per_line, 3)
        if not lines[-1].endswith("\u2026"):
            break

    lead = round(size * 1.22)
    out = out.replace("{{TITLE_SIZE}}", str(size))
    out = out.replace("{{TITLE_Y}}", str(560 - (len(lines) - 1) * lead))
    out = out.replace("{{TITLE_TSPANS}}", "".join(
        f'<tspan x="70" dy="{0 if i == 0 else lead}">{escape(l)}</tspan>'
        for i, l in enumerate(lines)))
    out = out.replace("{{TAGS}}", escape(tags.upper()))
    out = out.replace("{{LABEL}}", attr(title))
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None

    cover_tpl = strip_comment(open(os.path.join(HERE, "cover-template.svg"), encoding="utf-8").read())
    header_tpl = strip_comment(open(os.path.join(HERE, "header-template.svg"), encoding="utf-8").read())

    written = 0
    stamp = str(int(time.time()))
    for kind in ("posts", "projects"):
        path = os.path.join(ROOT, kind, f"{kind}.json")
        items = json.load(open(path, encoding="utf-8"))
        for item in items:
            slug = item["slug"]
            if only and slug != only:
                continue
            if item.get("cover", "cover.svg") == "":
                print(f"  skip   {kind}/{slug} (cover disabled)")
                continue
            folder = os.path.join(ROOT, kind, slug)
            os.makedirs(folder, exist_ok=True)
            open(os.path.join(folder, "cover.svg"), "w", encoding="utf-8").write(
                render(cover_tpl, item, "cover"))
            open(os.path.join(folder, "header.svg"), "w", encoding="utf-8").write(
                render(header_tpl, item, "header"))
            # a version stamp the page appends as ?v=, so regenerated art is
            # never masked by a cached copy
            item["art"] = stamp
            print(f"  wrote  {kind}/{slug}/cover.svg + header.svg")
            written += 2

        json.dump(items, open(path, "w", encoding="utf-8"), indent=2)
        open(path, "a", encoding="utf-8").write("\n")

    if only and written == 0:
        print(f"No item with slug '{only}'.")
        return 1
    print(f"\n{written} files written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
