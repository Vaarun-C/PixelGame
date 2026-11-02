"""Build the prologue's art from the chosen PixelLab drafts (see generate.py): the dead man prop,
the Wanderer's kneel, and the two cutscene close-ups (stone in the palm, the hilt's sockets).

Run from the repo root: .venv/bin/python art/drafts/prologue/assemble.py
grip_s27_0.png is body_base.png (the sitting Hollow corpse) edited to clench a wired stone. The edit
re-rendered the whole body, so only the fist is pasted onto the base. The snap keeps world colors
only, so the stone (Pale, wired, knuckles curled over it) is painted by hand.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from check_art import load_palette
from snap_palette import snap
from cleanup_sprite import AROUND, CROSS, Grid, cleanup, denoise, ramp
from pixel import save, sheet

D = Path("art/drafts/prologue")
OUT = Path("art/props/dead_man_hd.png")
CUTSCENES = Path("art/cutscenes")
PALETTE = {name: rgb for rgb, name in load_palette().items()}
PALETTE_NAME = load_palette()
FIST = (34, 68, 52, 82)
# Rows from the top-left corner at STONE_AT; "." leaves the pixel as it is.
STONE_AT = (41, 73)
STONE = [
    "kklkk",
    "lcmwl",
    "vmwmv",
    "vdmdv",
    ".vvv.",
]
# Light from the top-left: lit back of the hand on the left, the edit's bright right side dimmed.
TOUCH_UPS = {(39, 74): "ash-3", (46, 76): "ash-2", (47, 75): "ash-3", (45, 80): "steel-1", (38, 77): "void-3"}
INK = {"k": "ash-3", "l": "ash-2", "v": "void-1", "w": "steel-3", "c": "rune-pale-core", "m": "rune-pale-mid", "d": "rune-pale-dark"}

img = snap(Image.open(D / "body_base.png"))
edit = Grid(snap(Image.open(D / "grip_s27_0.png")))
denoise(edit)
img.paste(edit.image().crop(FIST), FIST[:2])
# The fist's bottom row takes the plate shading of the base row under it, so the paste has no seam.
for x in range(43, 48):
    img.putpixel((x, FIST[3] - 1), img.getpixel((x, FIST[3])))
for xy, name in TOUCH_UPS.items():
    img.putpixel(xy, PALETTE[name] + (255,))
for dy, row in enumerate(STONE):
    for dx, key in enumerate(row):
        if key != ".":
            img.putpixel((STONE_AT[0] + dx, STONE_AT[1] + dy), PALETTE[INK[key]] + (255,))
save(img, OUT)
print(OUT)


def paint(img, at, rows, ink):
    for dy, row in enumerate(rows):
        for dx, key in enumerate(row):
            if key != ".":
                img.putpixel((at[0] + dx, at[1] + dy), PALETTE[ink[key]] + (255,))


def outline(img):
    """The exterior outline is void-1, never the darkest void."""
    for y in range(img.height):
        for x in range(img.width):
            if img.getpixel((x, y))[:3] == PALETTE["void-0"] and img.getpixel((x, y))[3] and any(
                not (0 <= x + dx < img.width and 0 <= y + dy < img.height) or not img.getpixel((x + dx, y + dy))[3]
                for dx, dy in CROSS
            ):
                img.putpixel((x, y), PALETTE["void-1"] + (255,))


def luma(rgb):
    return 0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]


# The kneel and reach, facing right only (the prologue turns him to face the dead man).
def fix_kneel(img, lie_down):
    """The draft wraps the grip in ember and blood; it takes the idle sheets' bronze. Once he leans
    forward the cape lies flat, so its lit rim moves from the left side to the top edge."""
    g = Grid(img)
    for x, y in g.cells():
        if ramp(g.px[y][x]) == "ember":
            g.px[y][x] = "bronze-1"
            for dx, dy in AROUND:
                if ramp(g.get(x + dx, y + dy)) == "blood":
                    g.px[y + dy][x + dx] = "bronze-0"
    if lie_down:
        for x, y in g.cells():
            if g.px[y][x] == "blood-1" and ramp(g.get(x, y - 1)) != "blood" and x // 3 % 3 != 2:
                g.px[y][x] = "blood-2"
    return g.image()


kneel = [fix_kneel(cleanup(snap(Image.open(D / f"kneel/s19/{n}.png"))), n >= 4) for n in range(1, 9)]
save(sheet([kneel], *kneel[0].size), Path("art/characters/wanderer_hd/wanderer_hd_kneel.png"))

# The stone in the gauntlet: the draft's grey ball takes the Pale ramp by brightness, crossed by
# wire, in two frames (light low, light high) that the cutscene swaps slowly.
BALL = (74, 46)
BALL_R = 8.5
RAMPS = [["rune-pale-dark", "rune-pale-dark", "rune-pale-mid"], ["rune-pale-dark", "rune-pale-mid", "rune-pale-core"]]
WIRE = [(BALL[0] - 6 + i, BALL[1] - 6 + i) for i in range(13)] + [(BALL[0] + 4 - i, BALL[1] - 7 + i) for i in range(12)]
hand = snap(Image.open(D / "stone_closeup_s19.png"))
frames = []
for light in RAMPS:
    img = hand.copy()
    for y in range(hand.height):
        for x in range(hand.width):
            rgb = hand.getpixel((x, y))
            if rgb[3] and (x - BALL[0]) ** 2 + (y - BALL[1]) ** 2 <= BALL_R ** 2 and not PALETTE_NAME[rgb[:3]].startswith("void"):
                img.putpixel((x, y), PALETTE[light[min(2, int(luma(rgb) / 60))]] + (255,))
    for xy in WIRE:
        if (xy[0] - BALL[0]) ** 2 + (xy[1] - BALL[1]) ** 2 <= BALL_R ** 2:
            img.putpixel(xy, PALETTE["steel-1"] + (255,))
    outline(img)
    frames.append(img)
save(sheet([frames], *hand.size), CUTSCENES / "stone_closeup.png")

# The hilt close-up, drawn to match his greatsword in the character sheets: a dark ash blade with a
# lit bone edge on top, a plain dark bar guard, a bronze-wrapped grip and a dark pommel. The blade
# runs off the screen's left edge at 2x. Light from the top-left.
HILT_SIZE = (480, 96)
BLADE_ROWS = ["void-1"] + ["bone-0"] * 5 + ["ash-4", "ash-1"] + ["ash-0"] * 15 + ["ash-1", "steel-1", "void-2", "void-1"]
BLADE_TOP = 48 - len(BLADE_ROWS) // 2
GUARD = (410, 420, 16, 80)
GRIP = (420, 458, 42, 54)
POMMEL = (458, 470, 39, 57)


def rect(img, box, name):
    for y in range(box[2], box[3]):
        for x in range(box[0], box[1]):
            img.putpixel((x, y), PALETTE[name] + (255,))


def border(img, box, lit):
    """Outline a box in void-1, lit on its top and left edges."""
    x0, x1, y0, y1 = box
    rect(img, (x0, x1, y0, y0 + 1), "void-1")
    rect(img, (x0, x1, y1 - 1, y1), "void-1")
    rect(img, (x0, x0 + 1, y0, y1), "void-1")
    rect(img, (x1 - 1, x1, y0, y1), "void-1")
    rect(img, (x0 + 1, x1 - 1, y0 + 1, y0 + 2), lit)
    rect(img, (x0 + 1, x0 + 2, y0 + 1, y1 - 1), lit)


hilt = Image.new("RGBA", HILT_SIZE, (0, 0, 0, 0))
for dy, name in enumerate(BLADE_ROWS):
    rect(hilt, (0, GUARD[0], BLADE_TOP + dy, BLADE_TOP + dy + 1), name)
wear = random.Random(7)
for _ in range(9):
    x, w, depth = wear.randrange(GUARD[0] - 40), wear.randint(2, 5), wear.randint(1, 3)
    for i in range(w):
        rect(hilt, (x + i, x + i + 1, BLADE_TOP, BLADE_TOP + 1 + min(depth, i + 1, w - i)), "void-1")
for _ in range(70):
    x, y = wear.randrange(GUARD[0] - 3), BLADE_TOP + wear.randint(6, 21)
    rect(hilt, (x, x + wear.randint(2, 4), y, y + 1), wear.choice(["ash-1", "ash-1", "void-2"]))
rect(hilt, GUARD, "ash-0")
border(hilt, GUARD, "ash-2")
for y in range(GUARD[2] + 4, GUARD[3] - 2, 7):
    hilt.putpixel((GUARD[1] - 2, y), PALETTE["steel-1"] + (255,))
for x, y in ((GUARD[0], GUARD[2] + 3), (GUARD[0], GUARD[2] + 4), (GUARD[1] - 1, GUARD[3] - 6), (GUARD[0] + 4, GUARD[3] - 1)):
    hilt.putpixel((x, y), (0, 0, 0, 0))
rect(hilt, GRIP, "bronze-0")
for x in range(GRIP[0] + 2, GRIP[1] - 1, 4):
    for i in range(GRIP[3] - GRIP[2] - 2):
        hilt.putpixel((x + i // 4, GRIP[2] + 1 + i), PALETTE["bronze-1"] + (255,))
hilt.putpixel((GRIP[0] + 18, GRIP[2] + 1), PALETTE["void-1"] + (255,))
hilt.putpixel((GRIP[0] + 18, GRIP[2] + 2), PALETTE["bronze-0"] + (255,))
border(hilt, GRIP, "ash-1")
rect(hilt, POMMEL, "steel-1")
border(hilt, POMMEL, "ash-1")
rect(hilt, (POMMEL[0] + 2, POMMEL[0] + 4, POMMEL[2] + 2, POMMEL[2] + 4), "ash-0")
for x, y in ((POMMEL[0], POMMEL[2]), (POMMEL[1] - 1, POMMEL[2]), (POMMEL[0], POMMEL[3] - 1), (POMMEL[1] - 1, POMMEL[3] - 1), (POMMEL[1] - 2, POMMEL[2])):
    hilt.putpixel((x, y), (0, 0, 0, 0))

# The threading, frame by frame: the stone pressed to the ricasso, each turn of its wire tail wound
# over the blade with the loose end pulled off-frame by his hand (down while it crosses the front,
# up once it has gone round the back), the first turns slipping toward the tip, then all of them
# pulled tight with blood on the wire. Each strand is a lit and a shaded pixel.
LASH_AT = (397, 48)
STONE_R = 4.5
EDGE = (BLADE_TOP - 1, BLADE_TOP + len(BLADE_ROWS) + 1)
SLACK = "slack"
# (finished turns, turn being wound and how far across, where the loose end goes, slip, bloody)
THREADING = [
    ([], None, "down", 0, False),
    ([], (-6, 0.35), "down", 0, False),
    ([], (-6, 0.7), "down", 0, False),
    ([-6], None, "up", 0, False),
    ([-6], (6, 0.35), "down", 0, False),
    ([-6], (6, 0.7), "down", 0, False),
    ([-6, 6], None, "up", 0, False),
    ([-6, 6], None, SLACK, -4, False),
    ([-6, 6], (-9, 0.5), "down", 0, False),
    ([-9, -6, 6], (9, 0.5), "down", 0, False),
    ([-9, -6, 6, 9], None, "up", 0, False),
    ([-9, -6, 6, 9], None, None, 0, True),
]


def strand(img, x, y, bloody=False):
    """Blood sits in short irregular runs along the wire."""
    if 0 <= x < img.width - 1 and 0 <= y < img.height:
        run = random.Random(x * 1000 + y // 3).random()
        img.putpixel((x, y), PALETTE["blood-2" if bloody and run < 0.3 else "blood-1" if bloody and run < 0.4 else "ash-4"] + (255,))
        img.putpixel((x + 1, y), PALETTE["void-1"] + (255,))


def turn_x(dx, y, slip):
    slant = 3 if slip else 10
    return LASH_AT[0] + dx + slip + (y - EDGE[0]) // slant


# The gauntlet pulling each finished turn through (the "up" frames): the draft's own wire is cut away
# and the hilt's wire runs up into the fist. The draft is reshaded from its brightness, tilted
# toward the top-left light, into the steel ramp in the stone close-up's proportions (steel-1 base).
STEEL_SHARE = [("steel-0", 0.12), ("steel-1", 0.45), ("steel-2", 0.67), ("steel-3", 1.0)]
HAND_WIRE = (28, 43)
HAND_GRIP = (22, 48)
HAND_TOP = 14


def clean_hand():
    draft = Image.open(D / "pull_hand_taut_s19.png").convert("RGBA")
    light = draft.convert("L")
    inside = {(x + 1, y + 1): light.getpixel((x, y)) - 0.7 * (x + y) for y in range(draft.height) for x in range(draft.width)
              if draft.getpixel((x, y))[3] and not (x >= HAND_WIRE[0] and y >= HAND_WIRE[1])}
    order = sorted(inside, key=inside.get)
    g = Grid(Image.new("RGBA", (draft.width + 2, draft.height + 2)))
    for i, (x, y) in enumerate(order):
        g.px[y][x] = next(name for name, share in STEEL_SHARE if i < share * len(order))
    denoise(g)
    for x, y in g.cells():
        if g.get(x - 1, y) is None or g.get(x, y - 1) is None:
            g.px[y][x] = "bone-0" if g.px[y][x] in ("steel-2", "steel-3") else g.px[y][x]
        elif g.get(x + 1, y) is None or g.get(x, y + 1) is None:
            g.px[y][x] = "steel-0"
    for x, y in [(x, y) for y in range(g.h) for x in range(g.w) if (x, y) not in inside]:
        if any((x + dx, y + dy) in inside for dx, dy in CROSS):
            g.px[y][x] = "void-1"
    return g.image()


pull_hand = clean_hand()


def threaded(done, winding, tail, slip, bloody):
    img = hilt.copy()
    cx, cy = LASH_AT
    for y in range(cy - 5, cy + 6):
        for x in range(cx - 5, cx + 6):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            lit = (x - cx) + (y - cy)
            name = "rune-pale-core" if lit < -4 else "rune-pale-mid" if lit < 3 else "rune-pale-dark"
            if d <= STONE_R + 1:
                img.putpixel((x, y), PALETTE[name if d <= STONE_R else "void-1"] + (255,))
    # The wire crossing the stone runs out to the turns once there are any, so it reads as tied.
    reach = 7 if done else 3
    for i in range(-reach, reach + 1):
        for x, y in ((cx + i, cy + i), (cx + i, cy - i)):
            img.putpixel((x, y), PALETTE["ash-4" if done else "steel-1"] + (255,))
            if abs(i) > 3 and y + 1 < img.height:
                img.putpixel((x, y + 1), PALETTE["void-1"] + (255,))
    for dx in done:
        for y in range(*EDGE):
            strand(img, turn_x(dx, y, slip), y, bloody)
    end = (cx + 4, cy + 4)
    if winding:
        dx, part = winding
        last = EDGE[0] + int((EDGE[1] - EDGE[0]) * part)
        for y in range(EDGE[0], last):
            strand(img, turn_x(dx, y, 0), y)
        end = (turn_x(dx, last, 0), last)
    elif done:
        end = (turn_x(done[-1], EDGE[1] - 1 if tail == "down" else EDGE[0], slip), EDGE[1] - 1 if tail == "down" else EDGE[0])
    if tail in ("down", "up"):
        step = 1 if tail == "down" else -1
        y = end[1]
        while (HAND_TOP if tail == "up" else 0) <= y < img.height:
            strand(img, end[0] + abs(y - end[1]) // 3, y)
            y += step
        if tail == "up":
            grip_x = end[0] + (end[1] - HAND_TOP) // 3
            img.paste(pull_hand, (grip_x - HAND_GRIP[0], HAND_TOP - HAND_GRIP[1]), pull_hand)
            for y in (HAND_TOP - 1, HAND_TOP - 2):
                strand(img, grip_x, y)
    elif tail == SLACK:
        for i in range(40):
            strand(img, end[0] + i, end[1] + int(12 * (1 - ((i - 20) / 20) ** 2)))
    return img


save(sheet([[threaded(*f) for f in THREADING]], *HILT_SIZE), CUTSCENES / "hilt_closeup.png")
print("kneel, stone_closeup, hilt_closeup")
