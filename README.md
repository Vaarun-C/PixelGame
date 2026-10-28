# PixelGame

A dark fantasy pixel RPG about finding, trading, carving and fusing runes in a ruined world. Grim and heavy in tone.

**Play it in your browser: https://vaarun-c.github.io/PixelGame/**

## Controls

| Key | Action |
|---|---|
| WASD / arrows | Move (hold Shift to run) |
| Left click | Swing toward the mouse; click again mid-swing to chain the 4-hit combo |
| Space | Dodge |
| E | Search a body or crate, talk, barter |
| I / Tab | Inventory |
| Esc | Close |

In the inventory, click a rune and then a socket on the wanderer to set it. Click a socketed rune to take it out. **Carve** spends shards on a notch that strengthens a rune; **Fuse** joins two runes of different types into one.

## The game

- **A procedural world**, new each load: the Battlefield, Rot Swamp, Chapel Ruins, Ashen Forest and Frozen Pass, each with its own ground, props and loot. Rare stockade villages hold villagers and a barterer.
- **Combat**: a four-hit sword combo with a heavy finisher, dodging, hit-stop and screen shake against Hollows, husks of dead soldiers that telegraph their spear thrusts.
- **Runes**: three types (Rend, Ward, Hunger) across six tiers, from Pale to cursed Crimson. Set them into the three blade sockets and two armor sockets. Combinations in one item form **resonances** (Flay, Gorge, Bloodletting, Riposte, Leech-shell, Bulwark, Scab).
- **No coins**: bronze, silver and gold are carried and traded by weight.

Your inventory is saved in the browser (localStorage).

## Run it locally

No build step and no JavaScript dependencies. Serve the folder with any static server:

```
python3 -m http.server 8137 --bind 127.0.0.1
```

Then open http://127.0.0.1:8137.

## Art tools

The art follows [`ART_RULES.md`](ART_RULES.md): a fixed 44-colour world palette, with saturated colour reserved for runes. Sprites are drawn at 2× resolution (64×64 tiles, 96×96 hero), and the world is rendered at 2× so they keep their native pixels.

Many sprites are AI-generated with [PixelLab](https://www.pixellab.ai/), picked on review pages, snapped to the palette and cleaned up by the scripts here. Older art is procedural placeholder art.

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/check_art.py art/props/*.png      # automated art checks
.venv/bin/python art/drafts/wanderer/assemble.py          # rebuild the hero sheets
.venv/bin/python art/drafts/hollow/assemble.py            # rebuild the Hollow sheets
.venv/bin/python art/drafts/props/assemble.py             # rebuild the 2x prop sheets
.venv/bin/python art/drafts/ui/icons.py                   # rebuild the item and rune icons
```

Generating new art needs a PixelLab key in `.env` as `PIXELLAB_API_KEY=...` (ignored by git).

## Layout

```
index.html        game entry
src/              game code (ES modules): main loop, world, combat, enemies, runes, inventory, UI
art/              palette, sprites, tiles, props, icons; art/drafts holds the generation sources
tools/            Python art tools: PixelLab client, palette snapping, sprite cleanup, checks
ART_RULES.md      art rulebook
CLAUDE.md         notes for working on the code with Claude Code
```
