"""Build the village building sheets (art/props/<kind>_hd.png) from the approved concepts in clean/
(made by preview.py), and copy them into godot/art/props/.

Each frame is square, the building centred with its base 4 px above the bottom edge (the prop anchor).
Prints each kind's frame size and per-variant collision boxes for godot/scripts/world/props.gd.

Run from the repo root: .venv/bin/python art/drafts/village/assemble.py
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tools")
from check_art import load_palette
from snap_palette import despeckle, drop_specks, step_down

D = Path("art/drafts/village")
COLORS = {name: rgb for rgb, name in load_palette().items()}
NAME = {rgb: name for name, rgb in COLORS.items()}
FLOOR = 4
# Signed off on the review page (signoff collection), in variant order.
APPROVED = {
    "cottage": ["cottage_front_s29", "cottage_front_s5", "cottage_front_s17", "cottage_s29", "cottage_s17", "cottage_s5"],
    "barn": ["barn_s17", "barn_s29", "barn_s5"],
    "longhouse": ["longhouse_s17", "longhouse_s5", "longhouse_s29"],
    "shed": ["shed_big_s17", "shed_big_s5", "shed_big_s29"],
}
# A baked plinth whose colours repeat in the walls: below a share of the height, each column is
# cleared under its lowest dark outline pixel, which runs along the foot of the walls.
PLINTHS = {"cottage_front_s17": 0.7}
OUTLINES = ("void-0", "void-1")
# A baked lawn and path cleared outright (sheet px of the cleaned concept): everything below the wall
# foot, and everything outside the walls' columns lower than the eaves, except a kept box (the hay bales).
LAWNS = {"barn_s17": {"foot": 217, "eaves": 160, "walls": (27, 227), "keep": (28, 190, 73, 226)}}
# Smoke drawn into the art: near-white, brighter than any actor. Recoloured to mid grey above this share
# of the height.
SMOKE = {"cottage_front_s29": 0.35, "longhouse_s29": 0.6, "longhouse_s17": 0.3}
SMOKE_COLOURS = {"bone-1": "ash-3", "bone-0": "ash-3", "steel-3": "ash-2", "ash-4": "ash-3"}
SIDE_MARGIN = 4
# Steps down each colour's ramp, so no building outshines the Wanderer (mean luminance ~63).
DARKER = {"cottage_s17": 2, "cottage_s5": 2, "cottage_s29": 1, "cottage_front_s17": 1, "cottage_front_s5": 1}
# Loose pieces cut off from the building (fence posts) smaller than this are dropped.
LOOSE = {"longhouse_s5": 600}
# A loose piece that touches the building, cut by box (x0, y0, x1, y1) in the cropped image.
CUTS = {"longhouse_s5": [(64, 185, 76, 225)]}
DESPECKLE_PASSES = 2
# The collision floor: this share of the building's width, and this deep as a share of that.
FOOTPRINT = 0.8
DEPTH = 0.35


def cleaned(name):
    img = Image.open(D / "clean" / f"{name}.png").convert("RGBA")
    px = img.load()
    if name in PLINTHS:
        top = int(img.height * PLINTHS[name])
        cut = []
        for x in range(img.width):
            dark = [y for y in range(img.height) if px[x, y][3] and NAME[px[x, y][:3]] in OUTLINES]
            cut.append(max(top, dark[-1] + 1 if dark else 0))
        # A plank column with no dark pixel low down keeps the cut of its neighbours.
        for x in range(img.width):
            for y in range(max(cut[max(0, x - 2):x + 3]), img.height):
                px[x, y] = (0, 0, 0, 0)
    if name in LAWNS:
        lawn = LAWNS[name]
        k = lawn["keep"]
        for y in range(lawn["eaves"], img.height):
            for x in range(img.width):
                kept = k[0] <= x < k[2] and k[1] <= y < k[3]
                outside = y >= lawn["foot"] or not lawn["walls"][0] <= x <= lawn["walls"][1]
                if outside and not kept:
                    px[x, y] = (0, 0, 0, 0)
    for y in range(int(img.height * SMOKE.get(name, 0))):
        for x in range(img.width):
            if px[x, y][3] and NAME[px[x, y][:3]] in SMOKE_COLOURS:
                px[x, y] = COLORS[SMOKE_COLOURS[NAME[px[x, y][:3]]]] + (255,)
    for _ in range(DARKER.get(name, 0)):
        for y in range(img.height):
            for x in range(img.width):
                if px[x, y][3]:
                    px[x, y] = COLORS[step_down(NAME[px[x, y][:3]])] + (255,)
    for _ in range(DESPECKLE_PASSES):
        img = despeckle(img)
    img = drop_specks(img, LOOSE.get(name, 2))
    img = img.crop(img.getbbox())
    for box in CUTS.get(name, []):
        img.paste((0, 0, 0, 0), box)
    return img.crop(img.getbbox())


def base_box(img):
    """Collision box [dx, dy, w, h] in world px (half the sheet's px) from the anchor: the floor under
    the building. Corner views touch the bottom only at one corner, so it's sized from the full width."""
    w = round(img.width * FOOTPRINT / 2)
    h = round(w * DEPTH)
    return [-w // 2, -h, w, h + 1]


for kind, names in APPROVED.items():
    frames = [cleaned(n) for n in names]
    size = max(max(f.width + 2 * SIDE_MARGIN, f.height + FLOOR) for f in frames)
    size = (size + 63) // 64 * 64
    sheet = Image.new("RGBA", (size * len(frames), size))
    boxes = []
    for i, f in enumerate(frames):
        sheet.alpha_composite(f, (i * size + (size - f.width) // 2, size - FLOOR - f.height))
        boxes.append(base_box(f))
    out = Path(f"art/props/{kind}_hd.png")
    sheet.save(out)
    shutil.copy(out, Path("godot") / out)
    print(f'"{kind}": {{"sheet": "{kind}_hd", "size": {size}, "scale": 0.5, "variants": {len(frames)}, "solid": {boxes}}},')
