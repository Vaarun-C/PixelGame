"""Generate draft sprites with the SpriteCook API (key in .env as SPRITECOOK_API_KEY).

Uses the pixel engine (exact size up to 128, transparent background) with the master palette.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from check_art import load_palette
from pixellab import ENV_FILE

API = "https://api.spritecook.ai/v1/api"


def api_key():
    if os.environ.get("SPRITECOOK_API_KEY"):
        return os.environ["SPRITECOOK_API_KEY"]
    for line in ENV_FILE.read_text().splitlines():
        name, _, value = line.partition("=")
        if name.strip() == "SPRITECOOK_API_KEY":
            return value.strip()
    sys.exit("SPRITECOOK_API_KEY missing from .env")


def request(endpoint, body=None):
    req = urllib.request.Request(f"{API}/{endpoint}", data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"SpriteCook {e.code}: {e.read().decode()}")


def generate(out_stem, width, height, prompt, variations=1, **options):
    """Saves <out_stem>_<n>.png for each variation and returns the paths."""
    colors = ["#%02X%02X%02X" % rgb for rgb in load_palette()][:64]
    result = request("generate-sync", {"prompt": prompt, "width": width, "height": height, "variations": variations,
                                       "pixel": True, "bg_mode": "transparent", "model": "pixel-engine-image-v1",
                                       "colors": colors, **options})
    return save(result, out_stem)


def save(result, out_stem):
    paths = []
    for i, asset in enumerate(result["assets"], 1):
        path = Path(f"{out_stem}_{i}.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(asset["url"], timeout=120) as res:
            path.write_bytes(res.read())
        paths.append(path)
    print(f"{result['credits_used']} credits used, {result['credits_remaining']} left")
    return paths
