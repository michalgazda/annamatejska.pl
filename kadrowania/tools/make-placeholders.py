#!/usr/bin/env python3
"""Generate dark, cinematic placeholder photos for the kadrowania site.

Writes into kadrowania/images/ -- hero images plus numbered folders per
portfolio category. Renders soft, out-of-focus, low-key "photos"
(near-black gradient + moody light pools + grain + vignette) in a muted
dark palette. Output is seeded, so re-running reproduces the same files.

Usage:
  python3 tools/make-placeholders.py            # regenerate everything
  python3 tools/make-placeholders.py --quality 80
"""
import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent          # kadrowania/
OUT = ROOT / "images"
SIZE = 1600                                             # long edge

# Palette = (shadow, midtone, [light accents]); near-black bases per family.
PALETTES = {
    "hero":     ("#050505", "#1a1713", ["#c9a26a", "#8a6a42", "#4a3a28", "#e8d5b0"]),
    "komercyjne": ("#0a0a0a", "#242220", ["#d8d2c4", "#8f887a", "#5a554c", "#b0a894"]),
    "wizerunkowe": ("#0b0908", "#2a201a", ["#caa06a", "#7a5c3e", "#3e3228", "#e2c496"]),
    "biznesowe": ("#08090a", "#1c2226", ["#9fb2bd", "#5a6d7a", "#2e3a42", "#c8d5dc"]),
    "eventy":   ("#0a0709", "#251a20", ["#b8849a", "#6a4a58", "#3a2a32", "#dcb0c0"]),
}


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def base_gradient(shadow, midtone, w, h, rnd):
    """Near-black diagonal gradient with a slightly lifted zone."""
    ramp = Image.linear_gradient("L").resize((w, h))
    sc = Image.new("RGB", (w, h), hex2rgb(shadow))
    mc = Image.new("RGB", (w, h), hex2rgb(midtone))
    grad = Image.composite(mc, sc, ramp)
    pad = int(max(w, h) * 1.8)
    canvas = Image.new("RGB", (pad, pad), hex2rgb(shadow))
    canvas.paste(grad, ((pad - w) // 2, (pad - h) // 2))
    canvas = canvas.rotate(rnd.uniform(-30, 30), resample=Image.Resampling.BICUBIC)
    x, y = (pad - w) // 2, (pad - h) // 2
    return canvas.crop((x, y, x + w, y + h))


def moody_lights(img, lights, rnd):
    """A few very soft, dim light pools -- like a lit subject / window."""
    w, h = img.size
    for _ in range(rnd.randint(2, 4)):
        col = hex2rgb(rnd.choice(lights))
        # Dim the accent way down so highlights stay filmic, not blown.
        col = tuple(int(c * rnd.uniform(0.35, 0.6)) for c in col)
        rx = rnd.randint(int(w * 0.10), int(w * 0.30))
        ry = int(rx * rnd.uniform(0.7, 1.4))
        cx, cy = rnd.randint(0, w), rnd.randint(0, h)
        blob = Image.new("RGB", (w, h), (0, 0, 0))
        d = ImageDraw.Draw(blob)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
        blob = blob.filter(ImageFilter.GaussianBlur(rnd.randint(150, 280)))
        img = ImageChops.screen(img, blob)
    return img


def grain(img, amount):
    noise = Image.effect_noise(img.size, 10).convert("L")
    g = noise.point(lambda v: 128 + (v - 128) * amount // 128)
    return ImageChops.soft_light(img, g.convert("RGB"))


def vignette(img, strength):
    vig = Image.radial_gradient("L").resize(img.size)
    factor = vig.point(lambda v: 255 - int(v * strength))
    ch = [ImageChops.multiply(img.getchannel(c), factor) for c in range(3)]
    return Image.merge("RGB", ch)


def letterbars(img, rnd):
    """Occasional subtle cinematic crop-bars baked into the frame."""
    if rnd.random() < 0.45:
        w, h = img.size
        bar = int(h * rnd.uniform(0.05, 0.09))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, w, bar], fill=(2, 2, 2))
        d.rectangle([0, h - bar, w, h], fill=(2, 2, 2))
    return img


def make_one(palette, seed, landscape):
    shadow, midtone, lights = PALETTES[palette]
    rnd = random.Random(seed)
    w, h = (SIZE, int(SIZE * 0.72)) if landscape else (int(SIZE * 0.72), SIZE)
    img = base_gradient(shadow, midtone, w, h, rnd)
    img = moody_lights(img, lights, rnd)
    img = grain(img, rnd.randint(60, 100))
    img = vignette(img, rnd.randint(46, 62))
    img = letterbars(img, rnd)
    return img.point(lambda v: min(255, max(0, int(v * 1.05 + 2))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", type=int, default=84)
    args = ap.parse_args()

    total = 0

    def save(img, rel):
        nonlocal total
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, "JPEG", quality=args.quality, optimize=True)
        total += 1
        print(f"  images/{rel}  ({img.size[0]}x{img.size[1]})")

    # Hero: wide, darkest of all.
    save(make_one("hero", 20260906, True), "hero.jpg")
    save(make_one("hero", 777001, False), "manifesto.jpg")

    # Portfolio categories: 4 photos each, numbered folders.
    counts = {"komercyjne": 4, "wizerunkowe": 4, "biznesowe": 4, "eventy": 4}
    for cat, n in counts.items():
        print(f"[{cat}]")
        for i in range(n):
            img = make_one(cat, hash_seed := 9100 + abs(hash(cat)) % 9973 + i * 977, i % 2 == 0)
            save(img, f"portfolio/{cat}/{i + 1:02d}.jpg")

    print(f"\nWrote {total} placeholder image(s) into kadrowania/images/")


if __name__ == "__main__":
    main()
