"""Build the 32 px item and rune icon sheets from the PixelLab drafts.

Run from the repo root: .venv/bin/python art/drafts/ui/icons.py
- art/items/item_icons_hd.png: same column order as item_icons.png (shard, blade, helm, plate, then
  bronze/silver/gold in small, medium, large clumps), then the empty stone.
- art/runes/rune_icons_hd.png: columns are tiers 1-6, rows are the subtypes then the fused pairs. The
  stones are AI-drawn; glyphs, tier glow and halo are drawn here so every tier shares one exact glyph (ART_RULES §5).
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

# Glyphs on a 14x16 grid, straight cuts only: each family has a spine and each subtype adds its marks
# (lore/Runes/rune-types.md). Order matches godot/scripts/game/rune_book.gd ORDER.
SPINES = {
    "grudge": [((3, 1), (11, 15))],
    "mortmain": [((4, 15), (4, 1)), ((4, 1), (11, 1)), ((11, 1), (11, 5))],
    "hush": [((3, 1), (3, 14)), ((3, 14), (11, 14)), ((11, 14), (11, 8))],
}
# subtype: (family, mark strokes, key pixels lit in the tier's core colour)
SUBTYPES = {
    "rend": ("grudge", [((7, 1), (13, 11))], [(3, 1), (7, 1)]),
    "break": ("grudge", [((3, 10), (7, 7)), ((8, 11), (12, 8))], [(7, 7), (8, 11)]),
    "sting": ("grudge", [((3, 1), (2, 6)), ((11, 15), (12, 10))], [(2, 6), (12, 10)]),
    "ward": ("mortmain", [((4, 15), (11, 15)), ((11, 15), (11, 11))], [(4, 1), (11, 11)]),
    "still": ("mortmain", [((7, 8), (12, 8))], [(7, 8), (4, 1)]),
    "sink": ("mortmain", [((11, 5), (8, 14))], [(8, 14), (4, 1)]),
    "hunger": ("hush", [((6, 14), (6, 10)), ((9, 14), (9, 11))], [(6, 10), (9, 11)]),
    "flee": ("hush", [((11, 8), (14, 4))], [(14, 4), (3, 1)]),
}
ORDER = list(SUBTYPES)
PAIRS = [(a, b) for i, a in enumerate(ORDER) for b in ORDER[i + 1:]]
# Which blank stone (cell of the 4x4 stones grid) each family is carved into.
STONES = {"grudge": (1, 0), "mortmain": (3, 0), "hush": (0, 2)}
FUSED_STONE = (2, 0)  # the broad rounded tablet, wide enough for two glyphs
# The empty stone the barterer sells: a cracked blank the monk filled with mortar, no glyph, no glow.
EMPTY_STONE = (1, 2)
MORTAR = [((-6, -7), (-1, -1)), ((-1, -1), (6, 1)), ((-1, -1), (-3, 7))]  # from the stone's centre


def glyph(*kinds):
    """Strokes and key pixels for one symbol: a family spine with every given subtype's marks."""
    strokes = SPINES[SUBTYPES[kinds[0]][0]] + [m for k in kinds for m in SUBTYPES[k][1]]
    return strokes, [p for k in kinds for p in SUBTYPES[k][2]][:3]


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


# Forced stones are bound in iron wire from the dead man's mail (lore: Willing and forced): two turns
# across the lower-left end, iron greys only, inside the outline and clear of the glyph (ART_RULES \u00a75),
# with a short tail off the lower turn that ties the stone on. Crimson is bare.
WIRE_ROWS = (4, 7)  # rows above the stone's bottom; stone shows between them
WIRE_MIN = 4  # a turn with fewer pixels left after the glyph and outline is dropped
OUTLINE = (C["void-0"], C["void-1"])


def wired(img, glyph_pixels):
    px = img.load()
    bb = img.getbbox()
    mid = (bb[0] + bb[2]) // 2
    inside = lambda x, y: px[x, y][3] and px[x, y] not in OUTLINE and all(
        px[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    clear = lambda x, y: not any((x + dx, y + dy) in glyph_pixels for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    for i, up in enumerate(WIRE_ROWS):
        y = bb[3] - 1 - up
        turn = [x for x in range(bb[0], mid) if inside(x, y) and clear(x, y)]
        if len(turn) < WIRE_MIN:
            continue
        for x in turn:
            px[x, y] = C["steel-2"]
            if inside(x, y + 1) and clear(x, y + 1):
                px[x, y + 1] = C["steel-0"]
        if i == 0:
            for k in (1, 2):
                if px[turn[0] - k, y][3] == 0 or px[turn[0] - k, y] in OUTLINE:
                    px[turn[0] - k, y + k - 1] = C["steel-1"]
    return img


def carve(stone, symbols, tier, crack=False):
    """symbols: one (strokes, keys) per glyph; two are narrowed side by side (a cross-family fuse)."""
    img = stone.copy()
    px = img.load()
    bb = img.getbbox()
    ox, oy = (bb[0] + bb[2]) // 2 - 7, (bb[1] + bb[3]) // 2 - 8
    rng = random.Random(repr(symbols))
    cursed = TIERS[tier] == "crimson"
    pair = len(symbols) > 1
    place = lambda x, i: round(7 + (x - 7) * FUSED_SCALE + (i * 2 - 1) * FUSED_SHIFT) if pair else x
    cut, keys = set(), []
    for i, (strokes, key_pixels) in enumerate(symbols):
        for a, b in strokes:
            for x, y in line((place(a[0], i), a[1]), (place(b[0], i), b[1])):
                jitter = rng.choice((0, 0, 1)) if cursed else 0  # cursed strokes run slightly uneven
                cut.add((ox + x + jitter, oy + y))
        keys += [(ox + place(x, i), oy + y) for x, y in key_pixels[:2 if pair else 3]]
    light = {(ox + x, oy + y) for a, b in CRACK for x, y in line(a, b)} if crack else set()
    ramp = lambda part: C[f"rune-{TIERS[tier]}-{part}"]
    for x, y in cut | light:  # carved depth: shadow below-right of each cut
        if (x + 1, y + 1) not in cut | light and px[x + 1, y + 1][3]:
            px[x + 1, y + 1] = C["void-1"]
    for x, y in cut:
        px[x, y] = ramp("mid")
    for x, y in light:
        if px[x, y][3]:
            px[x, y] = ramp("core")
    for x, y in keys:
        px[x, y] = ramp("core")
    if not cursed:
        wired(img, cut | light | set(keys))
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


def patched(stone):
    """Mortar seams across the stone: pale fill, lit on the top-left, a dark lip below-right."""
    img = stone.copy()
    px = img.load()
    bb = img.getbbox()
    cx, cy = (bb[0] + bb[2]) // 2, (bb[1] + bb[3]) // 2
    seam = {(cx + x, cy + y) for a, b in MORTAR for x, y in line(a, b)}
    for x, y in seam:
        if px[x + 1, y + 1][3] and (x + 1, y + 1) not in seam:
            px[x + 1, y + 1] = C["void-1"]
    for x, y in seam:
        if px[x, y][3]:
            px[x, y] = C["ash-4"] if (x - 1, y) not in seam else C["ash-3"]
    return img


def fused_icon(a, b, tier):
    """Same family: one spine carrying both marks on the family's stone. Across families: both
    glyphs narrowed on the broad tablet, joined by a crack of light."""
    if SUBTYPES[a][0] == SUBTYPES[b][0]:
        return carve(stones[SUBTYPES[a][0]], [glyph(a, b)], tier)
    return carve(fused_stone, [glyph(a), glyph(b)], tier, crack=True)


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
items.append(patched(fit(cell(D / "icons_stones.png", *EMPTY_STONE, 32))))
save(sheet([items], S, S), Path("art/items/item_icons_hd.png"))

stones = {f: fit(cell(D / "icons_stones.png", c, r, 32)) for f, (c, r) in STONES.items()}
fused_stone = fit(cell(D / "icons_stones.png", *FUSED_STONE, 32))
# Rows: the single subtypes in ORDER, then every pair in PAIRS order. Crimson can't be fused, so the
# fused rows leave that column empty.
runes = [[carve(stones[SUBTYPES[k][0]], [glyph(k)], t) for t in range(6)] for k in ORDER]
runes += [[fused_icon(a, b, t) for t in range(5)] + [Image.new("RGBA", (S, S))] for a, b in PAIRS]
save(sheet(runes, S, S), Path("art/runes/rune_icons_hd.png"))
print("item_icons_hd", len(items), f"rune_icons_hd 6x{len(runes)}")
