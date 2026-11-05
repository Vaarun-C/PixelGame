"""Snap AI output to the master palette (world colors only) with hard alpha.

Usage: .venv/bin/python tools/snap_palette.py <in.png> <out.png>
"""
import sys
from PIL import Image
from check_art import load_palette

WORLD = [rgb for rgb, name in load_palette().items() if not name.startswith("rune-")]


def distance(a, b):
    """Redmean-weighted RGB distance: cheap and close to perceived difference."""
    rm = (a[0] + b[0]) / 2
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return (2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db


def nearest(rgb, cache={}):
    if rgb not in cache:
        cache[rgb] = min(WORLD, key=lambda c: distance(rgb, c))
    return cache[rgb]


def snap(img):
    img = img.convert("RGBA")
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a >= 128:
                out.putpixel((x, y), nearest((r, g, b)) + (255,))
    return drop_specks(out)


def drop_specks(img, max_size=2):
    """Clear tiny islands of opaque pixels (AI noise) not touching the main sprite."""
    w, h = img.size
    px = img.load()
    seen = set()
    for start in ((x, y) for y in range(h) for x in range(w)):
        if start in seen or px[start][3] == 0:
            continue
        island, stack = [], [start]
        seen.add(start)
        while stack:
            x, y = stack.pop()
            island.append((x, y))
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)):
                if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and px[n][3]:
                    seen.add(n)
                    stack.append(n)
        if len(island) <= max_size:
            for p in island:
                px[p] = (0, 0, 0, 0)
    return img


COLORS = {name: rgb for rgb, name in load_palette().items()}


def step_down(name):
    family, _, level = name.rpartition("-")
    if level.isdigit() and int(level) > 0 and f"{family}-{int(level) - 1}" in COLORS:
        return f"{family}-{int(level) - 1}"
    return {"bone-0": "ash-4"}.get(name, name)


def despeckle(img):
    """AI speckle: a pixel unlike all 8 neighbours takes its side neighbours' most common colour."""
    px = img.load()
    w, h = img.size
    fixes = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not px[x, y][3]:
                continue
            around = [px[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            corners = [px[x + dx, y + dy] for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1))]
            if px[x, y] not in around + corners and all(a[3] for a in around):
                fixes.append(((x, y), max(set(around), key=around.count)))
    for xy, colour in fixes:
        px[xy] = colour
    return img


if __name__ == "__main__":
    snap(Image.open(sys.argv[1])).save(sys.argv[2])
