#!/usr/bin/env python3
"""Migawka feedu Instagrama na stronę główną (sekcja „Instagram”, 6 × 2 kwadraty).

Skąd zdjęcia: stara strona WordPress (wtyczka Smash Balloon) publikuje bieżący feed
wraz z podpisanymi linkami do CDN Instagrama. Skrypt pobiera stronę główną starej
witryny, wyciąga 12 najnowszych postów, kadruje je do kwadratu 600 × 600
i zapisuje jako public/images/instagram/NN.jpg + src/data/instagram.json.

Użycie:
    python3 tools/instagram-snapshot.py            # 12 zdjęć
    python3 tools/instagram-snapshot.py --count 18 # więcej niż dwa rzędy

Uwaga: to migawka — nowe posty pojawią się dopiero po ponownym uruchomieniu skryptu
(albo po ręcznej podmianie plików w public/images/instagram/).
"""
import argparse
import html
import json
import os
import re
import subprocess
import urllib.request

FF = os.environ.get("FFMPEG", "ffmpeg")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "public/images/instagram")
JSON_PATH = os.path.join(REPO, "src/data/instagram.json")
FEED_SOURCE = "https://www.annamatejska.pl/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def fetch_feed_html() -> str:
    req = urllib.request.Request(FEED_SOURCE, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "ignore")


def parse_items(page: str):
    """Każdy kafelek: <a class="sbi_photo" href="POST" ... data-full-res="IMG">."""
    items = []
    for m in re.finditer(r'<a class="sbi_photo" href="([^"]+)"(.*?)>', page, re.S):
        post, rest = m.group(1), m.group(2)
        img = re.search(r'data-full-res="([^"]+)"', rest)
        if not img:
            continue
        items.append({"post": html.unescape(post), "img": html.unescape(img.group(1))})
    seen, out = set(), []
    for it in items:                       # bez powtórzeń (karuzele mają kilka zdjęć)
        if it["post"] in seen:
            continue
        seen.add(it["post"])
        out.append(it)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=12, help="ile zdjęć pobrać (domyślnie 12)")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    page = fetch_feed_html()
    posts = parse_items(page)[: args.count]
    print(f"postów w feedzie: {len(parse_items(page))}, pobieram: {len(posts)}")

    ok = []
    for i, it in enumerate(posts, start=1):
        dest = os.path.join(OUT, f"{i:02d}.jpg")
        tmp = os.path.join(OUT, f".src-{i:02d}.bin")
        try:
            req = urllib.request.Request(it["img"], headers={
                "User-Agent": UA, "Referer": "https://www.instagram.com/"})
            open(tmp, "wb").write(urllib.request.urlopen(req, timeout=90).read())
        except Exception as e:                                    # noqa: BLE001
            print(f"  {i:02d}: pomijam ({e})")
            continue
        r = subprocess.run([FF, "-y", "-v", "error", "-i", tmp, "-vf",
                            "scale=600:600:force_original_aspect_ratio=increase,crop=600:600",
                            "-q:v", "4", dest])
        os.remove(tmp)
        if r.returncode == 0:
            ok.append({"photo": f"/images/instagram/{i:02d}.jpg", "url": it["post"]})
            print(f"  {i:02d}: OK")
        else:
            print(f"  {i:02d}: błąd ffmpeg")

    # usuń stare pliki, których nie ma już w migawce
    for f in sorted(os.listdir(OUT)):
        if re.fullmatch(r"\d{2}\.jpg", f) and f"/images/instagram/{f}" not in [o["photo"] for o in ok]:
            os.remove(os.path.join(OUT, f))

    data = {
        "profile": "annamatejska.fotografia",
        "profile_url": "https://www.instagram.com/annamatejska.fotografia/",
        "load_more_label": "Załaduj więcej zdjęć",
        "follow_label": "Obserwuj mnie na Instagramie",
        "items": ok,
    }
    with open(JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"zapisano {len(ok)} zdjęć → public/images/instagram/ i src/data/instagram.json")


if __name__ == "__main__":
    main()
