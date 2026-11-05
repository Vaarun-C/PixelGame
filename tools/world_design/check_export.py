"""Checks the tile-resolution export in out/. Usage: .venv/bin/python tools/world_design/check_export.py"""
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).parent / "out"
SIZE = 2000
WATER = range(40, 44)
# Terrain ids (biome * 4 + ground) nobody can walk on: deep water, river, wood thicket, mountain crag.
SOLID = {40, 41, 31, 35}
# Villages.REACH in godot/scripts/world/villages.gd: no village outline reaches further from its well.
VILLAGE_REACH = 20
COUNTS = {"village": 5, "prisoner": 6, "chapel": 3, "shrine": 7}


def layer(name):
    img = Image.open(OUT / f"{name}.png")
    assert img.size == (SIZE, SIZE) and img.mode == "L", f"{name}.png is {img.size} {img.mode}"
    return np.asarray(img)


def tiles_walkable(terrain, level, ramp):
    """The game's rule (godot/scripts/world/world_map.gd walkable), for tile (x, y) with corners
    (x, y) to (x + 1, y + 1): blocked when two or more corners are solid ground, open on any ramp
    corner, else blocked across a level edge or on a wall face (higher ground just north)."""
    solid = np.isin(terrain, list(SOLID)).astype(np.int8)
    tl, tr, bl, br = (slice(0, -1), slice(0, -1)), (slice(0, -1), slice(1, None)), (slice(1, None), slice(0, -1)), (slice(1, None), slice(1, None))
    corners = lambda a: [a[tl], a[tr], a[bl], a[br]]
    solid_count = sum(corners(solid))
    any_ramp = np.logical_or.reduce([c > 0 for c in corners(ramp)])
    lv = corners(level.astype(np.int16))
    flat = (lv[1] == lv[0]) & (lv[2] == lv[0]) & (lv[3] == lv[0])
    north = np.full(level.shape, 255, np.int16)
    north[1:] = level[:-1]
    wall = (north[tl] > lv[0]) | (north[tr] > lv[1])
    return (solid_count < 2) & (any_ramp | (flat & ~wall))


def reachable(start, walk):
    seen = np.zeros(walk.shape, bool)
    seen[start] = True
    queue = deque([start])
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < walk.shape[0] and 0 <= nx < walk.shape[1] and walk[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                queue.append((ny, nx))
    return seen


def main():
    terrain, level, ramp = layer("terrain"), layer("level"), layer("ramp")
    assert terrain.max() < 48, f"terrain id {terrain.max()}"
    assert level.max() <= 5, f"level {level.max()}"
    assert set(np.unique(ramp)) <= {0, 1}, f"ramp values {np.unique(ramp)}"
    wet = level == 0
    assert np.isin(terrain[wet], list(WATER)).all(), "level 0 corner without water terrain"

    places = json.loads((OUT / "places.json").read_text())
    for kind, n in COUNTS.items():
        found = [p for p in places if p["kind"] == kind]
        assert len(found) == n, f"{len(found)} {kind}s, want {n}"
    starts = [p for p in places if p.get("start")]
    assert len(starts) == 1, f"{len(starts)} start places"

    # The game paints village ground over everything within VILLAGE_REACH of a village's well, so
    # nothing there may be solid or on another level, or it would block as an invisible wall.
    solid = np.isin(terrain, list(SOLID))
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    for p in places:
        if p["kind"] == "village":
            x, y = p["tile"]
            near = (ys - y) ** 2 + (xs - x) ** 2 < VILLAGE_REACH ** 2
            assert not solid[near].any(), f"{p['name']} has solid ground inside its walls"
            assert (level[near] == level[y, x]).all(), f"{p['name']} has a level edge inside its walls"
    walk = tiles_walkable(terrain, level, ramp)
    for p in places:
        x, y = p["tile"]
        assert walk[y, x], f"{p['name']} at {p['tile']} is not walkable"
    x, y = starts[0]["tile"]
    seen = reachable((y, x), walk)
    for p in places:
        if p["kind"] == "village":
            x, y = p["tile"]
            assert seen[y, x], f"{p['name']} can't be reached from {starts[0]['name']}"
    print("export OK")


if __name__ == "__main__":
    main()
