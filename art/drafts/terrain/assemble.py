"""Builds the game's ground and cliff sheets from the PixelLab drafts (generate.py).
Usage: .venv/bin/python art/drafts/terrain/assemble.py

Grounds: each chosen 128 px texture is snapped to the world palette, held to the ground value budget
(ART_RULES §3: void-2 … ash-2), and turned into a sheet row by tools/ground_tiles.py; rows repeat
over the four animation frames the tileset expects. Written to art/tiles/<biome>/<biome>_ground_hd.png.

Cliffs: per biome one sheet, art/tiles/cliffs/<biome>_cliffs_hd.png. Row 0 holds the 25 tall-wall
tiles in tall_patterns.json order; row 1 the 16 ramp tiles by our corner mask (top-left 1, top-right 2,
bottom-left 4, bottom-right 8 = upper). A tall tile is picked by its 4 x 4 pattern of corner states
round it (0 lower, 1 upper, 2 wall top, 255 any): the same four corners can need a different tile
depending on what lies north, so the game takes the most specific pattern that matches.
Every sheet is copied to the same path under godot/art/.
"""
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from ground_tiles import T, grid, ground_row  # noqa: E402
from pixel import COLORS, sheet  # noqa: E402
from snap_palette import WORLD, distance  # noqa: E402

RAW = HERE / "raw"
FRAMES = 4
luma = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
BUDGET = (luma(COLORS["void-2"]), luma(COLORS["ash-2"]))
GROUND_COLORS = [c for c in WORLD if BUDGET[0] <= luma(c) <= BUDGET[1]]
# biome: four (draft folder, tile, bank) for ground rows 0-3, in the order biomes.gd describes them.
# Flat single-colour tiles PixelLab returned (fallow2 0, 1, 3, 4; water 2, 3, 4) are skipped; the
# furrows never came out, so fallow's third row is a second dry-grass tile.
GROUND_ROWS = {
    "fallow": [("fallow", "tile_0", 0), ("fallow", "tile_5", 1), ("fallow", "tile_4", 0), ("fallow2", "tile_5", -1)],
    "woods": [("woods", "tile_0", 0), ("woods", "tile_4", 1), ("woods", "tile_2", 0), ("woods", "tile_3", 1)],
    "mountain": [("mountain", "tile_0", 0), ("mountain", "tile_2", 1), ("mountain", "tile_4", 0), ("mountain", "tile_5", 1)],
    "cinder": [("cinder", "tile_3", 0), ("cinder", "tile_1", 0), ("cinder", "tile_2", -1), ("cinder", "tile_0", 1)],
    "water": [("water", "tile_0", -1), ("water", "tile_1", -1), ("water", "tile_5", -1), ("water", "tile_1", -1)],
    "road": [("road", "tile_1", 0), ("road", "tile_2", 1), ("road", "tile_3", 1), ("road", "tile_4", 1)],
}
CLIFF_BIOMES = ["battlefield", "swamp", "ruins", "ashen", "frozen", "fallow", "woods", "mountain", "cinder"]
TALL_PATTERNS = []


def held(img):
    """Every pixel on the nearest world colour inside the ground value budget; alpha kept hard."""
    img = img.convert("RGBA")
    px = img.load()
    cache = {}
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a < 128:
                px[x, y] = (0, 0, 0, 0)
                continue
            if (r, g, b) not in cache:
                cache[(r, g, b)] = min(GROUND_COLORS, key=lambda c: distance((r, g, b), c))
            px[x, y] = cache[(r, g, b)] + (255,)
    return img


def ground_sheet(biome):
    rows = []
    for folder, tile, bank in GROUND_ROWS[biome]:
        patch = grid(held(Image.open(RAW / folder / f"{tile}.png")))
        rows.append(ground_row(patch, bank, seed=len(rows)) * FRAMES)
    return sheet(rows, T, T)


def pattern(tile):
    return tuple(v for row in ("row_0", "row_1", "row_2", "row_3") for v in tile["pattern_4x4"][row])


def tiles_by(folder, key):
    data = json.loads((folder / "tileset.json").read_text())
    return {key(t): held(Image.open(next(folder.glob(f"{i:02d}_*.png")))) for i, t in enumerate(data["tileset"]["tiles"])}


def mask(tile):
    return sum(1 << i for i, k in enumerate(("NW", "NE", "SW", "SE")) if tile["corners"][k] == "upper")


def cliff_sheet(biome):
    tall = tiles_by(RAW / "cliff" / biome, pattern)
    assert sorted(tall) == TALL_PATTERNS, f"{biome} tall set has other patterns"
    ramp = tiles_by(RAW / "ramp" / biome, mask)
    assert sorted(ramp) == list(range(16)), f"{biome} ramp set has masks {sorted(ramp)}"
    return sheet([[tall[p] for p in TALL_PATTERNS], [ramp[m] for m in range(16)]], T, T)


def write(img, rel):
    for base in (ROOT / "art", ROOT / "godot/art"):
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        img.save(base / rel)
    print(rel)


def main():
    global TALL_PATTERNS
    TALL_PATTERNS = sorted(pattern(t) for t in json.loads((RAW / "cliff/fallow/tileset.json").read_text())["tileset"]["tiles"])
    assert len(set(TALL_PATTERNS)) == 25, "tall patterns are not unique"
    (ROOT / "godot/art/tiles/cliffs/tall_patterns.json").write_text(json.dumps([list(p) for p in TALL_PATTERNS]))
    for biome in GROUND_ROWS:
        write(ground_sheet(biome), f"tiles/{biome}/{biome}_ground_hd.png")
    for biome in CLIFF_BIOMES:
        write(cliff_sheet(biome), f"tiles/cliffs/{biome}_cliffs_hd.png")


if __name__ == "__main__":
    main()
