# CLAUDE.md

A dark fantasy online pixel RPG. Players find, trade, upgrade and combine runes scattered across a ruined world. The tone is grim and heavy, Berserk-like.

## Code style

- **Keep it simple (KISS).** Choose the most straightforward solution that works. No speculative abstractions, frameworks or config for needs we don't have yet.
- **Don't repeat yourself (DRY).** Before writing new code, look for an existing helper and reuse or extend it. Extract shared logic once it's used twice.
- **Small over big.** Never write 500 lines when 100 will do. If a change is getting long, stop and look for a simpler approach.
- **Few comments.** Code should explain itself through clear names. Comment only the *why* of something non-obvious. No comments that restate the code, no commented-out code, no banner comments.
- Readable code over clever code. Short functions, early returns, flat control flow.
- Only change what the task needs. No unrelated refactors or drive-by "improvements".
- Don't add dependencies without asking.

## Art

All art follows **`ART_RULES.md`**. Read it before creating, generating, editing or describing any visual asset. Key points:

- 32×32 tile grid, 32×48 characters, top-down 3/4 view, light from the top-left, integer scaling only.
- Colors only from `art/palette/master.gpl`. No pure black or white.
- The world is desaturated. **Rune colors are reserved for runes**: glow color = tier, glyph shape = type.
- Heavy, worn, grim silhouettes. Never cute or chibi.
- No copying protected Berserk or other IP designs (§10).
- AI-assisted art must be cleaned up and palette-snapped before commit (§11).

### Review

- After any art change, run `.venv/bin/python tools/check_art.py <files>`, then use the **`art-reviewer`** agent for the full checklist review.
- Gameplay code that touches visuals (colors in UI, VFX, rune rarity display) must use the palette and tier colors from `ART_RULES.md`, never ad-hoc hex values.

## Setup

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Add Python dependencies to `requirements.txt` and always run tools with `.venv/bin/python`.

## Run

```
python3 -m http.server 8137 --bind 127.0.0.1   # then open http://127.0.0.1:8137 (8000 is taken)
```

Browser game in plain JavaScript (ES modules) on a canvas. No build step and no JS dependencies. Controls: WASD/arrows to move, Shift to run, left click to swing (toward the mouse; click again mid-swing to chain the 4-hit combo), Space to dodge, E to search / talk / barter, I/Tab for inventory (click a rune, then a socket to set it; click a socketed rune to take it out; Carve and Fuse spend shards), click to trade (Shift-click x10), Esc to close. The world is procedural with a new seed each load (biomes as large regions, villages rare); the inventory persists in localStorage.

Regenerate placeholder art: `.venv/bin/python tools/gen_placeholder_<character|terrain|props|items>.py`

Rebuild the HD sheets from the chosen PixelLab drafts: `.venv/bin/python art/drafts/wanderer/assemble.py` (player) and `.venv/bin/python art/drafts/hollow/assemble.py` (Hollow); battlefield props (`*_hd` sheets in art/props): `art/drafts/props/fix_stuck.py`, `combine_tree.py`, then `assemble.py`

## Layout

```
ART_RULES.md          art rulebook (source of truth for visuals)
index.html            game entry
src/main.js           loop, camera, asset loading, interaction (search / talk / barter)
src/actor.js          movement + animation shared by the player, villagers and enemies; HIGH_RES frames for 2x sprites
src/combat.js         sword combo (tuning table COMBO), dodge, attack animation playback (ATTACK_FRAMES)
src/enemies.js        Hollows: spawning, AI, damage, spear-thrust and death animations (corpse prop: body)
src/effects.js        hit-stop, screen shake, particles, flash tints
src/world.js          biome regions, ground (dual-grid autotiling across biomes), prop placement, collision
src/biomes.js         biome definitions: ground effects, spawn odds per ground, loot modifiers
src/props.js          prop definitions (sheets, collision boxes, loot)
src/village.js        village placement, stockade layout, villagers, dialogue, barter rates
src/barter.js         barter panel and metal trades
src/items.js          item definitions, loot tables, icons
src/runes.js          rune sockets, passives, resonances, carving and fusing, rune combat hooks
src/inventory.js      inventory slots, stacking, save, panel (2x-resolution style A: bag, rune sockets, detail, summary)
src/ui.js             frames (incl. the 2x iron frame), tooltips, prompts, pickup messages
src/font.js           3x5 HUD font and 5x7 font for the 2x UI
src/noise.js          hash + value noise
src/input.js          keyboard + mouse input
art/                  assets; folder structure in ART_RULES.md §13
tools/check_art.py    automated art checks
tools/pixel.py        shared helpers for the placeholder art generators
tools/pixellab.py     PixelLab API: generate and edit sprites (key in .env as PIXELLAB_API_KEY)
tools/snap_palette.py snap AI output to the master palette, drop stray pixels
tools/cleanup_sprite.py   automated ART_RULES fixes for snapped AI sprites (noise, cape ramp, wear, outline)
tools/build_sheet.py  assemble frames into a sprite sheet (one row per facing: down, left, right, up)
art/drafts/ui/          inventory mockups (mockup.py), 5x7 font source (font5x7.py), icons.py builds the 32px item/rune icon sheets
tools/ground_tiles.py seamless 64px ground tiles and corner-mask bank overlays from a texture patch (draft, unused)
tools/gen_placeholder_*.py   placeholder character, terrain, prop and item art
requirements.txt      Python dependencies (.venv)
.claude/agents/       art-reviewer agent
```
