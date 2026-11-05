"""The Stammerer's base and key poses, edited with PixelLab at game size (96x96, feet at y=93).

Run from the repo root: .venv/bin/python art/drafts/stammerer/pixellab_keys.py <key> [seeds...]
Writes art/drafts/stammerer/keys/<key>_<seed>.png, each edited from keys/base.png. That base is seed 4 of
the "base" edit, made from his old SpriteCook walk frame (no longer kept); the chosen cast, choke and dead
keys are copied to keys/<key>.png.
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, "tools")
from pixellab import edit

D = Path("art/drafts/stammerer")
KEEP = ("Keep the rune stones nailed into his chest and forearms glowing faint blue, his broken hanging jaw, "
        "the stained leather apron, the satchel at his hip and the same colors.")
KEYS = {
    "base": "Make him far more emaciated, a starved corpse: skeletal face with sunken cheeks and eye sockets, "
            "ribs and collarbones showing through tight grey skin, stick-thin arms and legs with knobbly joints, "
            "a sunken chest, the robes hanging loose off bony shoulders. Same height and standing pose. " + KEEP,
    "cast": "He hunches forward mid-incantation, both clawed hands raised in front of his chest with fingers twisted, "
            "the rune stones flaring brighter blue, his broken jaw straining open to speak. " + KEEP,
    "choke": "His utterance chokes: he jerks back, head thrown back, one clawed hand clutching his throat and the "
             "other flailing, jaw locked open, the rune stones dimmed. " + KEEP,
    "dead": "He has collapsed dead on the ground, a crumpled heap lying on his side facing the viewer, the robes "
            "spread, the rune stones dark grey and unlit. Same character, same colors otherwise.",
}

if __name__ == "__main__":
    key, seeds = sys.argv[1], [int(s) for s in sys.argv[2:]] or [1, 2, 3, 4]
    (D / "keys").mkdir(exist_ok=True)
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(lambda s: edit(D / "keys/base.png", D / f"keys/{key}_{s}.png", KEYS[key], seed=s), seeds))
