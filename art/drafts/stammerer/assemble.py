"""Join the Stammerer's PixelLab segments into game animations and build his idle.

Run from the repo root: .venv/bin/python art/drafts/stammerer/assemble.py
Reads art/drafts/stammerer/segments/<segment>_<seed>/<n>.png (96x96, from pixellab_anims.py)
and writes art/drafts/stammerer/snapped/<anim>/<n>.png plus strip.png. Frame 0 of each segment is its
start key pose, so later segments skip it. The idle is a breathing loop made from his base pose.
The game sheets go to art/enemies/stammerer_hd/ (and godot/art/), his body prop (the last death frame)
to art/props/stammerer_body.png. Frames the
art review found broken are left out: the walk's standing base (loops from the first step), choke frames
where the stones vanish or the body changes, and the death frame where the corpse flips.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tools")
from pixel import breathing, export_game, grounded, segment_frames

D = Path("art/drafts/stammerer")
SIZE, FEET = 96, 94
ANIMS = {
    "base": [("walk_2", [0])],
    "walk_south": [("walk_2", range(1, 8))],
    # The stammer loops while he mouths the name; shown twice here, then he finishes the word.
    "cast_south": [("cast_in_2", range(7)), ("stammer_1", range(1, 5)), ("stammer_1", range(1, 5)), ("cast_out_2", range(1, 7))],
    "choke_south": [("choke_1", [0, 1, 2, 4]), ("choke_out_1", [1, 2, 3, 5, 6])],
    "death_south": [("death_1", [0, 1, 2, 3, 4, 5, 6, 8])],
}


def save(name, imgs):
    folder = D / "snapped" / name
    folder.mkdir(parents=True, exist_ok=True)
    strip = Image.new("RGBA", (SIZE * len(imgs), SIZE))
    for i, f in enumerate(imgs):
        f.save(folder / f"{i}.png")
        strip.alpha_composite(f, (i * SIZE, 0))
    strip.save(folder / "strip.png")
    return strip


if __name__ == "__main__":
    done = {a: segment_frames(D / "segments", parts) for a, parts in ANIMS.items()}
    base = done.pop("base")[0]
    for a in ("walk_south", "death_south"):
        done[a] = grounded(done[a], FEET)
    done["idle_south"] = breathing(base, hips=0.5, neck=0.22)
    strips = {a: save(a, imgs) for a, imgs in done.items()}
    sheets = {f"enemies/stammerer_hd/stammerer_hd_{a.split('_')[0]}.png": s for a, s in strips.items()}
    export_game({**sheets, "props/stammerer_body.png": done["death_south"][-1]})
