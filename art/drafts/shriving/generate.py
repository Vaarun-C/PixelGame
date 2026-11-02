"""PixelLab drafts for the shriving pair: a dying soldier on his back gripping a grey stone, and the
chaplain cut down from behind while kneeling at his side, fallen forward across him (lore/Locations/battlefield.md).

Run from the repo root: .venv/bin/python art/drafts/shriving/generate.py
Costs PixelLab credits.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/shriving")
STYLE = "dark fantasy, grim, desaturated, pixel art, top-down three-quarter view, light from top-left"

for seed in (3, 11, 27):
    pixellab.generate(D / f"pair_s{seed}.png", 96, 96,
                      "two dead bodies on the ground: a soldier in worn mail lying on his back with his hands closed on his chest around a small grey stone, "
                      f"and a monk in a dark hooded robe fallen face down across him, a sword cut in his back, blood pooled under them, {STYLE}",
                      seed=seed)
    print("done", seed)
