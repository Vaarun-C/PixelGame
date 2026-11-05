"""Build the last-rite prop sheets from the chosen concepts and copy them into godot/art/props/:
art/props/ledger_hd.png (one 64 px frame) and art/props/wayside_shrine_hd.png (two 128 px frames: the
niche open, then shut behind an iron grate drawn here in palette colours).

Each frame has the prop centred with its ground contact 4 px above the bottom edge (the prop anchor).
Prints each kind's props.gd entry with its collision box.

Run from the repo root: .venv/bin/python art/drafts/rites/assemble.py
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tools")
from check_art import load_palette
from cleanup_sprite import Grid, denoise
from snap_palette import COLORS, despeckle, drop_specks, snap, step_down

D = Path("art/drafts/rites/concepts")
NAME = load_palette()
FLOOR = 4
# The AI's colours that snap to the wrong material: lectern wood to flesh, its cord to bronze, the
# shrine's moss to gilt.
RECOLOUR = {
    "ledger": {"flesh-0": "leather-1", "flesh-1": "leather-2", "flesh-2": "leather-3", "flesh-3": "leather-3",
               "bronze-2": "leather-3", "bronze-3": "leather-3"},
    "shrine": {"gilt-0": "rot-1", "gilt-1": "rot-2", "gilt-2": "rot-3"},
}
# Steps down each colour's ramp, so neither outshines the Wanderer (mean luminance ~63).
DARKER = {"ledger": 1, "shrine": 1}
# The shrine's baked dirt disc: each column is cleared from its first dirt pixel down.
DIRT = ("flesh", "leather")
# A point inside the shrine's niche (cropped frame px), where the grate goes.
NICHE = (21, 92)
NICHE_DARK = ("void-0", "void-1")
# Iron caps on the ledger's cover corners (frame px), lit from the top-left.
IRON = {(9, 18): "steel-3", (10, 18): "steel-2", (11, 18): "steel-1", (12, 19): "steel-1",
        (54, 20): "steel-2", (55, 20): "steel-1", (53, 21): "steel-1", (54, 21): "steel-0",
        (37, 26): "steel-3", (38, 26): "steel-2", (37, 27): "steel-2", (38, 27): "steel-1"}
# The ledger's pages (frame px): AI stipple repainted as lines of writing, the page beyond the
# spine crease (from GUTTER's first point to its second) in shade.
PAGE_COLOURS = ("bone-0", "bone-1", "ash-4", "ash-1")
PAGE_ROWS = range(2, 28)
GUTTER = ((38, 7), (24, 20))
NUB = ((27, 2), (28, 2))
# The AI drew the lectern's foot as a corner-on diamond; it's redrawn front-facing from this row down:
# the column carried on (copying this row) to a low plinth (x0, x1, top row, front-face row, bottom row).
BASE_TOP = 41
COLUMN_ROW = 39
PLINTH = (16, 45, 52, 54, 59)
# Column px left of this get the lit wood tone.
COLUMN_LIT = range(22, 28)


def recolour(img, mapping):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] and NAME[px[x, y][:3]] in mapping:
                px[x, y] = COLORS[mapping[NAME[px[x, y][:3]]]] + (255,)


def clear_dirt(img):
    px = img.load()
    for x in range(img.width):
        dirt = [y for y in range(img.height) if px[x, y][3] and NAME[px[x, y][:3]].startswith(DIRT)]
        for y in range(dirt[0] if dirt else img.height, img.height):
            px[x, y] = (0, 0, 0, 0)


def cleaned(kind, src):
    img = snap(Image.open(D / f"{src}.png"))
    if kind == "shrine":
        clear_dirt(img)
    recolour(img, RECOLOUR[kind])
    for _ in range(DARKER[kind]):
        recolour(img, {n: step_down(n) for n in COLORS})
    for _ in range(2):
        img = despeckle(img)
    img = drop_specks(img, 40)
    return img.crop(img.getbbox())


def niche(img):
    """The dark opening's pixels, flooded from NICHE."""
    px = img.load()
    todo, seen = [NICHE], set()
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < img.width and 0 <= y < img.height):
            continue
        if not px[x, y][3] or NAME[px[x, y][:3]] not in NICHE_DARK:
            continue
        seen.add((x, y))
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return seen


def grated(img):
    """The same shrine with an iron grate shut over the niche: a frame round the opening, bars every
    3 px, two crossbars riveted where they cross, a hasp on the lower one, rust under a few rivets."""
    img = img.copy()
    px = img.load()
    hole = niche(img)
    x0 = min(x for x, _ in hole)
    ys = sorted({y for _, y in hole})
    top, bottom = ys[0], ys[-1]
    rails = (top + (bottom - top) // 3, top + 2 * (bottom - top) // 3)
    mid = (x0 + max(x for x, _ in hole)) // 2
    paint = lambda x, y, name: px.__setitem__((x, y), COLORS[name] + (255,))
    for x, y in hole:
        if y + 1 >= img.height or not px[x, y + 1][3]:
            continue  # the shrine's bottom outline
        bar = (x - x0) % 3 == 1
        edge = any(n not in hole for n in ((x + 1, y), (x - 1, y), (x, y - 1)))
        if edge:
            paint(x, y, "steel-1")
        elif y in rails:
            paint(x, y, "steel-3" if bar else "steel-2")
        elif bar:
            rust = y == rails[0] + 1 and (x - x0) % 6 == 1
            paint(x, y, "blood-0" if rust else "steel-2" if y < rails[0] else "steel-1")
        elif y - 1 in rails:
            paint(x, y, "void-2")
    for x in range(mid, mid + 2):
        for y in range(rails[1] - 1, rails[1] + 2):
            paint(x, y, "steel-2" if y < rails[1] + 1 else "void-1")
    return img


def outline(img):
    """Close the open left and bottom edges: a dark tone of the local ramp on the lit left edge,
    void-0 along the bottom."""
    px = img.load()
    open_at = lambda x, y: not (0 <= x < img.width and 0 <= y < img.height) or not px[x, y][3]
    fixes = {}
    for y in range(img.height):
        for x in range(img.width):
            if not px[x, y][3]:
                continue
            name = NAME[px[x, y][:3]]
            ramp = name.split("-")[0]
            if open_at(x, y + 1) and ramp != "void":
                fixes[x, y] = "void-0"
            elif open_at(x - 1, y) and ramp != "void":
                fixes[x, y] = f"{ramp}-0" if f"{ramp}-0" in COLORS else "void-1"
    for xy, name in fixes.items():
        px[xy] = COLORS[name] + (255,)


def denoised(img):
    g = Grid(img)
    denoise(g)
    denoise(g)
    return g.image()


def write_pages(img):
    px = img.load()
    (gx0, gy0), (gx1, gy1) = GUTTER
    for y in PAGE_ROWS:
        gutter_x = gx0 + (gx1 - gx0) * (y - gy0) / (gy1 - gy0)
        for x in range(img.width):
            if not px[x, y][3] or NAME[px[x, y][:3]] not in PAGE_COLOURS:
                continue
            # Lines of writing run square to the spine, which on this turned book is a 1:4 slope.
            ink = (4 * y - x) % 12 < 4 and (x * 5 + y) % 13 > 2
            lit = x < gutter_x
            name = "ash-1" if ink else "bone-0" if lit else "ash-3"
            px[x, y] = COLORS[name] + (255,)
    for xy in NUB:
        px[xy] = (0, 0, 0, 0)


def redraw_foot(img):
    px = img.load()
    for y in range(BASE_TOP, img.height):
        for x in range(img.width):
            px[x, y] = (0, 0, 0, 0)
    for y in range(31, BASE_TOP):
        for x in COLUMN_LIT:
            if px[x, y][3] and NAME[px[x, y][:3]] == "leather-0":
                px[x, y] = COLORS["leather-1"] + (255,)
    for y in range(BASE_TOP, PLINTH[2]):
        for x in range(img.width):
            px[x, y] = px[x, COLUMN_ROW]
    x0, x1, top, face, bottom = PLINTH
    for y in range(top, bottom + 1):
        for x in range(x0, x1 + 1):
            if y == bottom or x in (x0, x1) or (y == top and not px[x, y - 1][3]):
                name = "void-0"
            elif y < face:
                name = "leather-2" if x < (x0 + x1) // 2 else "leather-1"
            elif y == bottom - 2 and x0 + 2 < x < x1 - 2:
                name = "void-2"
            else:
                name = "leather-1" if x < x0 + 6 else "leather-0"
            px[x, y] = COLORS[name] + (255,)
    # Worn: a chip off the plinth's top corners.
    for x in (x0, x1):
        px[x, top] = (0, 0, 0, 0)


def base_box(img, footprint, depth):
    """Collision box [dx, dy, w, h] in world px (half sheet px) from the anchor."""
    w = round(img.width * footprint / 2)
    h = round(w * depth)
    return [-w // 2, -h, w, h + 1]


def placed(img, size):
    frame = Image.new("RGBA", (size, size))
    frame.alpha_composite(img, ((size - img.width) // 2, size - FLOOR - img.height))
    return frame


def build(kind, frames, box):
    size = frames[0].height
    sheet = Image.new("RGBA", (size * len(frames), size))
    for i, f in enumerate(frames):
        sheet.alpha_composite(f, (i * size, 0))
    out = Path(f"art/props/{kind}_hd.png")
    sheet.save(out)
    shutil.copy(out, Path("godot") / out)
    print(f'"{kind}": {{"sheet": "{kind}_hd", "size": {size}, "scale": 0.5, "variants": {len(frames)}, "solid": {box}}},')


ledger = cleaned("ledger", "ledger_s5")
box = base_box(ledger, 0.6, 0.4)
ledger = placed(ledger, 64)
write_pages(ledger)
redraw_foot(ledger)
for xy, name in IRON.items():
    ledger.putpixel(xy, COLORS[name] + (255,))
build("ledger", [ledger], box)
shrine = denoised(cleaned("shrine", "shrine_s17"))
outline(shrine)
build("wayside_shrine", [placed(shrine, 128), placed(grated(shrine), 128)], base_box(shrine, 0.8, 0.35))
