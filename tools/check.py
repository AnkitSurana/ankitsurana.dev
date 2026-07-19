#!/usr/bin/env python3
"""
Check the site's content before pushing.

    python3 tools/check.py

This is the thing that keeps the design from drifting as posts and projects
pile up. The layout can absorb any number of items, but only if each entry
stays inside the budgets the cards were designed around. Run it after adding
anything; it exits non-zero if something would look wrong or break.
"""

import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cards clamp title to 2 lines and blurb to 3. These budgets keep text inside
# the clamp so nothing is silently cut off mid-word on a narrow card.
LIMITS = {
    "title":    (70,  "card title clamps to 2 lines"),
    "name":     (34,  "project name sits on one line"),
    "summary":  (170, "card blurb clamps to 3 lines"),
    "blurb":    (170, "card blurb clamps to 3 lines"),
    "status":   (26,  "shares the label row with a badge"),
}

problems, warnings = [], []


def err(msg):
    problems.append(msg)


def warn(msg):
    warnings.append(msg)


def check_manifest(kind):
    path = os.path.join(ROOT, kind, f"{kind}.json")
    if not os.path.exists(path):
        err(f"{kind}/{kind}.json is missing")
        return []
    try:
        items = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{kind}/{kind}.json is not valid JSON: {e}")
        return []

    seen = set()
    required = ["slug", "title", "summary", "date"] if kind == "posts" \
        else ["slug", "name", "blurb", "status"]

    for item in items:
        slug = item.get("slug", "?")

        for field in required:
            if not item.get(field):
                err(f"{kind}/{slug}: missing required field '{field}'")

        if slug in seen:
            err(f"{kind}: duplicate slug '{slug}'")
        seen.add(slug)

        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            err(f"{kind}/{slug}: slug should be lower-case letters, digits and hyphens")

        display = str(item.get("display", "show")).lower()
        if display not in ("show", "hide"):
            err(f"{kind}/{slug}: display is '{item.get('display')}', expected \"show\" or \"hide\"")

        if kind == "posts" and item.get("date"):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", item["date"]):
                err(f"{kind}/{slug}: date '{item['date']}' should be YYYY-MM-DD")

        for field, (limit, why) in LIMITS.items():
            val = item.get(field)
            if isinstance(val, str) and len(val) > limit:
                warn(f"{kind}/{slug}: {field} is {len(val)} chars, over {limit} ({why})")

        if kind == "posts" and len(item.get("tags", [])) > 3:
            warn(f"{kind}/{slug}: {len(item['tags'])} tags, 3 fit comfortably on a card")
        if kind == "projects" and len(item.get("stack", [])) > 6:
            warn(f"{kind}/{slug}: {len(item['stack'])} stack chips, 6 fit before wrapping")

        folder = os.path.join(ROOT, kind, slug)
        md = os.path.join(folder, "index.md")
        if not os.path.isfile(md):
            err(f"{kind}/{slug}: no index.md")
            continue

        for field in ("cover", "header"):
            ref = item.get(field)
            if ref and not os.path.isfile(os.path.join(folder, ref)):
                err(f"{kind}/{slug}: {field} '{ref}' not found (run tools/make-covers.py)")

        body = open(md, encoding="utf-8").read()
        for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", body):
            if src.startswith(("http://", "https://", "data:")):
                continue
            if not os.path.isfile(os.path.normpath(os.path.join(folder, src))):
                err(f"{kind}/{slug}: image '{src}' not found")
            if not alt.strip():
                warn(f"{kind}/{slug}: image '{src}' has no alt text, so it gets no caption")

    # orphan folders
    for folder in glob.glob(os.path.join(ROOT, kind, "*", "")):
        name = os.path.basename(folder.rstrip(os.sep))
        if name not in seen:
            warn(f"{kind}/{name}/ exists but is not listed in {kind}.json, so it is unreachable")

    return items


def check_svgs():
    files = glob.glob(os.path.join(ROOT, "*", "*", "*.svg")) + \
            glob.glob(os.path.join(ROOT, "assets", "*.svg"))
    for f in files:
        try:
            ET.parse(f)
        except ET.ParseError as e:
            rel = os.path.relpath(f, ROOT)
            err(f"{rel}: not valid XML ({e}). Unescaped & or \" is the usual cause.")
    return len(files)


def main():
    posts = check_manifest("posts")
    projects = check_manifest("projects")
    svgs = check_svgs()

    shown = lambda xs: [x for x in xs if str(x.get("display", "show")).lower() != "hide"]

    print(f"posts     {len(shown(posts))} shown, {len(posts) - len(shown(posts))} hidden")
    print(f"projects  {len(shown(projects))} shown, {len(projects) - len(shown(projects))} hidden")
    print(f"svg       {svgs} files")

    if warnings:
        print("\nWarnings (it will render, but it may not look how you want):")
        for w in warnings:
            print(f"  ~ {w}")

    if problems:
        print("\nProblems (fix these):")
        for p in problems:
            print(f"  x {p}")
        print(f"\nFAIL: {len(problems)} problem(s), {len(warnings)} warning(s)")
        return 1

    print(f"\nPASS{' with ' + str(len(warnings)) + ' warning(s)' if warnings else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
