"""In-betweens for the Misborn's bite and flail between his key poses, with PixelLab.

Run from the repo root: .venv/bin/python art/drafts/misborn/pixellab_anims.py [seed] [segment ...]
Writes art/drafts/misborn/segments/<name>_<seed>/<n>.png; assemble.py joins them into bite_south and flail_south.
"""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from pixellab import animate_segments

D = Path("art/drafts/misborn")
REST, KEYS = D / "keys/rest.png", D / "keys"
BODY = " The body, hind legs, harness and the boot at its flank stay the same; no new body parts, no motion lines, smears or effects."
SEGMENTS = {
    "bite_in": (REST, KEYS / "bite_4.png", 6,
                "The horse head draws back slightly, then lunges forward and down, jaws opening wide to bite." + BODY),
    "bite_out": (KEYS / "bite_4.png", REST, 6, "The jaws snap shut and the head pulls back up to rest." + BODY),
    "flail_up": (REST, KEYS / "windup_8.png", 4, "The right foreleg swings up high above the head." + BODY),
    "flail_hit": (KEYS / "windup_8.png", KEYS / "strike_10.png", 4,
                  "The raised foreleg smashes down hard and fast toward the viewer." + BODY),
    "flail_out": (KEYS / "strike_10.png", REST, 6, "The foreleg drags back to hang at its side, body straightening." + BODY),
    "death": (REST, KEYS / "dead.png", 8, "Its snapped knees give out and the heavy body crashes to the ground, "
              "falling onto its side." + BODY),
}

if __name__ == "__main__":
    animate_segments(D / "segments", SEGMENTS, int(sys.argv[1]) if len(sys.argv) > 1 else 1, sys.argv[2:])
