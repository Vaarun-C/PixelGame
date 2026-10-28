"""Redraw the edge-on greatsword in the north/south heavy-chop keyframes as a 3 px slab.

PixelLab draws the blade edge-on as a 1-2 px line that reads as a spear and vanishes after
cleanup. Run from the repo root before assemble.py:
.venv/bin/python art/drafts/wanderer/fix_edge_blades.py
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS

A = Path("art/drafts/wanderer/attacks")
FILL = ("ash-4", "ash-3", "ash-1")  # lit edge, face, shadow side
CHIPS = 11  # a chipped pixel on the lit edge every this many rows


def blade(img, x, top, bottom, tip_up=True):
    """Vertical edge-on blade: fill columns x..x+2 from top to bottom with an outline either side,
    tapering to a point at the top (tip_up) or at the bottom."""
    color = lambda name: COLORS[name] + (255,)
    for y in range(top - 3, bottom + 4):
        for xx in range(x - 1, x + 4):
            img.putpixel((xx, y), (0, 0, 0, 0))
    for y in range(top, bottom + 1):
        img.putpixel((x - 1, y), color("void-1"))
        img.putpixel((x + 3, y), color("void-1"))
        for i, name in enumerate(FILL):
            img.putpixel((x + i, y), color(name))
        if (y - top) % CHIPS == CHIPS - 2:
            img.putpixel((x, y), color("ash-2"))
    step = -1 if tip_up else 1
    end = top if tip_up else bottom
    for k, cols in enumerate(((0, 1), (1,))):
        y = end + step * (k + 1)
        for i in cols:
            img.putpixel((x + i, y), color(FILL[i]))
        img.putpixel((x + cols[0] - 1, y), color("void-1"))
        img.putpixel((x + cols[-1] + 1, y), color("void-1"))
    img.putpixel((x + 1, end + step * 3), color("void-1"))


def fix(src, out, *blades):
    img = snap(Image.open(src))
    for args in blades:
        blade(img, *args)
    img.save(out)
    print(out)


fix(A / "base/north_raised_edge.png", A / "base/north_raised_edge_fixed.png", (68, 12, 48))
fix(A / "base/south_raised_edge.png", A / "base/south_raised_edge_fixed.png", (55, 8, 45))
fix(A / "heavy_south_key/8.png", A / "base/south_impact_edge_fixed.png", (64, 102, 135, False))
