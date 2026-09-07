#!/usr/bin/env python3
"""Rewrite all HTML files: drop Google Fonts CDN links, use local fonts.css.

Run once after tools/selfhost-fonts.py. Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN_PRECONNECT = re.compile(
    r'\s*<link rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>')
CDN_CSS = re.compile(
    r'\s*<link href="https://fonts\.googleapis\.com/[^"]+"[^>]*>')


def rel_depth(p: Path) -> str:
    return "../" * (len(p.relative_to(ROOT).parts) - 1)


changed = 0
for html in ROOT.rglob("*.html"):
    if "kadrowania" in html.parts:
        continue  # v2 site manages its own fonts
    text = html.read_text()
    new = CDN_CSS.sub(lambda m: f'\n<link rel="stylesheet" href="{rel_depth(html)}assets/fonts/fonts.css">',
                      text)
    new = CDN_PRECONNECT.sub("", new)
    if new != text:
        html.write_text(new)
        changed += 1
        print(f"updated {html.relative_to(ROOT)}")
print(f"done, {changed} files changed")
