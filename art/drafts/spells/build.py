"""Build the spell-casting review strips (lore: Uttering): for each spell the Wanderer stops, takes his
held pose, shouts the rune's name, then the spell plays out while he holds it, and he recovers.

Each strip is one row of STAGE-sized frames at FPS. The tier glow is drawn in the Pale ramp (TIER),
which the review page and the game swap for the uttered stone's tier ramp.
Writes art/drafts/spells/review/<spell>.png and timeline.json. With --game, writes the signed-off
spells' game sheets too (GAME), into art/ and godot/art/: the cast frames (in-betweens, the last one
the held pose) on the base frame's 160x160 canvas, feet at y=143, and the effect with its back layer
(under characters) in row 0 and front layer in row 1, feet at FEET.

Run from the repo root: .venv/bin/python art/drafts/spells/build.py [--game] [spell ...]
"""
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "tools")
from check_art import load_palette
from cleanup_sprite import cleanup
from snap_palette import drop_specks, snap

D = Path("art/drafts/spells")
OUT = D / "review"
NAME = load_palette()
C = {name: rgb + (255,) for rgb, name in NAME.items()}
TIER = {"dark": C["rune-pale-dark"], "mid": C["rune-pale-mid"], "core": C["rune-pale-core"]}
STAGE = (320, 256)
FEET = (160, 176)
FPS = 12
IDLE, POSE, RECOVER = 3, 5, 4
# Grenze Gotisch at its heaviest: blackletter whose k doesn't read as an f.
FONT = ImageFont.truetype("godot/art/fonts/GrenzeGotisch.ttf", 24)
FONT.set_variation_by_axes([800])
GROUND = Image.open("godot/art/tiles/battlefield/battlefield_ground_hd.png").convert("RGBA").crop((15 * 64, 64, 16 * 64, 128))
BASE = "art/drafts/wanderer/attacks/base/south.png"


FEET_Y = 143
FOOT_PIXELS = 8


def feet_row(img):
    """The lowest row with a foot's worth of pixels (a planted blade tip alone doesn't count)."""
    alpha = img.getchannel("A").load()
    for y in range(img.height - 1, -1, -1):
        if sum(1 for x in range(img.width) if alpha[x, y]) >= FOOT_PIXELS:
            return y
    return FEET_Y


def finished(path, feet=None):
    """A PixelLab frame snapped to the palette, cleaned like his other sheets (cape and tabard ramps,
    noise, outline; cleanup_sprite expects the feet on the canvas bottom) and stood on y=143."""
    img = drop_specks(snap(Image.open(path)), 3)
    feet = feet or feet_row(img)
    body = cleanup(img.crop((0, 0, img.width, feet + 1)))
    out = Image.new("RGBA", img.size)
    out.alpha_composite(body, (0, FEET_Y - feet))
    # A planted blade tip below the feet keeps its place under them.
    out.alpha_composite(img.crop((0, feet + 1, img.width, feet + img.height - FEET_Y)), (0, FEET_Y + 1))
    return out


def edited(spell):
    return finished(D / f"edit_{spell}_s7.png")


def cast_frames(spell):
    """The in-betweens from his base frame to the held pose (generate.py anims), snapped; the last
    one is the pose. All share the base frame's canvas. Without them, just the edited pose."""
    folder = D / f"anim_{spell}"
    if not folder.exists():
        return [edited(spell)]
    picks = PICKS.get(spell, range(1, len(list(folder.glob("*.png")))))
    frames = [finished(folder / f"{i}.png") for i in picks]
    if spell in KEY:
        frames.append(finished(D / KEY[spell][0], KEY[spell][1]))
    return [mend_cape(f) for f in frames] if spell in MEND else frames


def mend_cape(img):
    """The snap reads a flaring cape's shaded folds as bronze and leather: pixels mostly ringed by
    cape red go back into its ramp."""
    px = img.load()
    for _ in range(4):
        stray = [(x, y) for y in range(1, img.height - 1) for x in range(1, img.width - 1)
                 if px[x, y][3] and NAME.get(px[x, y][:3]) in ("bronze-0", "leather-0")
                 and sum(NAME.get(px[x + dx, y + dy][:3], "").startswith("blood")
                         for dx in (-1, 0, 1) for dy in (-1, 0, 1)) >= 3]
        for x, y in stray:
            px[x, y] = C["blood-0"]
    return drop_specks(img, 3)


# In-betweens left out: Break goes from the raised sword straight into its slam (its drafts painted
# white impact stars on 3 and 5, swung the sword sideways on 4 and hid it on 6); Flee's last two
# tangle his arms; Still's sword flips on 5.
PICKS = {"break": [1, 2], "flee": [1, 2, 3, 4], "still": [1, 2, 3, 4, 6]}
# Held poses redrawn with SpriteCook edits (from sc_<spell>*.png), ending the cast, with the feet row
# where the planted blade is wide enough to pass for feet.
KEY = {"break": ("key_break_push.png", 135), "flee": ("key_flee_sc.png", None)}
MEND = {"flee"}


# Ticks each in-between is held: Rend's rise is slow.
SLOW = {"rend": 2}
SHAKE = {"rend": (5, -5, 4, -3, 2, -1)}


def on_stage(sprite):
    """The sprite's canvas with its feet (lowest opaque row) on FEET, centred on FEET.x."""
    box = sprite.getbbox()
    return sprite, (FEET[0] - sprite.width // 2, FEET[1] - box[3])


def backdrop():
    img = Image.new("RGBA", STAGE)
    for y in range(0, STAGE[1], 64):
        for x in range(0, STAGE[0], 64):
            img.paste(GROUND, (x, y))
    return img


def ellipse(d, cx, cy, rx, ry, colour, width=1):
    if rx >= 1 and ry >= 1:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=colour, width=width)


def dot(d, x, y, colour, size=1):
    d.rectangle((round(x), round(y), round(x) + size - 1, round(y) + size - 1), fill=colour)


def ramp(age):
    """The tier ramp as a burst cools: core, then mid, then dark."""
    return TIER["core"] if age < 0.34 else TIER["mid"] if age < 0.67 else TIER["dark"]


def sparks(rng, n, origin, speed, spread=(0, math.tau), gravity=0.0, colours=None):
    out = []
    for _ in range(n):
        a = rng.uniform(*spread)
        out.append({"o": origin, "v": (math.cos(a) * rng.uniform(*speed), math.sin(a) * rng.uniform(*speed)),
                    "c": rng.choice(colours) if colours else None, "life": rng.uniform(0.5, 1.0), "g": gravity})
    return out


def draw_sparks(d, list_, t, n, size=1):
    for s in list_:
        age = t / (n * s["life"])
        if age >= 1:
            continue
        x = s["o"][0] + s["v"][0] * t
        y = s["o"][1] + s["v"][1] * t + s["g"] * t * t
        dot(d, x, y, s["c"] or ramp(age), size)


CHEST = (FEET[0], FEET[1] - 56)


# Rend: a blood-red scythe crescent swept through him from high left to low right, white-hot at its
# cutting edge, leaving a gouge in the ground and blood and embers in the air.
# Angles count anticlockwise from screen-right with y up; the arc's middle (240) crosses his chest. The
# inner circle is pushed away from that middle so the blade is thickest where it passes through him.
SCYTHE = {"centre": (FEET[0] + 60, FEET[1] - 150), "radius": 150, "bite": (13, -22), "from": 185, "to": 295}
SCYTHE_RAMP = ["bone-0", "blood-4", "blood-4", "blood-3", "blood-3", "blood-2", "blood-1"]


def crescent(img, reveal, cool):
    """The scythe's crescent: inside the outer circle, outside the inner one, swept from `from` to
    the revealed angle. Shade by depth from the cutting (outer) edge; `cool` steps it down the ramp."""
    px = img.load()
    cx, cy = SCYTHE["centre"]
    r = SCYTHE["radius"]
    ix, iy = cx + SCYTHE["bite"][0], cy + SCYTHE["bite"][1]
    hi = SCYTHE["from"] + (SCYTHE["to"] - SCYTHE["from"]) * reveal
    for y in range(max(0, cy - r), min(STAGE[1], cy + r + 1)):
        for x in range(max(0, cx - r), min(STAGE[0], cx + r + 1)):
            outer = math.hypot(x - cx, (y - cy) * 1.15)
            if outer > r or math.hypot(x - ix, (y - iy) * 1.15) <= r:
                continue
            a = math.degrees(math.atan2(-(y - cy), x - cx)) % 360
            if not SCYTHE["from"] <= a <= hi:
                continue
            k = min(len(SCYTHE_RAMP) - 1, int((r - outer) / 2.2) + cool)
            # The tail of the sweep, near where it started, is already cooling.
            k = min(len(SCYTHE_RAMP) - 1, k + int((hi - a) / 40))
            px[x, y] = C[SCYTHE_RAMP[k]]


def fx_rend(t, n, back, front, rng, state):
    f = ImageDraw.Draw(front)
    b = ImageDraw.Draw(back)
    cx, cy = SCYTHE["centre"]
    if "spray" not in state:
        state["spray"] = []
        for a in range(SCYTHE["from"], SCYTHE["to"] + 1, 4):
            o = (cx + math.cos(math.radians(a)) * SCYTHE["radius"], cy - math.sin(math.radians(a)) * SCYTHE["radius"] / 1.15)
            state["spray"] += sparks(rng, 2, o, (1, 4), (math.radians(-a) - 0.5, math.radians(-a) + 0.5), 0.25, [C["blood-3"], C["blood-4"], C["ember-2"], C["ember-3"]])
    sweep = [0.35, 0.8, 1.0, 1.0]
    if t < len(sweep):
        crescent(front, sweep[t], 0 if t < 3 else 1)
    elif t < 7:
        crescent(front, 1.0, t - 2)
    gouge = [(FEET[0] - 70, FEET[1] + 4), (FEET[0] + 10, FEET[1] + 14), (FEET[0] + 96, FEET[1] + 2)]
    if t >= 1:
        b.line(gouge, fill=C["void-0"], width=3)
        if t < n - 3:
            b.line(gouge, fill=C["blood-2"] if t < 6 else C["blood-1"], width=1)
    if t >= 1:
        draw_sparks(f, state["spray"], t - 1, n - 1, 2)


def fx_break(t, n, back, front, rng, state):
    p = (FEET[0] + 4, FEET[1] + 6)
    b = ImageDraw.Draw(back)
    f = ImageDraw.Draw(front)
    if "cracks" not in state:
        state["cracks"] = []
        for k in range(7):
            a = k / 7 * math.tau + rng.uniform(-0.3, 0.3)
            pts = [p]
            for step in range(1, 6):
                r = step * 14
                pts.append((p[0] + math.cos(a) * r + rng.uniform(-4, 4), p[1] + math.sin(a) * r * 0.45 + rng.uniform(-2, 2)))
            state["cracks"].append(pts)
        state["debris"] = sparks(rng, 26, (p[0], p[1] - 4), (2, 6), (math.pi * 1.1, math.pi * 1.9), 0.45, [C["ash-2"], C["ash-3"], C["leather-1"], C["void-2"]])
    reach = min(5, t + 2)
    for pts in state["cracks"]:
        b.line(pts[:reach + 1], fill=C["void-0"], width=2)
        if t < n - 3:
            b.line(pts[:reach + 1], fill=TIER["mid"] if t < 5 else TIER["dark"], width=1)
    rx = 12 + t * 14
    if t < n - 3:
        ellipse(b, p[0], p[1], rx, rx * 0.42, ramp(t / n), 2 if t < 4 else 1)
    draw_sparks(f, state["debris"], t, n, 2)


def fx_sting(t, n, back, front, rng, state):
    d = ImageDraw.Draw(front)
    if "shards" not in state:
        state["shards"] = [(k / 28 * math.tau + rng.uniform(-0.1, 0.1), rng.uniform(9, 14), rng.uniform(5, 10)) for k in range(28)]
    for a, speed, length in state["shards"]:
        r = 10 + speed * t
        if t >= n - 1:
            continue
        x, y = CHEST[0] + math.cos(a) * r, CHEST[1] + math.sin(a) * r * 0.75
        tx, ty = x - math.cos(a) * length, y - math.sin(a) * length * 0.75
        d.line((tx, ty, x, y), fill=TIER["mid"] if t < n * 0.6 else TIER["dark"], width=1)
        dot(d, x, y, TIER["core"] if t < n * 0.6 else TIER["mid"])
    if t < 2:
        ellipse(d, CHEST[0], CHEST[1], 8 + t * 6, 6 + t * 5, TIER["core"], 2)


def fx_ward(t, n, back, front, rng, state):
    cx, cy = FEET[0], FEET[1] - 46
    rx, ry = 38, 58
    f = ImageDraw.Draw(front)
    b = ImageDraw.Draw(back)
    shown = min(1.0, (t + 1) / 5)
    # At its brightest for 3 frames at most (ART_RULES §8 flashes).
    colour = TIER["core"] if t < 3 else TIER["mid"] if t < n - 3 else TIER["dark"]
    f.arc((cx - rx, cy - ry, cx + rx, cy + ry), 90 - 180 * shown, 90 + 180 * shown, fill=colour, width=2 if t < 4 else 1)
    f.arc((cx - rx * 0.5, cy - ry, cx + rx * 0.5, cy + ry), 90 - 180 * shown, 90 + 180 * shown, fill=TIER["dark"], width=1)
    band = cy - ry + (t * 12) % (2 * ry)
    if t >= 4:
        half = rx * math.sqrt(max(0.0, 1 - ((band - cy) / ry) ** 2))
        f.line((cx - half + 2, band, cx + half - 2, band), fill=TIER["core"])
    ellipse(b, FEET[0], FEET[1] + 2, rx + 4, 10, colour, 1)


def fx_still(t, n, back, front, rng, state):
    tip = (FEET[0] - 54, FEET[1] - 62)
    f = ImageDraw.Draw(front)
    b = ImageDraw.Draw(back)
    if "motes" not in state:
        state["motes"] = [(FEET[0] + rng.uniform(-140, 140), FEET[1] + rng.uniform(-110, 30)) for _ in range(40)]
    r = min(150, 20 + t * 45)
    ellipse(b, FEET[0], FEET[1] + 2, r, r * 0.42, TIER["mid"] if t < n - 3 else TIER["dark"], 1)
    if t < 3:
        ellipse(f, tip[0], tip[1], 6 + t * 10, 6 + t * 10, TIER["core"], 2)
    for k, (x, y) in enumerate(state["motes"]):
        if t >= 2 and (x - FEET[0]) ** 2 / 150 ** 2 + (y - FEET[1]) ** 2 / 110 ** 2 < 1 and t < n - 1:
            dot(f, x, y, TIER["core"] if k % 3 == 0 else TIER["mid"], 2)


def fx_sink(t, n, back, front, rng, state):
    b = ImageDraw.Draw(back)
    f = ImageDraw.Draw(front)
    # The pool is centred on his feet, though it spreads from where his palm meets the ground.
    hand = (FEET[0], FEET[1] - 4)
    if "streaks" not in state:
        state["streaks"] = [(hand[0] + rng.uniform(-140, 140), rng.uniform(-120, -20), rng.uniform(8, 14)) for _ in range(22)]
    r = min(150, 16 + t * 30) if t < n - 2 else 150
    fade = t >= n - 3
    b.ellipse((hand[0] - r, hand[1] - r * 0.4, hand[0] + r, hand[1] + r * 0.4), fill=None if fade else C["void-1"])
    ellipse(b, hand[0], hand[1], r, r * 0.4, TIER["dark"], 2)
    for k in range(3):
        rr = r * (1 - ((t * 0.15 + k / 3) % 1))
        ellipse(b, hand[0], hand[1], rr, rr * 0.4, TIER["mid"] if not fade else TIER["dark"], 1)
    for x, y0, speed in state["streaks"]:
        y = FEET[1] + y0 + speed * t
        ground = hand[1] + 0.4 * math.sqrt(max(0.0, r * r - (x - hand[0]) ** 2))
        if y < ground and abs(x - hand[0]) < r and t < n - 1:
            f.line((x, y - 6, x, y), fill=TIER["mid"])
            dot(f, x, y, TIER["core"])


def fx_hunger(t, n, back, front, rng, state):
    f = ImageDraw.Draw(front)
    hand = (FEET[0] + 30, FEET[1] - 80)
    if "drops" not in state:
        state["drops"] = [(rng.uniform(0, math.tau), rng.uniform(100, 130), rng.uniform(0.0, 0.35), rng.choice([C["blood-3"], C["blood-4"], TIER["mid"], TIER["core"]])) for _ in range(90)]
    for a, r0, delay, colour in state["drops"]:
        p = (t / (n - 2) - delay) / (1 - delay)
        if p <= 0 or p >= 1:
            continue
        r = r0 * (1 - p)
        ang = a + p * 2.2
        x, y = hand[0] + math.cos(ang) * r, hand[1] + 30 * (1 - p) + math.sin(ang) * r * 0.5
        dot(f, x, y, colour, 2)
    if t >= n * 0.6:
        ellipse(f, hand[0], hand[1], 4 + (t % 3) * 2, 4 + (t % 3) * 2, TIER["core"], 1)


def fx_flee(t, n, back, front, rng, state):
    f = ImageDraw.Draw(front)
    if "lines" not in state:
        state["lines"] = [(rng.uniform(-150, 150), rng.uniform(-100, 10), rng.uniform(16, 40)) for _ in range(18)]
    for x0, y0, length in state["lines"]:
        x = FEET[0] + x0 - t * 10
        if t < n - 2:
            f.line((x, FEET[1] + y0, x + length, FEET[1] + y0), fill=TIER["mid"] if t < n / 2 else TIER["dark"])
    state["ghost"] = True


FX = {"rend": (fx_rend, 12), "break": (fx_break, 12), "sting": (fx_sting, 10), "ward": (fx_ward, 12),
      "still": (fx_still, 12), "sink": (fx_sink, 12), "hunger": (fx_hunger, 14), "flee": (fx_flee, 10)}


def ghost(sprite, colour):
    tint = Image.new("RGBA", sprite.size, colour)
    mask = sprite.getchannel("A")
    out = Image.new("RGBA", sprite.size)
    out.paste(tint, (0, 0), mask)
    return out


def shout(img, text, top):
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    w = d.textlength(text, font=FONT)
    x, y = FEET[0] - w / 2, max(2, top - 30)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            d.text((x + dx, y + dy), text, font=FONT, fill=C["void-0"])
    d.text((x, y), text, font=FONT, fill=C["bone-0"])


# All spells go in the game.
GAME = list(FX)


def export(spell):
    moves = cast_frames(spell)
    size = moves[0].width
    cast = Image.new("RGBA", (size * len(moves), size))
    for i, sprite in enumerate(moves):
        cast.paste(sprite, (i * size, 0))
    fx, n = FX[spell]
    rng, state = random.Random(spell), {}
    sheet = Image.new("RGBA", (STAGE[0] * n, STAGE[1] * 2))
    for t in range(n):
        back, front = Image.new("RGBA", STAGE), Image.new("RGBA", STAGE)
        fx(t, n, back, front, rng, state)
        sheet.paste(back, (t * STAGE[0], 0))
        sheet.paste(front, (t * STAGE[0], STAGE[1]))
    for img, path in ((cast, f"characters/wanderer_hd/wanderer_hd_cast_{spell}.png"), (sheet, f"vfx/spell_{spell}_hd.png")):
        for root in ("art", "godot/art"):
            Path(root, path).parent.mkdir(parents=True, exist_ok=True)
            img.save(Path(root, path))
    print("exported", spell, len(moves), "cast frames,", n, "effect frames")


def build(spell):
    idle, at = on_stage(Image.open(BASE).convert("RGBA"))
    moves = cast_frames(spell)
    pose = moves[-1]
    fx, n = FX[spell]
    rng = random.Random(spell)
    state = {}
    frames, phases = [], []
    ground = backdrop()
    top = at[1] + pose.getbbox()[1]
    shakes = SHAKE.get(spell, (2, -2, 1))

    def frame(sprite, t=None, say=False, shake=0):
        img = ground.copy()
        back, front = Image.new("RGBA", STAGE), Image.new("RGBA", STAGE)
        if t is not None:
            fx(t, n, back, front, rng, state)
            if state.get("ghost") and t < n - 2:
                for k, colour in ((3, "steel-0"), (2, "steel-1")):
                    back.alpha_composite(ghost(sprite, C[colour]), (at[0] - 14 * k, at[1]))
        img.alpha_composite(back)
        img.alpha_composite(sprite, (at[0] + shake, at[1]))
        img.alpha_composite(front)
        if say:
            shout(img, spell.capitalize() + "!", top)
        return img

    def add(img, phase, times=1):
        for _ in range(times):
            frames.append(img)
            phases.append(phase)

    add(frame(idle), "stop", IDLE)
    for sprite in moves[:-1]:
        add(frame(sprite), "pose", SLOW.get(spell, 1))
    add(frame(pose), "pose", SLOW.get(spell, 1))
    add(frame(pose, say=True), "shout", POSE - 1)
    for t in range(n):
        add(frame(pose, t, say=t < n // 2, shake=shakes[t] if t < len(shakes) else 0), "spell")
    for sprite in reversed(moves[:-1]):
        add(frame(sprite), "recover")
    add(frame(idle), "recover", 2)

    strip = Image.new("RGBA", (STAGE[0] * len(frames), STAGE[1]))
    for i, img in enumerate(frames):
        strip.paste(img, (i * STAGE[0], 0))
    OUT.mkdir(parents=True, exist_ok=True)
    strip.save(OUT / f"{spell}.png")
    return phases


if __name__ == "__main__":
    game = "--game" in sys.argv
    spells = [a for a in sys.argv[1:] if a != "--game"] or list(FX)
    timeline = json.loads((OUT / "timeline.json").read_text())["spells"] if (OUT / "timeline.json").exists() else {}
    for spell in spells:
        timeline[spell] = build(spell)
        print(spell, len(timeline[spell]), "frames")
    (OUT / "timeline.json").write_text(json.dumps({"fps": FPS, "stage": STAGE, "tier": {k: v[:3] for k, v in TIER.items()}, "spells": {k: v for k, v in timeline.items() if k in FX}}))
    if game:
        for spell in spells:
            if spell in GAME:
                export(spell)
