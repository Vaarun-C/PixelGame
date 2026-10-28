"""Build the 2x battlefield prop sheets in art/props/ from the chosen drafts (one row, one column per variant).

Run from the repo root after fix_stuck.py and combine_tree.py: .venv/bin/python art/drafts/props/assemble.py
Every sprite is moved down so its lowest pixel sits 2 rows above the frame bottom, where drawProp's default
anchor (size - 4) puts the ground contact.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS, sheet, save

P = Path("art/drafts/props")
OUT = Path("art/props")
NAME = {rgb + (255,): name for name, rgb in COLORS.items()}


def load(name):
    img = Image.open(P / f"{name}.png").convert("RGBA")
    return img if name.endswith(("_fixed", "_marked")) else snap(img)


def quadrant(name, q):
    return load(name).crop(((q % 2) * 64, (q // 2) * 64, (q % 2) * 64 + 64, (q // 2) * 64 + 64))


def strip(img, names, from_row=0):
    """Drop baked-in ground (shadow smudges, grass patches) the game draws itself."""
    for y in range(from_row, img.height):
        for x in range(img.width):
            if NAME.get(img.getpixel((x, y)), "").startswith(names):
                img.putpixel((x, y), (0, 0, 0, 0))
    return img


def recolour(img, mapping):
    for y in range(img.height):
        for x in range(img.width):
            name = NAME.get(img.getpixel((x, y)))
            if name in mapping:
                img.putpixel((x, y), COLORS[mapping[name]] + (255,))
    return img


def outline(img, above=None):
    """1 px void-1 exterior outline (ART_RULES §2), only on rows above `above` (mud mounds stay soft)."""
    rows = range(above if above is not None else img.height)
    solid = lambda x, y: 0 <= x < img.width and 0 <= y < img.height and img.getpixel((x, y))[3]
    edge = [(x, y) for y in rows for x in range(img.width)
            if not solid(x, y) and any(solid(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for xy in edge:
        img.putpixel(xy, COLORS["void-1"] + (255,))
    return img


def dim(img, above):
    """Bring near-white steel into the steel ramp so props never outshine the player; every 9th pixel stays a glint."""
    for y in range(above):
        for x in range(img.width):
            name = NAME.get(img.getpixel((x, y)))
            if name in DIM and (x + y) % 9:
                img.putpixel((x, y), COLORS[DIM[name]] + (255,))
    return img


def lit_left(img, colour, every=2):
    """Light the bark just inside the left silhouette edge on every other row (key light from the top-left)."""
    solid = lambda x, y: img.getpixel((x, y))[3]
    for y in range(0, img.height - 20, every):
        for x in range(1, img.width - 2):
            if not solid(x - 1, y) and solid(x, y) and solid(x + 1, y):
                img.putpixel((x + 1, y), COLORS[colour] + (255,))
    return img


def strip_patch(img):
    """Drop a baked ground patch (gilt/rot grass and the void-0 rim left around it), keeping figure outlines."""
    strip(img, ("gilt-", "rot-", "leather-", "flesh-"))
    px = img.load()
    for _ in range(2):
        rim = [(x, y) for y in range(img.height) for x in range(img.width) if NAME.get(px[x, y]) == "void-0"
               and not any(px[x + dx, y + dy][3] and NAME.get(px[x + dx, y + dy]) != "void-0"
                           for dx in (-1, 0, 1) for dy in (-1, 0, 1) if 0 <= x + dx < img.width and 0 <= y + dy < img.height)]
        for xy in rim:
            px[xy] = (0, 0, 0, 0)
    return drop_islands(img, 30)


def drop_islands(img, smaller_than):
    px = img.load()
    seen = set()
    for start in [(x, y) for y in range(img.height) for x in range(img.width) if px[x, y][3]]:
        if start in seen:
            continue
        island, todo = [], [start]
        seen.add(start)
        while todo:
            x, y = todo.pop()
            island.append((x, y))
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < img.width and 0 <= ny < img.height and (nx, ny) not in seen and px[nx, ny][3]:
                    seen.add((nx, ny))
                    todo.append((nx, ny))
        if len(island) < smaller_than:
            for xy in island:
                px[xy] = (0, 0, 0, 0)
    return img


def grounded(img):
    bottom = img.getbbox()[3]
    out = Image.new("RGBA", img.size)
    out.alpha_composite(img, (0, img.height - 2 - bottom))
    return out


DIM = {"bone-1": "steel-2", "bone-0": "steel-2", "steel-3": "steel-2", "ash-4": "steel-2", "ash-3": "steel-1"}
NO_EMBER = {"ember-3": "steel-2", "ember-2": "steel-2", "ember-1": "blood-2", "ember-0": "blood-1"}
stuck = [load(f"{n}_fixed") for n in ("C_sword", "stuck_greatsword", "stuck_short", "stuck_halberd")]
dim(stuck[2], 44)
outline(recolour(stuck[1], NO_EMBER), 48)
BONE_DIM = {"bone-1": "ash-4", "bone-0": "ash-3", "ash-4": "ash-3", "ash-3": "ash-2", "ash-2": "ash-1"}  # old bone, never brighter than the player
YELLOW_BONE = {"bone-1": "ash-4", "gilt-3": "ash-3", "gilt-2": "ash-3", "flesh-3": "ash-3", "flesh-2": "ash-2", "gilt-0": "leather-1"}
STRAW = {"gilt-3": "bone-0", "gilt-2": "leather-3", "gilt-1": "leather-2", "gilt-0": "leather-1"}
GRAIN = {"bronze-3": "leather-2", "flesh-3": "leather-3"}
SAND = ("flesh-3", "bronze-3", "flesh-0", "flesh-2")


def tilt(img, rows_per_px=10):
    """Lean a sprite right by shearing whole rows, so pixels stay crisp (no rotation)."""
    bottom = img.getbbox()[3]
    out = Image.new("RGBA", img.size)
    for y in range(bottom):
        out.paste(img.crop((0, y, img.width, y + 1)), ((bottom - y) // rows_per_px, y))
    return out


GILT_TO_WOOD = {"gilt-0": "leather-0", "gilt-1": "leather-1", "gilt-2": "leather-2", "gilt-3": "leather-3"}
SHEETS = {
    "weapons_stuck": stuck,
    "stumps": [load("stump_rotted"), strip(quadrant("stump_spear_grid", 1), ("ash-3",), 40)],
    "remains": [recolour(strip_patch(quadrant("bodies_B_old", q)), BONE_DIM) for q in range(4)]
    + [recolour(strip(quadrant("bones_grid", q), ("steel-1",)), YELLOW_BONE) for q in (2, 3)],
    "rocks": [drop_islands(strip(quadrant("stones_stakes_grid", 1), ("steel-0",), 44), 20),
              drop_islands(strip(load("rocks_jagged"), ("flesh-", "bronze-", "gilt-", "leather-3"), 40), 20)],
    "stakes": [load(f"stake_helm_rot/{k}") for k in (1, 7)],  # the approved helm stake, turned to 3/4 views
    "crates": [recolour(quadrant("crates_grid", q), STRAW) for q in range(4)],
    "carts": [drop_islands(recolour(strip(load("cart_broken"), SAND, 100), {**GRAIN, **STRAW}), 20),
              drop_islands(strip(load("cart_wreck"), ("steel-1",), 86), 20)],
    "gibbets": [load("gibbet_cage"), load("gibbet_noose")],
    "banners": [load("banner_upright"), tilt(load("banner_fallen"))],
    "boulders": [drop_islands(load("boulder_big_280"), 20)],  # the approved boulder repainted at 2x size
    "shields": [drop_islands(strip(quadrant("debris_grid", 0), ("rot-",), 44), 20)],
    "trees": [load("C_tree_marked"), recolour(load("tree_splintered"), GILT_TO_WOOD), lit_left(load("tree_gallows"), "leather-2")],
}

for name, frames in SHEETS.items():
    frames = [grounded(f) for f in frames]
    save(sheet([frames], *frames[0].size), OUT / f"{name}_hd.png")
    print(name, len(frames), "x", frames[0].size)
