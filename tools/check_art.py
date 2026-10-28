"""Automated checks from ART_RULES.md. Usage: .venv/bin/python tools/check_art.py <png>..."""
import sys
from pathlib import Path
from PIL import Image

PALETTE_FILE = Path(__file__).resolve().parent.parent / "art/palette/master.gpl"

# Folder -> allowed frame sizes; sheet dimensions must be multiples of one of them.
FRAME_SIZES = {
    "characters": [(32, 48), (96, 96), (128, 144)],
    "enemies": [(32, 48), (64, 64), (64, 96), (128, 112)],
    "bosses": [(96, 96), (128, 128)],
    "runes": [(16, 16), (32, 32)],
    "tiles": [(32, 32)],
    "items": [(16, 16)],
    "props": [(32, 32), (64, 64), (96, 96), (128, 128)],
}
ALPHA_ALLOWED = ("vfx", "shadow", "fog")
RUNE_ALLOWED = ("runes", "ui", "vfx")


def load_palette():
    palette = {}
    for line in PALETTE_FILE.read_text().splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0].isdigit():
            palette[tuple(map(int, parts[:3]))] = parts[3]
    return palette


def check(path, palette):
    issues = []
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    parts = Path(path).parts
    name = str(path).lower()

    for folder, sizes in FRAME_SIZES.items():
        if folder in parts and not any(w % fw == 0 and h % fh == 0 for fw, fh in sizes):
            issues.append(f"FAIL size {w}x{h} is not a multiple of {sizes} for {folder}/")

    off_palette, partial_alpha, rune_colors = set(), 0, set()
    for count, (r, g, b, a) in img.getcolors(w * h):
        if a == 0:
            continue
        if a < 255:
            partial_alpha += count
        color = palette.get((r, g, b))
        if color is None:
            off_palette.add(f"#{r:02X}{g:02X}{b:02X}")
        elif color.startswith("rune-"):
            rune_colors.add(color)

    if off_palette:
        issues.append(f"FAIL {len(off_palette)} off-palette colors: {', '.join(sorted(off_palette)[:10])}")
    if partial_alpha and not any(k in name for k in ALPHA_ALLOWED):
        issues.append(f"FAIL {partial_alpha} semi-transparent pixels (hard edges required)")
    if rune_colors and not any(k in parts for k in RUNE_ALLOWED):
        issues.append(f"WARN rune colors outside rune assets: {', '.join(sorted(rune_colors))} (ok only if rune-infused)")
    return issues


def main(paths):
    palette = load_palette()
    failed = False
    for path in paths:
        issues = check(path, palette)
        failed |= any(i.startswith("FAIL") for i in issues)
        print(f"{path}: {'PASS' if not issues else 'ISSUES'}")
        for issue in issues:
            print(f"  {issue}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
