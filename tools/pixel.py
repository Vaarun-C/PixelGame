"""Shared helpers for the placeholder art generators."""
from PIL import Image
from check_art import load_palette

COLORS = {name: rgb for rgb, name in load_palette().items()}


class Sprite:
    def __init__(self, w, h, mirror=False):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]
        self.mirror = mirror

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.dot(x, y, c)

    def dot(self, x, y, c):
        x = self.w - 1 - x if self.mirror else x
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def rows(self, y0, spans, c):
        """Fill one horizontal span (x0, x1) per row starting at y0."""
        for i, (x0, x1) in enumerate(spans):
            self.rect(x0, y0 + i, x1, y0 + i, c)

    def line(self, x0, y0, x1, y1, c, width=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            self.rect(x, y, x + width - 1, y + width - 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2 <= 1:
                    self.dot(x, y, c)

    def pattern(self, x0, y0, rows, c):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == "#":
                    self.dot(x0 + dx, y0 + dy, c)

    def recolor(self, ramps=None, colors=None):
        """Swap whole ramps (keeping shade index, clamped) and exact colors. Use before finish()."""
        for row in self.px:
            for x, c in enumerate(row):
                if not c:
                    continue
                if colors and c in colors:
                    row[x] = colors[c]
                    continue
                ramp, i = c.rsplit("-", 1)
                if ramps and ramp in ramps:
                    target = ramps[ramp]
                    i = min(int(i), max(int(n.rsplit("-", 1)[1]) for n in COLORS if n.rsplit("-", 1)[0] == target))
                    row[x] = f"{target}-{i}"
        return self

    def snowcap(self, color="bone-0"):
        """Dust every top edge with snow. Use after finish()."""
        for y in range(1, self.h):
            for x in range(self.w):
                if self.px[y][x] == "void-1" and self.px[y - 1][x] is None and y + 1 < self.h and self.px[y + 1][x]:
                    self.px[y + 1][x] = color

    def empty(self, x, y):
        return not (0 <= x < self.w and 0 <= y < self.h) or self.px[y][x] is None

    def finish(self):
        self.shade()
        self.outline()
        return self

    def shade(self):
        """Light from top-left: brighten top/left edges (broken rim), darken right edges."""
        src = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                c = src[y][x]
                if not c or c.startswith(("rune", "void")):
                    continue
                edge = lambda dx, dy: not (0 <= x + dx < self.w and 0 <= y + dy < self.h) or src[y + dy][x + dx] is None
                if (edge(-1, 0) or edge(0, -1)) and (x + y) % 3:
                    self.px[y][x] = step(c, 1)
                elif edge(1, 0):
                    self.px[y][x] = step(c, -1)

    def outline(self):
        src = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x] is None and any(
                    0 <= x + dx < self.w and 0 <= y + dy < self.h and src[y + dy][x + dx]
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                ):
                    self.px[y][x] = "void-1"

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x]:
                    img.putpixel((x, y), COLORS[self.px[y][x]] + (255,))
        return img


def step(color, delta):
    ramp, i = color.rsplit("-", 1)
    target = f"{ramp}-{int(i) + delta}"
    return target if target in COLORS else color


def sheet(rows, w, h):
    """Paste rows of same-sized images into one sheet."""
    img = Image.new("RGBA", (w * max(map(len, rows)), h * len(rows)), (0, 0, 0, 0))
    for r, row in enumerate(rows):
        for c, frame in enumerate(row):
            img.paste(frame, (c * w, r * h))
    return img


def save(img, path, preview_dir=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    if preview_dir:
        img.resize((img.width * 6, img.height * 6), Image.NEAREST).save(f"{preview_dir}/{path.name}")
