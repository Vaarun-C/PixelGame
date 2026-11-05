"""PixelLab drafts for the fixed world's new ground and its cliff and ramp edges.
Usage: .venv/bin/python art/drafts/terrain/generate.py grounds [name ...]
       .venv/bin/python art/drafts/terrain/generate.py cliffs <biome> <reference.png>

grounds: one tiles-pro call per biome, four 128 px top-down textures (one per ground row), locked to
the master palette and matched to the battlefield ground's style. Saved to raw/<biome>/.
cliffs: pro corner tilesets (64 px) for an edge between two levels of one biome's ground, both
terrains matched to a reference tile of that ground: a tall cliff (walls a full tile high, 25 tiles)
and a ramp (a low bank sloping gently, 16 tiles). Saved to raw/cliff/<biome>/ and raw/ramp/<biome>/.
assemble.py turns these into the game's sheets.
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import pixellab  # noqa: E402
from pixel import COLORS  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
PALETTE = {"colors": ["#%02x%02x%02x" % c for c in COLORS.values()], "name": "Master"}
STYLE = "grim, desaturated dark fantasy ground, worn and dead, seen from straight above, seamless"
GROUNDS = {
    "fallow": ["dry dead grass on brown earth", "thistles and dark weeds on a fallow field", "old plough furrows in brown soil", "bare packed earth with small stones"],
    "woods": ["dead leaf litter and twigs on dark soil", "dark green moss on damp ground", "twisted dead roots in dark earth", "dense black undergrowth and brambles"],
    "mountain": ["grey scree and loose stones", "dirty old snow over rock", "cracked grey bedrock", "jagged dark crags and boulders"],
    "cinder": ["scorched black rock", "grey ash ground", "cracked black rock with a few glowing embers", "jagged burnt rock"],
    "water": ["deep dark still water", "dark flowing river water with ripples", "shallow murky water over mud", "a shallow stream over pebbles"],
    "road": ["a worn dirt road with wheel ruts", "old grey cobblestones", "a causeway of packed grey rubble", "old weathered wooden bridge planks"],
    # Redo of fallow's furrows and bare earth: the first run gave wood grain and flat grey.
    "fallow2": ["rows of dark ploughed soil, overgrown, seen from above", "bare brown packed earth with pebbles and a few dry stalks"],
}


def encoded(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def style_tile():
    """A 128 px patch of the battlefield's base ground, so new grounds match the existing sheets."""
    sheet = Image.open(ROOT / "art/tiles/battlefield/battlefield_ground_hd.png").convert("RGBA")
    tile = sheet.crop((15 * 64, 0, 16 * 64, 64))
    patch = Image.new("RGBA", (128, 128))
    for x in (0, 64):
        for y in (0, 64):
            patch.paste(tile, (x, y))
    return {"base64": encoded(patch), "width": 128, "height": 128}


def grounds(biomes):
    style = style_tile()
    for biome in biomes:
        description = " ".join(f"{i + 1}). {d}" for i, d in enumerate(GROUNDS[biome])) + f". {STYLE}"
        pixellab.tiles(HERE / "raw" / biome, description, 128, tile_view="top-down", target_palette=PALETTE,
                       style_images=[style], style_options={"detail": True, "shading": True, "outline": True, "color_palette": False})
        print(biome)


CLIFF_WALLS = {
    "battlefield": "a bank of grey earth and rubble", "swamp": "a crumbling bank of black mud and roots",
    "ruins": "an old wall of grey dressed stone", "ashen": "a scorched rock face", "frozen": "an icy grey rock face",
    "fallow": "a bank of brown earth and rock", "woods": "a bank of dark earth and tangled roots",
    "mountain": "a sheer grey rock face", "cinder": "a black volcanic rock face",
}


def cliffs(biome, reference):
    """reference: a 64 px tile of the biome's base ground; both levels are painted to match it."""
    tile = {"type": "base64", "base64": encoded(Image.open(reference).convert("RGBA").crop((0, 0, 64, 64)))}
    common = {"mode": "pro", "tile_size": {"width": 64, "height": 64}, "view": "high top-down", "target_palette": PALETTE,
              "lower_reference_image": tile, "upper_reference_image": tile, "seed": 7}
    ground = f"{biome} ground like the reference tile"
    wall = f"{CLIFF_WALLS[biome]}, dark and weathered, no pale rim along the top edge"
    pixellab.tileset(HERE / "raw" / "cliff" / biome, ground, f"the same {ground}, raised", transition_description=wall,
                     transition_size=1.0, **common)
    pixellab.tileset(HERE / "raw" / "ramp" / biome, ground, f"the same {ground}, raised", transition_description="an earthen slope",
                     transition_size=0.25, step_slope=2.0, **common)
    print(biome)


if __name__ == "__main__":
    what, *args = sys.argv[1:]
    grounds(args or list(GROUNDS)) if what == "grounds" else cliffs(*args)
