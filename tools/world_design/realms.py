import numpy as np
from PIL import Image, ImageDraw, ImageFont
from elevation import variant, render, N, FONT, LEVELS
from pathlib import Path

MAPS = Path(__file__).parent / "maps"

S = 2
land, lv = variant("court hill + isle peak")
if __name__ == "__main__":
    img = render(land, lv, "").resize((N * S, N * S), Image.NEAREST)
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 26)
    mid = ImageFont.truetype(FONT, 19)
    small = ImageFont.truetype(FONT, 15)


    def at(x, y):
        return (x * S, y * S)


    def label(x, y, text, font=mid, colour=(250, 240, 215)):
        w = d.textlength(text, font=font)
        p = (x * S - w / 2, y * S)
        for ox, oy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, 2)):
            d.text((p[0] + ox, p[1] + oy), text, fill=(20, 20, 24), font=font)
        d.text(p, text, fill=colour, font=font)


    def dashed(points, colour=(150, 40, 36), width=4):
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            steps = int(np.hypot(x1 - x0, y1 - y0) / 6)
            for k in range(0, steps, 2):
                a, b = k / steps, min(1, (k + 1) / steps)
                d.line([at(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), at(x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=colour, width=width)


    # The heirs' line: from the bay head north through the field to the mountains.
    dashed([(262, 238), (268, 200), (258, 160), (270, 120), (262, 70)])
    d.ellipse([at(258, 196), at(270, 208)], outline=(230, 200, 120), width=3)

    label(250, 12, "THE WAKE", big)
    label(305, 80, "the White Teeth  (Frozen Pass)")
    label(100, 215, "Court Hill", mid)
    label(100, 238, "the Old Court  (king's seat)", small)
    label(140, 290, "ELDER SIDE", big, (225, 205, 170))
    label(390, 160, "YOUNGER SIDE", big, (225, 205, 170))
    label(262, 212, "crossroads", small, (240, 215, 140))
    label(262, 228, "the Long Field", mid)
    label(262, 360, "the Black Mere", mid, (170, 180, 185))
    label(195, 330, "Rot Swamp", small)
    label(352, 262, "Rot Swamp", small)
    label(418, 330, "Ashholm", mid)
    label(418, 352, "(Ashen Forest, the Cinder peak)", small)
    label(470, 470, "N up", small, (170, 165, 150))

    legend = Image.new("RGB", (N * S, 90), (24, 24, 28))
    ld = ImageDraw.Draw(legend)
    x = 16
    for i, (name, colour) in enumerate(LEVELS[1:], 1):
        ld.rectangle([x, 14, x + 18, 32], fill=colour)
        ld.text((x + 26, 14), f"{i} {name}", fill=(200, 195, 180), font=small)
        x += 180
    ld.line([(16, 60), (60, 60)], fill=(150, 40, 36), width=4)
    ld.text((70, 50), "the heirs' line (where the two claims met)    the whole map is ~2000 tiles, ~18 min walk", fill=(200, 195, 180), font=small)
    out = Image.new("RGB", (N * S, N * S + 90))
    out.paste(img, (0, 0))
    out.paste(legend, (0, N * S))
    out.save(MAPS / "realms.png")
