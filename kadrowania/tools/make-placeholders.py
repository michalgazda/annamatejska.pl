#!/usr/bin/env python3
"""Generate light, soft placeholder photos for the kadrowania site.

Writes into kadrowania/images/ -- hero images plus numbered folders per
portfolio category. Renders gentle, bright, out-of-focus "photos"
(near-white gradient + soft light pools + grain + vignette) in a light
monochrome palette, with occasional baked-in composition guides so each
frame feels like a plausible scene. Output is seeded, so re-running
reproduces the same files.

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

# Palette = (shadow, midtone, regions); light monochrome bases per family.
PALETTES = {
    "hero":        ("#c9c6c0", "#ecebe8", ["#ffffff", "#dcdbd8", "#bfbfb8"]),
    "wydarzenia":  ("#c8c5bf", "#ecebe7", ["#ffffff", "#dddcd8", "#b8b5ae"]),
    "architektura":("#b9c0c2", "#e6e9ea", ["#ffffff", "#d3dfe2", "#9fb0b4"]),
    "podroze":     ("#c6cdc2", "#ebefe8", ["#ffffff", "#dde6da", "#aab8a6"]),
}


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def base_gradient(shadow, midtone, w, h, rnd):
    """Light diagonal gradient with a slightly shaded zone."""
    ramp = Image.linear_gradient("L").resize((w, h))
    sc = Image.new("RGB", (w, h), hex2rgb(shadow))
    mc = Image.new("RGB", (w, h), hex2rgb(midtone))
    grad = Image.composite(mc, sc, ramp)
    pad = int(max(w, h) * 1.8)
    canvas = Image.new("RGB", (pad, pad), hex2rgb(shadow))
    canvas.paste(grad, ((pad - w) // 2, (pad - h) // 2))
    canvas = canvas.rotate(rnd.uniform(-12, 12), resample=Image.Resampling.BICUBIC)
    x, y = (pad - w) // 2, (pad - h) // 2
    return canvas.crop((x, y, x + w, y + h))


def soft_lights(img, lights, rnd):
    """A few very soft, bright pools -- like light falling on a subject."""
    w, h = img.size
    for _ in range(rnd.randint(2, 4)):
        col = hex2rgb(rnd.choice(lights))
        # Keep bright but slightly below pure white so it stays soft.
        col = tuple(int(c * rnd.uniform(0.85, 1.0)) for c in col)
        rx = rnd.randint(int(w * 0.12), int(w * 0.34))
        ry = int(rx * rnd.uniform(0.7, 1.4))
        cx, cy = rnd.randint(0, w), rnd.randint(0, h)
        blob = Image.new("RGB", (w, h), (0, 0, 0))
        d = ImageDraw.Draw(blob)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
        blob = blob.filter(ImageFilter.GaussianBlur(rnd.randint(140, 260)))
        img = ImageChops.screen(img, blob)
    return img


def grain(img, amount):
    noise = Image.effect_noise(img.size, 8).convert("L")
    g = noise.point(lambda v: 128 + (v - 128) * amount // 128)
    return ImageChops.soft_light(img, g.convert("RGB"))


def vignette(img, strength):
    """Subtle darkening toward the corners; center stays full brightness.
    strength is a fraction (e.g. 0.08-0.2)."""
    vig = Image.radial_gradient("L").resize(img.size)
    # radial_gradient: center = 255 (bright), edges = 0 (dark).
    # factor: center -> 255, edges -> 255 - 255*strength (only corners dim).
    factor = vig.point(lambda v: int(255 - (255 - v) * strength))
    ch = [ImageChops.multiply(img.getchannel(c), factor) for c in range(3)]
    return Image.merge("RGB", ch)


def make_one(palette, seed, landscape):
    shadow, midtone, lights = PALETTES[palette]
    rnd = random.Random(seed)
    w, h = (SIZE, int(SIZE * 0.72)) if landscape else (int(SIZE * 0.72), SIZE)
    img = base_gradient(shadow, midtone, w, h, rnd)
    img = soft_lights(img, lights, rnd)
    img = grain(img, rnd.randint(30, 55))
    img = vignette(img, rnd.uniform(0.08, 0.16))
    return img.point(lambda v: min(255, max(0, int(v * 1.02 + 2))))


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

    # Hero: wide horizontal; manifesto: portrait.
    save(make_one("hero", 20260907, True), "hero.jpg")
    save(make_one("hero", 777101, False), "manifesto.jpg")

    # Portfolio categories: 4 photos each, numbered folders.
    counts = {"wydarzenia": 4, "architektura": 4, "podroze": 4}
    for cat, n in counts.items():
        print(f"[{cat}]")
        for i in range(n):
            img = make_one(cat, hash_seed := 9100 + abs(hash(cat)) % 9973 + i * 977, i % 2 == 0)
            save(img, f"portfolio/{cat}/{i + 1:02d}.jpg")

    print(f"\nWrote {total} placeholder image(s) into kadrowania/images/")


if __name__ == "__main__":
    main()
