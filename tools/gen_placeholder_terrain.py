"""Generates placeholder ground tiles for every biome.
Usage: .venv/bin/python tools/gen_placeholder_terrain.py [preview_dir]

One sheet per biome, one row per ground type (base first, matching src/biomes.js).
Cols 0-15 = corner mask (bit 0 TL, 1 TR, 2 BL, 3 BR; 15 = full), cols 16-18 = extra full-tile variants.
Every row has masks so a biome's base can blend over a neighbouring biome."""
import math
import random
import sys
from pathlib import Path
from pixel import Sprite, save, sheet

T = 32
ART = Path(__file__).resolve().parent.parent / "art"


def ground(base, speckles, edge=None, feature=None):
    return {"base": base, "speckles": speckles, "edge": edge, "feature": feature}


GRASS = ("grass", ["rot-2", "rot-2", "rot-3", "leather-3"])
BIOMES = {
    "battlefield": [
        ground("ash-0", [("void-3", 0.05), ("leather-1", 0.05), ("ash-1", 0.02)], feature=("pits", "void-3", "ash-1")),
        ground("leather-2", [("leather-1", 0.07), ("leather-3", 0.03), ("ash-1", 0.01)], "leather-1"),
        ground("rot-1", [("rot-0", 0.05)], "rot-0", GRASS),
        ground("blood-0", [("blood-1", 0.14), ("leather-0", 0.08), ("blood-2", 0.02)], "leather-0"),
    ],
    "swamp": [
        ground("rot-0", [("void-3", 0.06), ("rot-1", 0.05), ("leather-0", 0.03)], "void-3", ("pits", "void-2", "rot-1")),
        ground("rot-1", [("rot-2", 0.06), ("rot-0", 0.04)], "rot-0", ("grass", ["rot-2", "rot-3", "rot-2"])),
        ground("void-3", [("rot-0", 0.05)], "rot-0", ("water", "steel-1", "steel-2")),
        ground("void-2", [("void-3", 0.05)], "void-3", ("water", "steel-0", "steel-1")),
    ],
    "ruins": [
        ground("ash-1", [("ash-0", 0.06), ("ash-2", 0.05), ("void-3", 0.02)], "ash-0", ("pebbles", "ash-2")),
        ground("ash-1", [], "void-3", ("flagstone", ["ash-1", "ash-2", "ash-1", "ash-0"], "void-3")),
        ground("rot-1", [("rot-2", 0.07), ("ash-1", 0.03)], "rot-0", ("grass", ["rot-2", "rot-3", "ash-2"])),
        ground("void-2", [("void-3", 0.1), ("ash-0", 0.05)], "ash-0"),
    ],
    "ashen": [
        ground("ash-2", [("ash-1", 0.07), ("ash-3", 0.03), ("void-3", 0.02)]),
        ground("void-3", [("void-2", 0.08), ("ash-0", 0.05)], "void-2"),
        ground("leather-0", [("leather-1", 0.06)], "void-3", ("grass", ["leather-1", "ash-1", "void-3"])),
        ground("void-2", [("void-3", 0.08), ("ember-0", 0.03), ("ember-1", 0.015), ("ember-2", 0.005)], "void-3"),
    ],
    "frozen": [
        ground("steel-2", [("steel-3", 0.07), ("steel-1", 0.04), ("bone-0", 0.01)]),
        ground("ash-1", [("ash-0", 0.08), ("ash-2", 0.06), ("steel-1", 0.03)], "ash-0", ("pebbles", "steel-2")),
        ground("steel-1", [("steel-2", 0.04)], "steel-0", ("ice", "steel-2", "steel-3")),
        ground("leather-1", [("steel-2", 0.05), ("leather-0", 0.05)], "leather-0"),
    ],
    "village": [
        ground("leather-1", [("leather-0", 0.06), ("leather-2", 0.05)], "leather-0"),
        ground("rot-1", [("rot-0", 0.05)], "rot-0", GRASS),
        ground("leather-3", [("leather-2", 0.08)], "leather-2", ("straw", "leather-2", "bone-0")),
        ground("void-3", [("rot-0", 0.05)], "leather-0", ("water", "void-2", "steel-1")),
    ],
}
# Integer wave counts keep the edge noise periodic, so neighbouring tiles line up.
WAVES = [(1, 2, 0.3), (2, -1, 1.7), (3, 1, 4.1), (-2, 3, 2.2), (5, 4, 0.9), (4, -5, 5.3), (7, 2, 3.3)]


def add_feature(px, rng, feature):
    kind, *args = feature
    if kind == "grass":
        for _ in range(60):
            x, y = rng.randrange(T), rng.randrange(2, T)
            px[y][x] = px[y - 1][x] = rng.choice(args[0])
    elif kind == "pits":
        hole, lip = args
        for _ in range(3):
            x, y = rng.randrange(1, T - 2), rng.randrange(1, T - 1)
            px[y][x] = px[y][x + 1] = hole
            px[y - 1][x] = lip
    elif kind == "water":
        ripple, glint = args
        for _ in range(14):
            x, y = rng.randrange(T - 4), rng.randrange(T)
            for dx in range(rng.randrange(2, 5)):
                px[y][x + dx] = ripple
        for _ in range(4):
            px[rng.randrange(T)][rng.randrange(T)] = glint
    elif kind == "pebbles":
        for _ in range(6):
            x, y = rng.randrange(T - 1), rng.randrange(T)
            px[y][x] = px[y][x + 1] = args[0]
    elif kind == "flagstone":
        stones, mortar = args
        for row in range(4):
            offset = 4 * (row % 2)
            for col in range(5):
                color = rng.choice(stones)
                for y in range(row * 8, row * 8 + 8):
                    for x in range(col * 8 - offset, col * 8 + 8 - offset):
                        if 0 <= x < T:
                            px[y][x] = mortar if y == row * 8 + 7 or x == col * 8 + 7 - offset else color
            if rng.random() < 0.5:
                x = rng.randrange(T - 3)
                for i in range(3):
                    px[row * 8 + 2 + i][x + i] = mortar
    elif kind in ("ice", "straw"):
        dark, light = args
        for _ in range(10 if kind == "ice" else 30):
            x, y = rng.randrange(T - 4), rng.randrange(T - 4)
            for i in range(rng.randrange(2, 5)):
                px[y + (i if kind == "ice" else 0)][x + i] = dark if kind == "straw" or i else light
        if kind == "straw":
            for _ in range(8):
                px[rng.randrange(T)][rng.randrange(T)] = light


def texture(spec, seed):
    rng = random.Random(f"{spec['base']}{spec['feature']}{seed}")
    px = [[spec["base"]] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            r = rng.random()
            for color, density in spec["speckles"]:
                if r < density:
                    px[y][x] = color
                    break
                r -= density
    if spec["feature"]:
        add_feature(px, rng, spec["feature"])
    return px


def edge_noise(x, y):
    return sum(math.sin(2 * math.pi * (kx * x + ky * y) / T + ph) for kx, ky, ph in WAVES) / len(WAVES)


def overlay_tile(spec, mask):
    tex = texture(spec, 0)
    tl, tr, bl, br = ((mask >> i) & 1 for i in range(4))
    filled = [[False] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            u, v = (x + 0.5) / T, (y + 0.5) / T
            b = tl * (1 - u) * (1 - v) + tr * u * (1 - v) + bl * (1 - u) * v + br * u * v
            filled[y][x] = b > 0.5 + 0.55 * edge_noise(x, y)
    s = Sprite(T, T)
    for y in range(T):
        for x in range(T):
            if not filled[y][x]:
                continue
            border = any(0 <= x + dx < T and 0 <= y + dy < T and not filled[y + dy][x + dx]
                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            s.px[y][x] = spec["edge"] if border and spec["edge"] else tex[y][x]
    return s.image()


def full_tile(spec, seed):
    s = Sprite(T, T)
    s.px = texture(spec, seed)
    return s.image()


def ground_sheet(grounds):
    rows = [[overlay_tile(spec, m) for m in range(15)] + [full_tile(spec, i) for i in range(4)] for spec in grounds]
    return sheet(rows, T, T)


def main(preview_dir=None):
    for biome, grounds in BIOMES.items():
        save(ground_sheet(grounds), ART / f"tiles/{biome}/{biome}_ground.png", preview_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
