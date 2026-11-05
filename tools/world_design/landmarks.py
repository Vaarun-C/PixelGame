import numpy as np
from PIL import Image, ImageDraw, ImageFont

import water
from pathlib import Path

MAPS = Path(__file__).parent / "maps"

g = vars(water)
land, lake, river, lv, paths, N, S, FONT = g["land"], g["lake"], g["river"], g["lv"], g["paths"], g["N"], g["S"], g["FONT"]
ok = land & ~lake & ~river


def snap(y, x):
    ys, xs = np.nonzero(ok)
    i = np.argmin((ys - y) ** 2 + (xs - x) ** 2)
    return int(ys[i]), int(xs[i])


VILLAGES = {  # name: (y, x), why
    "Greywell (start)": ((248, 182), "by the King's Road bridge, under Court Hill"),
    "Ravengate": ((172, 318), "foot of the Pass road"),
    "Blackford": ((262, 322), "stilts on the east shore of the bay"),
    "Ashbarrow": ((222, 402), "the last village before Ashholm"),
    "Thornstead": ((372, 124), "end of the Low road, south-west shore"),
}
CRIMSON = {
    "Paymaster": ((200, 332), "his company's earthworks, east Long Field"),
    "Ford-holder": ((318, 168), "the drowned ford, mouth of the Court river"),
    "Coal-master": ((322, 398), "the great pyres of Ashholm"),
    "Pass warden": ((42, 306), "the ice tombs, top of the Pass"),
    "King's champion": ((226, 104), "the Court Chapel, Old Court"),
    "Court keeper": ((96, 150), "the Mother House undercroft"),
}
CHAPELS = {
    "Court Chapel": (226, 104),
    "Mere Chapel (chapel ruins)": (124, 208),
    "First keeper's chapel": (82, 292),
}
PROLOGUE = (214, 216)
SHRINES = [("the King's Road", 0.45), ("the Low road", 0.6), ("the Pass road", 0.3), ("the Pass road", 0.75),
           ("the East road", 0.3), ("the East road", 0.62), ("the East road", 0.88)]

if __name__ == "__main__":
    img = Image.open(MAPS / "water_roads.png").crop((0, 0, N * S, N * S))
    d = ImageDraw.Draw(img)
    mid, small = ImageFont.truetype(FONT, 17), ImageFont.truetype(FONT, 13)


    def label(px, py, text, font=small, colour=(250, 240, 215)):
        for o in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, 2)):
            d.text((px + o[0], py + o[1]), text, fill=(18, 18, 22), font=font)
        d.text((px, py), text, fill=colour, font=font)


    def at(y, x):
        return x * S, y * S


    for name, (yx, _) in VILLAGES.items():
        x, y = at(*snap(*yx))
        d.rectangle([x - 9, y - 4, x + 9, y + 9], fill=(150, 112, 70), outline=(20, 18, 16), width=2)
        d.polygon([(x - 12, y - 3), (x, y - 13), (x + 12, y - 3)], fill=(96, 70, 48), outline=(20, 18, 16))
        label(x + 14, y - 8, name, mid)
    for name, yx in CHAPELS.items():
        x, y = at(*snap(*yx))
        d.rectangle([x - 2, y - 12, x + 2, y + 8], fill=(225, 220, 205), outline=(20, 18, 16))
        d.rectangle([x - 7, y - 7, x + 7, y - 3], fill=(225, 220, 205), outline=(20, 18, 16))
        label(x + 10, y + (14 if name == "Court Chapel" else 6), name)
    for name, (yx, _) in CRIMSON.items():
        x, y = at(*snap(*yx))
        d.rectangle([x - 6, y - 6, x + 6, y + 6], fill=(150, 30, 34), outline=(240, 200, 190), width=2)
        offset = {"King's champion": (-50, -30), "Court keeper": (9, -24)}.get(name, (9, -6))
        label(x + offset[0], y + offset[1], name, small, (240, 170, 160))
    cx, cy = at(*snap(96, 150))
    for a in range(0, 360, 30):
        d.arc([cx - 18, cy - 18, cx + 18, cy + 18], a, a + 15, fill=(240, 210, 130), width=3)
    label(cx + 9, cy - 6, "Mother House (hidden, no road)", small, (240, 215, 140))
    x, y = at(202, 264)
    d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=(240, 210, 130), width=3)
    label(x - 35, y - 30, "crossroads", small, (240, 215, 140))
    x, y = at(*snap(*PROLOGUE))
    d.line([x - 7, y - 7, x + 7, y + 7], fill=(230, 60, 50), width=4)
    d.line([x - 7, y + 7, x + 7, y - 7], fill=(230, 60, 50), width=4)
    label(x - 40, y + 10, "prologue field", small, (240, 170, 160))
    for road, f in SHRINES:
        path = paths[road]
        y, x = path[int(len(path) * f)]
        x, y = at(y, x)
        d.polygon([(x, y - 8), (x + 7, y), (x, y + 8), (x - 7, y)], fill=(235, 235, 240), outline=(20, 18, 16))

    legend = Image.new("RGB", (N * S, 76), (24, 24, 28))
    ld = ImageDraw.Draw(legend)
    f14 = ImageFont.truetype(FONT, 14)
    ld.rectangle([16, 18, 34, 32], fill=(150, 112, 70)); ld.text((42, 14), "village (safe, respawn)", fill=(205, 200, 185), font=f14)
    ld.polygon([(262, 14), (270, 23), (262, 32), (254, 23)], fill=(235, 235, 240)); ld.text((280, 14), "wild shrine (claim as respawn)", fill=(205, 200, 185), font=f14)
    ld.rectangle([520, 16, 534, 30], fill=(150, 30, 34)); ld.text((542, 14), "Crimson prisoner", fill=(205, 200, 185), font=f14)
    ld.rectangle([700, 12, 704, 32], fill=(225, 220, 205)); ld.text((714, 14), "chapel", fill=(205, 200, 185), font=f14)
    ld.text((16, 46), "Roads, rivers and vegetation as before. Mother House: up the north-west valley, only found once its ledger clues are gathered.", fill=(170, 165, 150), font=f14)
    out = Image.new("RGB", (N * S, N * S + 76))
    out.paste(img, (0, 0))
    out.paste(legend, (0, N * S))
    out.save(MAPS / "landmarks.png")
    for name, (yx, why) in VILLAGES.items():
        print("village", name, yx, "->", snap(*yx), "lv", lv[snap(*yx)])
