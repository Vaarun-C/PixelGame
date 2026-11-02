"""PixelLab drafts for the prologue's cutscenes (kneel, stone close-up, hilt close-up).

Run from the repo root: .venv/bin/python art/drafts/prologue/generate.py
Costs PixelLab credits; the chosen drafts are named in assemble.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/prologue")
STYLE = "dark fantasy, grim, desaturated grey steel, heavy worn armor, pixel art, light from top-left"

for seed in (5, 19):
    pixellab.animate("art/drafts/wanderer/idle_east/1.png", D / f"kneel/s{seed}",
                     "kneels down on one knee and reaches forward and down with his left hand to take something from the ground",
                     8, seed=seed)
    pixellab.generate(D / f"stone_closeup_s{seed}.png", 128, 128,
                      f"close-up of a steel gauntlet held palm up, holding a small smooth grey stone wrapped in thin iron wire, {STYLE}",
                      seed=seed)
    pixellab.generate(D / f"hilt_closeup_s{seed}.png", 192, 96,
                      f"close-up of a huge worn greatsword lying horizontal, the base of the blade and the crossguard, three small empty round sockets set in a row into the blade, {STYLE}",
                      seed=seed)
    print("done", seed)

# The gauntlet that pulls the wire tail in the threading close-up (round 39: stones are lashed).
for seed in (5, 19):
    pixellab.generate(D / f"pull_hand_s{seed}.png", 64, 64,
                      f"close-up of a steel plate gauntlet seen from the side, fingers pinched tight around a thin iron wire, pulling it, {STYLE}",
                      seed=seed)

# s19 held the wire slack; edit it taut. Snap the chosen edit: tools/snap_palette.py pull_hand_taut_s19.png pull_hand.png
for seed in (5, 19):
    pixellab.edit(D / "pull_hand_s19.png", D / f"pull_hand_taut_s{seed}.png",
                  "the armoured fingers pinch the thin iron wire tight and pull it taut sideways to the right "
                  "in a straight tense line, all fingers covered in steel plate, no bare skin", seed=seed)
