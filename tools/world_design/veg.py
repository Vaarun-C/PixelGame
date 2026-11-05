import numpy as np
from PIL import Image, ImageDraw, ImageFont
from elevation import variant, N, FONT, blur
from pathlib import Path

MAPS = Path(__file__).parent / "maps"

S = 2
land, lv = variant("court hill + isle peak")
yy, xx = np.mgrid[0:N, 0:N]
rng = np.random.default_rng(91)
noise = blur(rng.random((N, N)).astype(np.float32), 6, 3)
noise = (noise - noise.mean()) / noise.std()

ZONES = [  # name, colour, existing art?
    ("Fen (Rot Swamp): reeds, drowned trees", (78, 96, 86), "yes"),
    ("The Long Field: churned mud, no trees", (120, 98, 80), "yes"),
    ("Fallow fields: dry grass, thistle, hedges", (150, 140, 96), "new"),
    ("Dead woods: grey leafless forest, dense", (92, 88, 74), "new"),
    ("Court grounds + chapel ruins", (140, 120, 128), "yes"),
    ("Frost pines: highland, cairns", (112, 128, 132), "yes"),
    ("Bare mountain: rock, snow", (214, 214, 212), "new"),
    ("Ashen Forest: charred trees, embers", (70, 62, 60), "yes"),
    ("Cinder peak: scorched rock", (112, 96, 90), "new"),
]
z = np.full((N, N), -1)
island = (((xx - 418) / 100.0) ** 2 + ((yy - 365) / 120.0) ** 2 + noise * 0.08) < 1
court = (xx < 190) & (yy > 110) & (yy < 330)
field = (((xx - 262) / 95.0) ** 2 + ((yy - 215) / 45.0) ** 2 + noise * 0.15) < 1
z[land & (lv == 1)] = 0
z[land & (lv == 2)] = 2
z[land & (lv == 3)] = 2
z[land & (lv == 3) & (noise > 0.15)] = 3
z[land & (lv == 2) & (noise > 0.9)] = 3
z[land & (lv >= 2) & (lv <= 3) & field] = 1
z[land & (lv == 4)] = 5
z[land & (lv == 5)] = 6
z[land & court & (lv >= 4)] = 4
z[land & island & (lv >= 2)] = 7
z[land & island & (lv == 5)] = 8

if __name__ == "__main__":
    px = np.zeros((N, N, 3), np.uint8)
    px[:] = (34, 34, 40)
    for i, (_, c, _) in enumerate(ZONES):
        px[z == i] = c
    cliff = np.zeros((N, N), bool)
    for axis in (0, 1):
        cliff |= (np.roll(lv, 1, axis) != lv) & land & np.roll(land, 1, axis)
    px[cliff] = (44, 40, 36)
    img = Image.fromarray(px).resize((N * S, N * S), Image.NEAREST)
    d = ImageDraw.Draw(img)
    mid, small = ImageFont.truetype(FONT, 19), ImageFont.truetype(FONT, 15)


    def label(x, y, text, font=mid):
        w = d.textlength(text, font=font)
        p = (x * S - w / 2, y * S)
        for o in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, 2)):
            d.text((p[0] + o[0], p[1] + o[1]), text, fill=(18, 18, 22), font=font)
        d.text(p, text, fill=(250, 240, 215), font=font)


    label(262, 205, "the Long Field")
    label(100, 225, "Old Court")
    label(305, 80, "the White Teeth")
    label(418, 340, "Ashholm")
    label(262, 360, "the Black Mere", small)
    label(140, 300, "Elder Side", small)
    label(400, 175, "Younger Side", small)

    legend = Image.new("RGB", (N * S, 190), (24, 24, 28))
    ld = ImageDraw.Draw(legend)
    for i, (name, c, art) in enumerate(ZONES):
        x, y = 16 + (i % 2) * 500, 12 + (i // 2) * 34
        ld.rectangle([x, y, x + 20, y + 20], fill=c)
        ld.text((x + 30, y + 2), f"{name}{'   [new art]' if art == 'new' else ''}", fill=(205, 200, 185), font=small)
    out = Image.new("RGB", (N * S, N * S + 190))
    out.paste(img, (0, 0))
    out.paste(legend, (0, N * S))
    out.save(MAPS / "vegetation.png")
    for i, (name, _, _) in enumerate(ZONES):
        print(f"{(z == i).sum() / land.sum() * 100:5.1f}%  {name}")
