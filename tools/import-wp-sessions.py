#!/usr/bin/env python3
"""Import the old WordPress session pages: main (hero) photo, page gallery and examples.

For each of the six session types the old site had: a big photo at the top, sometimes a
photo grid („galeria”) and a list of example galleries („Przykładowe … sesje”). This tool
downloads the heroes and the page grids, imports the missing example gallery
(emilia-kobieca-sesja-wizerunkowa) and writes src/data/sesje.json.

Usage: python3 tools/import-wp-sessions.py [--force]
Cache: $TMPDIR/wp-session-import/
"""
import argparse
import concurrent.futures as cf
import html as html_mod
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("TMPDIR", "/tmp").rstrip("/") + "/wp-session-import"
FFMPEG = "/home/michal/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
PUBLIC = "/annamatejska.pl/images"

# hero photo + page-gallery photos per session slug, taken from the old pages
PLAN = {
    "romantyczne": {
        "hero_url": "https://www.annamatejska.pl/wp-content/uploads/2026/01/DSC_4006.jpg",
        "photos": [
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-12-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-34.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-40.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-13-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-28.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-11.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_4349-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-36.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_3956-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-1-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-29.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-3-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-32.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-22-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-26.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-7-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-17-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-19-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_2462-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-2-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-14.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-6-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-38.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-37-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-9.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-8-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-21.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-16.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_4038-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_3831-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-10.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-42.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_2444-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-44-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-15.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-18.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-5-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjeromantyczne-27.jpg"
        ]
    },
    "dzieciece": {
        "hero_url": "https://www.annamatejska.pl/wp-content/uploads/2026/02/DSC_4861.jpg",
        "photos": [
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-55-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-47-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-60-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1874-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-53-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-12-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-57-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-15-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_5733-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_6010-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-58-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-39.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-3-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-48-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-13-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-1-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-22-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-43-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-54-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-56-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-30-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-59-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-16-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-19-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1898-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-40.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_5939-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_5735-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-32-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-42.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjedzieciece-27-scaled.jpg"
        ]
    },
    "kobiece": {
        "hero_url": "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_2440.jpg",
        "photos": [
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-8-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-15-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-12-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-10-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_5488-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_0705-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_5492-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1484-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-31-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1469-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_3543-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1463-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-2-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-30-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_0837-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-3-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-18-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-23-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-7-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1486-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_0645-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_1482-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_0707-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-29-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-9-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-sesjekobiece-33-scaled.jpg"
        ]
    },
    "ciazowe": {
        "hero_url": "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-23.png",
        "photos": [
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-16.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-2.png",
            "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_3156-scaled.jpg",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-24.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-12.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-8.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-5.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-20.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-26.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-1.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-6.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-21.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-22.png",
            "https://www.annamatejska.pl/wp-content/uploads/2025/11/annamatejskagazda-nw-28.png"
        ]
    },
    "rodzinne": {
        "hero_url": "https://www.annamatejska.pl/wp-content/uploads/2026/03/DSC_8406-2.jpg",
        "photos": []
    },
    "wizerunkowe": {
        "hero_url": "https://www.annamatejska.pl/wp-content/uploads/2025/06/annamatejskagazda-marysia-6-1.jpg",
        "photos": []
    }
}

# example galleries exactly as listed on the old pages
SAMPLES = {
    "rodzinne": {
        "title": "Przykładowe rodzinne sesje zdjęciowe:",
        "items": [
            {
                "title": "Sesja rodzinna w Parku Lotników",
                "slug": "sesja-rodzinna-w-parku-lotnikow"
            },
            {
                "title": "Sesja rodzinna w Parku Reduta",
                "slug": "sesja-rodzinna-w-parku-reduta"
            },
            {
                "title": "Sesja rodzinna w Parku Lotników (2)",
                "slug": "sesja-rodzinna-w-parku-lotnikow-2"
            },
            {
                "title": "Sesja rodzinna w Parku Tysiąclecia",
                "slug": "sesja-rodzinna-w-parku-tysiaclecia"
            },
            {
                "title": "Sesja rodzinna w Parku Białoprądnickim",
                "slug": "sesja-rodzinna-w-parku-bialopradnickim"
            },
            {
                "title": "Sesja Gosi i Olka w parku",
                "slug": "sesja-gosi-i-olka-w-parku"
            }
        ]
    },
    "kobiece": {
        "title": "Przykładowe kobiece sesje zdjęciowe:",
        "items": [
            {
                "title": "Agnieszka – sesja stylizowana",
                "slug": "sesja-kobieca-agnieszki"
            },
            {
                "title": "Emilia – sesja portretowa",
                "slug": "emilia-kobieca-sesja-wizerunkowa"
            },
            {
                "title": "Marysia – sesja świąteczna",
                "slug": "marysia-swiateczna-sesja-w-studio"
            }
        ]
    },
    "wizerunkowe": {
        "title": "Przykładowe realizacje sesji wizerunkowych:",
        "items": [
            {
                "title": "Ania i Piotrek – networkerzy",
                "slug": "ania-i-piotrek-networkerzy"
            },
            {
                "title": "Marysia – graficzka, geolożka",
                "slug": "marysia-graficzka-geolozka"
            },
            {
                "title": "Agnieszka – animatorka kultury, artystka",
                "slug": "agnieszka-animatorka-kultury-artystka"
            },
            {
                "title": "Paulina – edukatorka muzyczna",
                "slug": "paulina-edukatorka-muzyczna"
            },
            {
                "title": "Weronika – trenerka mentalna sportu",
                "slug": "weronika-trenerka-mentalna-sportu"
            },
            {
                "title": "Emilia – psycholożka",
                "slug": "emilia-psycholozka"
            }
        ]
    }
}

EXTRA_GALLERY = {
    "slug": "emilia-kobieca-sesja-wizerunkowa",
    "title": "Emilia \u2014 sesja portretowa",
    "category": "Sesje kobiece",
    "date": "2025-06-04",
    "excerpt": "Sesja kobieca \u2014 \u015bwiat\u0142o, spok\u00f3j i uwa\u017cno\u015b\u0107.",
    "page": "https://www.annamatejska.pl/emilia-kobieca-sesja-wizerunkowa/",
}


def safe_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path), p.query, p.fragment))


def fetch(url, binary=False):
    req = urllib.request.Request(safe_url(url), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def export(name, url, full, thumb, full_max=1600, quality=4):
    raw = os.path.join(CACHE, "src-" + re.sub(r"[^A-Za-z0-9_.-]", "_", name))
    if not os.path.exists(raw) or os.path.getsize(raw) == 0:
        try:
            open(raw, "wb").write(fetch(url, binary=True))
        except Exception as exc:
            return f"download failed: {exc}"
    for dest, edge, q in ((full, full_max, quality), (thumb, 800, 5)):
        if not dest:
            continue
        try:
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", raw,
                            "-vf", f"scale='min({edge},iw)':-2", "-q:v", str(q), dest], check=True)
        except subprocess.CalledProcessError as exc:
            return f"ffmpeg failed: {exc}"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)

    jobs = []
    for slug, spec in PLAN.items():
        hero_dest = os.path.join(REPO, "public/images/sesje", f"{slug}.jpg")
        os.makedirs(os.path.dirname(hero_dest), exist_ok=True)
        jobs.append((f"hero-{slug}", spec["hero_url"], hero_dest, None))
        d = os.path.join(REPO, "public/images/sesje", slug)
        os.makedirs(d, exist_ok=True)
        for i, url in enumerate(spec["photos"], 1):
            jobs.append((f"{slug}-{i:02d}", url, os.path.join(d, f"{i:02d}.jpg"),
                         os.path.join(d, f"{i:02d}-thumb.jpg")))

    # the one example gallery that exists as a WP page (not a post, so the gallery import missed it)
    page_html = fetch(EXTRA_GALLERY["page"])
    urls, seen = [], set()
    for u in re.findall(r"https://www\.annamatejska\.pl/wp-content/uploads/[^\"'\s)]+\.(?:jpg|jpeg|png)", page_html):
        key = re.sub(r"-\d{2,4}x\d{2,4}(?=\.[A-Za-z]+$)", "", os.path.basename(u))
        if key in seen:
            continue
        seen.add(key)
        urls.append(u)
    urls = urls[:12]
    extra_dir = os.path.join(REPO, "public/images/galleries", EXTRA_GALLERY["slug"])
    os.makedirs(extra_dir, exist_ok=True)
    for i, url in enumerate(urls, 1):
        jobs.append((f"extra-{i:02d}", url, os.path.join(extra_dir, f"{i:02d}.jpg"),
                     os.path.join(extra_dir, f"{i:02d}-thumb.jpg")))

    print(f"→ {len(jobs)} files to export")
    done, failed = 0, []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for res, job in zip(pool.map(lambda j: export(j[0], j[1], j[2], j[3]), jobs), jobs):
            done += 1
            if res:
                failed.append((job[0], res))
            if done % 20 == 0:
                print(f"   {done}/{len(jobs)}")
    print(f"exported {done - len(failed)}, failures {len(failed)}")
    for name, err in failed[:8]:
        print("   !", name, err)

    failed_names = {name for name, _ in failed}
    out = {}
    for slug, spec in PLAN.items():
        photos = [{"photo": f"{PUBLIC}/sesje/{slug}/{i:02d}.jpg",
                   "thumb": f"{PUBLIC}/sesje/{slug}/{i:02d}-thumb.jpg"}
                  for i in range(1, len(spec["photos"]) + 1)
                  if f"{slug}-{i:02d}" not in failed_names]
        sample = SAMPLES.get(slug, {})
        out[slug] = {
            "hero": "" if f"hero-{slug}" in failed_names else f"{PUBLIC}/sesje/{slug}.jpg",
            "photos": photos,
            "samples_title": sample.get("title", ""),
            "samples": sample.get("items", []),
        }

    # the extra example gallery belongs in galleries.json (card + detail page)
    galleries_path = os.path.join(REPO, "src/data/galleries.json")
    data = json.load(open(galleries_path, encoding="utf-8"))
    existing = {g["slug"] for g in data["galleries"]}
    n_extra = sum(1 for n in failed_names if n.startswith("extra-"))
    count = max(0, len(urls) - n_extra)
    if EXTRA_GALLERY["slug"] not in existing and count >= 3:
        data["galleries"].append({
            "slug": EXTRA_GALLERY["slug"],
            "title": EXTRA_GALLERY["title"],
            "category": EXTRA_GALLERY["category"],
            "date": EXTRA_GALLERY["date"],
            "excerpt": EXTRA_GALLERY["excerpt"],
            "photos": count,
            "photos_list": [f"{PUBLIC}/galleries/{EXTRA_GALLERY['slug']}/{i:02d}-thumb.jpg" for i in range(1, count + 1)],
            "cover": f"{PUBLIC}/galleries/{EXTRA_GALLERY['slug']}/01-thumb.jpg",
        })
        data["galleries"].sort(key=lambda g: g["date"], reverse=True)
        json.dump(data, open(galleries_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(galleries_path, "a").write("\n")
        print(f"✓ added gallery {EXTRA_GALLERY['slug']} ({count} photos)")

    json.dump({"sessions": [dict(slug=slug, **data) for slug, data in out.items()]},
              open(os.path.join(REPO, "src/data/sesje.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    open(os.path.join(REPO, "src/data/sesje.json"), "a").write("\n")
    print("✓ wrote src/data/sesje.json")


if __name__ == "__main__":
    sys.exit(main())
