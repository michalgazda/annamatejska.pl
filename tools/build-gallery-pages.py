#!/usr/bin/env python3
"""Generate static HTML pages for every gallery registered in data/galleries.json.

Reads each registry entry {slug, title, category, date, cover, excerpt, photos, wide}
and writes galerie/<slug>.html with a photo grid + lightbox (same markup as
tools/new-gallery.py produces). Safe to re-run; overwrites pages for entries
present in the registry. Gallery pages not in the registry are left untouched.

Usage: python3 tools/build-gallery-pages.py
"""
import html as html_mod
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "galleries.json"

MONTHS_PL = ["", "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
             "lipca", "sierpnia", "września", "października", "listopada",
             "grudnia"]

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Galeria | Anna Matejska-Gazda Fotograf Kraków</title>
<meta name="description" content="{excerpt}">
<link rel="canonical" href="https://annamatejska.pl/galerie/{page_slug}.html">
<link rel="stylesheet" href="../assets/fonts/fonts.css">
<link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
<header>
  <nav class="nav">
    <a class="brand" href="../index.html">Anna Matejska<em>-Gazda</em></a>
    <button class="menu-toggle" aria-label="Menu">☰</button>
    <div class="nav-links">
      <a href="../index.html#o-mnie">O mnie</a>
      <a href="../index.html#sesje">Sesje</a>
      <a href="../galerie.html">Galerie</a>
      <a href="../index.html#opinie">Opinie</a>
      <a href="../kontakt.html" class="btn">Umów sesję</a>
    </div>
  </nav>
</header>

<section class="page-hero">
  <div class="container gal-meta">
    <span class="kicker">{category} · {date_pl}</span>
    <h1>{title}</h1>
    <p>{excerpt}</p>
  </div>
</section>

<section style="padding-top:0">
  <div class="container">
    <div class="photo-grid">
{figures}
    </div>
    <p style="text-align:center;margin-top:56px"><a class="btn btn-line" href="../galerie.html">← Wszystkie galerie</a></p>
  </div>
</section>

<footer class="site">
  <div class="container">
    <span>© {year} Anna Matejska-Gazda Fotografia · Kraków</span>
    <span><a href="https://www.instagram.com/annamatejska.fotografia/">Instagram</a> · <a href="https://www.facebook.com/annamatejska.fotografia">Facebook</a></span>
  </div>
</footer>

<script src="../assets/js/main.js"></script>
</body>
</html>
"""


def date_pl(iso: str) -> str:
    try:
        d = date.fromisoformat(iso[:10])
        return f"{d.day} {MONTHS_PL[d.month]} {d.year}"
    except ValueError:
        return iso


def figures_for(entry: dict) -> str:
    photos = entry.get("photos") or []
    wide = {int(n) for n in (entry.get("wide") or [])}
    if not photos:
        # Fallback: scan images/galleries/<slug>/ for numbered photos
        folder = ROOT / "images" / "galleries" / entry["slug"]
        if folder.is_dir():
            photos = sorted(
                f"images/galleries/{entry['slug']}/{p.name}"
                for p in folder.glob("*.jpg"))
    # Compute year from the gallery date to avoid date.today() drift
    gallery_year = date.today().year
    try:
        gallery_year = int(entry.get("date", "")[:4])
    except (ValueError, IndexError):
        pass
    lines = []
    for i, src in enumerate(photos, start=1):
        alt = html_mod.escape(f"{entry['title']} — zdjęcie {i}")
        cls = ' class="wide"' if i in wide else ""
        lines.append(
            f'      <figure{cls}><img src="../{html_mod.escape(src)}" alt="{alt}" loading="lazy"></figure>'
        )
    return "\n".join(lines) or "      <!-- brak zdjec -->"


def main() -> None:
    data = json.loads(DATA.read_text())
    for entry in data["galleries"]:
        out = ROOT / "galerie" / f"{entry['slug']}.html"
        # Use gallery date year instead of date.today() for idempotent builds
        try:
            yr = int(entry.get("date", "")[:4])
        except (ValueError, IndexError):
            yr = date.today().year
        out.write_text(PAGE_TEMPLATE.format(
            title=html_mod.escape(entry["title"]),
            excerpt=html_mod.escape(entry.get("excerpt", ""), quote=False),
            category=html_mod.escape(entry.get("category", "")),
            date_pl=date_pl(entry.get("date", "")),
            figures=figures_for(entry),
            year=yr,
            page_slug=entry["slug"],
        ))
        print(f"wrote {out.relative_to(ROOT)}")
    print(f"done: {len(data['galleries'])} gallery pages")


if __name__ == "__main__":
    main()