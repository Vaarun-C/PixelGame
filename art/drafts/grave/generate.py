"""PixelLab drafts for the grave marker prop.

Run from the repo root: .venv/bin/python art/drafts/grave/generate.py
Costs PixelLab credits.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/grave")
STYLE = "dark fantasy, grim, desaturated, worn and chipped, pixel art, top-down three-quarter view, light from top-left"

for seed in (3, 11, 27):
    pixellab.generate(D / f"grave_s{seed}.png", 64, 64,
                      f"a single weathered grey stone headstone with a rounded top, standing upright, a deep X carved into its face, cracked edges, {STYLE}",
                      seed=seed)
    print("done", seed)
