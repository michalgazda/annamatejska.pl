#!/usr/bin/env python3
"""Import the curated portfolio photos (the old /portfolio/ page) into the repo.

The WordPress /portfolio/ page is a hand-picked grid of ~86 photos — Anna wants exactly
those "best of" pictures in the new Portfolio section. This tool:

  1. fetches https://www.annamatejska.pl/portfolio/ and collects the unique full-size
     upload URLs in page order,
  2. downloads the originals and writes public/images/portfolio/NN.jpg (1600px, q4)
     plus NN-thumb.jpg (800px, q5) for the grid,
  3. writes src/data/portfolio.json (editable in Decap → „Portfolio — wybrane zdjęcia”).

Usage: python3 tools/import-wp-portfolio.py [--limit 86] [--force]
Cache: $TMPDIR/wp-portfolio-import/
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

SITE = "https://www.annamatejska.pl"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("TMPDIR", "/tmp").rstrip("/") + "/wp-portfolio-import"
FFMPEG = "/home/michal/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
OUT_DIR = os.path.join(REPO, "public/images/portfolio")
JSON_PATH = os.path.join(REPO, "src/data/portfolio.json")
PUBLIC_PREFIX = "/annamatejska.pl/images/portfolio"


def safe_url(url):
    # URLs from the WP site contain raw non-ASCII (e.g. „DSC_6342 — kopia”) — encode them
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc,
                                    urllib.parse.quote(parts.path), parts.query, parts.fragment))


def fetch(url, binary=False):
    url = safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def strip_size(name):
    return re.sub(r"-\d{2,4}x\d{2,4}(?=\.[A-Za-z]+$)", "", name)


def collect_urls():
    html = fetch(f"{SITE}/portfolio/")
    # src + data-src (the grid is lazy-loaded), ignore the badge/logo/icons
    raw = re.findall(r'(?:data-src|src)="(https://www\.annamatejska\.pl/wp-content/uploads/[^"]+\.(?:jpg|jpeg|png))"', html)
    if not raw:
        raw = re.findall(r"https://www\.annamatejska\.pl/wp-content/uploads/[^\"'\s)]+\.(?:jpg|jpeg|png)", html)
    candidates = {}
    order = []
    for u in raw:
        base = os.path.basename(u)
        if re.search(r"LOGA|cropped|-\d{2,4}x\d{2,4}\.png$|ebook|logo", base, re.I):
            continue
        key = strip_size(base)
        if key not in candidates:
            candidates[key] = []
            order.append(key)
        # prefer the un-suffixed original
        if base == key:
            candidates[key].insert(0, u)
        else:
            candidates[key].append(u)
    return [(k, candidates[k]) for k in order]


def resolve(cands):
    """Return the first URL that actually exists (originals may be -scaled variants)."""
    for u in cands:
        try:
            req = urllib.request.Request(safe_url(u), headers={"User-Agent": UA}, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return u
        except Exception:
            continue
    return cands[0] if cands else None



def process(job):
    idx, name, url = job
    raw = os.path.join(CACHE, "src-" + name)
    if not os.path.exists(raw):
        try:
            open(raw, "wb").write(fetch(url, binary=True))
        except Exception as exc:
            return (idx, f"download failed: {exc}")
    full = os.path.join(OUT_DIR, f"{idx:02d}.jpg")
    thumb = os.path.join(OUT_DIR, f"{idx:02d}-thumb.jpg")
    try:
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", raw,
                        "-vf", "scale='min(1600,iw)':-2", "-q:v", "4", full], check=True)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", raw,
                        "-vf", "scale='min(800,iw)':-2", "-q:v", "5", thumb], check=True)
    except subprocess.CalledProcessError as exc:
        return (idx, f"ffmpeg failed: {exc}")
    return (idx, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=86)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    print("→ fetching /portfolio/ …")
    entries = collect_urls()[: args.limit]
    print(f"  {len(entries)} unique photos, resolving originals …")
    urls = []
    for k, cands in entries:
        u = resolve(cands)
        if u:
            urls.append((k, u))
    print(f"  {len(urls)} urls resolved")

    jobs = [(i, name, url) for i, (name, url) in enumerate(urls, 1)]
    failed = []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for idx, err in pool.map(process, jobs):
            if err:
                failed.append((idx, err))
            if (idx % 20) == 0:
                print(f"   {idx}/{len(jobs)}")

    items = []
    for i, (name, url) in enumerate(urls, 1):
        if any(f[0] == i for f in failed):
            continue
        items.append({
            "photo": f"{PUBLIC_PREFIX}/{i:02d}.jpg",
            "thumb": f"{PUBLIC_PREFIX}/{i:02d}-thumb.jpg",
            "alt": "",
        })

    json.dump({"items": items}, open(JSON_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    open(JSON_PATH, "a").write("\n")
    print(f"✓ wrote {JSON_PATH}: {len(items)} photos, {len(failed)} failures")
    for idx, err in failed[:8]:
        print("   !", idx, err)


if __name__ == "__main__":
    sys.exit(main())
