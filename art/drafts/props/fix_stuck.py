"""Snap the stuck-weapon drafts, recolour every mound to tree C's sword mud and snap the broken sword's blade.

Run from the repo root: .venv/bin/python art/drafts/props/fix_stuck.py
Writes art/drafts/props/stuck_<n>_fixed.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS

P = Path("art/drafts/props")
NAME = {rgb + (255,): name for name, rgb in COLORS.items()}
MUD = ["void-2", "void-3", "leather-1", "flesh-0", "flesh-1"]  # dark to light, as on C_sword's mound
luma = lambda name: sum(w * c for w, c in zip((0.3, 0.59, 0.11), COLORS[name]))
# draft: (first mound row, colours that belong to the mound there)
MOUNDS = {
    "C_sword": (99, []),
    "stuck_broken": (44, ["flesh-0", "flesh-2", "leather-0", "leather-3", "void-3"]),
    "stuck_greatsword": (48, ["ember-1", "bone-1", "bone-0", "steel-3", "flesh-0", "void-3", "void-2", "ember-2", "ember-0"]),
    "stuck_axe": (40, ["flesh-3", "flesh-2", "ember-3", "gilt-3", "bronze-3", "flesh-1", "flesh-0", "ash-0", "ash-1", "gilt-2"]),
    "stuck_short": (44, ["bronze-3", "leather-3", "flesh-1", "flesh-0", "bronze-2", "void-3", "gilt-2"]),
    "stuck_halberd": (48, ["ash-1", "ash-0", "void-3", "void-2"]),
}
BREAK = 33  # the broken sword keeps its blade below this row, under a jagged edge
JAG = [0, 1, 3, 1, 2, 0, 2, 3]


def recolour(img, top, names):
    ranked = sorted(names, key=luma)
    target = {n: MUD[min(len(MUD) - 1, i * len(MUD) // max(1, len(ranked)))] for i, n in enumerate(ranked)}
    for y in range(top, img.height):
        for x in range(img.width):
            name = NAME.get(img.getpixel((x, y)))
            if name in target:
                img.putpixel((x, y), COLORS[target[name]] + (255,))


def snap_blade(img):
    for x in range(img.width):
        cut = BREAK + JAG[x % len(JAG)]
        for y in range(cut):
            img.putpixel((x, y), (0, 0, 0, 0))
        if img.getpixel((x, cut))[3]:
            img.putpixel((x, cut), COLORS["void-1"] + (255,))


for name, (top, names) in MOUNDS.items():
    img = snap(Image.open(P / f"{name}.png"))
    if name == "stuck_broken":
        snap_blade(img)
    recolour(img, top, names)
    img.save(P / f"{name}_fixed.png")
    print(P / f"{name}_fixed.png")
