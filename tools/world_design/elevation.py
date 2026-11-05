import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from horseshoe import make, N, FONT  # noqa: E402  (seed 23's outline)
from pathlib import Path

MAPS = Path(__file__).parent / "maps"

LEVELS = [
    ("Shallows / bog", (66, 72, 74)),
    ("Lowland", (88, 100, 84)),
    ("Plain", (128, 120, 92)),
    ("Upland", (156, 132, 96)),
    ("Highland", (150, 146, 140)),
    ("Mountain", (205, 205, 204)),
]
SHARES = [0.07, 0.20, 0.33, 0.20, 0.12, 0.08]

yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N - 0.5


def blur(a, r=4, passes=3):
    for _ in range(passes):
        p = np.pad(a, r, mode="edge")
        a = sum(p[r + k:r + k + N, r:r + N] for k in range(-r, r + 1)) / (2 * r + 1)
        p = np.pad(a, r, mode="edge")
        a = sum(p[r:r + N, r + k:r + k + N] for k in range(-r, r + 1)) / (2 * r + 1)
    return a


def bump(cx, cy, rx, ry):
    return np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))


def edge_falloff():
    # Pull the coast in from the east, west and south frame edges; the north edge is a mountain wall.
    d = np.minimum.reduce([xx + 0.5, 0.5 - xx, 0.5 - yy]) / 0.12
    return np.clip(d, 0, 1)


def levels(height, land):
    h = blur(height, 2, 2)
    out = np.zeros(h.shape, np.int8)
    cuts = np.quantile(h[land], np.cumsum(SHARES)[:-1])
    out[land] = 1 + np.searchsorted(cuts, h[land]).clip(0, len(LEVELS) - 2)
    out[land & (out == 0)] = 1
    return out


def variant(kind):
    land, height = make(23)
    height = height - (1 - edge_falloff()) * 0.8
    land = height > 0
    land &= yy > -0.47
    shaped = blur(height, 3) * 1.1
    north = (-yy + 0.5) * 1.4
    if kind == "north wall":
        shaped += north
    elif kind == "two spines":
        shaped += north * 0.9 + bump(0.33, 0.05, 0.10, 0.35) * 0.8
    elif kind == "court hill":
        shaped += north * 1.0 + bump(-0.30, 0.0, 0.12, 0.14) * 0.9
    elif kind == "court hill + isle peak":
        shaped += north * 1.0 + bump(-0.30, 0.0, 0.12, 0.14) * 0.9 + bump(0.36, 0.22, 0.06, 0.13) * 1.0
    shaped -= np.exp(-(((xx - 0.02) / 0.22) ** 2 + ((yy - 0.25) / 0.35) ** 2)) * 0.5  # sinks toward the bay
    variant.shaped = shaped
    return land, levels(shaped, land)


def render(land, lv, title):
    px = np.zeros((N, N, 3), np.uint8)
    px[:] = (34, 34, 40)
    for i, (_, colour) in enumerate(LEVELS):
        if i:
            px[land & (lv == i)] = colour
    cliff = np.zeros_like(land)
    for axis, step in ((0, 1), (1, 1)):
        cliff |= (np.roll(lv, step, axis) != lv) & land & np.roll(land, step, axis)
    px[cliff] = (52, 46, 40)
    coast = land & ~(np.roll(land, 1, 0) & np.roll(land, -1, 0) & np.roll(land, 1, 1) & np.roll(land, -1, 1))
    px[coast] = (60, 58, 56)
    img = Image.fromarray(px)
    d = ImageDraw.Draw(img)
    d.text((14, 10), title, fill=(235, 225, 200), font=ImageFont.truetype(FONT, 20))
    d.text((N - 30, 10), "N", fill=(235, 225, 200), font=ImageFont.truetype(FONT, 20))
    return img


if __name__ == "__main__":
    kinds = ["north wall", "two spines", "court hill"]
    sheet = Image.new("RGB", (3 * (N + 10) + 10, N + 70), (24, 24, 28))
    for i, kind in enumerate(kinds):
        land, lv = variant(kind)
        sheet.paste(render(land, lv, f"{chr(65 + i)}  {kind}"), (10 + i * (N + 10), 10))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(FONT, 14)
    x = 14
    for i, (name, colour) in enumerate(LEVELS[1:], 1):
        d.rectangle([x, N + 24, x + 14, N + 38], fill=colour)
        d.text((x + 20, N + 23), f"{i} {name}", fill=(190, 185, 170), font=f)
        x += 150
    d.text((14, N + 46), "Dark lines between levels = cliffs (crossed only at ramps, stairs, ladders or drops). North edge = mountain wall.",
           fill=(170, 165, 150), font=f)
    sheet.save(MAPS / "elevation.png")
