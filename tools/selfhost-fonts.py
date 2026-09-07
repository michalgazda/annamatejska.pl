#!/usr/bin/env python3
"""Self-host Google Fonts (Cormorant Garamond + Jost) for GDPR compliance.

Downloads latin + latin-ext woff2 files into assets/fonts/ and generates
assets/fonts/fonts.css. Then update_html.py rewrites the HTML files.
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = ROOT / "assets" / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# UA that makes Google return woff2
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

CSS_URL = ("https://fonts.googleapis.com/css2"
           "?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400"
           "&family=Jost:ital,wght@0,300;0,400;0,500;1,300"
           "&display=swap")

req = urllib.request.Request(CSS_URL, headers={"User-Agent": UA})
css = urllib.request.urlopen(req, timeout=30).read().decode()

# Keep only latin and latin-ext blocks (Polish needs latin-ext)
blocks = re.findall(r"/\* (\S+) \*/\s*(@font-face \{[^}]+\})", css)
out_css = []
seen = set()
for subset, face in blocks:
    if subset not in ("latin", "latin-ext"):
        continue
    m = re.search(r"url\((https://[^)]+\.woff2)\)", face)
    fam = re.search(r"font-family: '([^']+)'", face).group(1).replace(" ", "")
    style = re.search(r"font-style: (\w+)", face).group(1)
    weight = re.search(r"font-weight: (\d+)", face).group(1)
    fname = f"{fam}-{weight}{'-italic' if style == 'italic' else ''}-{subset}.woff2"
    if m and fname not in seen:
        seen.add(fname)
        data = urllib.request.urlopen(
            urllib.request.Request(m.group(1), headers={"User-Agent": UA}),
            timeout=30).read()
        (FONTS_DIR / fname).write_bytes(data)
        print(f"downloaded {fname} ({len(data)} bytes)")
    face = re.sub(r"url\(https://[^)]+\.woff2\)", f"url('{fname}')", face)
    face = re.sub(r"unicode-range:[^;]+;", "", face)  # single file per subset: merge ranges not needed; keep both faces
    out_css.append(face)

(FONTS_DIR / "fonts.css").write_text("\n".join(out_css) + "\n")
print(f"wrote fonts.css with {len(out_css)} @font-face rules")
