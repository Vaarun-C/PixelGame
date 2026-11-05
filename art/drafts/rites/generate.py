"""PixelLab concepts for two of the last-rite props (lore/Mechanics/the-six-rites.md): the chapel ledger
on its lectern (Ennick / Hush) and Wend's wayside shrine with the niche at its foot (Wend / Mortmain).

Run from the repo root: .venv/bin/python art/drafts/rites/generate.py
Costs PixelLab credits (one generation per image).
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/rites/concepts")
STYLE = ("dark fantasy medieval, grim, old and worn, desaturated greys and browns, no glow, pixel art, "
         "top-down three-quarter view, seen from the front, light from top-left, single object, no ground")
PROPS = {
    "ledger": (64, 64, "a heavy worn wooden lectern, a single thick post on a wide foot, holding a huge open book "
                       "of names with yellowed pages and iron-bound corners, a knotted cord hanging from the book"),
    "shrine": (128, 128, "a weathered grey stone wayside shrine by a road, a tall narrow stele with a small peaked "
                         "roof stone, a faint worn carving of a walking figure with a staff on its face, a small dark "
                         "empty arched niche at its foot, cracked and mossy, standing upright"),
}
SEEDS = (5, 17, 29, 41)

for name, (w, h, desc) in PROPS.items():
    for seed in SEEDS:
        out = D / f"{name}_s{seed}.png"
        if out.exists():
            continue
        pixellab.generate(out, w, h, f"{desc}, {STYLE}", seed=seed, view="high top-down",
                          outline="selective outline", shading="medium shading", detail="medium detail")
        print("done", out, flush=True)
