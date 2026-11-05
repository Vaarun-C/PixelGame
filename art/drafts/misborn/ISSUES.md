# Misborn: open art issues

From the art review of the PixelLab bite and flail (2026-11-05). Frames are in `snapped/<anim>/`; rebuild with `assemble.py`.

## Both attacks
- The brass harness fittings and the red chest wound fade out in the second half (bite 7–12, flail 5–13), then pop back when the loop returns to frame 0. Likely fix: paste the still parts (hind legs, harness fittings, wound, boot) from `keys/rest.png` into every frame.

## Flail
- Frames 5–7: the head disappears into a rounded hump, and the body turns lighter and browner (void pixels drop from 27% to 13%). Needs a key pose with the head visible during the swing, and those frames darkened back toward the base.
- Frames 1–5: the raised foreleg grows from the neck (from the muzzle in frame 1) instead of the shoulder or chest.
- Frames 1–3: the right hind hoof lifts 1 px (row y=157 is empty).
- The whole flail is lighter and browner than the bite.

## Bite
- Frames 5–8: the head turns a little reptile-like, with longer jaws and large bone-coloured eye whites. Check that it still reads as the same horse.

## Death
- The harness fittings, chest wound and boot vanish from frame 1 on instead of going down with the body (same cause as above).
- Frames 4–6: the body hangs in the air on one or two hooves, reading as a jump; the fall pauses between 5 and 6 and has no impact frame. Put the hindquarters down first.
- Frame 8 (also the body prop, `art/props/misborn_body.png`) is lighter than the rest, and it lies on its belly with legs folded, like a resting horse rather than one crashed onto its side. A stiff leg or a stretched-out neck would read as dead.
- 9 frames against ART_RULES §4's 6 for a death; the reviewer suggests keeping 0, 2, 4, 5, 7, 8.

## Not yet decided
- ART_RULES has no canvas size for elite attacks: walk and idle use 128×128 (feet at y=125), the attacks 160×160 (feet at y=157).

## In the game (godot/scripts/misborn.gd)
- Drawn facing south only: it faces the camera whichever way it walks or strikes.
- Lurch (knees giving out for 0.8 s) isn't in: it has no animation.
- The hammer doesn't knock the Wanderer down: the player has no knockdown yet.
- `check_art.py` fails its 160×160 attack and death sheets (no elite attack canvas in ART_RULES, above).
