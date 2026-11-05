"""PixelLab walk cycles for the guard (south, west, north; east is west mirrored by assemble.py).
Frame 0 of each result is the input rotation; assemble.py reads frames 1-6.

Run from the repo root: .venv/bin/python art/drafts/villagers/guard/walk.py
Costs PixelLab credits (one generation per facing).
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/villagers/guard")
for facing in ("south", "west", "north"):
    out = D / f"walk_{facing}"
    if (out / "1.png").exists():
        continue
    result = pixellab.animate(D / "rotations" / f"{facing}.png", out,
                              "walking slowly with heavy steps, spear held upright in one hand, each foot planted on the ground", 6)
    print(facing, result["status"], len(result["last_response"].get("images", [])), "frames", flush=True)
