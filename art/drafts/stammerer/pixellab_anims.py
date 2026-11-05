"""The Stammerer's animations as PixelLab segments between his key poses (96x96, feet at y=93).

Run from the repo root: .venv/bin/python art/drafts/stammerer/pixellab_anims.py [seed] [segment ...]
Writes art/drafts/stammerer/segments/<name>_<seed>/<n>.png; assemble.py joins them into animations.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from pixellab import animate_segments

K = Path("art/drafts/stammerer/keys")
BASE, CAST, CHOKE, DEAD = K / "base.png", K / "cast.png", K / "choke.png", K / "dead.png"
SAME = " Same emaciated man, same robes, apron, satchel and nailed rune stones; no new parts, no motion lines, no glowing aura or white light."
SEGMENTS = {
    "walk": (BASE, None, 8, "Walking toward the viewer in a slow shambling stride, each leg clearly stepping forward in turn, thin body swaying." + SAME),
    "cast_in": (BASE, CAST, 6, "He hunches forward and raises both clawed hands, the rune stones brightening." + SAME),
    "stammer": (CAST, CAST, 4, "His broken jaw stammers and twitches, clawed hands trembling, the stones flickering." + SAME),
    "cast_out": (CAST, BASE, 6, "He lowers his hands and straightens back to standing, the stones dimming." + SAME),
    "choke": (CAST, CHOKE, 4, "The word chokes: he jerks back, head thrown back, a hand clutching his throat." + SAME),
    "choke_out": (CHOKE, BASE, 6, "He recovers from choking, lowering his hands and straightening up." + SAME),
    "death": (BASE, DEAD, 8, "He crumples and collapses to the ground, the rune stones going dark." + SAME),
}

if __name__ == "__main__":
    animate_segments(Path("art/drafts/stammerer/segments"), SEGMENTS, int(sys.argv[1]) if len(sys.argv) > 1 else 1, sys.argv[2:])
