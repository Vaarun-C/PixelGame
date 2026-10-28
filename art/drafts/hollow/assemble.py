"""Snap the chosen Hollow frames and build the game sheets in art/enemies/hollow_hd/.

Run from the repo root: .venv/bin/python art/drafts/hollow/assemble.py
Rows are facings in game order: down, left, right, up. Animation frame 0 from PixelLab is the
input frame, so sequences start at 1. Only palette snapping here: cleanup_sprite.py is tuned to the
wanderer and would repaint the red sash as a cape.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import sheet, save

H = Path("art/drafts/hollow")
OUT = Path("art/enemies/hollow_hd")
BODIES = Path("art/props/hollow_bodies.png")
FACINGS = ["south", "west", "east", "north"]


def frames(folder, numbers):
    return [snap(Image.open(folder / f"{n}.png")) for n in numbers]


SHEETS = {
    "idle": [frames(H / f"idle_{d}", range(1, 5)) for d in FACINGS],
    "walk": [frames(H / f"walk_{d}", range(1, 7)) for d in FACINGS],
    "attack": [
        frames(H / "attack_south_key", range(1, 7)),
        frames(H / "attack_west", range(1, 7)),
        frames(H / "attack_east_v2", range(1, 7)),
        frames(H / "attack_north_key", [1, 2, 3, 6, 6, 6]),  # 4-5 swing the spear sideways; 6 is the thrust keyframe
    ],
    "death": [frames(H / d, range(1, 7)) for d in ("death_south_v2", "death_west", "death_east", "death_north_v2")],
}

for name, rows in SHEETS.items():
    w, h = rows[0][0].size
    save(sheet(rows, w, h), OUT / f"hollow_hd_{name}.png")
    print(name, f"{len(rows[0])}x{len(rows)} frames of {w}x{h}")

# The corpse prop is the last death frame of each facing, one column per facing.
last = [row[-1] for row in SHEETS["death"]]
save(sheet([last], *last[0].size), BODIES)
print("bodies", BODIES)
