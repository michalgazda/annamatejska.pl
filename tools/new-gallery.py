#!/usr/bin/env python3
"""Generate a gallery page for Anna's site.

Usage:
  python3 tools/new-gallery.py --slug "sesja-rodzinna-wawel" \
      --title "Rodzinna pod Wawelem" --category "Sesje rodzinne" \
      --date "2026-08-20" [--excerpt "Krótki opis sesji."] \
      [--wide "2,5" --tall "1,4"]

Steps it does for you:
  1. Creates images/galleries/<slug>/ folder (put full-size photos there: 01.jpg, 02.jpg, …)
  2. Creates galerie/<slug>.html — gallery page with responsive grid + lightbox
  3. Registers the gallery in data/galleries.json (shown on the homepage)
"""
import argparse
import html as html_mod
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Galeria | Anna Matejska-Gazda Fotograf Kraków</title>
<meta name="description" content="{excerpt}">
<link rel="canonical" href="https://annamatejska.pl/galerie/{slug}.html">
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

MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
          "sierpnia", "września", "października", "listopada", "grudnia"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--category", default="Galeria")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--excerpt", default="")
    ap.add_argument("--wide", default="", help="comma list of photo numbers shown as wide (21/9)")
    ap.add_argument("--tall", default="", help="comma list of photo numbers shown as tall")
    args = ap.parse_args()

    slug = args.slug.strip().lower().replace(" ", "-")
    y, m, d = (int(x) for x in args.date.split("-"))
    date_pl = f"{d} {MONTHS[m - 1]} {y}"

    # 1. image folder
    img_dir = ROOT / "images/galleries" / slug
    img_dir.mkdir(parents=True, exist_ok=True)

    photos = sorted(img_dir.glob("*.jpg")) + sorted(img_dir.glob("*.jpeg")) + sorted(img_dir.glob("*.webp"))
    if not photos:
        print(f"⚠ Folder {img_dir.relative_to(ROOT)} is empty.")
        print("  Put photos there now named 01.jpg, 02.jpg, … then re-run this command to build the page.")
        names = [f"{i + 1:02d}.jpg" for i in range(6)]
    else:
        names = [p.name for p in sorted(photos)]

    wide = {w.strip() for w in args.wide.split(",") if w.strip()}
    tall = {t_.strip() for t_ in args.tall.split(",") if t_.strip()}

    figs = []
    for name in names:
        num = name.split(".")[0].lstrip("0") or "0"
        cls = " wide" if num in wide else (" tall" if num in tall else "")
        alt = html_mod.escape(f"{args.title} — fot. Anna Matejska-Gazda")
        figs.append(f'      <figure class="{cls.strip()}"><img src="../images/galleries/{slug}/{html_mod.escape(name)}" loading="lazy" alt="{alt}"></figure>')

    # 2. page
    gal_dir = ROOT / "galerie"
    gal_dir.mkdir(exist_ok=True)
    page = gal_dir / f"{slug}.html"
    year = y
    page.write_text(TEMPLATE.format(
        title=html_mod.escape(args.title),
        excerpt=html_mod.escape(args.excerpt or "Galeria autorska — Anna Matejska-Gazda Fotografia.", quote=False),
        category=html_mod.escape(args.category),
        date_pl=date_pl,
        figures="\n".join(figs),
        slug=slug,
        year=year,
    ), encoding="utf-8")

    # 3. register in data/galleries.json
    data_file = ROOT / "data/galleries.json"
    data = json.loads(data_file.read_text(encoding="utf-8")) if data_file.exists() else {"galleries": []}
    entry = {
        "slug": slug, "title": args.title, "category": args.category,
        "date": args.date,
        "cover": f"images/galleries/{slug}/{names[0]}",
        "excerpt": args.excerpt or "",
        "page": f"galerie/{slug}.html",
    }
    data["galleries"] = [g for g in data["galleries"] if g["slug"] != slug] + [entry]
    data["galleries"].sort(key=lambda g: g["date"], reverse=True)
    data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rel = page.relative_to(ROOT)
    print(f"✓ Page created:  {rel}")
    print(f"✓ Photos folder: images/galleries/{slug}/  ({len(names)} photo(s) found)")
    print(f"✓ Registered on the homepage ({len(data['galleries'])} galleries total).")
    print("→ Rebuild homepage cards:  python3 tools/build-home-galleries.py")


if __name__ == "__main__":
    main()