"""Build the 2x villager sheets (art/characters/<role>/<role>_hd_idle.png and _walk.png) from the PixelLab drafts.

Run from the repo root: .venv/bin/python art/drafts/villagers/assemble.py
Rows are facings in game order: down, left, right, up. Only south, west and north walks were generated:
east is the west walk mirrored. Idle is made by hand from each facing's rotation: the body above the
waist sinks one pixel and rises again (breathing). The barterer never leaves his stall or turns, so his
sheets are the approved front view breathing in every row.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS, sheet, save

NAME = {rgb + (255,): name for name, rgb in COLORS.items()}

V = Path("art/drafts/villagers")
ROLES = ["peasant", "monk", "guard", "barterer"]
WAIST = 0.55  # share of the frame height above which the body breathes
MIRROR = Image.FLIP_LEFT_RIGHT
DIM_EYES = {"blood-4": "blood-1", "blood-3": "blood-1"}  # the guard's eyes glowed; glow belongs to runes (§1)


def load(path):
    img = snap(Image.open(path).convert("RGBA"))
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            name = NAME.get(px[x, y])
            if name in DIM_EYES:
                px[x, y] = COLORS[DIM_EYES[name]] + (255,)
    return img


def bobbing(frame):
    """Stand-in walk while the generated one is missing: the whole body lifts a pixel every third frame."""
    up = Image.new("RGBA", frame.size)
    up.alpha_composite(frame.crop((0, 1, frame.width, frame.height)), (0, 0))
    return [frame, up, frame, frame, up, frame]


def walk_frames(d, facing, rest):
    folder = d / f"walk_{facing}"
    if not (folder / "1.png").exists():
        return bobbing(rest)
    return [load(folder / f"{k}.png") for k in range(1, 7)]


def breathing(frame):
    """Four idle frames: rest, sink, sink, rest."""
    waist = int(frame.height * WAIST)
    sunk = frame.copy()
    sunk.paste((0, 0, 0, 0), (0, 0, frame.width, waist + 1))
    sunk.alpha_composite(frame.crop((0, 0, frame.width, waist)), (0, 1))
    return [frame, sunk, sunk, frame]


def standing(role):
    idle = breathing(load(V / role / "south_concept.png"))
    for name, row in (("idle", idle), ("walk", idle + idle[:2])):
        out = Path(f"art/characters/{role}/{role}_hd_{name}.png")
        save(sheet([row] * 4, 64, 96), out)
        print(out)


def build(role):
    if role == "barterer":
        return standing(role)
    d = V / role
    rot = {f: load(d / "rotations" / f"{f}.png") for f in ("south", "west", "north")}
    walk = {f: walk_frames(d, f, rot[f]) for f in ("south", "west", "north")}
    idle_rows = [breathing(rot["south"]), breathing(rot["west"]), [f.transpose(MIRROR) for f in breathing(rot["west"])], breathing(rot["north"])]
    walk_rows = [walk["south"], walk["west"], [f.transpose(MIRROR) for f in walk["west"]], walk["north"]]
    for name, rows in (("idle", idle_rows), ("walk", walk_rows)):
        out = Path(f"art/characters/{role}/{role}_hd_{name}.png")
        save(sheet(rows, 64, 96), out)
        print(out)


for role in sys.argv[1:] or ROLES:
    build(role)
