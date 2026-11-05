"""SpriteCook concept drafts for the Misborn: a man's loose soul in a dead warhorse, forced upright.

Run from the repo root: .venv/bin/python art/drafts/misborn/generate.py [variant ...]
Writes art/drafts/misborn/concepts/<variant>_<n>.png (south-facing, 128x128). The pixel engine
takes at most 100 words, style included.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import spritecook

OUT = Path("art/drafts/misborn/concepts")
BODY = (
    "dead grey warhorse corpse standing upright on hind legs like a man, knees bent wrong, hunched, "
    "long forelegs hanging like arms with dragging hooves, one lower, long drooping neck, head pushed forward"
)
GEAR = (
    ", dented steel face plate crooked over one eye, bridle with dragging reins, half a saddle slipped sideways, "
    "empty soldier's boot caught in a stirrup, broken spears in its flank"
)
STYLE = "grim dark fantasy, desaturated, top-down 3/4 RPG sprite facing viewer, dark outline, light from top-left"
VARIANTS = {
    "upright": BODY + GEAR,
    "hunched": BODY + ", almost falling forward" + GEAR,
    "gaunt": BODY + ", emaciated, ribs showing" + GEAR,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or VARIANTS:
        for path in spritecook.generate(OUT / name, 128, 128, VARIANTS[name], variations=2, style=STYLE):
            print(path)
