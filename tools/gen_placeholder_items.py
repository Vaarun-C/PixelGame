"""Generates placeholder 16x16 inventory icons.
Usage: .venv/bin/python tools/gen_placeholder_items.py [preview_dir]

rune_icons.png: rows = rune types (rend, ward, hunger), cols = tiers 1-6.
item_icons.png: shard, scrap_blade, scrap_helm, scrap_plate, then bronze/silver/gold clumps (small, medium, large)."""
import sys
from pathlib import Path
from pixel import Sprite, save, sheet

S = 16
ART = Path(__file__).resolve().parent.parent / "art"
TIERS = ["pale", "azure", "violet", "venom", "gold", "crimson"]
GLYPHS = {
    "rend": ["....#.", "...#..", "..#..#", ".#..#.", "#..#..", "..#...", ".#....", "......"],
    "ward": ["#....#", "##..##", ".####.", "..##..", "..##..", "..##..", ".#..#.", "#....#"],
    "hunger": ["######", "#.#.#.", "......", "......", ".#.#.#", "######", "..##..", "..##.."],
}
STONE = [(5, 10), (4, 11), (3, 11), (3, 12), (3, 12), (3, 12), (3, 12), (3, 12), (3, 12), (4, 12), (4, 11), (5, 10)]


def rune(glyph, tier):
    s = Sprite(S, S)
    s.rows(2, STONE, "ash-1")
    s.pattern(5, 4, glyph, f"rune-{TIERS[tier]}-mid")
    s.finish()
    first = next((x, y) for y, row in enumerate(glyph) for x, ch in enumerate(row) if ch == "#")
    s.dot(5 + first[0], 4 + first[1], f"rune-{TIERS[tier]}-core")
    if tier > 0:
        halo = [(x, y) for y in range(S) for x in range(S)
                if s.empty(x, y) and (x + y) % 2 == 0
                and any(0 <= x + dx < S and 0 <= y + dy < S and s.px[y + dy][x + dx] == "void-1"
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in halo:
            s.dot(x, y, f"rune-{TIERS[tier]}-dark")
    return s.image()


def shard():
    s = Sprite(S, S)
    s.rows(4, [(8, 9), (7, 10), (6, 10), (5, 11), (5, 11), (6, 10), (6, 9), (7, 8)], "ash-1")
    s.finish()
    for x, y in ((8, 5), (8, 6), (7, 7), (8, 8), (9, 9)):
        s.dot(x, y, "rune-pale-mid")
    s.dot(8, 8, "rune-pale-core")
    return s.image()


# Metal: (base, specular highlight). Clumps are piles of nuggets; bigger weights draw bigger piles.
METALS = {"bronze": ("bronze-1", "bronze-3"), "silver": ("steel-2", "bone-1"), "gold": ("gilt-1", "gilt-3")}
NUGGETS = [
    [(7, 9, 3, 2)],
    [(5, 10, 3, 2), (10, 9, 2, 2), (8, 6, 2, 1)],
    [(4, 11, 3, 2), (9, 11, 3, 2), (7, 7, 3, 2), (12, 7, 2, 1), (4, 7, 1, 1)],
]


def clump(metal, size):
    base, spec = METALS[metal]
    s = Sprite(S, S)
    for cx, cy, rx, ry in NUGGETS[size]:
        s.ellipse(cx, cy, rx, ry, base)
    s.finish()
    for cx, cy, rx, ry in NUGGETS[size]:
        s.dot(cx - rx // 2, cy - ry // 2, spec)
    return s.image()


def scrap_blade():
    s = Sprite(S, S)
    for i in range(8):
        s.rect(5 + i, 10 - i, 6 + i, 10 - i, "steel-2")
    s.rect(2, 10, 6, 10, "steel-1")
    s.rect(3, 11, 4, 12, "leather-1")
    s.finish()
    s.dot(8, 7, "blood-3")
    s.dot(10, 5, "blood-4")
    return s.image()


def scrap_helm():
    s = Sprite(S, S)
    s.rows(4, [(6, 9), (5, 10), (4, 11), (4, 11), (4, 11), (4, 11), (4, 11), (5, 10)], "steel-1")
    s.rect(7, 5, 8, 11, "steel-2")
    s.finish()
    s.rect(5, 8, 10, 8, "void-0")
    s.dot(9, 5, "blood-3")
    s.dot(5, 10, "blood-4")
    return s.image()


def scrap_plate():
    s = Sprite(S, S)
    s.rows(3, [(4, 11), (3, 12), (3, 12), (4, 11), (4, 11), (5, 10), (5, 10), (6, 9), (6, 9)], "steel-1")
    s.rect(7, 3, 8, 11, "steel-2")
    s.finish()
    for x, y in ((10, 4), (9, 5), (10, 6), (9, 7)):
        s.dot(x, y, "void-1")
    s.dot(5, 5, "blood-3")
    return s.image()


def main(preview_dir=None):
    runes = [[rune(glyph, t) for t in range(len(TIERS))] for glyph in GLYPHS.values()]
    save(sheet(runes, S, S), ART / "runes/rune_icons.png", preview_dir)
    items = [shard(), scrap_blade(), scrap_helm(), scrap_plate()]
    items += [clump(metal, size) for metal in METALS for size in range(3)]
    save(sheet([items], S, S), ART / "items/item_icons.png", preview_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
