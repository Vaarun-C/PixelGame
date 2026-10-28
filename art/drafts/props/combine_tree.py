"""Tree C with the red drape and hanging helmet from tree B, moved over by hand (no generation).

Run from the repo root: .venv/bin/python art/drafts/props/combine_tree.py
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS

P = Path("art/drafts/props")
BLOOD = {COLORS[f"blood-{i}"] + (255,) for i in range(5)}
DRAPE = (34, 40, 49, 108)  # box in tree B
HELMET = (76, 47, 98, 75)
ROPE = ("leather-2", "void-2")
TIED = 8  # rows of the drape top the branch is drawn over


def piece(img, box, keep=lambda c: c[3]):
    out = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]))
    for y in range(out.height):
        for x in range(out.width):
            c = img.getpixel((box[0] + x, box[1] + y))
            if keep(c):
                out.putpixel((x, y), c)
    return out


def combine(drape_at, helmet_at, rope_from):
    b, tree = snap(Image.open(P / "B_tree.png")), snap(Image.open(P / "C_tree.png"))
    hx, hy = helmet_at
    for y in range(rope_from[1], hy + 1):
        tree.putpixel((rope_from[0], y), COLORS[ROPE[y % 2]] + (255,))
    tree.alpha_composite(piece(b, HELMET), (hx - 11, hy))
    bare = tree.copy()
    tree.alpha_composite(piece(b, DRAPE, lambda c: c in BLOOD), drape_at)
    over = piece(bare, (drape_at[0], drape_at[1], drape_at[0] + 15, drape_at[1] + TIED))  # branch passes in front of the knot
    tree.alpha_composite(over, drape_at)
    return tree


if __name__ == "__main__":
    combine(drape_at=(18, 34), helmet_at=(96, 58), rope_from=(96, 47)).save(P / "C_tree_marked.png")
    print(P / "C_tree_marked.png")
