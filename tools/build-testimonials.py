#!/usr/bin/env python3
"""Rebuild the 'Opinie' (testimonials) section on the homepage.

Reads data/testimonials.json and replaces the content between
<!--/TESTIMONIALS:AUTO--> markers inside <div class="testi-grid">.

Usage: python3 tools/build-testimonials.py
"""
import html as html_mod
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "testimonials.json"
INDEX = ROOT / "index.html"

START = "<!--TESTIMONIALS:AUTO-->"
END = "<!--/TESTIMONIALS:AUTO-->"

data = json.loads(DATA.read_text())
cards = []
for t in data["testimonials"]:
    quote = html_mod.escape(t["quote"], quote=False)
    author = html_mod.escape(t["author"])
    cards.append(
        f'      <article class="testi"><div class="stars">★★★★★</div>'
        f'<p>„{quote}"</p><footer>{author}</footer></article>'
    )

block = f"{START}\n" + "\n".join(cards) + f"\n      {END}"

text = INDEX.read_text()

if START in text and END in text:
    pre = text.split(START)[0]
    post = text.split(END)[1]
    text = pre + block + post
else:
    # First run: inject markers around the existing testi-grid content
    import re
    m = re.search(r'(<div class="testi-grid">\n)(.*?)(\n    </div>)', text, re.S)
    if not m:
        raise SystemExit("testi-grid not found in index.html")
    text = text[:m.start(2)] + block + text[m.end(2):]

INDEX.write_text(text)
print(f"wrote {len(cards)} testimonials into index.html")
