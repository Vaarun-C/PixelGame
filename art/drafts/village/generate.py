"""PixelLab concepts for the village buildings: three takes each of a shed, a cottage, a barn and a
longhouse, at 2x (64 px per 32 px tile), so a cottage is 4 tiles wide.

Run from the repo root: .venv/bin/python art/drafts/village/generate.py
Costs PixelLab credits (one generation per image).
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/village/concepts")
STYLE = ("dark fantasy medieval, grim, poor and worn, desaturated browns and greys, pixel art, "
         "top-down three-quarter view showing the roof and the front wall, light from top-left, single building, no ground")
BUILDINGS = {
    "shed": (192, 192, "a small lean-to shed of rough split planks against a slanted plank roof, a stack of firewood beside it, sagging and patched"),
    "cottage": (256, 256, "a one-room peasant cottage with wattle-and-daub walls on a timber frame, a steep sagging thatched roof, a low door and one shuttered window, a smoke hole"),
    "barn": (320, 256, "a crooked timber barn with wide double doors, dark weathered boards, a heavy thatched roof with moss, hay spilling from a loft door"),
    "longhouse": (384, 256, "a long timber longhouse hall, low walls of dark logs, a huge steep thatched roof reaching almost to the ground, carved posts by the door, smoke rising from the roof"),
}
SEEDS = (5, 17, 29)
# Second round for the cottage: the first came out at a corner angle and too bright.
FRONT = ("seen straight from the front like the other props, the front wall facing the viewer squarely, "
         "the roof ridge running left to right, not at a corner angle, dark weathered timber and grey-brown thatch")
REDO = {"cottage_front": (256, 256, f"{BUILDINGS['cottage'][2]}, {FRONT}"),
        # The 192 sheds read too small beside a villager: same sheds, a size up.
        "shed_big": (256, 256, f"{BUILDINGS['shed'][2]}, tall enough for a man to stand inside")}

for name, (w, h, desc) in {**BUILDINGS, **REDO}.items():
    for seed in SEEDS:
        out = D / f"{name}_s{seed}.png"
        if out.exists():
            continue
        pixellab.generate(out, w, h, f"{desc}, {STYLE}", seed=seed, view="high top-down",
                          outline="selective outline", shading="medium shading", detail="medium detail")
        print("done", out, flush=True)
