#!/usr/bin/env python3
"""Import real galleries from the old WordPress site into src/data/galleries.json.

The live WordPress site (still online) exposes its sessions/reportages as posts via
the REST API; every post body holds the session photos. This tool:

  1. downloads the media index (wp-json/wp/v2/media) and maps each photo to the best
     WP-generated size (1536px preferred, then 1024px),
  2. walks the posts, groups their photos into one gallery per post,
  3. downloads + downscales the photos into public/images/galleries/<slug>/NN.jpg,
  4. rewrites src/data/galleries.json (title/date/category/excerpt/cover/photos_list).

Usage:  python3 tools/import-wp-galleries.py [--max-per-gallery 12] [--force]
        --full-max 2400   long edge of the stored photo (originals are 3000-6000px)
        --quality 3       ffmpeg -q:v for the full photo
        --no-thumbs       skip the 900px grid thumbnails
Cache:  $TMPDIR/wp-gallery-import/ (media index + downloaded originals)
"""
import argparse
import concurrent.futures as cf
import html
import json
import os
import re
import subprocess
import sys
import urllib.request

SITE = "https://www.annamatejska.pl"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("TMPDIR", "/tmp").rstrip("/") + "/wp-gallery-import"
FFMPEG = "/home/michal/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
MAX_FULL = 2400
MAX_QUALITY = 3
OUT_DIR = os.path.join(REPO, "public/images/galleries")
THUMB_SUFFIX = "-thumb"
JSON_PATH = os.path.join(REPO, "src/data/galleries.json")

try:
    from PIL import Image  # optional, not required
except Exception:  # pragma: no cover
    Image = None


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def api(path):
    return json.loads(fetch(f"{SITE}/wp-json/wp/v2/{path}"))


def load_media_index(force=False):
    os.makedirs(CACHE, exist_ok=True)
    idx = {}
    page = 1
    while True:
        path = os.path.join(CACHE, f"media-{page}.json")
        if force or not os.path.exists(path):
            try:
                body = fetch(f"{SITE}/wp-json/wp/v2/media?per_page=100&page={page}")
            except Exception as exc:
                print(f"  media page {page}: {exc}")
                break
            open(path, "w").write(body)
        items = json.load(open(path))
        if not items:
            break
        for it in items:
            src = it.get("source_url") or ""
            details = it.get("media_details") or {}
            sizes = details.get("sizes") or {}
            # originals (source_url / the „full” size) — Anna asked for the uncompressed files
            best = (sizes.get("full") or {}).get("source_url") or src
            names = {os.path.basename(src)}
            names.add(os.path.basename(src).replace("-scaled", ""))
            for n in list(names):
                root, ext = os.path.splitext(n)
                names.add(root.replace("-scaled", "") + ext)
            for n in names:
                idx[n] = best
        page += 1
        if page > 40:
            break
    print(f"  media index: {len(idx)} filenames")
    return idx


def strip_size(name):
    return re.sub(r"-\d{2,4}x\d{2,4}(?=\.[A-Za-z]+$)", "", name)


# slug -> gallery category. Everything not listed falls back to Reportaże.
CATEGORY_RULES = [
    (r"^sesja-rodzinna|^sesja-gosi", "Sesje rodzinne"),
    (r"^sesja-kobieca|kobieca-sesja|^emilia-psycholozka", "Sesje kobiece"),
    (r"^marysia|^agnieszka-|^ania-i-piotrek|^weronika-|^paulina-|wizerunkow", "Sesje wizerunkowe"),
    # „Warsztaty dla kobiet w ciąży” is an event reportage, not a session
    (r"^warsztaty-dla-kobiet-w-ciazy", "Reportaże"),
    (r"^sesja-ciazowa|ciaz", "Sesje ciążowe"),
    (r"^sesja-romantyczna|romantyczn", "Sesje romantyczne"),
    (r"^sesja-dziecie|dziecie|dzieci", "Sesje dziecięce"),
]

EXCERPT_BY_CATEGORY = {
    "Sesje rodzinne": "Sesja rodzinna w plenerze — naturalne kadry, bez pozowania.",
    "Sesje kobiece": "Sesja kobieca — światło, spokój i uważność.",
    "Sesje wizerunkowe": "Sesja wizerunkowa — naturalnie i profesjonalnie.",
    "Sesje ciążowe": "Sesja ciążowa — czułość i oczekiwanie w kadrze.",
    "Sesje romantyczne": "Sesja dla dwojga — bliskość i wspólny czas.",
    "Sesje dziecięce": "Sesja dziecięca — zabawa, ruch i prawdziwe emocje.",
    "Reportaże": "Reportaż z wydarzenia — emocje zamiast pozowania.",
}

# posts to ignore (empty or duplicate content)
SKIP_SLUGS = {"wizerunkowe", "tydzien-malzenstwa-w-krakowie", "carnavaldetenerife"}


def category_for(slug):
    for pattern, cat in CATEGORY_RULES:
        if re.search(pattern, slug):
            return cat
    return "Reportaże"


def photos_of(post, media):
    content = (post.get("content") or {}).get("rendered", "")
    urls = re.findall(
        r"https://www\.annamatejska\.pl/wp-content/uploads/[^\"'\s)]+\.(?:jpg|jpeg|png)",
        content,
    )
    out, seen = [], set()
    for u in urls:
        name = strip_size(os.path.basename(u))
        if name in seen:
            continue
        seen.add(name)
        out.append((name, media.get(name) or media.get(os.path.basename(u)) or u))
    return out


def download(args):
    name, url, dest = args
    is_thumb = "-thumb" in os.path.basename(dest)
    long_edge = 900 if is_thumb else MAX_FULL
    quality = 5 if is_thumb else MAX_QUALITY
    raw = os.path.join(CACHE, "src-" + name)
    if not os.path.exists(raw):
        try:
            data = fetch(url, binary=True)
        except Exception as exc:
            return (dest, f"download failed: {exc}")
        open(raw, "wb").write(data)
    try:
        subprocess.run(
            [FFMPEG, "-y", "-loglevel", "error", "-i", raw,
             "-vf", f"scale='min({long_edge},iw)':-2", "-q:v", str(quality), dest],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        return (dest, f"ffmpeg failed: {exc}")
    return (dest, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-per-gallery", type=int, default=12)
    ap.add_argument("--full-max", type=int, default=2400, help="long edge of the stored photo")
    ap.add_argument("--quality", type=int, default=3, help="ffmpeg -q:v for the full photo")
    ap.add_argument("--no-thumbs", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    global MAX_FULL, MAX_QUALITY, THUMB_SUFFIX
    MAX_FULL, MAX_QUALITY = args.full_max, args.quality
    if args.no_thumbs:
        THUMB_SUFFIX = ""

    os.makedirs(CACHE, exist_ok=True)
    print("→ media index")
    media = load_media_index(args.force)
    print("→ posts")
    posts = api("posts?per_page=100")
    posts.sort(key=lambda p: p["date"], reverse=True)

    galleries, used_photos = [], set()
    for post in posts:
        slug = post["slug"]
        if slug in SKIP_SLUGS:
            continue
        pics = [p for p in photos_of(post, media) if p[0] not in used_photos]
        if len(pics) < 3:
            print(f"  skip {slug}: only {len(pics)} photos")
            continue
        cat = category_for(slug)
        keep = pics[: args.max_per_gallery]
        galleries.append({
            "slug": slug,
            "title": html.unescape(re.sub("<[^>]+>", "", post["title"]["rendered"])).strip(),
            "category": cat,
            "date": post["date"][:10],
            "excerpt": EXCERPT_BY_CATEGORY.get(cat, "Galeria zdjęć."),
            "photos": len(keep),
            "photos_list": [f"/annamatejska.pl/images/galleries/{slug}/{i:02d}{THUMB_SUFFIX}.jpg"
                            for i in range(1, len(keep) + 1)],
            "cover": f"/annamatejska.pl/images/galleries/{slug}/01{THUMB_SUFFIX}.jpg",
            "_src": keep,
        })
        for name, _url in keep:
            used_photos.add(name)

    # drop galleries that duplicate an earlier one (near-identical photo sets)
    deduped = []
    for g in galleries:
        setg = {n for n, _ in g["_src"]}
        dup = False
        for kept in deduped:
            other = {n for n, _ in kept["_src"]}
            if not other:
                continue
            overlap = len(setg & other) / max(1, len(setg | other))
            if overlap > 0.6:
                print(f"  duplicate: {g['slug']} ≈ {kept['slug']} ({overlap:.0%})")
                dup = True
                break
        if not dup:
            deduped.append(g)
    galleries = deduped

    total = sum(len(g["_src"]) for g in galleries)
    print(f"→ {len(galleries)} galleries, {total} photos to fetch")

    jobs = []
    for g in galleries:
        d = os.path.join(OUT_DIR, g["slug"])
        os.makedirs(d, exist_ok=True)
        for i, (name, url) in enumerate(g["_src"], 1):
            jobs.append((name, url, os.path.join(d, f"{i:02d}.jpg")))
            if not args.no_thumbs:
                jobs.append((name, url, os.path.join(d, f"{i:02d}-thumb.jpg")))

    done, failed = 0, []
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for dest, err in pool.map(download, jobs):
            if err:
                failed.append((dest, err))
            else:
                done += 1
            if (done + len(failed)) % 25 == 0:
                print(f"   {done + len(failed)}/{len(jobs)}")

    # a gallery whose cover failed is useless — drop it and its photos_list tail
    drop = set()
    cover_name = f"01{THUMB_SUFFIX}.jpg"
    for g in galleries:
        d = os.path.join(OUT_DIR, g["slug"])
        present = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
        if cover_name not in present:
            print(f"  dropping {g['slug']} (cover missing)")
            drop.add(g["slug"])
            continue
        sized = [f for f in present if not f.endswith("-thumb.jpg")] if THUMB_SUFFIX else present
        n = min(len(sized), len(g["photos_list"]))
        if n < len(g["photos_list"]):
            g["photos_list"] = g["photos_list"][:n]
            g["photos"] = n
    galleries = [g for g in galleries if g["slug"] not in drop]
    for g in galleries:
        g.pop("_src", None)

    galleries.sort(key=lambda g: (g["category"] != "Reportaże", g["date"]), reverse=False)
    galleries.sort(key=lambda g: g["date"], reverse=True)
    json.dump({"galleries": galleries}, open(JSON_PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    open(JSON_PATH, "a").write("\n")
    print(f"✓ wrote {JSON_PATH}: {len(galleries)} galleries, "
          f"{sum(g['photos'] for g in galleries)} photos, {len(failed)} failures")
    for dest, err in failed[:10]:
        print("   !", dest, err)


if __name__ == "__main__":
    sys.exit(main())
