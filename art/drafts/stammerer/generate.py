"""SpriteCook concept drafts for the Stammerer: a dead king's reader whose loose soul still utters
the rune stones nailed into his own body, and stammers.

Run from the repo root: .venv/bin/python art/drafts/stammerer/generate.py [variant ...]
Writes art/drafts/stammerer/concepts/<variant>_<n>.png (GPT-Image-2, low quality, white background).
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import spritecook

OUT = Path("art/drafts/stammerer/concepts")
BODY = (
    "Pixel art game sprite, front view facing the viewer, full body. A horror creature: the walking corpse of an old "
    "scholar who read souls out of stones. Gaunt grey dead skin, tattered dark scholar's robes and a stained leather "
    "apron, a leather satchel of ledgers at his hip. Small rune stones are nailed into his bare chest and forearms with "
    "rusted iron nails, each stone glowing faint blue. His lower jaw is broken and hangs open, slack and crooked."
)
STYLE = " Grim dark fantasy, desaturated greys and browns, only the stones glow, dark outline, light from the top-left, plain white background."
VARIANTS = {
    "upright": BODY + " He stands stooped and still, arms hanging, staring." + STYLE,
    "casting": BODY + " He is hunched forward mid-incantation, both clawed hands raised, fingers twisted, the stones flaring, his broken mouth straining to speak." + STYLE,
}

if __name__ == "__main__":
    for name in sys.argv[1:] or VARIANTS:
        for path in spritecook.generate(OUT / name, 128, 128, VARIANTS[name], variations=2, model="gpt-image-2", quality="low", bg_mode="white"):
            print(path)
