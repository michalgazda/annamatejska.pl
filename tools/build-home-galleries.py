#!/usr/bin/env python3
"""Rebuild the "Najnowsze galerie" cards in index.html and galerie.html
from data/galleries.json.

Anna never edits the generated block by hand — just run:

    python3 tools/build-home-galleries.py

Rules:
  * index.html   → shows the 6 most recent galleries (a teaser) + a link to
                   the full list on galerie.html.
  * galerie.html → shows ALL registered galleries.
The generated block is delimited by the markers
  <!--GALLERIES:AUTO-->  ...  <!--/GALLERIES:AUTO-->
so it can be safely regenerated any number of times.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
          "sierpnia", "września", "października", "listopada", "grudnia"]

CARD = """      <a class="gal-card" href="{page}">
        <img src="{cover}" alt="{title}" loading="lazy">
        <div class="overlay"><h3>{title}</h3><p>{excerpt}</p><time>{date_pl}</time></div>
      </a>"""

START, END = "<!--GALLERIES:AUTO-->", "<!--/GALLERIES:AUTO-->"


def date_pl(iso: str) -> str:
    """2025-10-15 -> 15 października 2025"""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def esc(s: str) -> str:
    """Minimal HTML-escape for text injected into attributes/text nodes."""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def cards_html(galleries, limit=None):
    items = galleries if limit is None else galleries[:limit]
    return "\n".join(
        CARD.format(page=g["page"], cover=g["cover"], title=esc(g["title"]),
                    excerpt=esc(g.get("excerpt", "")), date_pl=date_pl(g["date"]))
        for g in items)


def build_block(galleries, limit):
    """Return the inner HTML that goes between the AUTO markers."""
    body = cards_html(galleries, limit)
    if not body:
        body = '      <p style="color:var(--ink-soft)">Brak galerii.</p>'
    return body


def main():
    data = json.loads((ROOT / "data/galleries.json").read_text(encoding="utf-8"))
    galleries = data["galleries"]

    # (file, limit). limit None = show everything.
    targets = {
        "index.html":   build_block(galleries, 6),      # 6 most recent teaser
        "galerie.html": build_block(galleries, None),   # full portfolio
    }

    for fname, block in targets.items():
        p = ROOT / fname
        if not p.exists():
            print(f"! {fname}: not found, skipped")
            continue
        html = p.read_text(encoding="utf-8")
        new_html, n = re.subn(
            re.escape(START) + r".*?" + re.escape(END),
            lambda _m: f"{START}\n{block}\n{END}",
            html, flags=re.S)
        if n:
            p.write_text(new_html, encoding="utf-8")
            shown = len(galleries) if fname == "galerie.html" else min(6, len(galleries))
            print(f"✓ {fname}: gallery block regenerated ({shown} card{'s' if shown != 1 else ''})")
        else:
            print(f"! {fname}: missing {START} … {END} markers — "
                  f"add them around the <div class=\"gal-list\">…</div> you want auto-managed")


if __name__ == "__main__":
    main()
