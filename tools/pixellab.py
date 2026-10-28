"""Generate a draft sprite with the PixelLab API (key in .env as PIXELLAB_API_KEY).

Usage: .venv/bin/python tools/pixellab.py <out.png> <width> <height> "<description>" [key=value ...]
Extra key=value pairs go straight into the request, e.g. shading="detailed shading" seed=7.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.pixellab.ai/v2"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def api_key():
    if os.environ.get("PIXELLAB_API_KEY"):
        return os.environ["PIXELLAB_API_KEY"]
    for line in ENV_FILE.read_text().splitlines():
        name, _, value = line.partition("=")
        if name.strip() == "PIXELLAB_API_KEY":
            return value.strip()
    sys.exit("PIXELLAB_API_KEY missing from env and .env")


def post(endpoint, body):
    req = urllib.request.Request(
        f"{API}/{endpoint}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as res:
                return json.load(res)
        except urllib.error.HTTPError:
            raise
        except urllib.error.URLError:  # connection never made (TLS handshake timeout), safe to resend
            if attempt == 2:
                raise
            time.sleep(10)


def generate(out, width, height, description, **options):
    body = {"description": description, "image_size": {"width": width, "height": height},
            "no_background": True, **options}
    image = post("create-image-pixflux", body)["image"]["base64"]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(base64.b64decode(image.split(",")[-1]))


def get(endpoint):
    req = urllib.request.Request(f"{API}/{endpoint}", headers={"Authorization": f"Bearer {api_key()}"})
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.load(res)


def wait_for(job_id):
    print("job", job_id, file=sys.stderr)
    while True:
        time.sleep(5)
        try:
            job = get(f"background-jobs/{job_id}")
        except OSError:  # PixelLab TLS handshakes time out now and then
            continue
        if job["status"] in ("completed", "failed"):
            return job


def edit(src, out, instruction, seed=0):
    """Edit an existing sprite with a text instruction, keeping its canvas size."""
    image = base64.b64encode(Path(src).read_bytes()).decode()
    job = post("edit-image-pro-flash", {"image": {"type": "base64", "base64": image, "format": "png"},
                                        "description": instruction, "no_background": True, "seed": seed})
    return wait_for(job["background_job_id"])


def animate(src, out_dir, action, frames, seed=0, last=None):
    """Animate a sprite from one frame, optionally toward a last-frame keyframe.
    Saves frames 0..n; frame 0 is the input itself."""
    encode = lambda path: {"type": "base64", "base64": base64.b64encode(Path(path).read_bytes()).decode(), "format": "png"}
    body = {"first_frame": encode(src), "action": action, "frame_count": frames, "no_background": True, "seed": seed}
    if last:
        body["last_frame"] = encode(last)
    job = post("animate-with-text-v3", body)
    result = wait_for(job["background_job_id"])
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for k, img in enumerate(result["last_response"].get("images", [])):
        (Path(out_dir) / f"{k}.png").write_bytes(base64.b64decode(img["base64"].split(",")[-1]))
    return result


def tiles(out_dir, description, size, **options):
    """Independent square top-down tile variations; number them in the description: '1). mud 2). grass'."""
    job = post("create-tiles-pro", {"description": description, "tile_type": "square_topdown",
                                    "tile_size": size, **options})
    wait_for(job["background_job_id"])
    result = get(f"tiles-pro/{job['tile_id']}")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for name, url in sorted(result["storage_urls"].items()):
        with urllib.request.urlopen(url, timeout=60) as res:
            (Path(out_dir) / f"{name}.png").write_bytes(res.read())
    return result


def parse_option(arg):
    name, _, value = arg.partition("=")
    return name, int(value) if value.lstrip("-").isdigit() else value


if __name__ == "__main__":
    out, w, h, desc, *rest = sys.argv[1:]
    generate(out, int(w), int(h), desc, **dict(map(parse_option, rest)))
    print(out)
