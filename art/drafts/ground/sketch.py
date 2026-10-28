"""Procedural init sketches for PixelLab ground generation: four 128 px quadrants (one ground each),
every quadrant periodic every 64 px so the AI paint-over stays close to tileable.

Usage: .venv/bin/python art/drafts/ground/sketch.py <style> <out.png>
"""
import math
import random
import sys

sys.path.insert(0, "tools")
from PIL import Image
from pixel import COLORS

T = 64


def wave_noise(x, y, seed, octaves=((1, 1.0), (2, 0.5), (4, 0.25))):
    """Sum of sines with integer frequencies: periodic every T pixels, values roughly -1..1."""
    rng = random.Random(seed)
    total = norm = 0
    for freq, amp in octaves:
        for _ in range(3):
            kx, ky = rng.choice([-1, 1]) * freq, rng.randint(-freq, freq)
            total += amp * math.sin(2 * math.pi * (kx * x + ky * y) / T + rng.uniform(0, 6.3))
            norm += amp
    return total / norm * 2


def ramp_texture(ramp, seed, cracks=0, specks=(), scale=((1, 1.0), (2, 0.6), (4, 0.3))):
    """Large soft value blobs over a dark-to-light ramp, with optional periodic cracks and specks."""
    rng = random.Random(seed)
    px = [[None] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            v = wave_noise(x, y, seed, scale) * 0.5 + 0.5
            px[y][x] = ramp[min(len(ramp) - 1, max(0, int(v * len(ramp))))]
    for _ in range(cracks):
        x, y = rng.randrange(T), rng.randrange(T)
        dx, dy = rng.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
        for _ in range(rng.randrange(6, 16)):
            px[y % T][x % T] = ramp[0]
            x, y = x + dx + rng.choice([0, 0, 1, -1]) * (dy != 0), y + dy + rng.choice([0, 0, 1, -1]) * (dx != 0)
    for color, count in specks:
        for _ in range(count):
            x, y = rng.randrange(T), rng.randrange(T)
            px[y][x] = color
    return px


QUIET = ((1, 1.0), (2, 0.35))
# Ramps repeat the main colour so it dominates; QUIET drops the busy high frequencies.
STYLES = {
    # A: warm packed earth, the current battlefield colours at 2x.
    "A": [
        dict(ramp=["leather-0", "leather-1", "leather-1", "leather-1", "leather-2"], seed=1, cracks=8, specks=[("ash-1", 20)], scale=QUIET),
        dict(ramp=["void-2", "void-3", "leather-0", "leather-0", "leather-1"], seed=2, specks=[("steel-0", 12)], scale=QUIET),
        dict(ramp=["rot-0", "rot-1", "rot-1", "rot-1", "rot-2"], seed=3, specks=[("rot-2", 50), ("leather-2", 15)], scale=QUIET),
        dict(ramp=["void-3", "blood-0", "blood-0", "leather-0", "blood-1"], seed=4, cracks=4, specks=[("blood-1", 15)], scale=QUIET),
    ],
    # B: cold ash and grey stone dust, Blasphemous-like cool ground with rust-brown mud.
    "B": [
        dict(ramp=["void-3", "ash-0", "ash-0", "ash-0", "ash-1"], seed=5, cracks=10, specks=[("ash-2", 15)], scale=QUIET),
        dict(ramp=["void-2", "leather-0", "leather-0", "void-3", "leather-1"], seed=6, specks=[("steel-1", 10)], scale=QUIET),
        dict(ramp=["void-3", "rot-0", "rot-1", "rot-1", "ash-1"], seed=7, specks=[("rot-2", 40), ("ash-2", 12)], scale=QUIET),
        dict(ramp=["void-2", "blood-0", "blood-0", "void-3", "blood-1"], seed=8, cracks=6, specks=[("ash-0", 12)], scale=QUIET),
    ],
    # C: wet and churned, darker values, puddles catching steel light.
    "C": [
        dict(ramp=["void-3", "leather-0", "leather-1", "leather-1", "leather-0"], seed=9, cracks=4, specks=[("steel-1", 15)], scale=QUIET),
        dict(ramp=["void-1", "void-2", "void-2", "steel-0", "void-3"], seed=10, specks=[("steel-2", 20)], scale=QUIET),
        dict(ramp=["void-3", "rot-0", "rot-0", "rot-1", "rot-1"], seed=11, specks=[("rot-2", 40), ("steel-1", 8)], scale=QUIET),
        dict(ramp=["void-2", "blood-0", "blood-0", "void-3", "blood-1"], seed=12, specks=[("steel-0", 15)], scale=QUIET),
    ],
}


def sketch(style):
    img = Image.new("RGBA", (4 * T, 4 * T))
    for i, spec in enumerate(STYLES[style]):
        tex = ramp_texture(**spec)
        ox, oy = (i % 2) * 2 * T, (i // 2) * 2 * T
        for y in range(2 * T):
            for x in range(2 * T):
                img.putpixel((ox + x, oy + y), COLORS[tex[y % T][x % T]] + (255,))
    return img


if __name__ == "__main__":
    sketch(sys.argv[1]).save(sys.argv[2])
