"""Assemble a sprite sheet: one row per argument, frames comma-separated, all the same size.

Usage: .venv/bin/python tools/build_sheet.py <out.png> <row1_a.png,row1_b.png,...> <row2...> ...
"""
import sys
from PIL import Image
from pixel import sheet, save
from pathlib import Path

if __name__ == "__main__":
    out, *rows = sys.argv[1:]
    frames = [[Image.open(f).convert("RGBA") for f in row.split(",")] for row in rows]
    w, h = frames[0][0].size
    save(sheet(frames, w, h), Path(out))
    print(out)
