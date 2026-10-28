"""Render a 960x540 mock of the game view from a draft ground sheet, using the game's dual-grid layering.

Usage: .venv/bin/python art/drafts/ground/scene.py <sheet.png> <out.png> [seed]
"""
import math
import random
import sys

from PIL import Image

T, W, H = 64, 15, 9
sheet_path, out, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1
tiles = Image.open(sheet_path)
rng = random.Random(seed)
blobs = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.2, 3), rng.choice([1, 1, 2, 2, 3])) for _ in range(14)]


def corner(x, y):
    hit = [g for bx, by, r, g in blobs if math.hypot(x - bx, (y - by) * 1.2) < r]
    return max(hit) if hit else 0


view = Image.new("RGBA", (W * T, H * T))
for ty in range(H):
    for tx in range(W):
        corners = [corner(tx, ty), corner(tx + 1, ty), corner(tx, ty + 1), corner(tx + 1, ty + 1)]
        for i, g in enumerate(sorted(set(corners))):
            mask = sum(1 << b for b, c in enumerate(corners) if c == g)
            col = 15 + (tx * 7 + ty * 13) % 4 if i == 0 or mask == 15 else mask
            tile = tiles.crop((col * T, g * T, col * T + T, g * T + T))
            view.alpha_composite(tile, (tx * T, ty * T))

shadow = Image.new("RGBA", (36, 10))
for y in range(10):
    for x in range(36):
        if ((x - 17.5) / 18) ** 2 + ((y - 4.5) / 5) ** 2 < 1:
            shadow.putpixel((x, y), (11, 10, 13, 110))


def put(sheet, frame, row, fw, fh, feet, x, y):
    img = Image.open(sheet).crop((frame * fw, row * fh, frame * fw + fw, row * fh + fh))
    view.alpha_composite(shadow, (x - 18, y - 5))
    view.alpha_composite(img, (x - fw // 2, y - feet))


put("art/props/hollow_bodies.png", 1, 0, 96, 96, 94, 700, 330)
put("art/characters/wanderer_hd/wanderer_hd_idle.png", 0, 0, 96, 96, 94, 470, 300)
put("art/enemies/hollow_hd/hollow_hd_walk.png", 2, 1, 64, 96, 94, 640, 250)
put("art/enemies/hollow_hd/hollow_hd_idle.png", 0, 2, 64, 96, 94, 280, 400)
view.crop((0, 0, 960, 540)).convert("RGB").save(out)
print(out)
