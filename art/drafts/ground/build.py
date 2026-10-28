"""Build a draft ground sheet from a painted 256 px image (four 128 px quadrants: base, then rows 1-3).

Usage: .venv/bin/python art/drafts/ground/build.py <paint.png> <out.png> <bank,bank,bank,bank>
"""
import sys

sys.path.insert(0, "tools")
from PIL import Image
from snap_palette import snap
from ground_tiles import grid, despeckle, ground_sheet

paint, out, banks = sys.argv[1], sys.argv[2], [int(b) for b in sys.argv[3].split(",")]
px = despeckle(grid(snap(Image.open(paint).convert("RGBA"))))
patches = [[row[(i % 2) * 128:(i % 2) * 128 + 128] for row in px[(i // 2) * 128:(i // 2) * 128 + 128]] for i in range(4)]
ground_sheet(patches, banks).save(out)
print(out)
