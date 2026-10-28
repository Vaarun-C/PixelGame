"""Generates placeholder props for every biome. Each sheet is one row of variants.
Usage: .venv/bin/python tools/gen_placeholder_props.py [preview_dir]

Ground contact (the prop's anchor) is 4px above the bottom edge: y=28 on 32px sprites, y=60 on 64px.
Sheet order must match PROPS in src/props.js."""
import sys
from pathlib import Path
from pixel import Sprite, save, sheet

OUT = Path(__file__).resolve().parent.parent / "art/props"


def finished(*sprites):
    return [s.finish().image() for s in sprites]


def mound(s, x, y):
    s.rect(x - 3, y, x + 4, y + 1, "leather-1")
    s.rect(x - 2, y - 1, x + 3, y - 1, "leather-2")


def blood_pool(s, cx, cy, rx, ry):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1 and s.empty(x, y):
                s.dot(x, y, "blood-1" if d > 0.55 else "blood-2")


def stuck_blade(s, x, top, length, lean, width=3, rust=()):
    for i in range(length):
        cx = x + round(lean * i / length)
        s.rect(cx, top + i, cx + width - 1, top + i, "steel-2")
    for dx, dy in rust:
        s.dot(x + round(lean * dy / length) + dx, top + dy, "blood-3")


def hilt(s, x, top, guard=7):
    s.rect(x, top - 7, x + 2, top - 6, "steel-2")
    s.rect(x + 1, top - 5, x + 1, top - 2, "leather-1")
    s.rect(x + 1 - guard // 2, top - 1, x + 1 + guard // 2, top - 1, "steel-1")


def axe_head(s, x, y, flip=False):
    """Crescent axe head with its back edge at x, centred on y."""
    spans = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 4), (0, 4), (0, 3), (0, 2), (0, 1)]
    for i, (a, b) in enumerate(spans):
        x0, x1 = (x - b, x - a) if flip else (x + a, x + b)
        s.rect(x0, y - 4 + i, x1, y - 4 + i, "steel-2")


def bearded_axe(s, x, handle_y):
    """Flat-lying axe head above a horizontal handle ending at x."""
    s.rows(handle_y - 7, [(x - 1, x + 1), (x - 2, x + 2), (x - 2, x + 3), (x - 2, x + 3), (x - 1, x + 3),
                          (x, x + 2), (x, x + 1), (x, x + 1)], "steel-2")


def weapons_stuck():
    sword = Sprite(32, 32)
    hilt(sword, 14, 10)
    stuck_blade(sword, 14, 10, 18, 1, rust=((1, 6), (0, 12), (2, 14)))
    mound(sword, 15, 28)

    snapped = Sprite(32, 32)
    stuck_blade(snapped, 15, 18, 10, 2, rust=((1, 3),))
    snapped.dot(15, 17, "steel-2")
    snapped.dot(17, 16, "steel-2")
    mound(snapped, 17, 28)

    great = Sprite(32, 32)
    hilt(great, 15, 7, guard=9)
    stuck_blade(great, 14, 7, 21, -2, width=5, rust=((1, 4), (3, 9), (2, 15)))
    great.rect(19, 6, 20, 12, "blood-2")
    great.rect(20, 13, 20, 14, "blood-1")
    mound(great, 14, 28)

    dagger = Sprite(32, 32)
    hilt(dagger, 15, 19, guard=5)
    stuck_blade(dagger, 15, 19, 8, 0, width=2)
    mound(dagger, 16, 28)

    axe = Sprite(32, 32)
    axe.line(14, 24, 22, 6, "leather-1", 2)
    axe_head(axe, 13, 24, flip=True)
    axe.rect(21, 5, 23, 6, "steel-1")
    mound(axe, 12, 28)

    spear = Sprite(32, 32)
    spear.line(12, 27, 20, 3, "leather-2")
    spear.rect(19, 6, 22, 9, "blood-2")
    spear.rect(21, 10, 22, 11, "blood-1")
    spear.rect(11, 25, 13, 27, "steel-1")
    mound(spear, 12, 28)
    return finished(sword, snapped, great, dagger, axe, spear)


def weapons_flat():
    sword = Sprite(32, 32)
    sword.line(5, 25, 20, 16, "steel-2", 2)
    sword.line(20, 13, 23, 18, "steel-1")
    sword.line(23, 15, 26, 13, "leather-1", 2)
    sword.rect(27, 12, 28, 13, "steel-2")
    sword.dot(11, 22, "blood-3")

    axe = Sprite(32, 32)
    axe.rect(4, 21, 24, 22, "leather-1")
    bearded_axe(axe, 22, 21)
    axe.rect(3, 21, 4, 22, "steel-1")

    dagger = Sprite(32, 32)
    dagger.line(9, 23, 17, 19, "steel-2", 2)
    dagger.line(18, 17, 19, 21, "steel-1")
    dagger.line(20, 19, 22, 18, "leather-1", 2)

    mace = Sprite(32, 32)
    mace.line(5, 25, 17, 19, "leather-1", 2)
    mace.ellipse(21, 17, 3, 3, "steel-1")
    for x, y in ((21, 13), (25, 17), (21, 21), (18, 15), (24, 14)):
        mace.dot(x, y, "steel-2")

    spear = Sprite(32, 32)
    spear.line(3, 24, 13, 22, "leather-2")
    spear.line(16, 21, 25, 19, "leather-2")
    spear.rows(17, [(26, 26), (26, 28), (26, 29), (26, 28), (26, 26)], "steel-2")
    return finished(sword, axe, dagger, mace, spear)


def knight_body(s):
    s.rows(15, [(9, 20), (8, 21), (8, 21), (8, 21), (8, 21), (9, 20), (9, 20), (10, 19)], "ash-0")
    s.rect(10, 16, 18, 21, "steel-1")
    s.rect(13, 16, 13, 21, "steel-2")
    s.rows(15, [(4, 8), (3, 9), (3, 9), (3, 9), (4, 8)], "steel-1")
    s.rect(4, 17, 6, 17, "void-0")
    s.rect(20, 16, 27, 17, "void-3")
    s.rect(20, 20, 26, 21, "void-3")
    s.rect(27, 15, 28, 18, "leather-1")
    s.rect(26, 19, 27, 22, "leather-1")
    s.rect(11, 23, 16, 24, "leather-1")
    s.rect(17, 23, 18, 24, "flesh-1")


def cloaked_body(s):
    s.rows(16, [(8, 22), (7, 23), (7, 24), (7, 24), (8, 23), (9, 22)], "ash-1")
    s.rows(16, [(3, 7), (2, 8), (2, 8), (3, 7)], "ash-0")
    s.rect(4, 17, 5, 18, "flesh-0")
    s.rect(24, 17, 27, 18, "leather-0")
    s.rect(23, 20, 27, 21, "leather-0")


def bodies():
    knight = Sprite(32, 32)
    knight_body(knight)

    archer = Sprite(32, 32)
    cloaked_body(archer)
    archer.rect(15, 10, 15, 17, "leather-2")
    archer.rect(14, 9, 16, 10, "bone-0")
    archer.rect(19, 12, 19, 17, "leather-2")
    archer.rect(18, 11, 20, 12, "bone-0")

    bones = Sprite(32, 32)
    bones.rows(16, [(4, 7), (3, 8), (3, 8), (4, 7)], "bone-0")
    bones.dot(4, 17, "void-0")
    bones.dot(6, 17, "void-0")
    bones.rect(9, 18, 20, 18, "bone-0")
    for x in range(11, 19, 2):
        bones.rect(x, 16, x, 21, "bone-0")
    bones.rect(13, 15, 17, 17, "steel-1")
    bones.dot(15, 16, "blood-3")
    bones.rect(21, 17, 27, 17, "bone-0")
    bones.rect(21, 20, 26, 20, "bone-0")
    bones.rect(9, 22, 13, 22, "bone-0")

    gripping = Sprite(32, 32)
    knight_body(gripping)
    gripping.rect(19, 22, 19, 27, "steel-1")
    gripping.rect(20, 24, 30, 25, "steel-2")

    axeman = Sprite(32, 32)
    cloaked_body(axeman)
    axeman.rect(12, 22, 16, 23, "ash-0")
    axeman.rect(17, 22, 18, 23, "flesh-1")
    axeman.rect(15, 25, 28, 25, "leather-1")
    bearded_axe(axeman, 26, 25)

    sprites = [knight, archer, bones, gripping, axeman]
    for s in sprites:
        s.finish()
    blood_pool(knight, 15, 22, 9, 4)
    blood_pool(archer, 14, 23, 8, 3)
    blood_pool(gripping, 13, 22, 8, 4)
    blood_pool(axeman, 13, 23, 9, 3)
    return [s.image() for s in sprites]


def rocks():
    stones = Sprite(32, 32)
    stones.ellipse(12, 23, 3, 2, "ash-1")
    stones.ellipse(19, 25, 2, 1, "ash-2")
    stones.ellipse(17, 20, 1, 1, "ash-1")

    pebbles = Sprite(32, 32)
    for x, y in ((9, 22), (14, 25), (20, 21), (23, 26), (12, 19)):
        pebbles.rect(x, y, x + 1, y, "ash-2")

    slab = Sprite(32, 32)
    slab.rows(19, [(9, 21), (8, 23), (8, 23), (9, 22), (10, 21)], "ash-1")
    slab.line(13, 19, 17, 23, "ash-0")
    return finished(stones, pebbles, slab)


def boulders():
    plain = Sprite(32, 32)
    plain.ellipse(16, 20, 9, 7, "ash-1")
    plain.ellipse(14, 17, 5, 3, "ash-2")
    plain.line(18, 16, 21, 22, "ash-0")

    mossy = Sprite(32, 32)
    mossy.ellipse(16, 21, 10, 6, "ash-1")
    mossy.ellipse(13, 17, 6, 2, "rot-2")
    mossy.rect(9, 19, 11, 20, "rot-1")
    mossy.line(19, 18, 17, 24, "ash-0")
    return finished(plain, mossy)


def runestones():
    shapes = [
        [(13, 17), (12, 18), (12, 19)] + [(11, 20)] * 15 + [(10, 21)] * 4,
        [(12, 15), (11, 17), (10, 19), (10, 20)] + [(9, 21)] * 6 + [(8, 22)] * 3,
    ]
    glyphs = [["#...#", ".#.#.", "..#..", "..#..", ".#.#.", "#...#"], ["#.#.#", "#####", "..#..", ".###."]]
    sprites = []
    for lit in (True, False):
        for i, (spans, glyph) in enumerate(zip(shapes, glyphs)):
            s = Sprite(32, 32)
            top = 29 - len(spans)
            s.rows(top, spans, "ash-1")
            s.finish()
            s.pattern(14, top + 5, glyph, "rune-pale-mid" if lit else "ash-0")
            if lit:
                s.dot(16, top + 7, "rune-pale-core")
            sprites.append(s.image())
    return sprites


def stump_sprites():
    stump = Sprite(32, 32)
    stump.rows(19, [(11, 21)] * 8, "leather-1")
    stump.ellipse(16, 18, 5, 2, "leather-2")
    stump.ellipse(16, 18, 2, 1, "leather-3")
    stump.rect(8, 26, 10, 27, "leather-1")
    stump.rect(22, 25, 24, 27, "leather-1")

    split = Sprite(32, 32)
    split.rows(14, [(15, 16), (14, 17), (13, 18), (12, 19), (12, 20)] + [(11, 21)] * 10, "leather-1")
    split.line(16, 14, 16, 22, "void-3")
    split.rect(21, 26, 24, 27, "leather-1")
    return [stump, split]


def stumps():
    return finished(*stump_sprites())


def tree_sprites():
    twisted = Sprite(64, 64)
    twisted.rows(52, [(29, 34)] * 6 + [(27, 36), (25, 38), (23, 40)], "leather-1")
    twisted.line(31, 52, 29, 26, "leather-1", 4)
    twisted.line(30, 34, 18, 20, "leather-1", 2)
    twisted.line(19, 21, 12, 18, "leather-1")
    twisted.line(18, 20, 17, 10, "leather-1")
    twisted.line(30, 28, 44, 14, "leather-1", 2)
    twisted.line(44, 14, 52, 12, "leather-1")
    twisted.line(43, 15, 45, 5, "leather-1")
    twisted.line(30, 26, 32, 8, "leather-1", 2)
    twisted.line(32, 9, 27, 3, "leather-1")

    broken = Sprite(64, 64)
    broken.rows(54, [(28, 35)] * 4 + [(26, 37), (24, 39)], "leather-1")
    broken.rect(28, 30, 35, 53, "leather-1")
    for x, top in ((28, 27), (30, 30), (32, 25), (34, 29)):
        broken.rect(x, top, x + 1, 30, "leather-1")
    broken.line(36, 40, 44, 34, "leather-1", 2)
    broken.line(8, 58, 24, 54, "leather-1", 3)

    hanging = Sprite(64, 64)
    hanging.rows(52, [(28, 33)] * 6 + [(26, 35), (24, 37), (22, 39)], "leather-1")
    hanging.line(30, 52, 36, 22, "leather-1", 4)
    hanging.line(37, 24, 18, 14, "leather-1", 2)
    hanging.line(38, 22, 50, 10, "leather-1", 2)
    hanging.line(37, 22, 40, 6, "leather-1")
    hanging.line(22, 16, 22, 33, "leather-2")
    hanging.rows(34, [(21, 23), (20, 20), (24, 24), (21, 23)], "leather-2")
    return [twisted, broken, hanging]


def trees():
    return finished(*tree_sprites())


def shields():
    round_ = Sprite(32, 32)
    round_.ellipse(16, 21, 8, 5, "steel-1")
    round_.ellipse(16, 21, 6, 4, "leather-2")
    round_.ellipse(16, 21, 1, 1, "steel-2")
    round_.line(10, 18, 14, 22, "void-1")
    round_.rows(22, [(20, 23), (21, 24), (22, 24)], "leather-1")

    kite = Sprite(32, 32)
    kite.rows(14, [(10, 20), (10, 20), (10, 20), (11, 19), (11, 19), (12, 18), (13, 17), (14, 16), (15, 15)], "blood-2")
    kite.rect(14, 14, 16, 20, "bone-0")
    kite.line(19, 10, 16, 17, "leather-2")
    kite.rect(19, 9, 20, 10, "bone-0")

    pile = Sprite(32, 32)
    pile.ellipse(12, 22, 6, 4, "leather-2")
    pile.ellipse(12, 22, 1, 1, "steel-2")
    pile.ellipse(20, 19, 6, 4, "steel-1")
    pile.ellipse(20, 19, 4, 2, "blood-2")
    return finished(round_, kite, pile)


def spears():
    cluster = Sprite(32, 32)
    cluster.line(11, 28, 7, 6, "leather-2")
    cluster.line(16, 28, 17, 3, "leather-2")
    cluster.line(21, 28, 25, 9, "leather-2")
    cluster.rect(18, 5, 21, 9, "blood-2")
    cluster.rect(20, 10, 21, 11, "blood-1")
    mound(cluster, 16, 28)

    broken = Sprite(32, 32)
    broken.line(12, 28, 10, 13, "leather-2")
    broken.line(19, 28, 21, 18, "leather-2")
    broken.dot(22, 17, "leather-2")
    broken.dot(9, 12, "leather-2")
    broken.dot(11, 11, "leather-2")
    mound(broken, 15, 28)
    return finished(cluster, broken)

def crates():
    crate = Sprite(32, 32)
    crate.rect(9, 16, 22, 27, "leather-2")
    crate.rows(12, [(13, 25), (12, 24), (11, 23), (10, 22)], "leather-3")
    crate.rect(23, 14, 25, 25, "leather-1")
    for y in (19, 23):
        crate.rect(9, y, 22, y, "leather-1")
    crate.line(9, 16, 22, 27, "leather-1")

    smashed = Sprite(32, 32)
    smashed.rect(9, 18, 22, 27, "leather-2")
    smashed.rect(10, 18, 21, 20, "void-1")
    for x, top in ((9, 15), (13, 17), (17, 16), (21, 15)):
        smashed.rect(x, top, x + 1, 18, "leather-2")
    smashed.line(23, 26, 28, 24, "leather-1")

    barrel = Sprite(32, 32)
    barrel.rows(13, [(12, 19), (11, 20)] + [(10, 21)] * 11 + [(11, 20), (12, 19)], "leather-2")
    barrel.ellipse(15, 14, 4, 1, "leather-1")
    for y in (16, 23):
        barrel.rect(10, y, 21, y, "steel-1")
    return finished(crate, smashed, barrel)


def wheel(s, cx, cy, r):
    s.ellipse(cx, cy, r, r, "leather-1")
    s.ellipse(cx, cy, r - 2, r - 2, "void-2")
    s.line(cx - r + 1, cy, cx + r - 1, cy, "leather-1")
    s.line(cx, cy - r + 1, cx, cy + r - 1, "leather-1")


def carts():
    wrecked = Sprite(64, 64)
    wrecked.rect(14, 38, 46, 50, "leather-2")
    wrecked.rows(32, [(18, 50), (17, 49), (16, 48), (15, 47), (14, 46), (14, 46)], "leather-3")
    for x in (22, 30, 38):
        wrecked.rect(x, 38, x, 50, "leather-1")
    wrecked.rect(19, 30, 21, 33, "void-1")
    wheel(wrecked, 20, 52, 7)
    wrecked.ellipse(50, 58, 7, 2, "leather-1")
    wrecked.line(46, 46, 60, 54, "leather-1", 2)

    overturned = Sprite(64, 64)
    overturned.rows(46, [(14, 40), (12, 44), (10, 46)] + [(10, 48)] * 10, "leather-2")
    overturned.rect(10, 56, 48, 58, "leather-1")
    for x in (18, 26, 34, 42):
        overturned.rect(x, 49, x, 55, "leather-1")
    wheel(overturned, 16, 42, 6)
    wheel(overturned, 44, 40, 6)
    overturned.rect(52, 57, 56, 59, "leather-2")
    overturned.rect(4, 58, 8, 59, "leather-3")
    return finished(wrecked, overturned)


def stakes():
    skull = Sprite(32, 32)
    skull.rect(15, 10, 16, 28, "leather-1")
    skull.rows(5, [(14, 17), (13, 18), (13, 18), (13, 18), (14, 17)], "bone-0")
    skull.dot(14, 7, "void-0")
    skull.dot(17, 7, "void-0")

    helm = Sprite(32, 32)
    helm.line(16, 28, 14, 10, "leather-1", 2)
    helm.rows(5, [(13, 16), (12, 17), (12, 17), (12, 17), (12, 17)], "steel-1")
    helm.rect(13, 7, 16, 7, "void-0")
    helm.rect(17, 12, 18, 18, "blood-2")

    cluster = Sprite(32, 32)
    for x, top in ((10, 12), (15, 8), (20, 14)):
        cluster.rect(x, top, x + 1, 28, "leather-1")
        cluster.dot(x, top - 1, "leather-1")
    cluster.rows(9, [(19, 22), (18, 23), (19, 22)], "bone-0")
    return finished(skull, helm, cluster)


def gibbets():
    cage = Sprite(64, 64)
    cage.rect(22, 10, 25, 60, "leather-1")
    cage.rect(22, 9, 46, 11, "leather-1")
    cage.line(25, 20, 34, 11, "leather-1", 2)
    cage.rect(43, 12, 43, 22, "steel-1")
    for x in range(37, 50, 3):
        cage.rect(x, 24, x, 42, "steel-1")
    cage.rect(37, 23, 49, 23, "steel-1")
    cage.rect(37, 43, 49, 43, "steel-1")
    cage.rows(36, [(41, 44), (40, 45), (41, 44)], "bone-0")
    cage.rect(19, 58, 28, 60, "leather-2")

    noose = Sprite(64, 64)
    noose.rect(22, 10, 25, 60, "leather-1")
    noose.rect(22, 9, 46, 11, "leather-1")
    noose.line(25, 20, 34, 11, "leather-1", 2)
    noose.rect(43, 12, 43, 30, "leather-2")
    noose.rows(31, [(42, 44), (41, 41), (45, 45), (41, 41), (45, 45), (42, 44)], "leather-2")
    noose.rect(19, 58, 28, 60, "leather-2")
    return finished(cage, noose)


def banners():
    standing = Sprite(64, 64)
    standing.rect(31, 8, 32, 60, "leather-1")
    standing.rect(24, 9, 39, 10, "leather-1")
    hem = [36, 38, 35, 39, 37, 40, 36, 38, 35, 37, 39, 36, 38, 34]
    for i, bottom in enumerate(hem):
        standing.rect(25 + i, 11, 25 + i, bottom, "blood-2")
    standing.line(28, 18, 32, 24, "bone-0")
    standing.line(36, 18, 32, 24, "bone-0")
    standing.rect(29, 59, 34, 60, "leather-2")

    fallen = Sprite(64, 64)
    fallen.line(14, 60, 40, 22, "leather-1", 2)
    fallen.rows(24, [(40, 50), (41, 51), (40, 53), (39, 52), (41, 54), (42, 52), (43, 55), (44, 53),
                     (45, 56), (45, 54), (46, 57)], "blood-2")
    fallen.line(44, 30, 50, 34, "bone-0")
    return finished(standing, fallen)


def remains():
    crow_bones = Sprite(32, 32)
    crow_bones.rows(21, [(8, 11), (7, 12), (8, 11)], "bone-0")
    crow_bones.rect(13, 23, 22, 23, "bone-0")
    for x in (15, 18, 21):
        crow_bones.rect(x, 21, x, 25, "bone-0")
    crow_bones.ellipse(19, 17, 3, 2, "void-2")
    crow_bones.rect(15, 16, 16, 17, "void-2")
    crow_bones.dot(14, 17, "ash-3")
    crow_bones.rect(19, 19, 19, 20, "ash-2")
    crow_bones.rect(21, 19, 21, 20, "ash-2")

    picking = Sprite(32, 32)
    picking.rows(20, [(8, 22), (7, 23), (8, 22), (9, 21)], "ash-0")
    picking.rect(10, 21, 14, 22, "flesh-0")
    picking.ellipse(16, 15, 3, 2, "void-2")
    picking.rect(12, 16, 13, 17, "void-2")
    picking.dot(11, 18, "ash-3")
    picking.rect(16, 17, 16, 19, "ash-2")
    return finished(crow_bones, picking)


# --- Swamp ---


def swamp_trees():
    mangrove = Sprite(64, 64)
    for x0, x1 in ((20, 29), (26, 30), (44, 35), (38, 34)):
        mangrove.line(x0, 60, x1, 46, "leather-0", 2)
    mangrove.rect(29, 20, 35, 47, "leather-0")
    mangrove.line(30, 26, 14, 14, "leather-0", 2)
    mangrove.line(34, 24, 52, 12, "leather-0", 2)
    mangrove.line(32, 21, 33, 6, "leather-0", 2)

    leaning = Sprite(64, 64)
    leaning.rows(54, [(26, 34)] * 4 + [(24, 36), (22, 38), (20, 40)], "leather-0")
    leaning.line(30, 54, 40, 18, "leather-0", 4)
    leaning.line(40, 20, 52, 14, "leather-0", 2)
    leaning.line(39, 24, 24, 16, "leather-0", 2)
    for s in (mangrove, leaning):
        s.finish()
    for x, top, length in ((16, 16, 9), (21, 19, 6), (46, 15, 10), (51, 13, 6), (33, 9, 5)):
        mangrove.rect(x, top, x, top + length, "rot-2")
    for x, top, length in ((26, 18, 8), (47, 17, 9), (51, 15, 5)):
        leaning.rect(x, top, x, top + length, "rot-2")
    return [mangrove.image(), leaning.image()]


def reeds():
    sprites = []
    for bases in ((10, 13, 16, 19, 22), (12, 15, 18), (9, 14, 20, 23)):
        s = Sprite(32, 32)
        for i, x in enumerate(bases):
            top = 8 + (i * 5) % 9
            s.line(x, 28, x + (i % 3) - 1, top, "rot-2")
            if i % 2 == 0:
                s.rect(x + (i % 3) - 1, top, x + (i % 3), top + 3, "leather-1")
        sprites.append(s)
    return finished(*sprites)


def drowned_chests():
    sprites = []
    for tilt in (0, 2):
        s = Sprite(32, 32)
        s.rows(14 + tilt, [(10, 21), (9, 22), (9, 22)], "leather-3")
        s.rect(9, 17 + tilt, 22, 25, "leather-2")
        s.rect(9, 19 + tilt, 22, 19 + tilt, "steel-1")
        s.rect(15, 18 + tilt, 16, 21 + tilt, "steel-2")
        s.finish()
        for y, (x0, x1) in zip(range(25, 29), ((6, 25), (5, 26), (6, 25), (8, 23))):
            s.rect(x0, y, x1, y, "void-3")
        s.rect(7, 25, 10, 25, "rot-1")
        s.rect(20, 27, 23, 27, "rot-1")
        sprites.append(s.image())
    return sprites


# --- Ruins ---


def pillars():
    standing = Sprite(64, 64)
    standing.rect(24, 10, 39, 13, "ash-2")
    standing.rect(26, 14, 37, 55, "ash-1")
    standing.rect(24, 56, 39, 60, "ash-2")
    for x in (29, 32, 35):
        standing.rect(x, 15, x, 54, "ash-0")

    broken = Sprite(64, 64)
    broken.rows(30, [(26, 28), (26, 31), (26, 33), (26, 37)], "ash-1")
    broken.rect(26, 34, 37, 55, "ash-1")
    broken.rect(24, 56, 39, 60, "ash-2")
    for x in (29, 32, 35):
        broken.rect(x, 35, x, 54, "ash-0")
    broken.ellipse(46, 58, 4, 2, "ash-1")

    toppled = Sprite(64, 64)
    toppled.rect(8, 48, 50, 57, "ash-1")
    for y in (50, 53):
        toppled.rect(9, y, 49, y, "ash-0")
    toppled.rect(51, 46, 55, 59, "ash-2")
    toppled.ellipse(5, 57, 3, 2, "ash-1")
    return finished(standing, broken, toppled)


def walls():
    tall = Sprite(64, 64)
    tops = [30, 28, 27, 27, 24, 22, 22, 25, 26, 30, 33, 33, 36, 40]
    for i, top in enumerate(tops):
        tall.rect(6 + i * 4, top, 9 + i * 4, 59, "ash-1")
    tall.rows(38, [(26, 33), (25, 34)] + [(25, 34)] * 9, "void-1")
    for y in range(32, 59, 5):
        tall.rect(6, y, 61, y, "ash-0")

    low = Sprite(64, 64)
    low_tops = [48, 46, 45, 47, 44, 46, 49, 50, 48, 51]
    for i, top in enumerate(low_tops):
        low.rect(10 + i * 4, top, 13 + i * 4, 59, "ash-1")
    low.rect(10, 53, 49, 53, "ash-0")
    sprites = [tall, low]
    for s in sprites:
        s.finish()
    low.rect(14, 45, 22, 46, "rot-2")
    tall.rect(30, 22, 36, 23, "rot-2")
    return [s.image() for s in sprites]


def statues():
    headless = Sprite(64, 64)
    headless.rect(22, 50, 41, 60, "ash-2")
    headless.rows(16, [(28, 35), (25, 38)] + [(26, 37)] * 14 + [(25, 38)] * 4 + [(24, 39)] * 14, "ash-1")
    headless.rect(31, 18, 32, 48, "ash-0")
    headless.line(26, 20, 22, 34, "ash-1", 3)

    head = Sprite(64, 64)
    head.ellipse(30, 48, 14, 11, "ash-1")
    head.rect(20, 44, 25, 47, "void-0")
    head.rect(33, 44, 38, 47, "void-0")
    head.rect(28, 50, 30, 53, "ash-0")
    head.line(24, 56, 36, 56, "ash-0")
    head.line(40, 38, 44, 50, "ash-0")
    return finished(headless, head)


def reliquaries():
    sprites = []
    for lit in (True, False):
        s = Sprite(32, 32)
        s.rect(8, 17, 23, 27, "ash-2")
        s.rect(8, 21, 23, 21, "ash-1")
        if lit:
            s.rows(13, [(9, 22), (8, 23), (8, 23), (8, 23)], "steel-1")
        else:
            s.rows(11, [(14, 27), (13, 28), (14, 27)], "steel-1")
            s.rect(9, 17, 22, 18, "void-1")
        s.finish()
        if lit:
            for x, y in ((15, 14), (16, 15), (14, 15), (15, 16)):
                s.dot(x, y, "rune-pale-mid")
            s.dot(15, 15, "rune-pale-core")
        sprites.append(s.image())
    return sprites


def rubble():
    sprites = []
    for stones in (((10, 22, 3, 2), (17, 24, 2, 2), (14, 19, 2, 1)),
                   ((8, 24, 2, 1), (13, 22, 4, 3), (21, 25, 2, 1)),
                   ((12, 21, 2, 2), (19, 22, 3, 2), (16, 26, 2, 1), (9, 26, 1, 1))):
        s = Sprite(32, 32)
        for cx, cy, rx, ry in stones:
            s.ellipse(cx, cy, rx, ry, "ash-1")
        sprites.append(s)
    return finished(*sprites)


# --- Ashen forest ---


def charred(sprites):
    for s in sprites:
        s.recolor(colors={"leather-1": "void-3", "leather-2": "void-2", "leather-3": "ash-0"})
        s.finish()
        wood = [(x, y) for y in range(s.h) for x in range(s.w) if s.px[y][x] == "void-3"]
        for x, y in wood[7::37]:
            s.dot(x, y, "ember-1")
    return [s.image() for s in sprites]


def charred_trees():
    return charred(tree_sprites())


def charred_stumps():
    return charred(stump_sprites())


def embers():
    sprites = []
    for cells in (((16, 23, 5, 2),), ((12, 22, 3, 2), (20, 24, 3, 1))):
        s = Sprite(32, 32)
        for cx, cy, rx, ry in cells:
            s.ellipse(cx, cy, rx, ry, "void-2")
        s.finish()
        for x, y, c in ((14, 22, "ember-1"), (17, 23, "ember-2"), (12, 23, "ember-1"), (19, 24, "ember-0"),
                        (21, 24, "ember-1"), (16, 22, "ash-2")):
            if s.px[y][x] == "void-2":
                s.dot(x, y, c)
        sprites.append(s.image())
    return sprites


def pyres():
    lit = Sprite(64, 64)
    for y in (52, 48, 44):
        lit.line(14, y + 4, 50, y, "leather-0", 3)
        lit.line(14, y, 50, y + 4, "leather-0", 3)
    lit.rows(38, [(22, 40), (20, 42), (22, 40)], "void-3")
    lit.rect(18, 38, 21, 40, "bone-0")

    spent = Sprite(64, 64)
    spent.ellipse(32, 54, 16, 5, "ash-1")
    spent.ellipse(30, 52, 8, 3, "ash-2")
    spent.line(18, 56, 26, 53, "void-3", 2)
    spent.rect(38, 51, 40, 52, "bone-0")
    for s in (lit, spent):
        s.finish()
    for x, y, c in ((26, 36, "ember-2"), (30, 35, "ember-3"), (34, 36, "ember-2"), (28, 34, "ember-1"),
                    (32, 33, "ember-1"), (24, 47, "ember-1"), (40, 50, "ember-1"), (36, 45, "ember-2")):
        lit.dot(x, y, c)
    spent.dot(33, 52, "ember-0")
    return [lit.image(), spent.image()]


# --- Frozen pass ---


def frozen_trees():
    sprites = tree_sprites()[:2]
    for s in sprites:
        s.recolor(colors={"leather-1": "ash-1", "leather-2": "ash-2"})
        s.finish()
        s.snowcap()
    return [s.image() for s in sprites]


def cairns():
    sprites = []
    for stack in (((16, 25, 6, 3), (16, 20, 5, 2), (16, 16, 3, 2), (16, 13, 2, 1)),
                  ((15, 25, 7, 3), (17, 20, 4, 2), (15, 16, 3, 2))):
        s = Sprite(32, 32)
        for cx, cy, rx, ry in stack:
            s.ellipse(cx, cy, rx, ry, "ash-1")
            s.rect(cx - rx + 1, cy + ry, cx + rx - 1, cy + ry, "ash-0")
        s.finish()
        s.snowcap()
        sprites.append(s.image())
    return sprites


def ice_tombs():
    sprites = []
    for whole in (True, False):
        for shape in range(2):
            s = Sprite(32, 32)
            if whole:
                s.rows(9 + shape * 3, [(10, 21)] * (19 - shape * 3), "steel-2")
                s.rows(14 + shape * 3, [(14, 17), (13, 18), (14, 17)] + [(13, 18)] * (8 - shape * 2), "void-3")
            else:
                for cx, cy, h in ((11, 27, 6), (16, 27, 9), (21, 27, 5)):
                    s.rows(cy - h, [(cx - 1, cx + 1)] * h, "steel-2")
                s.rect(13, 24, 19, 27, "void-3")
            s.finish()
            if whole:
                s.line(11, 10 + shape * 3, 12, 14 + shape * 3, "steel-3")
            sprites.append(s.image())
    return sprites


def ice_spikes():
    sprites = []
    for spikes in (((12, 12, 3), (17, 8, 3), (21, 16, 2)), ((14, 10, 3), (19, 15, 2))):
        s = Sprite(32, 32)
        for cx, top, half in spikes:
            for y in range(top, 29):
                w = round(half * (y - top) / (28 - top))
                s.rect(cx - w, y, cx + w, y, "steel-2")
        s.finish()
        for cx, top, _ in spikes:
            s.line(cx, top + 2, cx - 1, top + 7, "steel-3")
        sprites.append(s.image())
    return sprites


# --- Village ---


def thatch(s, x0, x1, peak, eave, roof, streak):
    """Triangular thatched roof from the peak row down to the eave row, spanning x0..x1 at the eave."""
    rows = eave - peak
    mid = (x0 + x1) // 2
    for i in range(rows + 1):
        half = round((x1 - x0) / 2 * i / rows)
        s.rect(mid - half, peak + i, mid + half, peak + i, roof)
    for i in range(0, rows, 3):
        s.dot(mid - i // 2 + (i % 5), peak + i + 1, streak)


def plank_walls(s, x0, x1, top, bottom=59, color="leather-2"):
    s.rect(x0, top, x1, bottom, color)
    for x in range(x0 + 2, x1, 4):
        s.rect(x, top + 1, x, bottom - 1, "leather-1")


def huts():
    thatched = Sprite(64, 64)
    plank_walls(thatched, 14, 50, 36)
    thatched.rect(28, 45, 35, 59, "void-1")
    thatch(thatched, 6, 57, 14, 38, "leather-3", "leather-2")

    mossy = Sprite(64, 64)
    plank_walls(mossy, 16, 48, 38)
    mossy.rect(22, 47, 28, 59, "void-1")
    mossy.rect(38, 44, 42, 48, "void-1")
    thatch(mossy, 8, 55, 16, 40, "rot-2", "rot-1")

    longhouse = Sprite(64, 64)
    plank_walls(longhouse, 4, 59, 40)
    longhouse.rect(40, 47, 46, 59, "void-1")
    longhouse.rows(24, [(14, 49), (11, 52), (8, 55), (6, 57), (4, 59), (2, 61)] + [(1, 62)] * 12, "leather-3")
    for x in range(6, 60, 6):
        longhouse.rect(x, 26, x, 41, "leather-2")
    longhouse.rect(12, 44, 18, 48, "void-1")

    stone = Sprite(64, 64)
    stone.rect(14, 48, 50, 59, "ash-1")
    for y, off in ((51, 0), (55, 3)):
        for x in range(14 + off, 50, 7):
            stone.rect(x, y, x, y + 3, "ash-0")
    plank_walls(stone, 14, 50, 34, 47)
    stone.rect(29, 46, 35, 59, "void-1")
    thatch(stone, 7, 57, 12, 36, "leather-3", "leather-1")
    stone.rect(42, 8, 46, 22, "ash-1")

    ruined = Sprite(64, 64)
    plank_walls(ruined, 14, 50, 40)
    for x, top in ((14, 36), (20, 38), (44, 34), (48, 37)):
        ruined.rect(x, top, x + 2, 40, "leather-2")
    ruined.rect(26, 46, 33, 59, "void-1")
    thatch(ruined, 6, 34, 20, 40, "leather-3", "leather-2")
    ruined.line(34, 22, 54, 40, "leather-1", 2)
    ruined.line(40, 26, 40, 40, "leather-1")

    sprites = [thatched, mossy, longhouse, stone, ruined]
    for sp in sprites:
        sp.finish()
    for x, y in ((44, 5), (45, 2), (43, 0)):
        stone.dot(x, y, "ash-3")
    return [sp.image() for sp in sprites]


def log_row(s, tops, x0=0):
    for i, top in enumerate(tops):
        x = x0 + i * 4
        s.rect(x, top + 2, x + 3, 28, "leather-1")
        s.rect(x + 1, top, x + 2, top + 1, "leather-1")


def palisade():
    """Variants 0-3 run east-west, 4-5 north-south, 6 is a torch post."""
    plain = Sprite(32, 32)
    log_row(plain, [6 + (x * 7) % 5 for x in range(0, 32, 4)])
    plain.rect(0, 20, 31, 20, "leather-0")

    shield = Sprite(32, 32)
    log_row(shield, [4, 8, 3, 7, 5, 9, 4, 6])
    shield.rect(0, 22, 31, 22, "leather-0")
    shield.ellipse(16, 16, 4, 4, "blood-2")
    shield.ellipse(16, 16, 1, 1, "steel-2")

    repaired = Sprite(32, 32)
    log_row(repaired, [7, 6, 8])
    repaired.rect(12, 12, 31, 28, "leather-2")
    for y in (15, 20, 25):
        repaired.rect(12, y, 31, y, "leather-1")
    repaired.rows(6, [(22, 25), (21, 26), (22, 25)], "bone-0")
    repaired.rect(23, 9, 24, 11, "leather-1")

    broken = Sprite(32, 32)
    log_row(broken, [6, 9, 18, 20, 16, 8, 7, 10])
    broken.rect(0, 22, 7, 22, "leather-0")
    broken.rect(20, 22, 31, 22, "leather-0")

    side = Sprite(32, 32)
    side.rect(12, 0, 19, 31, "leather-1")
    for y in range(3, 32, 8):
        side.rect(12, y, 19, y, "leather-0")

    braced = Sprite(32, 32)
    braced.rect(12, 0, 19, 31, "leather-1")
    braced.line(19, 4, 25, 26, "leather-2", 2)
    for y in range(5, 32, 9):
        braced.rect(12, y, 19, y, "leather-0")

    torch = Sprite(32, 32)
    torch.rect(13, 4, 18, 28, "leather-1")
    torch.rect(12, 2, 19, 3, "leather-0")
    sprites = [plain, shield, repaired, broken, side, braced, torch]
    for sp in sprites:
        sp.finish()
    for x, y, c in ((15, 0, "ember-3"), (16, 0, "ember-2"), (14, 1, "ember-1"), (17, 1, "ember-1")):
        torch.dot(x, y, c)
    return [sp.image() for sp in sprites]

def well():
    s = Sprite(32, 32)
    s.ellipse(16, 22, 9, 5, "ash-1")
    s.ellipse(16, 21, 6, 3, "void-0")
    s.rect(7, 6, 8, 22, "leather-1")
    s.rect(23, 6, 24, 22, "leather-1")
    s.rows(3, [(10, 21), (8, 23), (6, 25)], "leather-3")
    s.rect(16, 9, 16, 16, "leather-2")
    s.finish()
    return [s.image()]


def firepit():
    s = Sprite(32, 32)
    s.ellipse(16, 23, 8, 4, "ash-1")
    s.ellipse(16, 23, 6, 3, "void-2")
    s.line(11, 24, 21, 22, "leather-0", 2)
    s.finish()
    for x, y, c in ((15, 19, "ember-3"), (16, 18, "ember-2"), (17, 20, "ember-2"), (14, 21, "ember-1"),
                    (18, 22, "ember-1"), (16, 17, "ember-1"), (16, 20, "ember-3")):
        s.dot(x, y, c)
    return [s.image()]


def stall():
    s = Sprite(64, 64)
    s.rect(14, 22, 15, 58, "leather-1")
    s.rect(48, 22, 49, 58, "leather-1")
    s.rect(12, 44, 51, 50, "leather-2")
    s.rect(12, 51, 51, 51, "leather-1")
    for i, x in enumerate(range(10, 54, 4)):
        s.rect(x, 18, x + 3, 25, "blood-2" if i % 2 else "bone-0")
    s.finish()
    for x, c in ((18, "bronze-2"), (19, "bronze-1"), (24, "steel-3"), (30, "gilt-2"), (31, "gilt-3"), (40, "bronze-2")):
        s.dot(x, 43, c)
    return [s.image()]


SHEETS = {
    "weapons_stuck": (weapons_stuck, 32),
    "weapons_flat": (weapons_flat, 32),
    "bodies": (bodies, 32),
    "rocks": (rocks, 32),
    "boulders": (boulders, 32),
    "runestones": (runestones, 32),
    "stumps": (stumps, 32),
    "trees": (trees, 64),
    "shields": (shields, 32),
    "spears": (spears, 32),
    "crates": (crates, 32),
    "carts": (carts, 64),
    "stakes": (stakes, 32),
    "gibbets": (gibbets, 64),
    "banners": (banners, 64),
    "remains": (remains, 32),
    "swamp_trees": (swamp_trees, 64),
    "reeds": (reeds, 32),
    "drowned_chests": (drowned_chests, 32),
    "pillars": (pillars, 64),
    "walls": (walls, 64),
    "statues": (statues, 64),
    "reliquaries": (reliquaries, 32),
    "rubble": (rubble, 32),
    "charred_trees": (charred_trees, 64),
    "charred_stumps": (charred_stumps, 32),
    "embers": (embers, 32),
    "pyres": (pyres, 64),
    "frozen_trees": (frozen_trees, 64),
    "cairns": (cairns, 32),
    "ice_tombs": (ice_tombs, 32),
    "ice_spikes": (ice_spikes, 32),
    "huts": (huts, 64),
    "palisade": (palisade, 32),
    "well": (well, 32),
    "firepit": (firepit, 32),
    "stall": (stall, 64),
}


def main(preview_dir=None):
    for name, (build, size) in SHEETS.items():
        save(sheet([build()], size, size), OUT / f"{name}.png", preview_dir)


if __name__ == "__main__":
    main(*sys.argv[1:])
