"""Shared helpers for the placeholder art generators."""
from pathlib import Path

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


def outline(img, color="void-1"):
    """A 1 px exterior outline round every opaque pixel of an image."""
    px = img.load()
    out = img.copy()
    o = out.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] == 0 and any(0 <= x + dx < img.width and 0 <= y + dy < img.height and px[x + dx, y + dy][3]
                                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                o[x, y] = COLORS[color] + (255,)
    return out


def recolor_edge(img, color="void-1"):
    """Repaint the sprite's own outermost pixels as its outline (AI frames drift to other dark colours)."""
    px = img.load()
    out = img.copy()
    o = out.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] and any(not (0 <= x + dx < img.width and 0 <= y + dy < img.height) or px[x + dx, y + dy][3] == 0
                                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                o[x, y] = COLORS[color] + (255,)
    return out


def segment_frames(root, parts, recolor=None):
    """Frames joined from PixelLab segment folders [(folder, frame numbers)], already at game size:
    snapped, cleared of specks, recolored ({rgb: rgb}) and edged with the outline color."""
    from snap_palette import drop_specks, snap
    out = []
    for folder, picks in parts:
        for i in picks:
            f = Image.open(Path(root) / folder / f"{i}.png").convert("RGBA")
            f.putalpha(f.getchannel("A").point(lambda v: 255 if v > 160 else 0))
            f = drop_specks(snap(f), 16)
            if recolor:
                f.putdata([recolor.get(c[:3], c[:3]) + (c[3],) for c in f.get_flattened_data()])
            out.append(recolor_edge(f))
    return out


def grounded(imgs, feet):
    """PixelLab lets the body drift off the ground (the planted foot, a falling corpse); stand each
    frame's lowest pixel on row `feet`."""
    out = []
    for f in imgs:
        c = Image.new("RGBA", f.size)
        c.alpha_composite(f, (0, feet + 1 - f.getbbox()[3]))
        out.append(c)
    return out


def export_game(files):
    """Write finished game art {path under art/: image} to both art/ and the Godot copy, godot/art/."""
    for rel, img in files.items():
        for root in ("art", "godot/art"):
            path = Path(root) / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            img.save(path)


def breathing(base, hips=0.5, neck=0.25):
    """A 4-frame idle from one frame: the body above the hips sinks a pixel, the head above the neck
    a beat later. hips and neck are fractions of the sprite's height from its top."""
    top, bottom = base.getbbox()[1], base.getbbox()[3]
    cuts = top + round((bottom - top) * hips), top + round((bottom - top) * neck)
    frames = []
    for offsets in ((0, 0), (1, 0), (1, 1), (0, 1)):
        f = base.copy()
        for cut, dy in zip(cuts, offsets):
            if dy:
                band = f.crop((0, 0, f.width, cut))
                f.paste(Image.new("RGBA", (f.width, cut)), (0, 0))
                f.alpha_composite(band, (0, dy))
        frames.append(f)
    return frames


def game_frames(raw, scale, bottom, size, feet):
    """AI frames shrunk to game size with one scale and one feet row for the whole animation (so the
    creature doesn't grow or hop between frames), then snapped, cleaned and outlined."""
    from snap_palette import drop_specks, snap
    out = []
    for f in raw:
        f = f.resize((round(f.width * scale), round(f.height * scale)), Image.LANCZOS)
        f.putalpha(f.getchannel("A").point(lambda v: 255 if v > 160 else 0))
        c = Image.new("RGBA", size)
        c.alpha_composite(f, ((size[0] - f.width) // 2, feet - round(bottom * scale)))
        out.append(outline(drop_specks(snap(c), 3)))
    return out
