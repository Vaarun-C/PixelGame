"""Build the 2x battlefield prop sheets in art/props/ from the chosen drafts (one row, one column per variant).

Run from the repo root after fix_stuck.py and combine_tree.py: .venv/bin/python art/drafts/props/assemble.py
Every sprite is moved down so its lowest pixel sits 2 rows above the frame bottom, where drawProp's default
anchor (size - 4) puts the ground contact.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from pixel import COLORS, sheet, save

P = Path("art/drafts/props")
OUT = Path("art/props")
NAME = {rgb + (255,): name for name, rgb in COLORS.items()}


def load(name):
    img = Image.open(P / f"{name}.png").convert("RGBA")
    return img if name.endswith(("_fixed", "_marked")) else snap(img)


def quadrant(name, q, size=64):
    return load(name).crop(((q % 2) * size, (q // 2) * size, (q % 2) * size + size, (q // 2) * size + size))


def rotted(img, seed):
    """Waterlog a prop: moss along its top edge with drips running down, and a few planks broken into black holes."""
    rng = random.Random(seed)
    px = img.load()
    solid = lambda x, y: 0 <= x < img.width and 0 <= y < img.height and px[x, y][3]
    for x in range(img.width):
        top = next((y for y in range(img.height) if solid(x, y)), None)
        if top is None or rng.random() < 0.35:
            continue
        for y in range(top, top + 2 + rng.choice((0, 0, 1, 3, 5))):
            if solid(x, y):
                px[x, y] = COLORS["rot-2" if y == top else "rot-1" if y < top + 3 else "rot-0"] + (255,)
    for _ in range(3):
        x, y = rng.randrange(img.width), rng.randrange(img.height)
        if all(solid(x + dx, y + dy) for dx in (-2, 0, 2) for dy in (-2, 0, 2)):
            for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (1, 1)):
                px[x + dx, y + dy] = COLORS["void-0"] + (255,)
    return img


def knock_out(img, names):
    """Clear a baked backdrop and ground shadow: every pixel of these colours reachable from the frame edge."""
    px = img.load()
    w, h = img.size
    todo = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    seen = set()
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        if px[x, y][3] and not NAME.get(px[x, y], "").startswith(names):
            continue
        px[x, y] = (0, 0, 0, 0)
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return img


def sunk(img, waterline):
    """Sink a prop into an oval pool of black water, with a ripple where the prop meets it."""
    px = img.load()
    above = [x for x in range(img.width) if px[x, waterline - 1][3]]
    for y in range(waterline, img.height):
        for x in range(img.width):
            px[x, y] = (0, 0, 0, 0)
    cx, rx, ry = (above[0] + above[-1]) / 2, (above[-1] - above[0]) / 2 + 6, 6
    for y in range(waterline - ry, waterline + ry + 1):
        for x in range(img.width):
            d = ((x - cx) / rx) ** 2 + ((y - waterline) / ry) ** 2
            if d <= 1 and (y >= waterline or not px[x, y][3]):
                px[x, y] = COLORS["void-2" if d > 0.7 else "void-3"] + (255,)
    for x in range(above[0] - 1, above[-1] + 2):
        px[x, waterline] = COLORS["steel-0" if (x - above[0]) % 5 else "steel-1"] + (255,)
    return img


def strip(img, names, from_row=0):
    """Drop baked-in ground (shadow smudges, grass patches) the game draws itself."""
    for y in range(from_row, img.height):
        for x in range(img.width):
            if NAME.get(img.getpixel((x, y)), "").startswith(names):
                img.putpixel((x, y), (0, 0, 0, 0))
    return img


def recolour(img, mapping):
    for y in range(img.height):
        for x in range(img.width):
            name = NAME.get(img.getpixel((x, y)))
            if name in mapping:
                img.putpixel((x, y), COLORS[mapping[name]] + (255,))
    return img


def outline(img, above=None):
    """1 px void-1 exterior outline (ART_RULES §2), only on rows above `above` (mud mounds stay soft)."""
    rows = range(above if above is not None else img.height)
    solid = lambda x, y: 0 <= x < img.width and 0 <= y < img.height and img.getpixel((x, y))[3]
    edge = [(x, y) for y in rows for x in range(img.width)
            if not solid(x, y) and any(solid(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for xy in edge:
        img.putpixel(xy, COLORS["void-1"] + (255,))
    return img


def dim(img, above):
    """Bring near-white steel into the steel ramp so props never outshine the player; every 9th pixel stays a glint."""
    for y in range(above):
        for x in range(img.width):
            name = NAME.get(img.getpixel((x, y)))
            if name in DIM and (x + y) % 9:
                img.putpixel((x, y), COLORS[DIM[name]] + (255,))
    return img


def lit_left(img, colour, every=2):
    """Light the bark just inside the left silhouette edge on every other row (key light from the top-left)."""
    solid = lambda x, y: img.getpixel((x, y))[3]
    for y in range(0, img.height - 20, every):
        for x in range(1, img.width - 2):
            if not solid(x - 1, y) and solid(x, y) and solid(x + 1, y):
                img.putpixel((x + 1, y), COLORS[colour] + (255,))
    return img


def strip_patch(img):
    """Drop a baked ground patch (gilt/rot grass and the void-0 rim left around it), keeping figure outlines."""
    strip(img, ("gilt-", "rot-", "leather-", "flesh-"))
    px = img.load()
    for _ in range(2):
        rim = [(x, y) for y in range(img.height) for x in range(img.width) if NAME.get(px[x, y]) == "void-0"
               and not any(px[x + dx, y + dy][3] and NAME.get(px[x + dx, y + dy]) != "void-0"
                           for dx in (-1, 0, 1) for dy in (-1, 0, 1) if 0 <= x + dx < img.width and 0 <= y + dy < img.height)]
        for xy in rim:
            px[xy] = (0, 0, 0, 0)
    return drop_islands(img, 30)


def drop_orphans(img):
    """Clear pixels with no neighbour in any of the 8 directions."""
    px = img.load()
    w, h = img.size
    lone = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] and not any(
        px[x + dx, y + dy][3] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and 0 <= x + dx < w and 0 <= y + dy < h)]
    for xy in lone:
        px[xy] = (0, 0, 0, 0)
    return img


def drop_islands(img, smaller_than):
    px = img.load()
    seen = set()
    for start in [(x, y) for y in range(img.height) for x in range(img.width) if px[x, y][3]]:
        if start in seen:
            continue
        island, todo = [], [start]
        seen.add(start)
        while todo:
            x, y = todo.pop()
            island.append((x, y))
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < img.width and 0 <= ny < img.height and (nx, ny) not in seen and px[nx, ny][3]:
                    seen.add((nx, ny))
                    todo.append((nx, ny))
        if len(island) < smaller_than:
            for xy in island:
                px[xy] = (0, 0, 0, 0)
    return img


def body_mask(limbs, head, head_r):
    """A frozen body as a set of pixels: thick limbs (polyline, radius) plus a round head."""
    mask = set()
    for (x0, y0), (x1, y1), r in limbs:
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for t in range(n + 1):
            cx, cy = x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n
            mask |= {(round(cx) + dx, round(cy) + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if dx * dx + dy * dy <= r * r}
    hx, hy = head
    mask |= {(hx + dx, hy + dy) for dx in range(-head_r, head_r + 1) for dy in range(-head_r, head_r + 1) if dx * dx + dy * dy <= head_r * head_r + 1}
    return mask


LYING_BODY = [
    "  ###  ", " ##### ", "  ###  ", "       ", " ##### ", "#######", "# ### #", "# ### #", "# ### #",
    "# ### #", "  ###  ", " ## ## ", " ## ## ", " ## ## ", " ## ## ", " ## ## ", " #   # ",
]


def laid_on(template, head, along, across):
    """Pixels of a template (rows head to foot) mapped onto a slanted face spanned by two edge vectors."""
    (ax, ay), (bx, by) = along, across
    det = ax * by - ay * bx
    w = len(template[0])
    mask = set()
    for y in range(64):
        for x in range(64):
            dx, dy = x + 0.5 - head[0], y + 0.5 - head[1]
            r, c = math.floor((dx * by - dy * bx) / det), math.floor((ax * dy - ay * dx) / det + w / 2)
            if 0 <= r < len(template) and 0 <= c < w and template[r][c] == "#":
                mask.add((x, y))
    return mask


# The two ice tombs: a coffin lying down (body along its lid) and an upright slab (body standing in its face).
COFFIN_BODY = laid_on(LYING_BODY, (22, 32), (1.3, -0.95), (1.42, 0.71))
SLAB_BODY = body_mask([((36, 26), (36, 37), 2), ((35, 37), (34, 47), 1), ((37, 37), (38, 47), 1), ((34, 28), (32, 35), 1), ((38, 28), (40, 35), 1)], (36, 22), 2)


def frozen_in(tomb, mask, opened):
    """Sealed: a dark body shape inside the ice. Opened: the same shape hollowed out, ice shards at its edge."""
    img = tomb.copy()
    px = img.load()
    for x, y in mask:
        if px[x, y][3]:
            edge = any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            name = ("void-1" if edge else "void-0") if opened else ("steel-2" if edge else "steel-1")
            px[x, y] = COLORS[name] + (255,)
    if opened:  # shards of the broken ice at the tomb's foot
        bottom = img.getbbox()[3] - 3
        for x, dy in ((14, 0), (15, 0), (21, 1), (44, 0), (45, -1), (50, 1)):
            if not px[x, bottom + dy][3]:
                px[x, bottom + dy] = COLORS["steel-3"] + (255,)
    return img


def grounded(img):
    bottom = img.getbbox()[3]
    out = Image.new("RGBA", img.size)
    out.alpha_composite(img, (0, img.height - 2 - bottom))
    return out


DIM = {"bone-1": "steel-2", "bone-0": "steel-2", "steel-3": "steel-2", "ash-4": "steel-2", "ash-3": "steel-1"}
NO_EMBER = {"ember-3": "steel-2", "ember-2": "steel-2", "ember-1": "blood-2", "ember-0": "blood-1"}
stuck = [load(f"{n}_fixed") for n in ("C_sword", "stuck_greatsword", "stuck_short", "stuck_halberd")]
dim(stuck[2], 44)
outline(recolour(stuck[1], NO_EMBER), 48)
BONE_DIM = {"bone-1": "ash-4", "bone-0": "ash-3", "ash-4": "ash-3", "ash-3": "ash-2", "ash-2": "ash-1"}  # old bone, never brighter than the player
YELLOW_BONE = {"bone-1": "ash-4", "gilt-3": "ash-3", "gilt-2": "ash-3", "flesh-3": "ash-3", "flesh-2": "ash-2", "gilt-0": "leather-1"}
STRAW = {"gilt-3": "bone-0", "gilt-2": "leather-3", "gilt-1": "leather-2", "gilt-0": "leather-1"}
GRAIN = {"bronze-3": "leather-2", "flesh-3": "leather-3"}
SAND = ("flesh-3", "bronze-3", "flesh-0", "flesh-2")


def tilt(img, rows_per_px=10):
    """Lean a sprite right by shearing whole rows, so pixels stay crisp (no rotation)."""
    bottom = img.getbbox()[3]
    out = Image.new("RGBA", img.size)
    for y in range(bottom):
        out.paste(img.crop((0, y, img.width, y + 1)), ((bottom - y) // rows_per_px, y))
    return out


# Snow and ice stay under the player's brightness (§3): near-white becomes pale steel.
ICE_DIM = {"bone-1": "steel-3", "bone-0": "ash-4", "ash-4": "ash-3"}
# The searched pyre: flames and glowing coals go to ash and char.
BURNT_OUT = {"ember-3": "ash-2", "ember-2": "ash-1", "ember-1": "ash-0", "ember-0": "void-3", "blood-4": "ash-0", "blood-3": "void-3", "bone-1": "ash-2"}
tombs = [(recolour(quadrant("ashfrost_grid_1", 3), ICE_DIM), COFFIN_BODY), (recolour(quadrant("ashfrost_grid_2", 0), ICE_DIM), SLAB_BODY)]
# Swamp chests: soaked dark wood, tarnished fittings, no bright gilt or red trim.
WET_WOOD = {"ember-3": "bronze-2", "ember-2": "bronze-2", "ember-1": "bronze-1", "gilt-3": "leather-2", "gilt-2": "leather-2", "gilt-1": "leather-1", "gilt-0": "leather-0", "blood-2": "leather-1",
            "blood-1": "leather-0", "blood-0": "void-2", "bronze-3": "bronze-1", "bronze-2": "bronze-1", "flesh-3": "bronze-1",
            "flesh-2": "leather-1", "flesh-1": "leather-0", "flesh-0": "void-2"}
SOAKED = {"leather-2": "leather-1", "leather-1": "leather-0", "leather-3": "leather-2"}
WILLOW_MOSS = {"steel-3": "rot-2", "steel-2": "rot-1", "steel-1": "rot-0", "steel-0": "rot-0"}
SPECKS = {"steel-3": "void-2", "steel-0": "void-2", "bone-1": "void-2", "bone-0": "void-2"}
BARK_GRAIN = {"flesh-2": "leather-1", "leather-3": "leather-1"}  # the generated grain read as a pink seam
swamp_trees = [drop_orphans(recolour(knock_out(quadrant("swamp_tree_grid", q, 128), ("ash-",)), {} if q == 1 else SPECKS)) for q in range(4)]
recolour(swamp_trees[1], WILLOW_MOSS)
lit_left(swamp_trees[0], "ash-1")
recolour(swamp_trees[3], BARK_GRAIN)
# The rotting tree replaces the leaning trunk: its bright cartoon browns and yellow slime taken down to swamp darks.
ROT_DARK = {"flesh-0": "leather-0", "gilt-3": "rot-3", "gilt-2": "rot-2", "ember-3": "rot-3", "leather-3": "leather-1", "bronze-2": "leather-1"}
swamp_trees[2] = drop_orphans(recolour(knock_out(quadrant("swamp_rot_grid", 2, 128), ("ash-",)), ROT_DARK))
REED_DIM = {"bone-1": "ash-3", "bronze-0": "leather-0"}
# Chapel ruins: one generated grid (pillar, two walls, statue); the broken pillar and the beheaded statue are cut
# from it by hand; the fallen pillar is a PixelLab edit (crumbled end) of the pillar laid on its side.
ruins = [drop_islands(knock_out(quadrant("ruins_grid", q, 128), ("bone-0",)), 12) for q in range(4)]


def fill(img, seed, names, colour, box):
    """Flood a region of these colours from a seed, inside a box, with one colour."""
    px = img.load()
    todo, seen = [seed], set()
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (box[0] <= x < box[2] and box[1] <= y < box[3]) or NAME.get(px[x, y]) not in names:
            continue
        seen.add((x, y))
        px[x, y] = COLORS[colour] + (255,)
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return img


def broken_off(img, x0, x1, at, seed):
    """Snap a column off: clear everything above a jagged line, the break face in pale stone, outlined."""
    rng = random.Random(seed)
    px = img.load()
    out = img.copy()
    opx = out.load()
    cut = at
    for x in range(img.width):
        if x0 <= x < x1:
            cut = max(at - 4, min(at + 6, cut + rng.choice((-2, -1, 0, 1, 2))))
        for y in range(cut if x0 <= x < x1 else img.height if x0 - 6 <= x < x1 + 6 else 0):
            if y < (cut if x0 <= x < x1 else at + 8):
                opx[x, y] = (0, 0, 0, 0)
        if x0 <= x < x1 and px[x, cut][3]:
            opx[x, cut] = COLORS["void-0"] + (255,)
            for y in (cut + 1, cut + 2):
                opx[x, y] = COLORS["steel-2" if x < (x0 + x1) // 2 else "steel-1"] + (255,)
    return drop_islands(out, 12)


def beheaded(img, head_box, ground_at):
    """Strike the head off a statue and lay it on the ground beside the plinth."""
    head = img.crop(head_box).rotate(90, expand=True)
    out = img.copy()
    px = out.load()
    for y in range(head_box[1], head_box[3]):
        for x in range(head_box[0], head_box[2]):
            px[x, y] = (0, 0, 0, 0)
    for x in range(head_box[0], head_box[2]):
        if px[x, head_box[3]][3]:
            px[x, head_box[3]] = COLORS["steel-2"] + (255,)
    out.alpha_composite(head, ground_at)
    return out


ruins[3].paste((0, 0, 0, 0), (96, 110, 128, 128))  # the generator's signature
# Generated ruin stone came out far brighter than the wanderer (§3): every value down to the ash ramp, moss one step.
STONE_DIM = {"bone-1": "ash-3", "bone-0": "ash-2", "ash-4": "ash-2", "steel-3": "ash-2", "ash-3": "ash-1", "ash-2": "ash-1",
             "steel-2": "steel-1", "ash-1": "ash-0", "steel-1": "ash-0", "ash-0": "steel-0", "steel-0": "void-3", "rot-3": "rot-2"}
fill(ruins[0], (66, 21), {"void-0", "void-3", "void-1", "void-2", "steel-0", "ash-0", "steel-1"}, "steel-2", (54, 14, 80, 28))
for r in ruins:
    recolour(r, STONE_DIM)
# Reliquaries (sealed, then searched): A stone ossuary, B wooden casket, C candle shrine, D open iron box with a skull.
TARNISH = {"ember-2": "bronze-2", "ember-1": "bronze-1", "flesh-3": "leather-2", "blood-0": "leather-0"}
CANDLE_STONE = {k: v for k, v in STONE_DIM.items() if not k.startswith("bone")}
YELLOW_SKULL = {"ember-3": "bone-0", "ember-2": "gilt-1", "blood-4": "blood-2"}
EMPTY = ("void-2", "void-3")


def emptied(img, names, colour="void-1", box=(0, 0, 64, 64)):
    """The searched state: the relic's colours inside a box become the dark of an empty interior."""
    out = img.copy()
    px = out.load()
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if NAME.get(px[x, y], "").startswith(names):
                px[x, y] = COLORS[colour] + (255,)
    return out


candle_shrine = quadrant("reliquary_grid_2", 0)
for _ in range(3):  # its pale stone sat far above the wanderer; the candle wax stays bright
    recolour(candle_shrine, CANDLE_STONE)
for box in ((0, 36, 64, 64), (34, 0, 64, 36)):  # pale mortar away from the candle
    candle_shrine = emptied(candle_shrine, ("bone-",), "ash-1", box)
reliq = [recolour(quadrant("reliquary_grid", 0), STONE_DIM), recolour(quadrant("reliquary_grid", 1), TARNISH),
         candle_shrine, recolour(quadrant("reliquary_grid_2", 2), YELLOW_SKULL)]
reliq_open = [
    fill(reliq[0].copy(), (33, 27), {"ash-2", "ash-1", "ash-0", "steel-1", "steel-0"}, "void-2", (14, 12, 54, 40)),
    fill(reliq[1].copy(), (31, 18), {"bronze-2", "bronze-1", "leather-0"}, "void-2", (12, 4, 54, 32)),
    emptied(emptied(emptied(emptied(reliq[2], ("blood-",), "void-0"), ("flesh-", "gilt-", "ember-"), "void-0", (0, 0, 64, 20)),
                    ("gilt-", "ember-"), "void-2", (30, 30, 40, 42)), ("bone-",), "ash-2", (0, 0, 64, 20)),  # snuffed, relics gone
    emptied(reliq[3], ("bone-", "gilt-", "bronze-", "blood-", "flesh-", "ember-"), "void-0", (14, 14, 54, 54)),
]
# Village: four huts and a hall, a stall, wells and a firepit; the stockade is rebuilt log by log so its tiles join.
THATCH = {"gilt-3": "bronze-2", "gilt-2": "bronze-1", "gilt-1": "leather-1", "gilt-0": "leather-0"}
AWNING = {"blood-4": "blood-2", "blood-3": "blood-1", "blood-2": "blood-1"}
# Mirrored: the generator lit them from the top-right (§2).
huts = [knock_out(quadrant("village_huts_grid", q, 128), ("steel-3", "ash-4")).transpose(Image.FLIP_LEFT_RIGHT) for q in range(4)]
recolour(huts[1], {**THATCH, "bronze-2": "bronze-1"})
hall = knock_out(quadrant("village_build_grid", 0, 128), ("ash-3",))
stall = recolour(strip(knock_out(quadrant("village_build_grid", 1, 128), ("ash-3",)), ("ash-3",)), AWNING)
wells = [recolour(drop_islands(strip(quadrant("village_wells_grid", q), ("rot-", "gilt-"), 36), 12), STONE_DIM) for q in range(3)]
firepit = quadrant("village_small_grid", 2)


def stockade_logs(q, first, count):
    section = knock_out(quadrant("village_stockade_grid", q, 128), ("ash-",))
    logs = [section.crop((first + 14 * k, 0, first + 14 * k + 14, 128)) for k in range(count)]
    return [widened(log.crop((*log.getbbox()[:1], 0, log.getbbox()[2], 128)), 16) for log in logs]


def widened(log, width):
    """Stretch a log to a tile-friendly width by repeating its middle column."""
    while log.width < width:
        mid = log.width // 2
        out = Image.new("RGBA", (log.width + 1, log.height))
        out.paste(log.crop((0, 0, mid + 1, log.height)), (0, 0))
        out.paste(log.crop((mid, 0, log.width, log.height)), (mid + 1, 0))
        log = out
    return log


def row_of(logs):
    out = Image.new("RGBA", (128, 128))
    for k, log in enumerate(logs):
        out.alpha_composite(log, (32 + 16 * k, 0))
    return out


def lone(log):
    out = Image.new("RGBA", (128, 128))
    out.alpha_composite(log, (56, 0))
    return out


def torch_on(row, flame, x=56):
    """A wall tile with a torch burning on the log at x (corner and gate posts)."""
    top = min(y for y in range(row.height) if row.getpixel((x, y))[3])
    row.alpha_composite(flame, (x - flame.width // 2, top - flame.height + 4))
    return row


logs = stockade_logs(0, 15, 7) + stockade_logs(1, 11, 7)
torch = knock_out(quadrant("village_stockade_grid", 2, 128), ("ash-",))
flame = torch.crop(torch.getbbox()).crop((0, 0, torch.getbbox()[2] - torch.getbbox()[0], 30))
flame = flame.crop(flame.getbbox())
palisade = [recolour(drop_orphans(tile), {"void-1": "void-0"}) for tile in (
    row_of(logs[1:5]), row_of(logs[2:6]), row_of(logs[7:11]), row_of(logs[8:12]), lone(logs[1]), lone(logs[9]),
    torch_on(row_of(logs[2:6]), flame))]
GILT_TO_WOOD = {"gilt-0": "leather-0", "gilt-1": "leather-1", "gilt-2": "leather-2", "gilt-3": "leather-3"}
SHEETS = {
    "weapons_stuck": stuck,
    "stumps": [load("stump_rotted"), strip(quadrant("stump_spear_grid", 1), ("ash-3",), 40)],
    "remains": [recolour(strip_patch(quadrant("bodies_B_old", q)), BONE_DIM) for q in range(4)]
    + [recolour(strip(quadrant("bones_grid", q), ("steel-1",)), YELLOW_BONE) for q in (2, 3)],
    "rocks": [drop_islands(strip(quadrant("stones_stakes_grid", 1), ("steel-0",), 44), 20),
              drop_islands(strip(load("rocks_jagged"), ("flesh-", "bronze-", "gilt-", "leather-3"), 40), 20)],
    "stakes": [load(f"stake_helm_rot/{k}") for k in (1, 7)],  # the approved helm stake, turned to 3/4 views
    "crates": [recolour(quadrant("crates_grid", q), STRAW) for q in range(4)],
    "carts": [drop_islands(recolour(strip(load("cart_broken"), SAND, 100), {**GRAIN, **STRAW}), 20),
              drop_islands(strip(load("cart_wreck"), ("steel-1",), 86), 20)],
    "gibbets": [load("gibbet_cage"), load("gibbet_noose")],
    "banners": [load("banner_upright"), tilt(load("banner_fallen"))],
    "boulders": [drop_islands(load("boulder_big_280"), 20)],  # the approved boulder repainted at 2x size
    "shields": [drop_islands(strip(quadrant("debris_grid", 0), ("rot-",), 44), 20)],
    "charred_trees": [load(f"ash_tree_{k}") for k in (1, 2, 3)],
    "charred_stumps": [quadrant("ash_stumps", 0), quadrant("ashfrost_grid_1", 0)],
    "embers": [quadrant("ash_grid", q) for q in (2, 3)],
    "pyres": [load("pyre_2"), recolour(load("pyre_2"), BURNT_OUT)],
    "frozen_trees": [recolour(load(f"frost_tree_{k}"), ICE_DIM) for k in (1, 2)],
    "cairns": [recolour(quadrant("frost_grid", 0), ICE_DIM), recolour(quadrant("ashfrost_grid_1", 1), ICE_DIM)],
    "ice_spikes": [recolour(quadrant("frost_grid", 2), ICE_DIM), recolour(quadrant("ashfrost_grid_1", 2), ICE_DIM)],
    "ice_tombs": [frozen_in(t, m, False) for t, m in tombs] + [frozen_in(t, m, True) for t, m in tombs],
    "swamp_trees": swamp_trees,
    "reeds": [recolour(drop_islands(strip(quadrant("swamp_grid", q), ("void-",), 44), 20), {**STRAW, **REED_DIM}) for q in (0, 1)],
    "drowned_chests": [sunk(rotted(recolour(recolour(quadrant("swamp_grid", 2), WET_WOOD), SOAKED), 5), 33), sunk(rotted(recolour(quadrant("swamp_grid", 3), WET_WOOD), 6), 32)],
    "pillars": [ruins[0], broken_off(ruins[0], 50, 82, 58, 7), drop_orphans(load("pillar_fallen_edit_482_0"))],
    "walls": [ruins[1], ruins[2]],
    "rubble": [recolour(drop_islands(knock_out(quadrant("stones_grid", 0), ("steel-1",)), 12), STONE_DIM),
               recolour(quadrant("stones_stakes_grid", 1), STONE_DIM)],
    "reliquaries": reliq + reliq_open,
    "huts": huts + [hall],
    "stall": [stall],
    "wells": wells,
    "firepit": [firepit],
    "palisade": palisade,
    "statues": [ruins[3], beheaded(ruins[3], (50, 6, 68, 22), (90, 100))],
    "trees": [load("C_tree_marked"), recolour(load("tree_splintered"), GILT_TO_WOOD), lit_left(load("tree_gallows"), "leather-2")],
}

for name, frames in SHEETS.items():
    frames = [grounded(f) for f in frames]
    save(sheet([frames], *frames[0].size), OUT / f"{name}_hd.png")
    print(name, len(frames), "x", frames[0].size)
