"""Clean the building concepts (background off, palette snap, stray marks dropped) into clean/, and
stand each on village ground beside a peasant and the Wanderer at game scale into review/.

Run from the repo root: .venv/bin/python art/drafts/village/preview.py
"""
import sys
from collections import deque
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tools")
from snap_palette import drop_specks, snap

D = Path("art/drafts/village")
GROUND = Image.open("art/tiles/village/village_ground_hd.png").convert("RGBA").crop((15 * 64, 0, 16 * 64, 64))
PEASANT = Image.open("art/characters/peasant/peasant_hd_idle.png").convert("RGBA").crop((0, 0, 64, 96))
WANDERER = Image.open("art/characters/wanderer_hd/wanderer_hd_idle.png").convert("RGBA").crop((0, 0, 96, 96))
# How close to the corner colour a pixel must be to count as background, and how small a stray
# island (a signature, a speck) gets dropped.
BACKGROUND_TOLERANCE = 28
STRAY = 60


def background_off(img):
    """Flood the flat background in from the edges and clear it."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    base = px[0, 0][:3]
    near = lambda p: px[p][3] == 0 or sum(abs(a - b) for a, b in zip(px[p][:3], base)) < BACKGROUND_TOLERANCE
    todo = deque((x, y) for x in range(w) for y in (0, h - 1)) + deque((x, y) for y in range(h) for x in (0, w - 1))
    seen = set()
    while todo:
        p = todo.popleft()
        if p in seen or not near(p):
            continue
        seen.add(p)
        px[p] = (0, 0, 0, 0)
        x, y = p
        todo.extend(n for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if 0 <= n[0] < w and 0 <= n[1] < h)
    return img


def scene(building):
    """The building with its base on the ground, the peasant and the Wanderer standing to its right."""
    w = building.width + 220
    h = max(building.height, 96) + 40
    out = Image.new("RGBA", (w, h))
    for x in range(0, w, 64):
        for y in range(0, h, 64):
            out.alpha_composite(GROUND, (x, y))
    floor = h - 16
    out.alpha_composite(building, (10, floor - building.height))
    out.alpha_composite(PEASANT, (building.width + 20, floor - 96))
    out.alpha_composite(WANDERER, (building.width + 100, floor - 96))
    return out


for src in sorted((D / "concepts").glob("*.png")):
    clean = drop_specks(snap(background_off(Image.open(src))), STRAY)
    clean = clean.crop(clean.getbbox())
    (D / "clean").mkdir(exist_ok=True)
    (D / "review").mkdir(exist_ok=True)
    clean.save(D / "clean" / src.name)
    view = scene(clean)
    view.resize((view.width * 2, view.height * 2), Image.NEAREST).save(D / "review" / src.name)
    print(src.name, clean.size)
