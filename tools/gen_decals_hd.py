"""Ground detail decals at 2x: tufts, pebbles, twigs, bone chips, blood, moss, mushrooms, straw, embers.
Usage: .venv/bin/python tools/gen_decals_hd.py [preview_dir]

art/props/decals_hd.png: one row per decal (order must match godot/scripts/world/decals.gd), FRAMES
columns of 32 px. Tufts sway (their upper blades lean with the wind), embers flicker, the rest repeat
one frame. Art sits on row FEET, centred, lit from the top-left; small solid bits get a dark contact
pixel down-right instead of an outline so they lie in the ground rather than on it.
"""
import random
import sys
from pathlib import Path

from pixel import Sprite, save, sheet

ART = Path(__file__).resolve().parent.parent / "art"
S = 32
FRAMES = 4
FEET = 28
SWAY = [0, 1, 0, -1]
CONTACT = "void-2"


def tuft(rng, blades, colors, height=(6, 13), spread=6, tips=None):
    """Upright blades from a shared root; the top half of each leans by the frame's sway. A dark root
    and lit tips keep a tuft readable on ground of its own colour; tips: dry seed-head colour, if any."""
    dark, mid, light = colors
    shapes = [(16 + rng.randint(-spread, spread), rng.randint(*height), rng.choice((-1, 0, 0, 1))) for _ in range(blades)]

    def draw(s, frame):
        for x, h, curve in sorted(shapes, key=lambda b: -b[1]):
            for i in range(h):
                # Each row sits at most 1 px off the one below, so a swaying blade never breaks.
                lean = max(-1, min(1, SWAY[frame] + curve)) if i >= h // 2 else 0
                lean += curve if i >= h - 2 and h - 2 > h // 2 else 0
                top = tips if tips and i == h - 1 and x % 2 else light
                s.dot(x + lean, FEET - i, dark if i <= 1 else top if i >= h - 2 else mid)
        return s
    return draw


def stones(rng, count, colors):
    shadow, body, light = colors
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        for _ in range(count):
            x, y, w = 16 + r.randint(-8, 8), FEET - r.randint(0, 4), r.randint(1, 3)
            s.rect(x + 1, y - w + 2, x + w, y + 1, CONTACT)
            s.rect(x, y - w + 1, x + w - 1, y, body)
            s.dot(x, y - w + 1, light)
            if w > 1:
                s.dot(x + w - 1, y, shadow)
        return s
    return draw


def twigs(rng, colors):
    dark, light = colors
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        x, y = 16 - r.randint(6, 9), FEET - r.randint(0, 3)
        for i in range(r.randint(10, 15)):
            s.dot(x + i + 1, y + 1, CONTACT)
            s.dot(x + i, y, light if i % 4 == 0 else dark)
            if i % 5 == 3:
                s.dot(x + i + 1, y - 1, dark)
                s.dot(x + i + 2, y - 2, dark)
            y += r.choice((0, 0, 0, 1, -1))
        return s
    return draw


def bones(rng):
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        for _ in range(r.randint(2, 4)):
            x, y, n = 16 + r.randint(-8, 8), FEET - r.randint(0, 4), r.randint(2, 4)
            for i in range(n):
                s.dot(x + i + 1, y + 1, CONTACT)
                # Weathered grey with one pale end: bone-0 is kept for points of interest (§3).
                s.dot(x + i, y, "bone-0" if i == 0 and n >= 3 else "ash-2")
        return s
    return draw


def splat(rng, colors):
    """Blood: clusters of 2-4 px (ART_RULES §8)."""
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        for _ in range(r.randint(4, 7)):
            x, y = 16 + r.randint(-8, 8), FEET - r.randint(0, 6)
            c = r.choice(colors)
            for dx, dy in [(0, 0)] + r.sample([(1, 0), (0, 1), (1, 1), (-1, 0)], r.randint(1, 3)):
                s.dot(x + dx, y + dy, c)
        return s
    return draw


def patch(rng, colors, radius=(5, 8)):
    """A low irregular blob (moss, ash), lighter on its upper-left."""
    dark, mid, light = colors
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        rx, ry = r.randint(*radius), 3
        for y in range(-ry, ry + 1):
            for x in range(-rx, rx + 1):
                if (x / (rx + 0.5)) ** 2 + (y / (ry + 0.5)) ** 2 + r.random() * 0.35 <= 1:
                    s.dot(16 + x, FEET - 3 + y, light if x + 2 * y < -rx else dark if y >= ry - 1 else mid)
        return s
    return draw


def mushrooms(rng):
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        for _ in range(r.randint(2, 3)):
            x, y = 16 + r.randint(-6, 6), FEET - r.randint(0, 3)
            s.dot(x + 1, y + 1, CONTACT)
            s.rect(x, y - 1, x, y, "ash-2")
            s.rect(x - 1, y - 2, x + 1, y - 2, "leather-2")
            s.dot(x - 1, y - 2, "leather-3")
        return s
    return draw


def straw(rng):
    seed = rng.random()

    def draw(s, frame):
        r = random.Random(seed)
        for _ in range(r.randint(4, 6)):
            x, y, n, dy = 16 + r.randint(-9, 5), FEET - r.randint(0, 5), r.randint(3, 6), r.choice((0, 1, -1))
            for i in range(n):
                s.dot(x + i, y + (i // 2) * dy, r.choice(("leather-3", "leather-3", "ash-2")))
        return s
    return draw


def embers(rng):
    """Specks on a charred smudge: each flares and dims on its own phase."""
    count = rng.randint(3, 5)
    specks = [(16 + rng.randint(-4, 4), FEET - 3 + rng.randint(-2, 2), i % FRAMES) for i in range(count)]
    smudge = patch(rng, ("void-2", "void-3", "void-3"), (4, 6))

    def draw(s, frame):
        smudge(s, frame)
        for x, y, phase in specks:
            heat = (frame + phase) % FRAMES
            if heat == 2:
                continue  # cooled: the smudge shows through
            s.dot(x, y, ("ember-1", "ember-0", None, "ember-0")[heat])
            if heat == 0:
                s.dot(x + 1, y, "ember-0")
        return s
    return draw


GRASS = ("void-3", "rot-2", "rot-3")
DRY = ("leather-1", "leather-2", "leather-3")
FROST = ("steel-0", "steel-1", "steel-2")
BURNT = ("void-3", "leather-0", "ash-1")
rng = random.Random("decals")
DECALS = [
    ("grass_tuft", tuft(rng, 9, GRASS, tips="leather-3")),
    ("grass_tuft", tuft(rng, 12, GRASS, (5, 9), 7)),
    ("grass_tuft", tuft(rng, 7, ("void-3", "rot-1", "rot-2"), (7, 12), 4, "leather-3")),
    ("dry_tuft", tuft(rng, 8, DRY, tips="ash-2")),
    ("dry_tuft", tuft(rng, 8, ("leather-1", "leather-2", "ash-2"), (3, 7), 7)),
    ("frost_tuft", tuft(rng, 8, FROST, tips="ash-2")),
    ("frost_tuft", tuft(rng, 8, ("steel-0", "steel-1", "ash-2"), (3, 6), 7)),
    ("burnt_tuft", tuft(rng, 8, BURNT, (4, 9))),
    ("reed_sprig", tuft(rng, 4, ("rot-0", "rot-1", "leather-2"), (8, 13), 3)),
    ("pebbles", stones(rng, 3, ("ash-0", "ash-1", "ash-2"))),
    ("pebbles", stones(rng, 5, ("ash-0", "ash-1", "ash-2"))),
    ("pebbles", stones(rng, 2, ("void-3", "ash-0", "ash-1"))),
    ("frost_pebbles", stones(rng, 4, ("steel-0", "steel-1", "steel-2"))),
    ("twigs", twigs(rng, ("leather-0", "leather-2"))),
    ("twigs", twigs(rng, ("void-3", "leather-1"))),
    ("bone_chips", bones(rng)),
    ("bone_chips", bones(rng)),
    ("blood_splat", splat(rng, ("blood-2", "blood-3"))),
    ("blood_splat", splat(rng, ("blood-2", "blood-3", "blood-4"))),
    ("moss", patch(rng, ("rot-0", "rot-1", "rot-2"))),
    ("mushrooms", mushrooms(rng)),
    ("straw", straw(rng)),
    ("embers", embers(rng)),
    ("ash_pile", patch(rng, ("ash-0", "ash-1", "ash-2"), (4, 6))),
]


def lone_pixels(img):
    """Opaque pixels with no opaque neighbour, the orphans §2 forbids."""
    a = img.getchannel("A").load()
    near = lambda x, y: any(0 <= x + dx < S and 0 <= y + dy < S and a[x + dx, y + dy]
                            for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
    return [(x, y) for y in range(S) for x in range(S) if a[x, y] and not near(x, y)]


def main(preview_dir=None):
    rows = [[draw(Sprite(S, S), frame).image() for frame in range(FRAMES)] for _, draw in DECALS]
    for (name, _), frames in zip(DECALS, rows):
        for f, frame in enumerate(frames):
            assert not lone_pixels(frame), f"{name} frame {f} has lone pixels {lone_pixels(frame)}"
    save(sheet(rows, S, S), ART / "props/decals_hd.png", preview_dir)
    for i, (name, _) in enumerate(DECALS):
        print(i, name)


if __name__ == "__main__":
    main(*sys.argv[1:])
