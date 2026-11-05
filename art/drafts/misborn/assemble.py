"""Snap the Misborn's animations to game size and build its idle.

Run from the repo root: .venv/bin/python art/drafts/misborn/assemble.py
Reads art/drafts/misborn/<anim>/<n>.png (256x256 frames). Walk and idle go on a 128x128 canvas,
feet at y=125; the attacks on 160x160, feet at y=157, so the raised forelegs have room. One scale
for everything, set by the walk. The idle is a breathing loop made from the first walk frame.
Bite, flail and death are joined from PixelLab segments (pixellab_anims.py), already 160x160 at game
scale. The game sheets go to art/enemies/misborn_hd/ (and godot/art/), its body prop (the last death
frame) to art/props/misborn_body.png.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tools")
from pixel import COLORS, breathing, export_game, game_frames, grounded, segment_frames

D = Path("art/drafts/misborn")
HEIGHT = 118
CANVAS = {"walk_south": ((128, 128), 125), "hammer_south": ((160, 160), 157)}
# (segment folder, frames used); frame 0 of each segment is its start key pose. The flail impact
# takes the only smear-free in-betweens, one each from seeds 5 and 4.
SEGMENTS = {
    "bite_south": [("bite_in_1", range(7)), ("bite_out_2", range(1, 7))],
    "flail_south": [("flail_up_6", range(5)), ("flail_hit_5", [1]), ("flail_hit_4", [3]), ("flail_out_6", range(7))],
    "death_south": [("death_1", range(9))],
}


def frames(anim):
    return [Image.open(p).convert("RGBA") for p in sorted((D / anim).glob("[0-9]*.png"), key=lambda p: int(p.stem))]


# PixelLab paints the open-mouth teeth gold; the Misborn has no gold, so they become bone.
TEETH = {COLORS[g]: COLORS[b] for g, b in [("gilt-0", "bone-0"), ("gilt-1", "bone-0"), ("gilt-2", "bone-1"), ("gilt-3", "bone-1")]}


def save(name, imgs):
    folder = D / "snapped" / name
    folder.mkdir(parents=True, exist_ok=True)
    w, h = imgs[0].size
    strip = Image.new("RGBA", (w * len(imgs), h))
    for i, f in enumerate(imgs):
        f.save(folder / f"{i}.png")
        strip.alpha_composite(f, (i * w, 0))
    strip.save(folder / "strip.png")
    return strip


if __name__ == "__main__":
    raw = {a: frames(a) for a in CANVAS}
    walk = [f.getbbox() for f in raw["walk_south"]]
    scale = HEIGHT / (max(b[3] for b in walk) - min(b[1] for b in walk))
    bottom = max(f.getbbox()[3] for a in CANVAS for f in raw[a])
    done = {a: game_frames(raw[a], scale, bottom, size, feet) for a, (size, feet) in CANVAS.items()}
    done |= {a: segment_frames(D / "segments", parts, TEETH) for a, parts in SEGMENTS.items()}
    done["death_south"] = grounded(done["death_south"], 157)
    done["idle_south"] = breathing(done["walk_south"][0], hips=0.52, neck=0.30)
    strips = {a: save(a, imgs) for a, imgs in done.items()}
    sheets = {f"enemies/misborn_hd/misborn_hd_{a.split('_')[0]}.png": s for a, s in strips.items()}
    export_game({**sheets, "props/misborn_body.png": done["death_south"][-1]})
    print("scale", round(scale, 3))
