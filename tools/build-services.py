#!/usr/bin/env python3
"""Rebuild the offer (Oferta) pages sesje/*.html and the homepage services grid.

Reads data/services.json. For every service with enabled=true it writes
sesje/<slug>.html and one card into the homepage .svc-grid (between
<!--SERVICES:AUTO--> markers).

Usage: python3 tools/build-services.py
"""
import html as html_mod
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "services.json"
INDEX = ROOT / "index.html"

S_START = "<!--SERVICES:AUTO-->"
S_END = "<!--/SERVICES:AUTO-->"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta_title}</title>
<meta name="description" content="{meta_desc}">
<link rel="stylesheet" href="../assets/fonts/fonts.css">
<link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
<header>
  <nav class="nav">
    <a class="brand" href="../index.html">Anna Matejska<em>-Gazda</em></a>
    <button class="menu-toggle" aria-label="Menu">&#9776;</button>
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
    <span class="kicker">{category} &middot; {tagline}</span>
    <h1>{title}</h1>
    <p>{subtitle}</p>
  </div>
</section>

<section style="padding-top:0">
  <div class="container" style="max-width:820px">
{paragraphs}
    <div style="display:flex;gap:40px;flex-wrap:wrap;margin-top:36px;padding:26px 32px;border:1px solid var(--line);border-radius:3px;background:var(--white)">
      <div><span class="kicker" style="margin-bottom:.3rem">Czas trwania</span><strong style="font-family:var(--serif);font-size:1.5rem;font-weight:500">{duration}</strong></div>
      <div style="flex:1;min-width:240px"><span class="kicker" style="margin-bottom:.3rem">Zawsze w cenie</span><span style="color:var(--ink-soft);font-size:.92rem">{included}</span></div>
    </div>
    <blockquote style="font-family:var(--serif);font-style:italic;font-size:1.35rem;line-height:1.6;color:var(--ink-soft);border-left:2px solid var(--taupe);padding-left:24px;margin:52px 0">{quote}</blockquote>
    <p style="text-align:center;margin-top:44px"><a class="btn btn-taupe" href="../kontakt.html">Umów tę sesję</a></p>
  </div>
</section>

<footer class="site">
  <div class="container">
    <span>&copy; 2026 Anna Matejska-Gazda Fotografia &middot; Kraków</span>
    <span><a href="https://www.instagram.com/annamatejska.fotografia/">Instagram</a> &middot; <a href="https://www.facebook.com/annamatejska.fotografia">Facebook</a></span>
  </div>
</footer>
<script src="../assets/js/main.js"></script>
</body>
</html>
"""

PARA = ('    <p style="color:var(--ink-soft);margin-bottom:1rem">{}</p>')


def included_html(s: dict) -> str:
    return html_mod.escape(s.get("included", "")).replace("•", "&middot;")


def build_page(s: dict) -> str:
    paras = "\n".join(
        PARA.format(html_mod.escape(p, quote=False)) for p in s.get("description", []))
    return PAGE_TEMPLATE.format(
        meta_title=html_mod.escape(s["title"]) + " Kraków – naturalne zdjęcia | Anna Matejska-Gazda",
        meta_desc=html_mod.escape(s.get("subtitle", ""), quote=False),
        category=html_mod.escape(s["category"]),
        tagline=html_mod.escape(s.get("tagline", "Kraków i okolice")),
        title=html_mod.escape(s["title"]),
        subtitle=html_mod.escape(s.get("subtitle", ""), quote=False),
        paragraphs=paras,
        duration=html_mod.escape(s.get("duration", "")),
        included=included_html(s),
        quote=html_mod.escape(s.get("quote", ""), quote=False),
    )


def build_card(s: dict) -> str:
    return (
        f'      <a class="svc" href="sesje/{html_mod.escape(s["slug"])}.html">'
        f'<img src="{html_mod.escape(s.get("card_image", ""))}" alt="{html_mod.escape(s["title"])} Kraków">'
        f'<div class="overlay"><h3>{html_mod.escape(s.get("card_title", ""))}</h3>'
        f'<p>{html_mod.escape(s.get("card_short", ""), quote=False)}</p>'
        f'<small>{html_mod.escape(s.get("card_time", ""))}</small></div></a>'
    )


def main() -> None:
    data = json.loads(DATA.read_text())
    cards = []
    for s in data["services"]:
        if not s.get("enabled", True):
            print(f"skipped (disabled): {s['slug']}")
            continue
        out = ROOT / "sesje" / f"{s['slug']}.html"
        out.write_text(build_page(s))
        print(f"wrote {out.relative_to(ROOT)}")
        cards.append(build_card(s))

    # Homepage grid
    text = INDEX.read_text()
    block = S_START + "\n" + "\n".join(cards) + "\n      " + S_END
    if S_START in text and S_END in text:
        pre = text.split(S_START)[0]
        post = text.split(S_END)[1]
        text = pre + block + post
    else:
        import re
        m = re.search(r'(<div class="svc-grid">\n)(.*?)(\n    </div>)', text, re.S)
        if not m:
            raise SystemExit("svc-grid not found in index.html")
        text = text[:m.start(2)] + block + text[m.end(2):]
    INDEX.write_text(text)
    print(f"homepage: {len(cards)} service cards")


if __name__ == "__main__":
    main()
