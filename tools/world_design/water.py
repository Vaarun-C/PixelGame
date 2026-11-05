import heapq
import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from elevation import variant, N, FONT, blur
import veg  # noqa: F401  (builds the vegetation zones; reuse its image)

MAPS = Path(__file__).parent / "maps"

land, lv = variant("court hill + isle peak")
h = blur(variant.shaped, 2, 2)
NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# The surface the player climbs: the levels, smoothed, with peaks and saddles inside the mountain
# tier so passes exist.
top = (lv == 5)
cut5 = variant.shaped[top].min()
relief = np.where(top, (variant.shaped - cut5) / (variant.shaped[top].max() - cut5), 0) * 3.0
E = blur(lv.astype(np.float32) + relief, 2, 2)


def fill(surface):
    """Priority-flood: raise hollows until every land cell drains to the Mere."""
    filled = np.where(land, np.inf, surface)
    done = ~land
    heap = []
    for y in range(N):
        for x in range(N):
            if land[y, x] and any(0 <= y + dy < N and 0 <= x + dx < N and not land[y + dy, x + dx] for dy, dx in NB):
                filled[y, x] = surface[y, x]
                done[y, x] = True
                heapq.heappush(heap, (surface[y, x], y, x))
    while heap:
        z, y, x = heapq.heappop(heap)
        for dy, dx in NB:
            ny, nx = y + dy, x + dx
            if 0 <= ny < N and 0 <= nx < N and not done[ny, nx]:
                done[ny, nx] = True
                filled[ny, nx] = max(surface[ny, nx], z + 1e-6)
                heapq.heappush(heap, (filled[ny, nx], ny, nx))
    return filled


lake = land & (fill(h) - h > 0.02)

# Rivers run over the level surface plus fine roughness: across a cliff the drop wins (a fall),
# on a flat tier the roughness steers them into bends.
rough = np.random.default_rng(17)
Hr = E + blur(rough.random((N, N)).astype(np.float32), 5, 2) * 1.2 + blur(rough.random((N, N)).astype(np.float32), 1, 1) * 0.15
Hr[lake] = -5
filled = fill(Hr)
flow = np.where(land, 1.0, 0.0)
down = {}
for idx in np.argsort(-np.where(land, filled, -np.inf), axis=None):
    y, x = divmod(int(idx), N)
    if not land[y, x]:
        continue
    best, to = filled[y, x], None
    for dy, dx in NB:
        ny, nx = y + dy, x + dx
        if 0 <= ny < N and 0 <= nx < N and filled[ny, nx] < best:
            best, to = filled[ny, nx], (ny, nx)
    if to:
        down[(y, x)] = to
        if land[to]:
            flow[to] += flow[y, x]
river = land & (flow > 900) & ~lake
stream = land & (flow > 250) & ~river & ~lake
falls = [(y, x) for (y, x) in zip(*np.nonzero(river)) if (y, x) in down and land[down[(y, x)]] and lv[down[(y, x)]] < lv[y, x]]


def courses(mask):
    """Each water course as a list of cells from its head down to where it joins water."""
    heads = [c for c in zip(*np.nonzero(mask)) if not any(down.get((c[0] + dy, c[1] + dx)) == c and mask[c[0] + dy, c[1] + dx] for dy, dx in NB if 0 <= c[0] + dy < N and 0 <= c[1] + dx < N)]
    seen, out = set(), []
    for c in sorted(heads, key=lambda c: -flow[c]):
        line = [c]
        while line[-1] in down and line[-1] not in seen:
            seen.add(line[-1])
            line.append(down[line[-1]])
            if not land[line[-1]] or lake[line[-1]]:
                break
        out.append(line)
    return out

# Roads: cheapest paths over the land. Cliffs, mountains and woods cost more; rivers mean a bridge.
cost = np.where(land, 1.0, np.inf)
cost[lv == 4] = 2.5
cost[lv == 5] = 7.0
cost[veg.z == 3] += 2.5
near = land.copy()
for _ in range(5):
    near = near | np.roll(near, 1, 0) | np.roll(near, -1, 0) | np.roll(near, 1, 1) | np.roll(near, -1, 1)
shallow = near & ~land
cost[shallow] = 40.0
cost[lake] = np.inf
cost[river] = 25.0
cost[stream] = 4.0
# Roads pay steeply for grade, so they wind up slopes instead of climbing straight.
gy_, gx_ = np.gradient(E)
G0 = np.percentile(np.hypot(gx_, gy_)[land], float(os.environ.get("P", 55)))
W, T = float(os.environ.get("W", 80)), float(os.environ.get("T", 0.6))
MOVES = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3) if (dy, dx) != (0, 0) and abs(dy) + abs(dx) <= 3 and not (abs(dy) == 2 and abs(dx) == 2) and not (abs(dy) + abs(dx) == 2 and 0 in (dy, dx))]
wiggle = blur(np.random.default_rng(5).random((N, N)).astype(np.float32), 3, 2)
cost = cost * (1 + (wiggle - wiggle.mean()) / wiggle.std() * 0.35).clip(0.4, 2)


def route(a, b):
    best = np.full((N, N), np.inf)
    prev = {}
    best[a] = 0
    heap = [(0.0, a)]
    while heap:
        c, (y, x) = heapq.heappop(heap)
        if (y, x) == b:
            break
        if c > best[y, x]:
            continue
        for dy, dx in MOVES:
            ny, nx = y + dy, x + dx
            if not (0 <= ny < N and 0 <= nx < N) or cost[ny, nx] == np.inf or cost[y + round(dy / 2), x + round(dx / 2)] == np.inf:
                continue
            dist = (dy * dy + dx * dx) ** 0.5
            grade = abs(E[ny, nx] - E[y, x]) / dist / G0
            nc = c + dist * (cost[ny, nx] + W * max(0.0, grade - T) ** 2)
            if nc < best[ny, nx]:
                best[ny, nx] = nc
                prev[(ny, nx)] = (y, x)
                heapq.heappush(heap, (nc, (ny, nx)))
    path, p = [], b
    while p != a:
        path.append(p)
        p = prev[p]
    return path + [a]


def nearest_land(y, x):
    ys, xs = np.nonzero(land & ~lake & ~river)
    i = np.argmin((ys - y) ** 2 + (xs - x) ** 2)
    return int(ys[i]), int(xs[i])


P = {k: nearest_land(*v) for k, v in {
    "cross": (202, 264), "court": (230, 100), "pass": (22, 300), "notch": (160, 325), "tarn": (100, 300), "east": (200, 425),
    "ashholm": (360, 420), "southwest": (385, 115), "eastcoast": (250, 380),
}.items()}
ROADS = [
    ("the King's Road", ["cross", "court"]),
    ("the Pass road", ["cross", "notch", "tarn", "pass"]),
    ("the East road", ["cross", "east", "ashholm"]),
    ("the Low road", ["court", "southwest"]),
]
paths = {}
for name, stops in ROADS:
    paths[name] = sum((route(P[a], P[b])[::-1] for a, b in zip(stops, stops[1:])), [])

S = 2


def smooth(cells, every=2, rounds=3):
    pts = [(x * S + 1.0, y * S + 1.0) for y, x in cells[::every]] + [(cells[-1][1] * S + 1.0, cells[-1][0] * S + 1.0)]
    for _ in range(rounds):
        pts = [pts[0]] + [q for a, b in zip(pts, pts[1:]) for q in ((a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75))] + [pts[-1]]
    return pts


if __name__ == "__main__":
    img = Image.open(MAPS / "vegetation.png").crop((0, 0, N * S, N * S))
    px = np.array(img)


    def paint(mask, colour):
        big = np.kron(mask, np.ones((S, S), bool))
        px[big] = colour


    paint(lake, (52, 66, 78))
    img = Image.fromarray(px)
    d = ImageDraw.Draw(img)


    # Width grows with the water gathered: a stream at its head, a river near the Mere.
    for line in courses(river | stream):
        if len(line) < 3:
            continue
        pts = smooth(line)
        for i in range(len(pts) - 1):
            f = flow[line[min(len(line) - 1, i // 4)]]
            w = 1 if f < 900 else 3 if f < 3000 else 4
            d.line([pts[i], pts[i + 1]], fill=(70, 96, 112) if f < 900 else (60, 92, 118), width=w)
    bridges = []
    for name, path in paths.items():
        pts = smooth(path, 2, 2)
        d.line(pts, fill=(28, 24, 22), width=6)
        d.line(pts, fill=(196, 178, 140), width=3)
        bridges += [p for p in path if river[p] or stream[p]]
        causeway = [(x * S, y * S) for y, x in path if shallow[y, x]]
        for cx_, cy_ in causeway:
            d.rectangle([cx_ - 2, cy_ - 2, cx_ + 3, cy_ + 3], fill=(150, 120, 90))
    for y, x in falls[::6]:
        d.ellipse([x * S - 5, y * S - 5, x * S + 5, y * S + 5], outline=(230, 236, 240), width=2)
    for y, x in bridges[::3]:
        d.rectangle([x * S - 4, y * S - 4, x * S + 4, y * S + 4], fill=(120, 84, 56), outline=(28, 24, 22))
    cy, cx = P["cross"]
    d.ellipse([cx * S - 9, cy * S - 9, cx * S + 9, cy * S + 9], outline=(240, 210, 130), width=3)
    small = ImageFont.truetype(FONT, 15)
    legend = Image.new("RGB", (N * S, 70), (24, 24, 28))
    ld = ImageDraw.Draw(legend)
    items = [((60, 92, 118), "river"), ((70, 96, 112), "stream"), ((52, 66, 78), "lake / tarn"), ((196, 178, 140), "old crown road"),
             ((120, 84, 56), "bridge / ford"), ((230, 236, 240), "waterfall (river drops a level)")]
    for i, (c, t) in enumerate(items):
        x, y = 16 + (i % 3) * 330, 10 + (i // 3) * 28
        ld.rectangle([x, y, x + 20, y + 18], fill=c)
        ld.text((x + 30, y + 1), t, fill=(205, 200, 185), font=small)
    out = Image.new("RGB", (N * S, N * S + 70))
    out.paste(img, (0, 0))
    out.paste(legend, (0, N * S))
    out.save(MAPS / "water_roads.png")
    out.crop((480, 20, 780, 420)).resize((600, 800), Image.NEAREST).save(MAPS / "pass_zoom.png")
    out.crop((150, 380, 450, 620)).resize((600, 480), Image.NEAREST).save(MAPS / "court_zoom.png")
    print("lake%", round(lake.sum() / land.sum() * 100, 1), "river cells", river.sum(), "falls", len(falls))
    for name, path in paths.items():
        print(name, len(path) * 4, "tiles")
