"""Exports the agreed map at tile resolution for godot/tools/build_world.gd.
Usage: .venv/bin/python tools/world_design/export.py   (writes out/terrain.png, level.png, ramp.png, places.json)

The design is 500 px, one px = 4 tiles. Each of the 2000 x 2000 tile corners samples the design at
a slightly jittered spot so zone borders don't show the 4-tile steps, then rivers and roads are drawn
over at tile resolution. Pixel values: terrain id (biome * 4 + ground), level (0 water - 5), ramp (0/1).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import check_export
import cliffs
import landmarks
import veg
import water

OUT = Path(__file__).parent / "out"
SIZE = 2000
K = SIZE // water.N
# Biome indices in godot/scripts/world/biomes.gd.
BATTLEFIELD, SWAMP, RUINS, ASHEN, FROZEN, FALLOW, WOODS, MOUNTAIN, CINDER, WATER, ROAD = 0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11
DEEP, RIVER, SHALLOW, STREAM = WATER * 4, WATER * 4 + 1, WATER * 4 + 2, WATER * 4 + 3
# Zone (veg.ZONES order) -> biome; grounds come from noise.
# Villages.REACH in godot/scripts/world/villages.gd: no village outline reaches further from its well.
VILLAGE_REACH = check_export.VILLAGE_REACH
ZONE_BIOME = [SWAMP, BATTLEFIELD, FALLOW, WOODS, RUINS, FROZEN, MOUNTAIN, ASHEN, CINDER]
rng = np.random.default_rng(23)


def smooth_noise(cells):
    return np.asarray(Image.fromarray(rng.random((cells, cells)).astype(np.float32)).resize((SIZE, SIZE), Image.BICUBIC))


def sample(grid, jy, jx):
    """The design grid read at every tile corner, through the jitter."""
    ys, xs = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    iy = np.clip((ys / K + jy).astype(int), 0, water.N - 1)
    ix = np.clip((xs / K + jx).astype(int), 0, water.N - 1)
    return grid[iy, ix]


def grow(mask, tiles):
    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(tiles * 2 + 1))) > 0


def lines(polylines, width):
    """Rasterises design-cell polylines at tile resolution, `width` tiles wide (a number or a per-line list)."""
    img = Image.new("L", (SIZE, SIZE))
    d = ImageDraw.Draw(img)
    for i, cells in enumerate(polylines):
        pts = [((x - 1) / water.S * K + K / 2, (y - 1) / water.S * K + K / 2) for x, y in water.smooth(cells)]
        w = width[i] if isinstance(width, list) else width
        d.line(pts, fill=255, width=w, joint="curve")
    return np.asarray(img) > 0


def ground(zone_biome, n):
    """Ground row 0-2 by noise; ground 3 is set by rule (pools, thicket, crag) where the biome uses it."""
    g = np.where(n > 0.62, 2, np.where(n < 0.38, 1, 0))
    return np.where(np.isin(zone_biome, [BATTLEFIELD]) & (n > 0.8), 3, g)


def export():
    jitter = (smooth_noise(60) - 0.5) * 3, (smooth_noise(60) - 0.5) * 3
    zone = sample(veg.z, *jitter)
    level = sample(water.lv, *jitter).astype(np.uint8)
    lake = sample(water.lake, *jitter)
    core = sample(cliffs.core, *jitter)
    open_cell = sample(cliffs.gaps > 0.6, *jitter)
    n = smooth_noise(250)

    land = (zone >= 0) & ~lake
    biome = np.where(land, np.array(ZONE_BIOME)[np.clip(zone, 0, 8)], WATER)
    terrain = (biome * 4 + ground(biome, n)).astype(np.uint8)
    terrain[(biome == SWAMP) & (n > 0.85)] = SWAMP * 4 + 3
    terrain[(biome == WOODS) & core] = WOODS * 4 + 3
    level[~land] = 0
    shore = ~land & grow(land, 2)
    terrain[~land] = DEEP
    terrain[shore] = SHALLOW

    rivers = water.courses(water.river | water.stream)
    widths = [int(np.clip(water.flow[c[len(c) // 2]] / 400, 2, 8)) if water.flow[c[len(c) // 2]] > 900 else 2 for c in rivers]
    wet = lines(rivers, widths) & land
    big = lines([c for c, w in zip(rivers, widths) if w > 2], [w for w in widths if w > 2]) & land
    terrain[wet] = STREAM
    terrain[big] = RIVER

    road = lines(list(water.paths.values()), 3)
    pass_road = grow(lines([water.paths["the Pass road"]], 3), 4)
    mountain = biome == MOUNTAIN
    terrain[mountain] = MOUNTAIN * 4 + 3
    terrain[mountain & pass_road] = MOUNTAIN * 4 + np.where(n[mountain & pass_road] > 0.5, 1, 0)
    cy, cx = (np.array(landmarks.CHAPELS["Court Chapel"]) * K + K // 2)
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    near_court = (ys - cy) ** 2 + (xs - cx) ** 2 < 40 ** 2
    over_river = road & np.isin(terrain, [RIVER, STREAM])
    over_water = road & ~land
    terrain[road] = ROAD * 4
    terrain[road & near_court] = ROAD * 4 + 1
    terrain[over_water] = ROAD * 4 + 2
    terrain[over_river] = ROAD * 4 + 3
    level[over_water] = 1

    # The agreed rules: lowland-plain edges are slopes, plain-upland edges escarpments with gaps,
    # anything touching highland or mountain a cliff; roads always ramp.
    ramp = grow(road, 1)
    for axis in (0, 1):
        for step in (1, -1):
            other = np.roll(level, step, axis)
            hi = np.maximum(level, other)
            ramp |= (other != level) & ((hi <= 2) | ((hi == 3) & open_cell))
    ramp &= land | road

    found = places()
    for p in found:
        if p["kind"] == "village":
            settle(terrain, level, ramp, p["tile"], ys, xs)
    blocked = np.ones_like(land)
    blocked[:-1, :-1] = ~check_export.tiles_walkable(terrain, level, ramp.astype(np.uint8))
    for p in found:
        p["tile"] = nearest_walkable(blocked, p["tile"])

    OUT.mkdir(exist_ok=True)
    for name, data in (("terrain", terrain), ("level", level), ("ramp", ramp.astype(np.uint8))):
        Image.fromarray(data.astype(np.uint8), "L").save(OUT / f"{name}.png")
    (OUT / "places.json").write_text(json.dumps(found, indent=1))


def settle(terrain, level, ramp, xy, ys, xs):
    """The game paints village ground within VILLAGE_REACH of the well, so the land there is made
    one level and dry: solid or wet ground becomes the area's base land. A ring of ramps outside
    keeps the levelled ground from turning into a wall round the village."""
    x, y = xy
    dist = (ys - y) ** 2 + (xs - x) ** 2
    near = dist < VILLAGE_REACH ** 2
    base = terrain[y, x] // 4
    if base in (WATER, ROAD):
        base = FALLOW
    level[near] = level[y, x]
    terrain[near & np.isin(terrain, list(check_export.SOLID) + [SHALLOW, STREAM])] = base * 4
    ramp[near | (dist < (VILLAGE_REACH + 3) ** 2)] = True


def nearest_walkable(blocked, xy):
    """The nearest tile the game lets you stand on (check_export.tiles_walkable)."""
    x, y = xy
    for r in range(0, 40):
        box = blocked[y - r:y + r + 1, x - r:x + r + 1]
        free = np.argwhere(~box)
        if len(free):
            dy, dx = free[np.argmin(((free - r) ** 2).sum(1))] - r
            return [int(x + dx), int(y + dy)]
    raise ValueError(f"no walkable ground near {xy}")


def tile(yx):
    return [int(yx[1]) * K + K // 2, int(yx[0]) * K + K // 2]


def places():
    snap = landmarks.snap
    found = []
    for name, (yx, _) in landmarks.VILLAGES.items():
        found.append({"kind": "village", "name": name.replace(" (start)", ""), "tile": tile(snap(*yx)), "start": "(start)" in name})
    for name, (yx, _) in landmarks.CRIMSON.items():
        found.append({"kind": "prisoner", "name": name, "tile": tile(snap(*yx)), "start": False})
    for name, yx in landmarks.CHAPELS.items():
        found.append({"kind": "chapel", "name": name.replace(" (chapel ruins)", ""), "tile": tile(snap(*yx)), "start": False})
    for i, (road, f) in enumerate(landmarks.SHRINES):
        path = water.paths[road]
        found.append({"kind": "shrine", "name": f"Shrine {i + 1}", "tile": tile(path[int(len(path) * f)]), "start": False})
    found.append({"kind": "crossroads", "name": "Crossroads", "tile": tile(water.P["cross"]), "start": False})
    found.append({"kind": "mother_house", "name": "Mother House", "tile": tile(snap(96, 150)), "start": False})
    found.append({"kind": "prologue", "name": "Prologue field", "tile": tile(snap(*landmarks.PROLOGUE)), "start": False})
    return found


if __name__ == "__main__":
    export()
    print("exported to", OUT)
