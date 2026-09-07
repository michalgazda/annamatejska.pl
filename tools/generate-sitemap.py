#!/usr/bin/env python3
"""Generate sitemap.xml and robots.txt for annamatejska.pl.

Usage:  python3 tools/generate-sitemap.py
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SITE = "https://annamatejska.pl"

# Collect all public pages
PUBLIC = [
    ("/", date.today().strftime("%Y-%m-%d"), "1.0"),
    ("/galerie.html", date.today().strftime("%Y-%m-%d"), "0.8"),
    ("/kontakt.html", date.today().strftime("%Y-%m-%d"), "0.7"),
]

# Add gallery pages
gal_dir = ROOT / "galerie"
if gal_dir.is_dir():
    for f in sorted(gal_dir.glob("*.html")):
        PUBLIC.append((f"/galerie/{f.name}", date.today().strftime("%Y-%m-%d"), "0.6"))

# Add session pages
sesje_dir = ROOT / "sesje"
if sesje_dir.is_dir():
    for f in sorted(sesje_dir.glob("*.html")):
        PUBLIC.append((f"/sesje/{f.name}", date.today().strftime("%Y-%m-%d"), "0.6"))

# Generate sitemap
lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
for path, lastmod, priority in PUBLIC:
    lines.append(f"  <url>")
    lines.append(f"    <loc>{SITE}{path}</loc>")
    lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append(f"    <priority>{priority}</priority>")
    lines.append(f"  </url>")
lines.append("</urlset>")

sitemap = ROOT / "sitemap.xml"
sitemap.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"✓ sitemap.xml — {len(PUBLIC)} URLs")

# Generate robots.txt
robots_txt = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /panel.html

Sitemap: {SITE}/sitemap.xml
"""
robots = ROOT / "robots.txt"
robots.write_text(robots_txt, encoding="utf-8")
print(f"✓ robots.txt — sitemap URL uncommented")