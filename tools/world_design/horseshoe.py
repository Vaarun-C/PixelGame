import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

MAPS = Path(__file__).parent / "maps"

N = 500  # 1 px = 4 tiles: 2000 tiles across
FONT = "/System/Library/Fonts/Helvetica.ttc"


def make(seed):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N - 0.5

    def octave(cells):
        small = rng.random((cells, cells)).astype(np.float32)
        return np.asarray(Image.fromarray(small).resize((N, N), Image.BICUBIC)) - 0.5

    def fbm(base, octaves, falloff=0.5):
        total, amp = np.zeros((N, N), np.float32), 1.0
        for o in range(octaves):
            total += octave(base * 2 ** o) * amp
            amp *= falloff
        return total

    # Warp the coordinates so the horseshoe itself bends and leans.
    x = xx + fbm(2, 3) * 0.10
    y = yy + fbm(2, 3) * 0.10
    outer = np.clip((1 - np.sqrt((x / 0.44) ** 2 + ((y + 0.02) / 0.42) ** 2)) * 1.6, -1, 0.5)
    bay = np.exp(-(((x - 0.01) / 0.17) ** 2 + ((y - 0.30) / 0.30) ** 2) ** 1.5)
    detail = fbm(3, 7, 0.62)
    detail /= detail.std()
    height = outer - bay * 1.3 + detail * 0.36
    return height > 0.0, height


def render(land, height, title):
    px = np.zeros((N, N, 3), np.uint8)
    px[:] = (38, 38, 44)
    shallow = (~land) & (height > -0.06)
    px[shallow] = (52, 54, 60)
    px[land] = (132, 124, 106)
    px[land & (height > 0.35)] = (150, 143, 126)
    inner = np.roll(land, 1, 0) & np.roll(land, -1, 0) & np.roll(land, 1, 1) & np.roll(land, -1, 1)
    px[land & ~inner] = (72, 66, 58)
    img = Image.fromarray(px)
    d = ImageDraw.Draw(img)
    for i in range(1, 4):
        d.line([(i * N // 4, 0), (i * N // 4, N)], fill=(60, 60, 68))
        d.line([(0, i * N // 4), (N, i * N // 4)], fill=(60, 60, 68))
    d.text((14, 10), title, fill=(225, 215, 190), font=ImageFont.truetype(FONT, 22))
    d.text((N - 30, 10), "N", fill=(225, 215, 190), font=ImageFont.truetype(FONT, 22))
    return img


if __name__ == "__main__":
    seeds = [int(s) for s in sys.argv[1].split(",")]
    sheet = Image.new("RGB", (len(seeds) * (N + 10) + 10, N + 50), (24, 24, 28))
    for i, seed in enumerate(seeds):
        land, height = make(seed)
        sheet.paste(render(land, height, f"{chr(65 + i)}   seed {seed}"), (10 + i * (N + 10), 10))
    ImageDraw.Draw(sheet).text((14, N + 20), "2000 x 2000 tiles (~18 min walk across), grid every 500 tiles. Light = higher ground, dark band = shallows of the Grey.",
                               fill=(170, 165, 150), font=ImageFont.truetype(FONT, 14))
    sheet.save(sys.argv[2])
