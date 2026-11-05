from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import water
from pathlib import Path

MAPS = Path(__file__).parent / "maps"

g = vars(water)
land, lake, river, lv, paths, N, S, FONT, blur = (g[k] for k in ("land", "lake", "river", "lv", "paths", "N", "S", "FONT", "blur"))
woods = g["veg"].z == 3
NB4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

road = np.zeros_like(land)
for path in paths.values():
    for y, x in path:
        road[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = True

# Edges between levels. Low ground (lowland to plain) is all slope; high ground (anything up to
# highland or mountain) is all cliff; plain to upland is an escarpment broken by gaps. Roads always
# get a ramp.
gaps = blur(np.random.default_rng(29).random((N, N)).astype(np.float32), 6, 3)
gaps = (gaps - gaps.mean()) / gaps.std()


def edge_open(a, b):
    lo, hi = sorted((lv[a], lv[b]))
    if road[a] or road[b]:
        return True
    if hi >= 4:
        return False
    if hi == 2:
        return True
    return gaps[a] > 0.6


# Woods: the edge of a wood can be walked; its core (more than ~8 tiles in) is a wall of trees.
core = woods.copy()
for _ in range(2):
    core = core & np.roll(core, 1, 0) & np.roll(core, -1, 0) & np.roll(core, 1, 1) & np.roll(core, -1, 1)
core &= ~road

walk = land & ~lake & ~core & ((lv < 5) | road)
walk &= ~river | road


def reach(start):
    seen = np.zeros_like(land)
    q = deque([start])
    seen[start] = True
    while q:
        c = q.popleft()
        for dy, dx in NB4:
            n = (c[0] + dy, c[1] + dx)
            if 0 <= n[0] < N and 0 <= n[1] < N and walk[n] and not seen[n] and (lv[n] == lv[c] or edge_open(c, n)):
                seen[n] = True
                q.append(n)
    return seen


reached = reach((248, 182))

if __name__ == "__main__":
    # Draw: cliffs thick and dark, slopes faint, wood cores hatched, sealed ground tinted red.
    img = Image.open(MAPS / "landmarks.png")
    legend_h = img.height - N * S
    base = img.crop((0, 0, N * S, N * S))
    px = np.array(base).astype(np.int32)
    sealed = land & ~lake & ~reached & ~(lv == 5) & ~core
    big = lambda m: np.kron(m, np.ones((S, S), bool))
    px[big(sealed)] = (px[big(sealed)] * 0.55 + np.array([150, 40, 40]) * 0.45).astype(np.int32)
    hatch = big(core) & ((np.add.outer(np.arange(N * S), np.arange(N * S)) % 6) < 2)
    px[hatch] = (30, 28, 24)
    cliff = np.zeros((N, N), bool)
    slope = np.zeros((N, N), bool)
    for y in range(N - 1):
        for x in range(N - 1):
            for n in ((y + 1, x), (y, x + 1)):
                if land[y, x] and land[n] and lv[y, x] != lv[n]:
                    (slope if edge_open((y, x), n) else cliff)[y, x] = True
    px[big(slope)] = (px[big(slope)] * 0.6 + 200 * 0.4).astype(np.int32)
    thick = cliff | np.roll(cliff, 1, 0) | np.roll(cliff, 1, 1)
    px[big(thick)] = (26, 22, 20)
    out = Image.fromarray(px.astype(np.uint8))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(FONT, 14)
    legend = Image.new("RGB", (N * S, 64), (24, 24, 28))
    ld = ImageDraw.Draw(legend)
    ld.rectangle([16, 12, 46, 18], fill=(26, 22, 20), outline=(90, 90, 90)); ld.text((54, 6), "cliff (wall)", fill=(205, 200, 185), font=f)
    ld.rectangle([180, 12, 210, 16], fill=(200, 200, 200)); ld.text((218, 6), "slope / ramp (walkable)", fill=(205, 200, 185), font=f)
    for k in range(0, 24, 6):
        ld.line([(400 + k, 20), (412 + k, 8)], fill=(150, 150, 150), width=2)
    ld.text((430, 6), "dense wood core (wall)", fill=(205, 200, 185), font=f)
    ld.rectangle([640, 8, 660, 22], fill=(150, 60, 60)); ld.text((668, 6), "sealed: can't reach from Greywell", fill=(205, 200, 185), font=f)
    ld.text((16, 36), "Rivers block except at bridges; mountains block except on the Pass road.", fill=(170, 165, 150), font=f)
    full = Image.new("RGB", (N * S, N * S + 64))
    full.paste(out, (0, 0))
    full.paste(legend, (0, N * S))
    full.save(MAPS / "cliffs.png")

    # Report the sealed pockets, biggest first.
    lab = np.zeros((N, N), int)
    pockets = []
    for c in zip(*np.nonzero(sealed)):
        if lab[c]:
            continue
        q, cells = deque([c]), []
        lab[c] = len(pockets) + 1
        while q:
            a = q.popleft()
            cells.append(a)
            for dy, dx in NB4:
                n = (a[0] + dy, a[1] + dx)
                if 0 <= n[0] < N and 0 <= n[1] < N and sealed[n] and not lab[n]:
                    lab[n] = len(pockets) + 1
                    q.append(n)
        pockets.append(cells)
    pockets.sort(key=len, reverse=True)
    total = (land & ~lake & ~(lv == 5) & ~core).sum()
    print(f"reachable {reached.sum() / total * 100:.0f}% of walkable land; cliffs {cliff.sum()} cells, slopes {slope.sum()}")
    for cells in pockets[:10]:
        ys, xs = zip(*cells)
        print(f"pocket {len(cells) * 16:>7} tiles around (y{int(np.mean(ys))}, x{int(np.mean(xs))}) levels {sorted(set(int(lv[c]) for c in cells))}")
