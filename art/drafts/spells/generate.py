"""PixelLab drafts for the Wanderer's spell casts (lore: Uttering).

poses: his south-facing frame edited into one held pose per spell (6 generations each).
anims: in-between frames from that frame to the pose, ending on the pose as a keyframe (3 each).

Run from the repo root: .venv/bin/python art/drafts/spells/generate.py poses|anims [spell ...]
The chosen drafts are named in build.py.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, "tools")
import pixellab

D = Path("art/drafts/spells")
BASE = "art/drafts/wanderer/attacks/base/south.png"
HEAVY = "godot/art/characters/wanderer_hd/wanderer_hd_heavy.png"
KEEP = ", same armor, red cape and tabard"
SEED = 7
POSES = {
    "rend": "the knight raises his huge greatsword straight up high above his head with both hands, arms fully extended, head level and facing straight ahead at the enemy, not looking up",
    "sting": "the knight holds his huge greatsword upright in front of his face with both hands, blade vertical, elbows tucked in, braced and tense",
    "ward": "the knight plants his huge greatsword point-down in the ground in front of him and rests both hands on the pommel, head bowed, standing firm",
    "still": "the knight thrusts his huge greatsword straight forward toward the viewer at arm's length in one hand, the other arm held back, perfectly still",
    "sink": "the knight drops to one knee facing the viewer and presses his left palm flat on the ground, his right hand holding the huge greatsword planted point-down beside him",
    "hunger": "the knight holds his huge greatsword low at his right side and reaches his left arm forward toward the viewer, gauntlet fingers clawed open, pulling",
    "flee": "the knight crouches low with knees bent, his huge greatsword swept back behind him, cape flaring out, coiled to spring",
}
ANIMS = {
    "rend": "slowly lifts the greatsword off his shoulder and raises it straight up above his head with both hands, his head stays level",
    "break": "raises the greatsword high and slams it point-down into the ground with great force, bracing his legs",
    "sting": "brings the greatsword off his shoulder and grips it upright in front of his face with both hands, bracing",
    "ward": "lifts the greatsword off his shoulder and plants it point-down in the ground in front of him, resting both hands on the pommel, head bowed",
    "still": "swings the greatsword off his shoulder and thrusts it straight out at arm's length, then holds perfectly still",
    "sink": "drops down onto one knee, plants the greatsword beside him and presses his left palm flat on the ground",
    "hunger": "lowers the greatsword to his side and reaches his left hand forward, fingers clawing",
    "flee": "crouches low and sweeps the greatsword back behind him, cape flaring",
}


def key_pose(spell):
    """The pose the animation ends on: the edit, or for Break the heavy attack's impact frame on a
    canvas like the base's, feet on the same row."""
    if spell != "break":
        return D / f"edit_{spell}_s{SEED}.png"
    impact = Image.open(HEAVY).convert("RGBA").crop((5 * 128, 0, 6 * 128, 144))
    base = Image.open(BASE).convert("RGBA")
    canvas = Image.new("RGBA", base.size)
    canvas.alpha_composite(impact, ((base.width - 128) // 2, base.getbbox()[3] - impact.getbbox()[3]))
    path = D / "key_break.png"
    canvas.save(path)
    return path


if __name__ == "__main__":
    step, *spells = sys.argv[1:]
    for spell in spells or (POSES if step == "poses" else ANIMS):
        if step == "poses":
            pixellab.edit(BASE, D / f"edit_{spell}_s{SEED}.png", POSES[spell] + KEEP, seed=SEED)
        else:
            pixellab.animate(BASE, D / f"anim_{spell}", ANIMS[spell], 6, seed=SEED, last=key_pose(spell))
            print("animated", spell)
