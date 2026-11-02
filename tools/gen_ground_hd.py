"""Procedural 64 px (2x) ground sheets for every biome, built from palette ramps.
Usage: .venv/bin/python tools/gen_ground_hd.py [preview_dir]

Same layout as the 32 px sheets (one row per ground, base first, matching src/biomes.js):
cols 0-14 corner-mask overlays, cols 15-18 full tiles. Each texture tiles at 64 px: tonal shapes
come from periodic value noise, features (grass, stones, cracks, water...) are drawn wrapped and lit
from the top-left. tools/ground_tiles.py turns a texture into variants and bank-edged overlays.
The sheet holds FRAMES copies of those 19 columns side by side: animation frames (water ripples,
ember glow). Grounds without animated features repeat the same frame.
"""
import math
import random
import sys
from pathlib import Path

from ground_tiles import T, despeckle, image, overlay, variant
from pixel import COLORS, save, sheet

ART = Path(__file__).resolve().parent.parent / "art"


def periodic_noise(rng, cells):
    """Smooth value noise over a T x T tile that wraps, with `cells` lattice cells per side."""
    lattice = [[rng.random() for _ in range(cells)] for _ in range(cells)]
    smooth = lambda t: t * t * (3 - 2 * t)

    def at(x, y):
        fx, fy = x * cells / T, y * cells / T
        x0, y0 = int(fx), int(fy)
        sx, sy = smooth(fx - x0), smooth(fy - y0)
        v = lambda i, j: lattice[(y0 + j) % cells][(x0 + i) % cells]
        return (v(0, 0) * (1 - sx) + v(1, 0) * sx) * (1 - sy) + (v(0, 1) * (1 - sx) + v(1, 1) * sx) * sy

    return [[at(x, y) for x in range(T)] for y in range(T)]


def base_texture(rng, ramp, weights):
    """Mostly the middle shade with a fine grain (2-8 px clumps), ranked and cut by the weights so
    each shade covers its share exactly. No broad shading: it would repeat as a visible grid, so
    large-scale variation comes from the ground patches and the atmosphere instead."""
    clumps, grain = periodic_noise(rng, 8), periodic_noise(rng, 24)
    values = [[clumps[y][x] * 0.5 + grain[y][x] * 0.5 for x in range(T)] for y in range(T)]
    ranked = sorted(v for row in values for v in row)
    cuts = [ranked[min(len(ranked) - 1, int(len(ranked) * sum(weights[: i + 1]) / sum(weights)))] for i in range(len(weights))]
    return [[ramp[next((i for i, c in enumerate(cuts) if v < c), len(ramp) - 1)] for v in row] for row in values]


def put(px, x, y, color):
    px[y % T][x % T] = color


def grass(px, rng, clumps, dark, mid, light):
    """Clumps of upright 3-5 px blades, dark at the root and lit at the tip."""
    for _ in range(clumps):
        cx, cy = rng.randrange(T), rng.randrange(T)
        for _ in range(rng.randrange(3, 7)):
            x, y = cx + rng.randrange(-3, 4), cy + rng.randrange(-2, 3)
            height = rng.randrange(3, 6)
            for i in range(height):
                put(px, x, y - i, dark if i == 0 else light if i == height - 1 else mid)


def stones(px, rng, count, shadow, body, light, size=(1, 3)):
    """Small rounded stones: lit top-left pixel, shadow cast down-right."""
    for _ in range(count):
        cx, cy = rng.randrange(T), rng.randrange(T)
        r = rng.randint(*size)
        for dy in range(-r, r + 2):
            for dx in range(-r, r + 2):
                inside = dx * dx + dy * dy <= r * r + r
                below = (dx - 1) ** 2 + (dy - 1) ** 2 <= r * r + r
                if inside:
                    put(px, cx + dx, cy + dy, light if dx + dy <= -r else body)
                elif below:
                    put(px, cx + dx, cy + dy, shadow)


def cracks(px, rng, count, dark, lip, length=(6, 14)):
    """Meandering 1 px cracks with a lighter lip along their upper edge."""
    for _ in range(count):
        x, y = rng.randrange(T), rng.randrange(T)
        dx = rng.choice((-1, 1))
        for _ in range(rng.randint(*length)):
            put(px, x, y - 1, lip)
            put(px, x, y, dark)
            x += dx
            if rng.random() < 0.4:
                y += rng.choice((-1, 1))


FRAMES = 4
# How much of a ripple shows in each frame of its loop: it swells and fades.
RIPPLE_SWELL = [1.0, 0.7, 0.35, 0.7]


def ripples(px, rng, count, light, dark, length=(3, 7), frame=0):
    """Short horizontal ripple highlights with a dark trough under them. Phases are spread evenly,
    so a tile (all copies of which animate in step) never pulses as a whole."""
    for i in range(count):
        x, y = rng.randrange(T), rng.randrange(T)
        full, phase = rng.randint(*length), i % FRAMES
        shown = round(full * RIPPLE_SWELL[(frame + phase) % FRAMES])
        for i in range((full - shown) // 2, (full + shown) // 2):
            put(px, x + i, y, light)
            put(px, x + i + 1, y + 1, dark)


def strokes(px, rng, count, colors, length=(3, 6)):
    """Loose straws or ash streaks: short diagonal-ish strokes."""
    for _ in range(count):
        x, y = rng.randrange(T), rng.randrange(T)
        color = rng.choice(colors)
        dy = rng.choice((0, 0, 1))
        for i in range(rng.randint(*length)):
            put(px, x + i, y + (i // 2) * dy, color)


def sparks(px, rng, count, colors, frame=0):
    """Tight clusters of 3-5 glowing pixels (ember beds), never lone pixels. Each cluster's core
    flares and dims on its own phase; at its dimmest the whole cluster drops to the darkest colour."""
    for i in range(count):
        x, y = rng.randrange(T), rng.randrange(T)
        cluster = [(rng.randrange(-1, 2), rng.randrange(-1, 2), rng.choice(colors[:-1])) for _ in range(rng.randrange(3, 6))]
        glow = (frame + i) % FRAMES
        for dx, dy, color in cluster:
            put(px, x + dx, y + dy, colors[0] if glow == 2 else color)
        put(px, x, y, colors[0] if glow == 2 else colors[-1])


def flagstones(px, rng, mortar, edge_dark, edge_light, moss):
    """Courses of irregular slabs: dark mortar, lit top-left edges, shaded bottom-right, moss in joints.
    The layout has its own fixed seed, so every variant of the tile shares the same slab grid."""
    layout = random.Random("flagstones")
    heights = []
    while T - sum(heights) > 20:
        heights.append(layout.randrange(12, 19))
    heights.append(T - sum(heights))
    y0 = 0
    for h in heights:
        x = layout.randrange(T)
        widths = []
        while T - sum(widths) >= 34:
            widths.append(layout.randrange(12, 22))
        widths.append(T - sum(widths))
        for w in widths:
            jog = layout.choice((0, 0, 1))  # slabs sit a little unevenly, so courses don't read as brick rows
            for dx in range(w):
                for dy in range(jog + 1):
                    put(px, x + dx, y0 + dy, mortar)
                put(px, x + dx, y0 + jog + 1, edge_light)
                put(px, x + dx, y0 + h - 1, edge_dark)
            for dy in range(h):
                put(px, x, y0 + dy, mortar)
                put(px, x + 1, y0 + dy, edge_light if dy > jog + 1 else mortar)
                put(px, x + w - 1, y0 + dy, edge_dark)
            if rng.random() < 0.5:
                put(px, x + rng.randrange(w), y0, moss)
                put(px, x + 1, y0 + rng.randrange(2, h), moss)
            x += w
        y0 += h


def blots(px, rng, count, colors, radius=(2, 5)):
    """Irregular stains (blood, scum): a blob in the first colour, wetter centre in the last."""
    for _ in range(count):
        cx, cy = rng.randrange(T), rng.randrange(T)
        r = rng.randint(*radius)
        for dy in range(-r, r + 1):
            for dx in range(-r - 1, r + 2):
                d = math.hypot(dx * 0.8, dy) + rng.random() * 1.2
                if d < r:
                    put(px, cx + dx, cy + dy, colors[-1] if d < r * 0.45 else colors[0])


FEATURES = {
    "grass": grass, "stones": stones, "cracks": cracks, "ripples": ripples,
    "strokes": strokes, "sparks": sparks, "flagstones": flagstones, "blots": blots,
}


def ground(ramp, weights, *features, bank=0):
    """ramp: palette shades dark to light, weights: how much of each. features: (name, *args).
    bank: how its edge meets lower ground, 1 raised, -1 sunken, 0 flat."""
    return {"ramp": ramp, "weights": weights, "features": features, "bank": bank}


GRASS = ("grass", 70, "rot-0", "rot-2", "rot-3")
BIOMES = {
    "battlefield": [
        ground(["void-3", "ash-0", "ash-1"], [1, 8, 1], ("cracks", 5, "void-2", "ash-1"), ("stones", 10, "void-2", "ash-1", "ash-2")),
        ground(["leather-0", "leather-1", "leather-2"], [1, 8, 1], ("cracks", 7, "leather-0", "leather-2"), ("stones", 6, "leather-0", "ash-0", "ash-1")),
        ground(["rot-0", "rot-1", "rot-2"], [1, 8, 1], GRASS, bank=1),
        ground(["leather-0", "blood-1", "leather-1"], [4, 4, 2], ("blots", 4, ["blood-1", "blood-2"], (1, 3)), ("stones", 4, "void-2", "leather-1", "leather-2"), bank=-1),
    ],
    "swamp": [
        ground(["void-3", "rot-0", "rot-1"], [1, 8, 1], ("blots", 5, ["void-2", "void-3"]), ("grass", 18, "rot-0", "rot-1", "rot-2")),
        ground(["rot-0", "rot-1", "rot-2"], [1, 8, 1], ("grass", 60, "rot-0", "rot-2", "rot-3"), bank=1),
        ground(["void-2", "void-3", "rot-0"], [1, 10, 1], ("ripples", 30, "steel-2", "void-2", (4, 9)), ("blots", 4, ["rot-0", "rot-1"]), bank=-1),
        ground(["void-2", "void-3", "steel-0"], [3, 7, 1], ("ripples", 18, "steel-1", "void-2", (4, 9)), bank=-1),
    ],
    "ruins": [
        ground(["ash-0", "ash-1", "ash-2"], [1, 8, 1], ("stones", 26, "void-3", "ash-1", "ash-2")),
        ground(["ash-0", "ash-1", "ash-1"], [1, 8, 1], ("flagstones", "void-3", "ash-0", "ash-2", "rot-1"), ("cracks", 4, "void-3", "ash-2"), bank=1),
        ground(["rot-0", "rot-1", "rot-2"], [1, 8, 1], ("grass", 60, "rot-0", "rot-2", "ash-2"), bank=1),
        ground(["void-2", "void-3", "ash-0"], [1, 8, 1], ("stones", 18, "void-2", "ash-0", "ash-1"), ("cracks", 4, "void-2", "ash-0"), bank=-1),
    ],
    "ashen": [
        ground(["ash-0", "ash-1", "ash-1"], [3, 7, 1], ("strokes", 24, ["ash-2"]), ("stones", 6, "void-3", "ash-0", "ash-1")),
        ground(["void-2", "void-3", "ash-0"], [1, 8, 1], ("cracks", 6, "void-2", "ash-0"), ("strokes", 10, ["void-2"])),
        ground(["void-3", "leather-0", "leather-1"], [1, 8, 1], ("grass", 70, "void-3", "leather-1", "ash-1"), bank=1),
        ground(["void-2", "void-3", "ash-0"], [3, 7, 1], ("sparks", 7, ["ember-0", "ember-0", "ember-1"]), ("cracks", 4, "void-2", "ash-0"), bank=-1),
    ],
    "frozen": [
        ground(["steel-1", "steel-2", "steel-2"], [1, 8, 1], ("stones", 8, "steel-1", "steel-2", "ash-2"), ("strokes", 10, ["steel-1"])),
        ground(["ash-0", "ash-1", "ash-2"], [1, 8, 1], ("stones", 22, "void-3", "steel-1", "steel-2")),
        ground(["steel-0", "steel-1", "steel-2"], [1, 9, 1], ("cracks", 8, "steel-0", "steel-2", (12, 24)), ("strokes", 6, ["steel-2"], (4, 9)), bank=-1),
        ground(["leather-0", "leather-1", "steel-1"], [1, 8, 1], ("cracks", 5, "leather-0", "steel-1"), ("stones", 6, "leather-0", "steel-1", "steel-2")),
    ],
    "village": [
        ground(["leather-0", "leather-1", "leather-2"], [1, 8, 1], ("stones", 10, "leather-0", "leather-2", "ash-1"), ("cracks", 3, "leather-0", "leather-2")),
        ground(["rot-0", "rot-1", "rot-2"], [1, 8, 1], GRASS, bank=1),
        ground(["leather-1", "leather-2", "leather-2"], [3, 7, 1], ("strokes", 80, ["leather-3", "ash-2"], (4, 8))),
        ground(["void-2", "void-3", "leather-0"], [1, 8, 1], ("ripples", 10, "steel-1", "void-2"), ("blots", 3, ["leather-0", "leather-1"]), bank=-1),
    ],
}


ANIMATED = ("ripples", "sparks")


def texture(spec, seed, frame=0):
    """Every frame rolls the same random numbers, so only the animated features change."""
    rng = random.Random(f"{spec['ramp']}{seed}")
    # Despeckle only the tonal base: features are deliberately thin (blades, cracks, ripples).
    px = despeckle(base_texture(rng, spec["ramp"], spec["weights"]), 1)
    for name, *args in spec["features"]:
        FEATURES[name](px, rng, *args, **({"frame": frame} if name in ANIMATED else {}))
    return [[COLORS[c] + (255,) for c in row] for row in px]


# Edge shading may only step to colours already in the ground, kept inside the ground value budget
# (ART_RULES §3: void-2 … ash-2), so banks never pick up skin, metal or the void-0 shadow colour.
luma = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
BUDGET = (luma(COLORS["void-2"]), luma(COLORS["ash-2"]))


def edge_colors(tile):
    colors = {c for row in tile for c in row} | {COLORS["void-2"] + (255,), COLORS["void-3"] + (255,)}
    return [c for c in colors if BUDGET[0] <= luma(c) <= BUDGET[1]]


def ground_frame(spec, frame):
    base = texture(spec, 0, frame)
    # Variants swap nearly the whole interior for another texture, so only a thin ragged border
    # repeats. variant() reads a 128 px patch: tile the other texture to make one.
    layout = not any(name == "flagstones" for name, *_ in spec["features"])
    others = [texture(spec, i, frame) for i in range(1, 4)]
    full = [base] + [variant(base, [row * 2 for row in other] * 2, i, (27, 30), layout) for i, other in enumerate(others, 1)]
    options = edge_colors(texture(spec, 0))
    return [image(overlay(base, m, spec["bank"], 0.4, options)) for m in range(15)] + [image(t) for t in full]


def ground_row(spec):
    if not any(name in ANIMATED for name, *_ in spec["features"]):
        return ground_frame(spec, 0) * FRAMES
    return [tile for frame in range(FRAMES) for tile in ground_frame(spec, frame)]


def main(preview_dir=None):
    for biome, grounds in BIOMES.items():
        save(sheet([ground_row(spec) for spec in grounds], T, T), ART / f"tiles/{biome}/{biome}_ground_hd.png", preview_dir)
        print(biome)


if __name__ == "__main__":
    main(*sys.argv[1:])
