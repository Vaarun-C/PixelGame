"""Automated ART_RULES cleanup for palette-snapped AI sprites.

Usage: .venv/bin/python tools/cleanup_sprite.py <in.png> <out.png>
Fixes: orphan-pixel noise, cape and tabard repainted with one cloth ramp and hanging folds,
worn cloth edges (torn hem, frayed tabard, stain), shadow-side outline.
"""
import sys
from collections import Counter
from PIL import Image
from check_art import load_palette

NAMES = load_palette()
RGB = {name: rgb for rgb, name in NAMES.items()}
AROUND = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy]
CROSS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
SCARF_ABOVE_BOTTOM = 74  # sprites sit on the canvas bottom; the scarf ends this far above it


def ramp(c):
    return c.split("-")[0] if c else None


def shade(c):
    return int(c.split("-")[1])


class Grid:
    def __init__(self, img):
        self.w, self.h = img.size
        self.px = [[NAMES[img.getpixel((x, y))[:3]] if img.getpixel((x, y))[3] else None
                    for x in range(self.w)] for y in range(self.h)]

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def cells(self):
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.px[y][x]]

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for x, y in self.cells():
            img.putpixel((x, y), RGB[self.px[y][x]] + (255,))
        return img


def denoise(g):
    """Pixels matching none of their neighbours take the neighbour colour closest in value.
    Edge pixels count too, except the outline itself."""
    src = [row[:] for row in g.px]
    for x, y in g.cells():
        near = [n for dx, dy in AROUND if (n := src[y + dy][x + dx] if 0 <= x + dx < g.w and 0 <= y + dy < g.h else None)]
        edge = len(near) < len(AROUND)
        if len(near) < 5 or src[y][x] in near or (edge and ramp(src[y][x]) == "void"):
            continue
        counts = Counter(near)
        g.px[y][x] = min(counts, key=lambda c: (abs(luma(c) - luma(src[y][x])), -counts[c]))


def luma(c):
    r, g, b = RGB[c]
    return 0.3 * r + 0.59 * g + 0.11 * b


def cape_mask(g):
    """Red cloth below the scarf, plus the brown lining touching it."""
    cape = {(x, y) for x, y in g.cells() if y >= g.h - SCARF_ABOVE_BOTTOM and ramp(g.px[y][x]) == "blood"}
    edge = list(cape)
    while edge:
        x, y = edge.pop()
        for dx, dy in CROSS:
            n = (x + dx, y + dy)
            if n not in cape and g.get(*n) == "leather-1":
                cape.add(n)
                edge.append(n)
    return cape


def paint_cloth(g, mask, mass, lit, dark):
    """Flat AI cloth becomes a mass with a broken lit left rim, a broken shaded right side
    and long hanging folds that drift as they fall (light from the top-left)."""
    for x, y in mask:
        g.px[y][x] = mass
    for x, y in mask:
        if (x - 1, y) not in mask:
            if y // 3 % 3 != 2:
                g.px[y][x] = lit
        elif (x + 1, y) not in mask or ((x + 2, y) not in mask and y // 4 % 3 == 0):
            g.px[y][x] = dark
    xs = sorted({x for x, _ in mask})
    count = max(2, len(xs) // 7)
    for i in range(count):
        x = xs[0] + (i + 1) * len(xs) // (count + 1) + (i * 5) % 3 - 1
        column = sorted(y for xx, y in mask if xx == x)
        if not column:
            continue
        top, bottom = column[0], column[-1]
        start = top + (bottom - top) * (15 if i % 2 else 50) // 100
        drift = 1 if i % 2 else -1
        for y in range(start, bottom + 1):
            fx = x + drift * ((y - start) // (7 + i % 3))
            if (fx, y) in mask:
                g.px[y][fx] = dark
                if (fx - 1, y) in mask and y - start > 2:
                    g.px[y][fx - 1] = lit


def paint_cape(g):
    """One cape ramp for every facing, so front and back views read the same."""
    cape = cape_mask(g)
    if len(cape) < 30:
        return
    paint_cloth(g, cape, "blood-1", "blood-2", "blood-0")
    for x in {x for x, _ in cape}:
        g.px[max(y for xx, y in cape if xx == x)][x] = "blood-0"


def hem_top(g, x):
    """Lowest cape pixel in a column, looking past a void outline row."""
    y = next((y for y in range(g.h - 1, -1, -1) if g.px[y][x]), None)
    while y is not None and y >= 0 and ramp(g.px[y][x]) == "void":
        y -= 1
    return y if y is not None and y >= 0 and ramp(g.px[y][x]) == "blood" else None


def cut(g, x, y, depth, end=None):
    for yy in range(y - depth + 1, (end or y) + 1):
        g.px[yy][x] = None
    if g.get(x, y - depth):
        g.px[y - depth][x] = "void-1"


def tear_hem(g):
    cols = [x for x in range(g.w) if hem_top(g, x) is not None]
    if len(cols) < 8:
        return
    vary = len(cols) % 5
    for i, frac in enumerate((0.15, 0.45, 0.8)):
        x = cols[min(len(cols) - 1, int(len(cols) * (frac + vary / 40)))]
        deep = 2 + (vary + i) % 3
        for dx, depth in ((0, deep), (-1, 1), (1, deep - 1)):
            y = hem_top(g, x + dx)
            if y is not None:
                cut(g, x + dx, y, depth, end=max(yy for yy in range(g.h) if g.px[yy][x + dx]))


def fray_tabard(g, cloth):
    if len(cloth) < 20:
        return
    xs = sorted({x for x, _ in cloth})
    for x in xs:
        y = max(yy for xx, yy in cloth if xx == x)
        depth = 2 if x % 5 == 0 else 1 if x % 3 == 0 else 0
        if depth and g.get(x, y + 1) is None:
            cut(g, x, y, depth)
    top, bottom = min(y for _, y in cloth), max(y for _, y in cloth)
    sx, sy = xs[len(xs) // 3], top + (bottom - top) * 2 // 3
    for dx, dy in ((0, 0), (1, 0), (1, 1)):
        if (sx + dx, sy + dy) in cloth and g.get(sx + dx, sy + dy):
            g.px[sy + dy][sx + dx] = "blood-1"


def paint_tabard(g, cloth):
    """Flesh-ramp cloth reads as skin: repaint it as worn ash cloth, its brown fold lines included."""
    if len(cloth) < 20:
        return
    x0, x1 = min(x for x, _ in cloth), max(x for x, _ in cloth)
    y0, y1 = min(y for _, y in cloth), max(y for _, y in cloth)
    cloth |= {(x, y) for x, y in g.cells() if g.px[y][x] == "leather-3" and x0 <= x <= x1 and y0 <= y <= y1}
    paint_cloth(g, {p for p in cloth if g.get(*p)}, "ash-2", "ash-3", "ash-1")


def outline_shadow_side(g):
    for x, y in g.cells():
        c = g.px[y][x]
        if ramp(c) != "void" and shade(c) == 0 and (g.get(x + 1, y) is None or g.get(x, y + 1) is None):
            g.px[y][x] = "void-1"


def cleanup(img):
    g = Grid(img.convert("RGBA"))
    cloth = {(x, y) for x, y in g.cells() if ramp(g.px[y][x]) == "flesh"}
    denoise(g)
    denoise(g)
    paint_tabard(g, cloth)
    paint_cape(g)
    tear_hem(g)
    fray_tabard(g, cloth)
    outline_shadow_side(g)
    return g.image()


if __name__ == "__main__":
    cleanup(Image.open(sys.argv[1])).save(sys.argv[2])
