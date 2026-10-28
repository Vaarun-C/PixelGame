"""Build the 32 px item and rune icon sheets from the PixelLab drafts.

Run from the repo root: .venv/bin/python art/drafts/ui/icons.py
- art/items/item_icons_hd.png: same column order as item_icons.png (shard, blade, helm, plate, then
  bronze/silver/gold in small, medium, large clumps).
- art/runes/rune_icons_hd.png: columns are tiers 1-6, rows are types (rend, ward, hunger). The stones
  are AI-drawn; glyphs, tier glow and halo are drawn here so every tier shares one exact glyph (ART_RULES §5).
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS, sheet, save

D = Path("art/drafts/ui")
C = {k: v + (255,) for k, v in COLORS.items()}
NAME = {v: k for k, v in C.items()}
S = 32
TIERS = ["pale", "azure", "violet", "venom", "gold", "crimson"]
luma = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]

# Glyph strokes on a 14x16 grid, at most 6 strokes each, straight cuts only.
GLYPHS = {
    "rend": [((10, 1), (4, 8)), ((4, 8), (10, 8)), ((10, 8), (4, 15)), ((12, 11), (13, 9))],
    "ward": [((7, 1), (12, 6)), ((12, 6), (7, 15)), ((7, 15), (2, 6)), ((2, 6), (7, 1)), ((7, 4), (7, 11))],
    "hunger": [((1, 2), (13, 2)), ((1, 2), (7, 15)), ((13, 2), (7, 15)), ((5, 2), (5, 6)), ((9, 2), (9, 6))],
}
KEY_PIXELS = {"rend": [(10, 1), (4, 8)], "ward": [(7, 1), (7, 8)], "hunger": [(7, 15), (5, 6), (9, 6)]}
# Which blank stone (cell of the 4x4 stones grid) each type is carved into.
STONES = {"rend": (1, 0), "ward": (3, 0), "hunger": (0, 2)}
FUSED_STONE = (2, 0)  # the broad rounded tablet, wide enough for two glyphs


def cell(path, col, row, size, grid=None):
    img = snap(Image.open(path).convert("RGBA"))
    return img.crop((col * size, row * size, col * size + size, row * size + size))


def fit(img):
    """Centre the drawn pixels on a 32x32 canvas, keeping the 1 px padding of §5."""
    bb = img.getbbox()
    part = img.crop(bb)
    out = Image.new("RGBA", (S, S))
    out.alpha_composite(part, ((S - part.width) // 2, (S - part.height) // 2))
    return out


def line(a, b):
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(round(x0 + (x1 - x0) * t / n), round(y0 + (y1 - y0) * t / n)) for t in range(n + 1)]


# A fused rune (§5): both glyphs narrowed side by side on one stone, joined by a crack of light.
FUSED_SCALE = 0.6
FUSED_SHIFT = 5
CRACK = [((7, 0), (6, 5)), ((6, 5), (8, 10)), ((8, 10), (7, 16))]


def carve(stone, kinds, tier):
    img = stone.copy()
    px = img.load()
    bb = img.getbbox()
    ox, oy = (bb[0] + bb[2]) // 2 - 7, (bb[1] + bb[3]) // 2 - 8
    rng = random.Random("".join(kinds))
    cursed = TIERS[tier] == "crimson"
    fused = len(kinds) > 1
    place = lambda x, i: round(7 + (x - 7) * FUSED_SCALE + (i * 2 - 1) * FUSED_SHIFT) if fused else x
    glyph, keys = set(), []
    for i, kind in enumerate(kinds):
        for a, b in GLYPHS[kind]:
            for x, y in line((place(a[0], i), a[1]), (place(b[0], i), b[1])):
                jitter = rng.choice((0, 0, 1)) if cursed else 0  # cursed strokes run slightly uneven
                glyph.add((ox + x + jitter, oy + y))
        keys += [(ox + place(x, i), oy + y) for x, y in KEY_PIXELS[kind][:2 if fused else 3]]
    crack = {(ox + x, oy + y) for a, b in CRACK for x, y in line(a, b)} if fused else set()
    ramp = lambda part: C[f"rune-{TIERS[tier]}-{part}"]
    for x, y in glyph | crack:  # carved depth: shadow below-right of each cut
        if (x + 1, y + 1) not in glyph | crack and px[x + 1, y + 1][3]:
            px[x + 1, y + 1] = C["void-1"]
    for x, y in glyph:
        px[x, y] = ramp("mid")
    for x, y in crack:
        if px[x, y][3]:
            px[x, y] = ramp("core")
    for x, y in keys:
        px[x, y] = ramp("core")
    if cursed:
        for start, end in (((3, 14), (-2, 19)), ((12, 1), (16, -3))):  # weeping cracks and grown-in flesh
            for x, y in line(start, end):
                if 0 <= ox + x < S and 0 <= oy + y < S and px[ox + x, oy + y][3]:
                    px[ox + x, oy + y] = ramp("dark")
        for x, y in ((bb[0] + 2, bb[3] - 4), (bb[0] + 3, bb[3] - 3), (bb[2] - 4, bb[1] + 3)):
            if px[x, y][3]:
                px[x, y] = C["flesh-1"]
    if tier:  # broken halo outside the outline (tier 1 has none)
        edge = [(x, y) for y in range(S) for x in range(S) if not px[x, y][3]
                and any(0 <= x + dx < S and 0 <= y + dy < S and px[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for i, (x, y) in enumerate(edge):
            if (x * 3 + y * 5) % 7 > 2:
                px[x, y] = ramp("dark")
    return img


def recolour_by_luma(img, ramp):
    """Map every coloured pixel onto `ramp` (dark to light) by brightness, keeping outlines."""
    px = img.load()
    shades = sorted({px[x, y] for y in range(S) for x in range(S) if px[x, y][3] and NAME.get(px[x, y], "").split("-")[0] not in ("void",)}, key=luma)
    for y in range(S):
        for x in range(S):
            if px[x, y] in shades:
                px[x, y] = C[ramp[min(len(ramp) - 1, shades.index(px[x, y]) * len(ramp) // len(shades))]]
    return img


def ink(img):
    """Pixels of the icon's colours without its dark outline and shadows, darkest first."""
    return sorted((c for c in img.get_flattened_data() if c[3] and not NAME.get(c, "").startswith(("void", "leather-0"))), key=luma)


def match_colours(img, ref):
    """Repaint img in ref's colours by histogram matching on brightness: the darkest k% of img's ink
    takes the colours of the darkest k% of ref's, so the result has ref's balance of shades."""
    src, dst = ink(img), ink(ref)
    first = {}
    for i, c in enumerate(src):
        first.setdefault(c, i)
    mapping = {c: dst[min(len(dst) - 1, (first[c] + src.count(c) // 2) * len(dst) // len(src))] for c in first}
    px = img.load()
    for y in range(S):
        for x in range(S):
            if px[x, y] in mapping:
                px[x, y] = mapping[px[x, y]]
    return img


SHARD = ["rune-pale-dark", "rune-pale-mid", "rune-pale-core"]
CLUMPS = ((0, 0), (1, 0), (0, 1))  # small, medium, large in each metal's 2x2 grid
metals = {m: [fit(cell(D / f"icons_{m}.png", c, r, 32)) for c, r in CLUMPS] for m in ("bronze", "silver", "gold")}
# User picks (icon sign-off): bronze clumps all take the bronze heap's colours, gold takes the
# small bronze nugget's original warm colours.
warm = metals["bronze"][0].copy()
metals["bronze"][:2] = [match_colours(i, metals["bronze"][2]) for i in metals["bronze"][:2]]
metals["gold"] = [match_colours(i, warm) for i in metals["gold"]]
items = [recolour_by_luma(fit(cell(D / "icons_scrap.png", 0, 0, 32)), SHARD)]
items += [fit(cell(D / "icons_scrap.png", c, r, 32)) for c, r in ((1, 0), (0, 1))]
items += [fit(cell(D / "icons_plate.png", 0, 0, 32))]
for metal in ("bronze", "silver", "gold"):
    items += metals[metal]
save(sheet([items], S, S), Path("art/items/item_icons_hd.png"))

stones = {k: fit(cell(D / "icons_stones.png", c, r, 32)) for k, (c, r) in STONES.items()}
fused_stone = fit(cell(D / "icons_stones.png", *FUSED_STONE, 32))
# Rows: the three types, then the fused pairs in src/items.js FUSIONS order.
runes = [[carve(stones[k], [k], t) for t in range(6)] for k in ("rend", "ward", "hunger")]
runes += [[carve(fused_stone, pair, t) for t in range(6)] for pair in (("rend", "ward"), ("rend", "hunger"), ("ward", "hunger"))]
save(sheet(runes, S, S), Path("art/runes/rune_icons_hd.png"))
print("item_icons_hd", len(items), "rune_icons_hd 6x6")
