#!/usr/bin/env python3
"""Generate tasteful, palette-matched placeholder photos for a gallery.

DEV helper for populating sample galleries before Anna delivers real photos.
It renders soft, out-of-focus, editorial "photos" (gradient + light blobs +
grain + vignette) in the site's taupe/ivory family.

Each output is a 1200x1200 square; the CSS grid's object-fit:cover crops it to
wide/tall tiles and the lightbox shows the square. Photos are seeded, so
re-running with the same --seed reproduces them exactly.

Usage:
  python3 tools/make-placeholder.py --slug sesja-kobieca-studio \
      --palette studio --count 6 [--seed 7]

Palettes (3-4 colors each the renderer mixes): autumn, spring, studio,
maternity, dusk, slate. Anna replaces the whole images/galleries/<slug>/
folder with real photos — then these placeholders simply go away.
"""
import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SIZE = 1200

# Palette = (base_top, base_bottom, [light colors])
PALETTES = {
    # warm ambers / olive / rust — family, autumn Kraków
    "autumn":    ("#8a6f4a", "#3d2f22", ["#e8c78a", "#d9a86a", "#c98b4e", "#f0dcb4"]),
    # soft sage / blush / cream — kids, spring
    "spring":    ("#cdb99a", "#8f9a7f", ["#f2e6d2", "#e6c7b8", "#dfe3c9", "#f6efe2"]),
    # neutral taupe / warm grey / soft gold — women, studio
    "studio":    ("#c2b39f", "#6d5f52", ["#efe6d8", "#d8c4a8", "#c8b79f", "#f4ede1"]),
    # ivory / muted rose / sage — pregnancy, plenteer
    "maternity": ("#d8c3b4", "#9c8a86", ["#f3e8dc", "#e9cfc4", "#d9d8c4", "#f7efe6"]),
    # terracotta / dusk plum / warm amber — couple, sunset
    "dusk":      ("#7d5a52", "#3a2a30", ["#e2a678", "#c98b6a", "#9a6a72", "#f0cfa0"]),
    # cool neutral / slate / warm grey — business portrait
    "slate":     ("#a9a294", "#54504a", ["#e8e3d8", "#cfc7b8", "#b8b0a2", "#f2efe8"]),
}


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def vertical_gradient(top, bottom, w, h, angle_deg=0.0):
    """Smooth 2-colour vertical gradient, optionally rotated by angle_deg."""
    ramp = Image.linear_gradient("L").resize((w, h))  # 0 top -> 255 bottom
    tc = Image.new("RGB", (w, h), hex2rgb(top))
    bc = Image.new("RGB", (w, h), hex2rgb(bottom))
    grad = Image.composite(tc, bc, ramp)
    if angle_deg:
        # render bigger so rotated corners don't clip, then center-crop back
        pad = int(max(w, h) * 1.7)
        canvas = Image.new("RGB", (pad, pad), hex2rgb(top))
        canvas.paste(grad, ((pad - w) // 2, (pad - h) // 2))
        canvas = canvas.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=False)
        x = (pad - w) // 2
        y = (pad - h) // 2
        grad = canvas.crop((x, y, x + w, y + h))
    return grad


def add_light_blobs(img, light_colors, rnd):
    """Screen a few large, very-soft light discs for an out-of-focus feel."""
    w, h = img.size
    n = rnd.randint(3, 5)
    for _ in range(n):
        col = hex2rgb(rnd.choice(light_colors))
        r = rnd.randint(int(w * 0.18), int(w * 0.45))
        cx, cy = rnd.randint(0, w), rnd.randint(0, h)
        blob = Image.new("RGB", (w, h), (0, 0, 0))
        d = ImageDraw.Draw(blob)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        blob = blob.filter(ImageFilter.GaussianBlur(rnd.randint(120, 240)))
        img = ImageChops.screen(img, blob)
    return img


def add_grain(img, amount):
    """Add subtle monochrome film grain via a soft-light layer."""
    noise = Image.effect_noise(img.size, 8).convert("L")
    # recentre around mid-grey and scale by `amount` (0..~150)
    grain = noise.point(lambda v: max(0, min(255, 128 + (v - 128) * amount // 128)))
    return ImageChops.soft_light(img, grain.convert("RGB"))


def add_vignette(img, strength=0.35):
    """Darken toward the corners using a radial factor map (numpy-free)."""
    vig = Image.radial_gradient("L").resize(img.size)  # 0 center -> 255 edge
    factor = vig.point(lambda v: 255 - int(v * strength))  # 255 center -> ~165 edge
    # getchannel() returns a fresh image, so build each channel then merge
    channels = [ImageChops.multiply(img.getchannel(ch), factor) for ch in range(3)]
    return Image.merge("RGB", channels)


def make_one(palette, seed):
    top, bottom, lights = PALETTES[palette]
    rnd = random.Random(seed)
    img = vertical_gradient(top, bottom, SIZE, SIZE, angle_deg=rnd.uniform(-18, 18))
    img = add_light_blobs(img, lights, rnd)
    img = add_grain(img, rnd.randint(70, 120))
    img = add_vignette(img, strength=rnd.uniform(0.28, 0.42))
    # gentle editorial contrast lift
    img = img.point(lambda v: min(255, int(v * 1.03 + 4)))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--palette", choices=sorted(PALETTES), default="studio")
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    img_dir = ROOT / "images/galleries" / args.slug
    img_dir.mkdir(parents=True, exist_ok=True)
    for i in range(args.count):
        img = make_one(args.palette, seed=args.seed + i * 977)
        out = img_dir / f"{i + 1:02d}.jpg"
        img.save(out, "JPEG", quality=82, optimize=True)
        print(f"✓ {out.relative_to(ROOT)}  ({img.size[0]}x{img.size[1]})")
    print(f"\nWrote {args.count} placeholder photo(s) into images/galleries/{args.slug}/")
    print(f"Next: python3 tools/new-gallery.py --slug {args.slug} --title \"...\" "
          "--category \"...\" --date YYYY-MM-DD")


if __name__ == "__main__":
    main()
