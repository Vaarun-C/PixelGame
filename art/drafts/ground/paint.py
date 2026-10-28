"""Paint a ground sketch with PixelLab pixflux (1 generation per 256 px image).

Usage: .venv/bin/python art/drafts/ground/paint.py <sketch.png> <out.png> <strength> <seed> "<description>"
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import pixellab

sketch, out, strength, seed, desc = sys.argv[1:]
encode = lambda path: {"type": "base64", "base64": base64.b64encode(Path(path).read_bytes()).decode(), "format": "png"}
pixellab.generate(out, 256, 256, desc, no_background=False, view="high top-down", outline="lineless",
                  shading="medium shading", detail="medium detail", init_image=encode(sketch),
                  init_image_strength=int(strength), color_image=encode(sketch), seed=int(seed))
print(out, pixellab.get("balance")["subscription"]["generations"], "left")
