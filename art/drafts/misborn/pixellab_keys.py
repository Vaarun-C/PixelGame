"""Key poses for the Misborn's bite and flail, edited from his rest frame (the strike from the chosen wind-up) with PixelLab.

Run from the repo root: .venv/bin/python art/drafts/misborn/pixellab_keys.py <key> [seeds...]
Writes art/drafts/misborn/keys/<key>_<seed>.png (160x160, same canvas as the attack frames).
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, "tools")
from pixellab import edit

D = Path("art/drafts/misborn")
REST = D / "keys/rest.png"
KEEP = ("Keep the same creature exactly: same body, same hind legs and hooves, same harness, saddle and stirrup "
        "with the rider's boot hanging at its flank, same colors. Do not add any new body parts, straps or reins.")
LIMB = "The foreleg is a thin horse leg, exactly as thin as the other foreleg, ending in the same small hoof, attached at the shoulder. "
KEYS = {
    "bite": "The horse head lunges forward and down toward the viewer, neck stretched out low, "
            "jaws gaping wide open showing teeth. " + KEEP,
    "windup": "The creature raises its right foreleg high above its head, ready to smash down. " +
              LIMB + KEEP,
    "strike": "The raised foreleg has smashed down hard, swung down and forward toward the viewer: the hoof is now "
              "low in front of the chest, reaching toward the viewer, shoulders hunched and body leaning forward "
              "into the blow. " + LIMB + KEEP,
    "dead": "The creature has collapsed dead on the ground, a heavy horse corpse lying on its side facing the viewer, "
            "legs folded under it, head on the ground. Same harness, saddle and the boot in the stirrup, same colors. "
            "Do not add any new body parts.",
}
SOURCE = {"strike": D / "keys/windup_8.png"}

if __name__ == "__main__":
    key, seeds = sys.argv[1], [int(s) for s in sys.argv[2:]] or [1, 2, 3, 4]
    (D / "keys").mkdir(exist_ok=True)
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(lambda s: edit(SOURCE.get(key, REST), D / f"keys/{key}_{s}.png", KEYS[key], seed=s), seeds))
