#!/usr/bin/env python3
"""Rebuild the "Najnowsze galerie" cards on index.html and galerie.html from data/galleries.json.

Anna never edits this file — just run:  python3 tools/build-home-galleries.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data/galleries.json").read_text(encoding="utf-8"))

CARD = '''      <a class="gal-card" href="{page}">
        <img src="{cover}" alt="{title}">
        <div class="overlay"><h3>{title}</h3><p>{excerpt}</p><time>{date_pl}</time></div>
      </a>'''

MONTHS = ["stycznia","lutego","marca","kwietnia","maja","czerwca","lipca",
          "sierpnia","września","października","listopada","grudnia"]

def date_pl(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m-1]} {y}"

cards = "\n".join(
    CARD.format(page=g["page"], cover=g["cover"], title=g["title"],
                excerpt=g.get("excerpt", ""), date_pl=date_pl(g["date"]))
    for g in data["galleries"][:6])

for fname in ["index.html", "galerie.html"]:
    p = ROOT / fname
    if not p.exists():
        continue
    html = p.read_text(encoding="utf-8")
    new_html, n = re.subn(r"(<!--GALLERIES:AUTO-->).*?(/\s*-->)", lambda mm, body=mm: "", html) if False else (html, 0)
    # replace between markers
    import re as _re
    pattern = _re.compile(r"(<!--GALLERIES:AUTO-->)(.*?)(<!--/GALLERIES:AUTO-->)", _re.S)
    html2, n2 = pattern.subn(lambda mm: mm.group(1) + "\n" + cards + "\n    " + mm.group(3), html)
    if n2:
        p.write_text(html2, encoding="utf-8")
        print(f"✓ {fname}: {n2} gallery block updated ({min(6,len(data['galleries']))} cards)")
    else:
        print(f"! {fname}: no <!--GALLERIES:AUTO--> markers found")
