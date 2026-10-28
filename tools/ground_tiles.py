"""Build a 64 px ground sheet from painted texture patches (PixelLab output, palette-snapped).

Each ground: a 128 px patch -> seamless full tile + 3 variants (columns 15-18) and the 15 corner-mask
overlays (columns 0-14; bit 0 TL, 1 TR, 2 BL, 3 BR). Overlays get a bank along their border:
raised ground casts a dark face below its edge, sunken ground shows a shadowed lip at its top edge.
"""
import math
import random

from PIL import Image
from pixel import COLORS, sheet

T = 64
CUT = (6, 26)  # band the ragged seam may wander in
WAVES = [(1, 2, 0.3), (2, -1, 1.7), (3, 1, 4.1), (-2, 3, 2.2), (1, -3, 5.3), (4, 3, 0.9)]  # low frequencies: broad meanders, not spikes
NEIGHBOURS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def grid(img):
    w, h = img.size
    data = img.convert("RGBA").load()
    return [[data[x, y] for x in range(w)] for y in range(h)]


def image(px):
    img = Image.new("RGBA", (len(px[0]), len(px)))
    for y, row in enumerate(px):
        for x, c in enumerate(row):
            img.putpixel((x, y), c)
    return img


def despeckle(px, passes=2):
    """Replace pixels that share their colour with at most one of 8 neighbours: drops dither, keeps lines."""
    h, w = len(px), len(px[0])
    for _ in range(passes):
        out = [row[:] for row in px]
        for y in range(h):
            for x in range(w):
                around = [px[(y + dy) % h][(x + dx) % w] for dx, dy in NEIGHBOURS]
                if around.count(px[y][x]) <= 1:
                    out[y][x] = max(set(around), key=around.count)
        px = out
    return px


def diff(a, b):
    return sum(abs(p - q) for p, q in zip(a[:3], b[:3]))


def seam(cost):
    """Cheapest top-to-bottom path through cost[y][k] (k = cut offset in CUT), moving at most 1 per row."""
    ks = range(*CUT)
    total = [[cost[0][k] for k in ks]]
    for row in cost[1:]:
        prev = total[-1]
        total.append([row[k] + min(prev[max(0, i - 1):i + 2]) for i, k in enumerate(ks)])
    path = [min(range(len(ks)), key=lambda i: total[-1][i])]
    for y in range(len(cost) - 2, -1, -1):
        i = path[-1]
        path.append(min(range(max(0, i - 1), min(len(ks), i + 2)), key=lambda j: total[y][j]))
    return [ks[i] for i in reversed(path)]


def seamless(patch, ox=32, oy=32):
    """64 px tile from patch[oy:oy+64][ox:ox+64] whose left/top bands are swapped for what lies past the
    right/bottom edges, so it wraps; the swap boundary follows the least visible ragged path."""
    at = lambda x, y: patch[oy + y][ox + x]
    left = seam([[diff(at(k, y), at(k + T, y)) for k in range(CUT[1])] for y in range(T)])
    top = seam([[diff(at(x, k), at(x, k + T)) for k in range(CUT[1])] for x in range(T)])
    return [[at(x + T * (x < left[y]), y + T * (y < top[x])) for x in range(T)] for y in range(T)]


def variant(base, patch, seed):
    """Base tile with a ragged interior blob taken from elsewhere in the patch; borders stay identical."""
    rng = random.Random(seed)
    sx, sy = rng.randrange(0, 128 - T), rng.randrange(0, 128 - T)
    cx, cy, r = rng.uniform(26, 38), rng.uniform(26, 38), rng.uniform(16, 22)
    out = [row[:] for row in base]
    for y in range(T):
        for x in range(T):
            wobble = 4 * math.sin(math.atan2(y - cy, x - cx) * 5 + seed)
            if math.hypot(x - cx, y - cy) < r + wobble:
                out[y][x] = patch[sy + y][sx + x]
    return out


def edge_noise(x, y):
    return sum(math.sin(2 * math.pi * (kx * x + ky * y) / T + ph) for kx, ky, ph in WAVES) / len(WAVES)


def overlay(tile, mask, bank, raggedness):
    """Corner-mask overlay of tile: corners with their bit set are covered. bank: 1 raised, -1 sunken, 0 flat."""
    tl, tr, bl, br = ((mask >> i) & 1 for i in range(4))
    inside = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            u, v = (x + 0.5) / T, (y + 0.5) / T
            b = tl * (1 - u) * (1 - v) + tr * u * (1 - v) + bl * (1 - u) * v + br * u * v
            inside[y][x] = b > 0.5 + raggedness * edge_noise(x, y)
    filled = lambda x, y: inside[y][x] if 0 <= x < T and 0 <= y < T else inside[min(T - 1, max(0, y))][min(T - 1, max(0, x))]
    out = [[(0, 0, 0, 0)] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            if inside[y][x]:
                out[y][x] = tile[y][x]
                if not filled(x, y - 1) or not filled(x - 1, y):
                    out[y][x] = darker(tile[y][x], 1) if bank < 0 else lighter(tile[y][x])
                if bank < 0 and not filled(x, y - 2):
                    out[y][x] = darker(tile[y][x], 2)
                if not filled(x, y + 1) or not filled(x + 1, y):
                    out[y][x] = darker(tile[y][x], 1) if bank >= 0 else lighter(tile[y][x])
            elif bank > 0 and any(filled(x, y - d) for d in (1, 2, 3)):
                depth = next(d for d in (1, 2, 3) if filled(x, y - d))
                out[y][x] = darker(tile[y - depth][x], 4 - depth)  # the bank's face below its edge
    return out


PALETTE = [c + (255,) for n, c in COLORS.items() if not n.startswith("rune")]
luma = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def shifted(c, sign, steps=1):
    """Nearest palette colour that is darker (sign -1) or lighter (+1), stepping through the palette."""
    for _ in range(steps):
        options = [p for p in PALETTE if (luma(p) - luma(c)) * sign > 4]
        if not options:
            return c
        c = min(options, key=lambda p: diff(p, c) + 2 * abs(luma(p) - luma(c)))
    return c


darker = lambda c, steps=1: shifted(c, -1, steps)
lighter = lambda c: shifted(c, 1)


def ground_row(patch, bank, raggedness=0.4, seed=0):
    base = seamless(patch)
    full = [base] + [variant(base, patch, seed * 10 + i) for i in range(1, 4)]
    return [image(overlay(base, m, bank, raggedness)) for m in range(15)] + [image(t) for t in full]


def ground_sheet(patches, banks):
    return sheet([ground_row(p, b, seed=i) for i, (p, b) in enumerate(zip(patches, banks))], T, T)
