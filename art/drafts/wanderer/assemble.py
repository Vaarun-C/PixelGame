"""Clean the chosen wanderer frames and build the game sheets in art/characters/wanderer_hd/.

Run from the repo root after fix_edge_blades.py: .venv/bin/python art/drafts/wanderer/assemble.py
Rows are facings in game order: down, left, right, up. Animation frame 0 from PixelLab is the
input frame, so sequences start at 1.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from cleanup_sprite import cleanup
from pixel import sheet, save

W = Path("art/drafts/wanderer")
A = W / "attacks"
OUT = Path("art/characters/wanderer_hd")


def frames(folder, numbers):
    return [cleanup(snap(Image.open(folder / f"{n}.png"))) for n in numbers]


def still(path, count=1):
    return [cleanup(snap(Image.open(path)))] * count


SHEETS = {
    "idle": [
        frames(W / "idle_south/snapped", range(1, 5)),
        frames(W / "idle_west", range(1, 5)),
        frames(W / "idle_east", range(1, 5)),
        frames(W / "idle_north", range(1, 5)),
    ],
    "walk": [
        frames(W / "walk_south_v2_21", range(1, 7)),
        frames(W / "walk_west/snapped", range(1, 7)),
        frames(W / "walk_east/snapped", range(1, 7)),
        frames(W / "walk_north/snapped", range(1, 7)),
    ],
    "light": [
        # Facing down/up the light attack is a level sweep across the front: the edge leads sideways.
        frames(A / "light_south_sweep", range(1, 7)),
        frames(A / "light_west", range(1, 7)),
        frames(A / "light_east_v3", range(1, 7)),
        frames(A / "light_north_sweep2", range(1, 7)),
    ],
    "heavy": [
        # Facing down/up the chop shows the blade edge-on: edited keyframes for the raised hold and the impact.
        frames(A / "heavy_south_key", [1, 2, 3]) + still(A / "base/south_raised_edge_fixed.png", 2)
        + frames(A / "heavy_south_key", [7]) + still(A / "base/south_impact_edge_fixed.png", 2),
        frames(A / "heavy2_west", range(1, 9)),
        frames(A / "heavy_east_v4", range(1, 9)),
        frames(A / "heavy_north_key", [1, 2, 3]) + still(A / "base/north_raised_edge_fixed.png", 2)
        + frames(A / "heavy_north_key", [7, 8, 8]),
    ],
}

for name, rows in SHEETS.items():
    w, h = rows[0][0].size
    save(sheet(rows, w, h), OUT / f"wanderer_hd_{name}.png")
    print(name, f"{len(rows[0])}x{len(rows)} frames of {w}x{h}")
