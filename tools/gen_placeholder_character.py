"""Generates placeholder character sprite sheets (the Wanderer and villagers) until hand-drawn art exists.
Usage: .venv/bin/python tools/gen_placeholder_character.py [preview_dir]"""
import sys
from pathlib import Path
from pixel import Sprite, save, sheet

W, H = 32, 48
DIRS = ["down", "left", "right", "up"]
OUT = Path(__file__).resolve().parent.parent / "art/characters"
NO_RUNE = {"rune-pale-mid": "flesh-1", "rune-pale-core": "flesh-1", "rune-pale-dark": "flesh-0"}
# Villagers reuse the Wanderer's body with swapped ramps.
LOOKS = {
    "wanderer": {"armed": True},
    "peasant": {"armed": False, "ramps": {"ash": "leather", "steel": "leather", "blood": "rot"}, "colors": NO_RUNE},
    "monk": {"armed": False, "ramps": {"ash": "bone", "steel": "leather", "blood": "leather"}, "colors": NO_RUNE},
    "guard": {"armed": True, "ramps": {"ash": "blood", "blood": "steel"}, "colors": NO_RUNE},
    "barterer": {"armed": False, "ramps": {"ash": "bronze", "steel": "leather", "blood": "gilt"}, "colors": NO_RUNE},
    # The Wanderer with his blade drawn (the game draws the blade in his hand).
    "wanderer_bare": {"armed": False},
    # A husk of a dead soldier: hunched, rotted rags, dead skin, pale eyes.
    "hollow": {
        "armed": False,
        "hunch": 2,
        "ramps": {"ash": "rot", "blood": "leather", "steel": "leather"},
        "colors": {"ash-3": "bone-1", "flesh-0": "rot-2", "flesh-1": "rot-3", "rune-pale-mid": "rot-3", "rune-pale-core": "rot-3", "rune-pale-dark": "rot-2"},
    },
}

# Walk cycle: per-frame leg lift for front/back views, foot offset + lift for side views, body bob.
WALK_LIFT_A = [2, 1, 0, 0, 0, 1]
WALK_LIFT_B = [0, 0, 1, 2, 1, 0]
WALK_STRIDE = [(-3, 0), (-1, 0), (1, 0), (3, 0), (1, 1), (-1, 2)]
WALK_BOB = [0, 0, 1, 0, 0, 1]
IDLE_BOB = [0, 0, 1, 1]


def sword(s, x, top):
    """Greatblade carried on the back: pommel, grip, guard at `top`, blade below."""
    s.rect(x, top - 10, x + 3, top - 9, "steel-2")
    s.rect(x + 1, top - 8, x + 2, top - 2, "leather-1")
    for y in range(top - 7, top - 2, 2):
        s.rect(x + 1, y, x + 2, y, "leather-2")
    s.rect(x - 2, top - 1, x + 5, top, "steel-2")
    s.rect(x, top + 1, x + 3, top + 24, "steel-1")
    s.rect(x, top + 1, x, top + 24, "steel-2")
    s.rect(x + 1, top + 25, x + 2, top + 26, "steel-1")


def hood(s, x0, x1, dy):
    s.rect(x0 + 2, 7 + dy, x1 - 2, 7 + dy, "ash-1")
    s.rect(x0 + 1, 8 + dy, x1 - 1, 8 + dy, "ash-1")
    s.rect(x0, 9 + dy, x1, 16 + dy, "ash-1")


def folds(s, xs, y0, y1, dy):
    for x in xs:
        s.rect(x, y0 + dy, x, y1 + dy, "ash-0")


def legs_front(s, lift_a, lift_b, dark_a=False):
    for x0, lift, dark in ((11, lift_a, dark_a), (17, lift_b, False)):
        bottom = 46 - lift
        s.rect(x0, 36, x0 + 3, bottom, "void-2" if dark else "void-3")
        s.rect(x0, bottom - 4, x0 + 3, bottom, "leather-0" if dark else "leather-1")
        s.rect(x0, bottom - 4, x0 + 3, bottom - 4, "leather-2")


def leg_side(s, off, lift, far):
    bottom = 46 - lift
    for y in range(36, bottom + 1):
        cx = 14 + round(off * (y - 36) / 10)
        boot = y >= bottom - 4
        color = ("leather-0" if far else "leather-1") if boot else ("void-2" if far else "void-3")
        s.rect(cx, y, cx + 2, y, color)
    s.dot(14 + off - 1, bottom, "leather-0" if far else "leather-1")


def upper_front(s, dy, glow, armed):
    if armed:
        sword(s, 4, 14 + dy)
    hood(s, 11, 20, dy)
    s.rect(13, 11 + dy, 18, 16 + dy, "void-0")
    s.rect(14, 10 + dy, 17, 10 + dy, "void-0")
    s.dot(14, 13 + dy, "ash-3")
    s.dot(17, 13 + dy, "ash-3")
    s.rect(15, 16 + dy, 16, 16 + dy, "flesh-0")
    s.rect(12, 17 + dy, 19, 18 + dy, "blood-2")
    s.rect(20, 18 + dy, 24, 18 + dy, "ash-1")
    s.rect(20, 19 + dy, 25, 21 + dy, "ash-1")
    s.rect(10, 19 + dy, 21, 30 + dy, "leather-1")
    s.rect(11, 20 + dy, 20, 26 + dy, "steel-1")
    s.rect(11, 26 + dy, 20, 26 + dy, "steel-0")
    for i in range(9):
        s.dot(19 - i, 19 + i + dy, "leather-2")
    s.rect(7, 18 + dy, 10, 18 + dy, "steel-2")
    s.rect(6, 19 + dy, 11, 21 + dy, "steel-2")
    s.dot(8, 20 + dy, "bone-0")
    s.rect(6, 22 + dy, 9, 29 + dy, "leather-1")
    s.rect(6, 25 + dy, 9, 28 + dy, "steel-1")
    s.rect(6, 30 + dy, 9, 32 + dy, "flesh-1")
    s.rect(22, 22 + dy, 25, 29 + dy, "ash-0")
    s.rect(22, 30 + dy, 25, 32 + dy, "steel-1")
    s.dot(23, 31 + dy, glow)
    s.rect(20, 19 + dy, 21, 24 + dy, "blood-1")
    s.rect(10, 29 + dy, 21, 30 + dy, "leather-0")
    s.rect(15, 29 + dy, 16, 30 + dy, "steel-3")
    s.rect(10, 31 + dy, 21, 35 + dy, "ash-1")
    folds(s, (13, 18), 32, 35, dy)
    for x in (11, 14, 15, 19):
        s.dot(x, 36 + dy, "ash-1")


def upper_back(s, dy, glow, armed):
    hood(s, 11, 20, dy)
    s.rect(11, 17 + dy, 20, 17 + dy, "ash-1")
    s.rect(14, 9 + dy, 17, 15 + dy, "ash-0")
    s.rect(7, 18 + dy, 11, 21 + dy, "ash-1")
    s.rect(20, 18 + dy, 24, 18 + dy, "steel-2")
    s.rect(20, 19 + dy, 25, 21 + dy, "steel-2")
    s.rect(9, 18 + dy, 22, 35 + dy, "ash-1")
    folds(s, (11, 16, 19), 24, 35, dy)
    folds(s, (13,), 28, 35, dy)
    s.rect(12, 17 + dy, 19, 18 + dy, "blood-2")
    s.rect(14, 19 + dy, 15, 24 + dy, "blood-1")
    s.rect(6, 22 + dy, 9, 29 + dy, "ash-0")
    s.rect(6, 30 + dy, 9, 32 + dy, "steel-1")
    s.dot(7, 31 + dy, glow.replace("core", "dark").replace("mid", "dark"))
    s.rect(22, 22 + dy, 25, 29 + dy, "leather-1")
    s.rect(22, 25 + dy, 25, 28 + dy, "steel-1")
    s.rect(22, 30 + dy, 25, 32 + dy, "flesh-1")
    for x in (10, 13, 17, 20):
        s.dot(x, 36 + dy, "ash-1")
    if armed:
        sword(s, 20, 14 + dy)


def upper_side(s, dy, glow, armed, near_rune):
    """Drawn facing left; mirrored for right. `near_rune` picks which arm faces the camera."""
    if armed:
        sword(s, 19, 14 + dy)
    s.rect(19, 19 + dy, 21, 34 + dy, "ash-0")
    hood(s, 11, 19, dy)
    s.rect(11, 17 + dy, 19, 17 + dy, "ash-1")
    s.rect(10, 10 + dy, 10, 15 + dy, "ash-1")
    s.rect(11, 11 + dy, 13, 16 + dy, "void-0")
    s.dot(12, 13 + dy, "ash-3")
    s.dot(11, 15 + dy, "flesh-0")
    s.rect(12, 17 + dy, 18, 18 + dy, "blood-2")
    s.rect(19, 18 + dy, 20, 22 + dy, "blood-1")
    s.rect(12, 19 + dy, 19, 30 + dy, "leather-1")
    s.rect(12, 20 + dy, 15, 26 + dy, "steel-1")
    s.rect(16, 19 + dy, 19, 30 + dy, "ash-1")
    s.rect(12, 29 + dy, 19, 30 + dy, "leather-0")
    s.rect(11, 31 + dy, 20, 35 + dy, "ash-1")
    folds(s, (13, 17), 32, 35, dy)
    for x in (12, 15, 18):
        s.dot(x, 36 + dy, "ash-1")
    if near_rune:
        s.rect(14, 20 + dy, 17, 29 + dy, "ash-0")
        s.rect(14, 30 + dy, 17, 32 + dy, "steel-1")
        s.dot(15, 31 + dy, glow)
    else:
        s.rect(14, 18 + dy, 18, 21 + dy, "steel-2")
        s.dot(16, 20 + dy, "bone-0")
        s.rect(14, 22 + dy, 17, 29 + dy, "leather-1")
        s.rect(14, 25 + dy, 17, 28 + dy, "steel-1")
        s.rect(14, 30 + dy, 17, 32 + dy, "flesh-1")


def frame(direction, dy, legs, glow, look):
    """legs: (a, b) lifts for front/back, or ((off, lift), (off, lift)) for sides."""
    dy += look.get("hunch", 0)
    s = Sprite(W, H, mirror=direction == "right")
    if direction in ("down", "up"):
        legs_front(s, *legs)
        (upper_front if direction == "down" else upper_back)(s, dy, glow, look["armed"])
    else:
        (far, near) = legs
        leg_side(s, *far, far=True)
        leg_side(s, *near, far=False)
        upper_side(s, dy, glow, look["armed"], near_rune=direction == "left")
    s.recolor(look.get("ramps"), look.get("colors"))
    return s.finish().image()


def build(look):
    glows = ["rune-pale-mid", "rune-pale-mid", "rune-pale-core", "rune-pale-mid"]
    idle = [[frame(d, IDLE_BOB[i], (0, 0) if d in ("down", "up") else ((1, 0), (-1, 0)), glows[i], look)
             for i in range(4)] for d in DIRS]
    walk = []
    for d in DIRS:
        row = []
        for i in range(6):
            if d in ("down", "up"):
                legs = (WALK_LIFT_A[i], WALK_LIFT_B[i])
            else:
                legs = (WALK_STRIDE[(i + 3) % 6], WALK_STRIDE[i])
            row.append(frame(d, WALK_BOB[i], legs, "rune-pale-mid", look))
        walk.append(row)
    return {"idle": sheet(idle, W, H), "walk": sheet(walk, W, H)}


def main(preview_dir=None):
    for name, look in LOOKS.items():
        for anim, img in build(look).items():
            save(img, OUT / name / f"{name}_{anim}.png", preview_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
