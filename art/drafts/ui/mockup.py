"""Full-screen 960x540 mockups of the 2x inventory in three frame styles (A iron, B leather, C reliquary).

Usage: .venv/bin/python art/drafts/ui/mockup.py <background.png> <out_dir>
Item icons are today's 16 px icons doubled as placeholders until the 32 px set is drawn.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image
from pixel import COLORS
import font5x7 as font

C = {k: v + (255,) for k, v in COLORS.items()}
PW, PH = 640, 360
X0, Y0 = (960 - PW) // 2, (540 - PH) // 2
SLOT, GAP, COLS, ROWS = 36, 4, 6, 4
TIERS = ["pale", "azure", "violet", "venom", "gold", "crimson"]
ITEMS = [("bronze", 46, 4, 2), ("silver", 9, 7, 0), ("gold", 2, 10, 0), ("shard", 14, 0, 0), ("scrap_blade", 2, 1, 0),
         ("scrap_helm", 1, 2, 0), ("scrap_plate", 3, 3, 0), ("rune_rend_1", 1, None, (0, 0)),
         ("rune_ward_2", 1, None, (1, 1)), ("rune_hunger_3", 1, None, (2, 2))]
HOVER = 8
item_sheet = Image.open("art/items/item_icons.png")
rune_sheet = Image.open("art/runes/rune_icons.png")
wanderer = Image.open("art/characters/wanderer_hd/wanderer_hd_idle.png").crop((0, 0, 96, 96))


def icon(entry):
    key, count, col, extra = entry
    if col is None:
        row, tier = extra
        img = rune_sheet.crop((tier * 16, row * 16, tier * 16 + 16, row * 16 + 16))
    else:
        img = item_sheet.crop(((col + extra) * 16, 0, (col + extra) * 16 + 16, 16))
    return img.resize((32, 32), Image.NEAREST)


def rect(img, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            img.putpixel((xx, yy), color)


def outline(img, x, y, w, h, color):
    rect(img, x, y, w, 1, color); rect(img, x, y + h - 1, w, 1, color)
    rect(img, x, y, 1, h, color); rect(img, x + w - 1, y, 1, h, color)


def bevel(img, x, y, w, h, light, dark):
    rect(img, x, y, w, 1, light); rect(img, x, y, 1, h, light)
    rect(img, x, y + h - 1, w, 1, dark); rect(img, x + w - 1, y, 1, h, dark)


def wrap(text, chars):
    lines, line = [], ""
    for word in text.split():
        if len(line) + len(word) + (1 if line else 0) > chars:
            lines.append(line); line = word
        else:
            line = f"{line} {word}" if line else word
    return lines + [line]


def disc(img, cx, cy, r, color):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r + r:
                img.putpixel((cx + x, cy + y), color)


# Each style: frame(img), slot(img, x, y, hover), section(img, x, y, w, h), and text colours.
class Iron:
    title, body, muted, accent = C["bone-0"], C["ash-4"], C["ash-3"], C["gilt-2"]

    def frame(self, img):
        rect(img, X0 - 2, Y0 - 2, PW + 4, PH + 4, C["void-0"])
        rect(img, X0, Y0, PW, PH, C["steel-0"])
        bevel(img, X0, Y0, PW, PH, C["steel-2"], C["void-1"])
        rect(img, X0 + 6, Y0 + 6, PW - 12, PH - 12, C["void-1"])
        bevel(img, X0 + 6, Y0 + 6, PW - 12, PH - 12, C["void-0"], C["steel-1"])
        for x in range(X0 + 24, X0 + PW - 20, 32):  # rivets along the iron band
            for y in (Y0 + 2, Y0 + PH - 5):
                rect(img, x, y, 2, 2, C["ash-2"]); img.putpixel((x + 1, y + 1), C["void-0"])
        for cx, cy in ((X0, Y0), (X0 + PW - 16, Y0), (X0, Y0 + PH - 16), (X0 + PW - 16, Y0 + PH - 16)):
            self.corner(img, cx, cy)

    def corner(self, img, x, y):
        rect(img, x, y, 16, 16, C["gilt-0"])
        bevel(img, x, y, 16, 16, C["gilt-2"], C["void-0"])
        rect(img, x + 3, y + 3, 10, 10, C["gilt-1"])
        # a small skull in bone
        rect(img, x + 5, y + 4, 6, 5, C["bone-0"]); rect(img, x + 6, y + 9, 4, 2, C["bone-0"])
        img.putpixel((x + 6, y + 6), C["void-0"]); img.putpixel((x + 9, y + 6), C["void-0"])
        img.putpixel((x + 7, y + 10), C["void-1"]); img.putpixel((x + 8, y + 10), C["void-1"])
        rect(img, x + 5, y + 4, 6, 1, C["bone-1"])

    def slot(self, img, x, y, hover):
        rect(img, x, y, SLOT, SLOT, C["void-0"])
        bevel(img, x, y, SLOT, SLOT, C["void-0"], C["steel-1"])
        if hover:
            outline(img, x - 1, y - 1, SLOT + 2, SLOT + 2, C["gilt-2"])

    def section(self, img, x, y, w, h):
        rect(img, x, y, w, h, C["void-2"])
        bevel(img, x, y, w, h, C["void-0"], C["steel-0"])

    def rule(self, img, x, y, w):
        rect(img, x, y, w, 1, C["void-0"]); rect(img, x, y + 1, w, 1, C["steel-1"])


class Leather:
    title, body, muted, accent = C["bone-1"], C["bone-0"], C["leather-3"], C["bronze-3"]

    def stitch(self, img, x, y, w, h, color):
        for xx in range(x, x + w, 4):
            rect(img, xx, y, 2, 1, color); rect(img, xx, y + h - 1, 2, 1, color)
        for yy in range(y, y + h, 4):
            rect(img, x, yy, 1, 2, color); rect(img, x + w - 1, yy, 1, 2, color)

    def frame(self, img):
        rect(img, X0 - 2, Y0 - 2, PW + 4, PH + 4, C["void-0"])
        rect(img, X0, Y0, PW, PH, C["leather-1"])
        bevel(img, X0, Y0, PW, PH, C["leather-2"], C["leather-0"])
        self.stitch(img, X0 + 4, Y0 + 4, PW - 8, PH - 8, C["leather-3"])
        for x in range(X0 + 8, X0 + PW - 8, 3):  # worn grain
            for y in range(Y0 + 10, Y0 + PH - 10, 7):
                if (x * 7 + y * 13) % 23 == 0:
                    img.putpixel((x, y), C["leather-0"])
        for cx, cy in ((X0 + 10, Y0 + 10), (X0 + PW - 11, Y0 + 10), (X0 + 10, Y0 + PH - 11), (X0 + PW - 11, Y0 + PH - 11)):
            disc(img, cx, cy, 3, C["bronze-1"]); disc(img, cx - 1, cy - 1, 1, C["bronze-3"])
        # buckle strap over the top edge
        rect(img, X0 + PW // 2 - 14, Y0 - 2, 28, 14, C["leather-0"])
        outline(img, X0 + PW // 2 - 8, Y0 + 2, 16, 8, C["bronze-2"])
        rect(img, X0 + PW // 2 - 1, Y0 + 2, 2, 8, C["bronze-3"])

    def slot(self, img, x, y, hover):
        rect(img, x, y, SLOT, SLOT, C["leather-0"])
        bevel(img, x, y, SLOT, SLOT, C["void-2"], C["leather-2"])
        self.stitch(img, x + 2, y + 2, SLOT - 4, SLOT - 4, C["leather-1"] if not hover else C["bronze-3"])

    def section(self, img, x, y, w, h):
        rect(img, x, y, w, h, C["leather-0"])
        bevel(img, x, y, w, h, C["void-2"], C["leather-2"])
        self.stitch(img, x + 3, y + 3, w - 6, h - 6, C["leather-2"])

    def rule(self, img, x, y, w):
        for xx in range(x, x + w, 4):
            rect(img, xx, y, 2, 1, C["leather-3"])


class Reliquary:
    title, body, muted, accent = C["gilt-3"], C["ash-4"], C["ash-2"], C["gilt-2"]

    def frame(self, img):
        rect(img, X0, Y0, PW, PH, C["void-0"])
        outline(img, X0 + 4, Y0 + 4, PW - 8, PH - 8, C["gilt-1"])
        outline(img, X0 + 6, Y0 + 6, PW - 12, PH - 12, C["gilt-0"])
        for cx, cy in ((X0 + 4, Y0 + 4), (X0 + PW - 5, Y0 + 4), (X0 + 4, Y0 + PH - 5), (X0 + PW - 5, Y0 + PH - 5)):
            for d in range(4):  # small gilt diamond on each corner
                for e in range(-d, d + 1):
                    img.putpixel((cx + e, cy - 3 + d), C["gilt-2"]); img.putpixel((cx + e, cy + 3 - d), C["gilt-2"])
            img.putpixel((cx, cy), C["bone-1"])
        cx = X0 + PW // 2  # a cross finial over the title
        rect(img, cx - 1, Y0 - 6, 3, 13, C["gilt-2"]); rect(img, cx - 4, Y0 - 3, 9, 3, C["gilt-2"])
        rect(img, cx, Y0 - 5, 1, 11, C["gilt-3"])

    def slot(self, img, x, y, hover):
        rect(img, x, y, SLOT, SLOT, C["void-1"])
        outline(img, x, y, SLOT, SLOT, C["gilt-2"] if hover else C["void-3"])

    def section(self, img, x, y, w, h):
        outline(img, x, y, w, h, C["void-3"])

    def rule(self, img, x, y, w):
        rect(img, x, y, w, 1, C["gilt-0"])
        rect(img, x + w // 2 - 1, y - 1, 3, 3, C["gilt-1"])


def mockup(style, background):
    img = background.copy()
    shade = Image.new("RGBA", img.size, C["void-0"][:3] + (150,))
    img.alpha_composite(shade)
    style.frame(img)

    font.draw(img, "INVENTORY", X0 + (PW - font.width("INVENTORY")) // 2, Y0 + 14, style.title, C["void-0"])
    style.rule(img, X0 + 20, Y0 + 28, PW - 40)

    # Character and rune sockets
    cx, cy, cw, ch = X0 + 18, Y0 + 38, 160, 228
    style.section(img, cx, cy, cw, ch)
    font.draw(img, "WANDERER", cx + (cw - font.width("WANDERER")) // 2, cy + 8, style.muted)
    img.alpha_composite(wanderer, (cx + (cw - 96) // 2, cy + 26))
    sockets = [("BLADE", 3), ("ARMOR", 2)]
    sy = cy + 132
    for label, n in sockets:
        font.draw(img, label, cx + 12, sy + 5, style.body)
        for i in range(n):
            sx = cx + 70 + i * 26
            disc(img, sx + 9, sy + 8, 9, C["void-0"]); disc(img, sx + 9, sy + 8, 7, C["void-2"])
            disc(img, sx + 9, sy + 8, 2, C["void-3"])
        sy += 26
    font.draw(img, "EMPTY SOCKETS", cx + (cw - font.width("EMPTY SOCKETS")) // 2, sy + 10, style.muted)

    # Bag
    bx, by = X0 + 196, Y0 + 52
    font.draw(img, "BAG", bx, Y0 + 40, style.muted)
    for i in range(COLS * ROWS):
        x, y = bx + (i % COLS) * (SLOT + GAP), by + (i // COLS) * (SLOT + GAP)
        style.slot(img, x, y, i == HOVER)
        if i < len(ITEMS):
            img.alpha_composite(icon(ITEMS[i]), (x + 2, y + 2))
            count = ITEMS[i][1]
            if count > 1:
                t = str(count)
                font.draw(img, t, x + SLOT - 2 - font.width(t), y + SLOT - 9, C["bone-1"], C["void-0"])

    # Detail panel for the hovered item
    dx, dy, dw, dh = X0 + 446, Y0 + 38, 176, 228
    style.section(img, dx, dy, dw, dh)
    rect(img, dx + (dw - 40) // 2, dy + 12, 40, 40, C["void-0"])
    img.alpha_composite(icon(ITEMS[HOVER]), (dx + (dw - 32) // 2, dy + 16))
    name = ["AZURE RUNE", "OF WARD"]
    for i, line in enumerate(name):
        font.draw(img, line, dx + (dw - font.width(line)) // 2, dy + 62 + i * 10, C["rune-azure-mid"], C["void-0"])
    style.rule(img, dx + 16, dy + 86, dw - 32)
    for i, line in enumerate(wrap("HARDENS THE FLESH. SET IT IN ARMOR TO TURN ASIDE BLOWS.", 26)):
        font.draw(img, line, dx + 10, dy + 96 + i * 10, style.body)
    font.draw(img, "TIER 2 OF 6", dx + 10, dy + 140, style.muted)
    for t in range(6):
        disc(img, dx + 14 + t * 14, dy + 158, 4, C[f"rune-{TIERS[t]}-{'mid' if t <= 1 else 'dark'}"])
    font.draw(img, "TYPE: WARD", dx + 10, dy + 174, style.muted)

    # Summary strip: metals by weight, shards and runes
    sx, sy, sw, sh = X0 + 18, Y0 + 278, PW - 36, 64
    style.section(img, sx, sy, sw, sh)
    x = sx + 14
    for entry, label in ((ITEMS[0], "46 G"), (ITEMS[1], "9 G"), (ITEMS[2], "2 G"), (ITEMS[3], "14")):
        img.alpha_composite(icon(entry), (x, sy + 16))
        font.draw(img, label, x + 36, sy + 28, style.body)
        x += 36 + font.width(label) + 22
    font.draw(img, "RUNES", x + 6, sy + 12, style.muted)
    for t in range(6):
        tx = x + 6 + t * 30
        disc(img, tx + 5, sy + 34, 5, C[f"rune-{TIERS[t]}-mid"])
        font.draw(img, str([1, 1, 1, 0, 0, 0][t]), tx + 14, sy + 31, style.body)
    font.draw(img, "I  CLOSE", X0 + PW - 20 - font.width("I  CLOSE"), Y0 + PH - 14, style.muted)
    return img


if __name__ == "__main__":
    background = Image.open(sys.argv[1]).convert("RGBA")
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    for key, style in (("A", Iron()), ("B", Leather()), ("C", Reliquary())):
        mockup(style, background).convert("RGB").save(out / f"inventory_{key}.png")
        print(out / f"inventory_{key}.png")
