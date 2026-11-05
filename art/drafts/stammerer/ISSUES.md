# Stammerer: open art issues

From the art review of the PixelLab animations (2026-11-05). Frames are in `snapped/<anim>/`; rebuild with `assemble.py`.

## Cast
- Frames 4–14: the single satchel at his hip turns into a stack of 2–3 pouches, then shrinks back in frames 15–20. Needs the satchel repainted from the base in those frames.
- Frames 7–16: the chest stones blur into one large pale-blue patch, and in frame 15 the whole left forearm is filled with it. It reads as glowing flesh, not stones nailed in. Keep the light on the stones.

## Choke
- Frames 3–5: the robe flares out at his right like a cape. Check it suits his weight.

## Not yet decided
- ART_RULES has no size class for him: fodder enemies are 64×96, he is 96×96.
- ART_RULES §4 lists 6-frame walks and deaths and has no cast or choke row. These sheets are walk 7, cast 21, choke 9, death 8. Decide whether §4's counts apply to the 2× art.

## In the game (godot/scripts/stammerer.gd)
- Drawn facing south only: he faces the camera whichever way he walks.
- Out of stones he only keeps his distance. What he becomes then (a morph) is still to be designed.
- Whether a loose soul can utter at all is an open lore question; the game assumes he can.
