# Fixed World Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the endless procedural world in the Godot build with the fixed, hand-editable map of the Wake, walkable with placeholder art.

**Architecture:** Python design scripts export the agreed layout at tile resolution. A one-off Godot tool bakes it into 64 compressed region scenes (paint layers + prop markers) plus one places scene. At runtime a `WorldMap` reads those scenes lazily and the existing `Terrain` functions answer from it instead of noise, so chunk streaming, dual-grid ground, decals, props and villages keep working. The noise world stays for the prologue and `--biome` playtests.

**Tech Stack:** Godot 4 (GDScript, headless tools), Python 3 in `.venv` (Pillow, NumPy).

**Spec:** `docs/superpowers/specs/2026-11-05-fixed-world-map-design.md`

## Global Constraints

- CLAUDE.md code style: KISS, DRY, small functions, few comments (only the *why*), no drive-by refactors.
- Art: colours only from `art/palette/master.gpl`; no pure black or white; run `.venv/bin/python tools/check_art.py <files>` after any art change, then the `art-reviewer` agent.
- Art is generated into `art/…` and copied to the same path under `godot/art/…`.
- Tools run with `.venv/bin/python`. NumPy is used by the design scripts but is not in `requirements.txt`: ask the user before adding it (CLAUDE.md: no new dependencies without asking).
- Map size: 2000 × 2000 tile corners, corner (0, 0) at the design's top-left. Outside that range is deep water.
- Regions: 8 × 8, each 250 × 250 corners, `res://world/regions/r_<rx>_<ry>.scn`, saved with `ResourceSaver.FLAG_COMPRESS`.
- Terrain id = biome × 4 + ground. New biome indices: 6 fallow, 7 woods, 8 mountain, 9 cinder, 10 water, 11 road. `Biomes.WILD` stays 5 (the noise world only uses the first five).
- The noise world is used when `Terrain.only_biome >= 0` (prologue scene `biome = 1`, playtest `--biome`). `main.tscn` (biome 0) uses the fixed map.
- Commit steps: ask the user before each commit (harness rule: commit only when asked).

## Review Focus

1. **Zone titles on roads and rivers:** crossing a road or stream must not flash a "Road"/"Water" title. Road and water biomes have `"name": ""` and the interface keeps the current zone when the name is empty (Task 5 test).
2. **Walking off the map edge:** corners outside 0–1999 read as deep water, so the player is stopped by collision, never sees missing tiles (Task 3 test).
3. **Hollows on unreachable ledges:** a spawn spot across a cliff or river from the player is rejected (Task 5 test).
4. **Villages spanning region or cell borders:** a village whose outline crosses a 64-tile cell or a region edge still draws walls, ground and people whole (Task 5 test with Thornstead and Greywell).
5. **Loading hitch:** first entry into a region loads its scene; it must finish under 300 ms on the dev machine (Task 3 timing check), or the loader must be moved off the frame.

---

### Task 1: Design scripts and export

**Files:**
- Create: `tools/world_design/` (move `horseshoe.py`, `elevation.py`, `veg.py`, `water.py`, `landmarks.py`, `cliffs.py` from `/private/tmp/claude-501/-Users-varun-base-PixelGame/601cfd6f-496d-45be-ac33-8225192e03cb/scratchpad/`; keep their PNG outputs in `tools/world_design/maps/`)
- Create: `tools/world_design/export.py`
- Create: `tools/world_design/check_export.py`
- Output (git-ignored): `tools/world_design/out/terrain.png`, `level.png`, `ramp.png`, `places.json`

**Interfaces:**
- Produces: three 2000 × 2000 8-bit greyscale PNGs, pixel = value at that tile corner: terrain id (0–47), level (0–5, 0 = water), ramp (0/1). `places.json`: `[{"kind": "village"|"shrine"|"chapel"|"prisoner"|"crossroads"|"mother_house"|"prologue", "name": str, "tile": [x, y], "start": bool}]`; Greywell has `"start": true`.

- [ ] **Step 1: Move the design scripts** into `tools/world_design/`, change their outputs to `maps/`, and make `water.py`, `veg.py`, `landmarks.py` and `cliffs.py` importable without side effects (wrap the drawing in `if __name__ == "__main__":`). Run `.venv/bin/python tools/world_design/cliffs.py` and confirm it prints `reachable 77% of walkable land`.

- [ ] **Step 2: Write `check_export.py`** with these asserts on the `out/` files:
  - each PNG is 2000 × 2000, mode `L`; terrain values < 48, level ≤ 5, ramp ∈ {0, 1};
  - every corner with level 0 has a water-biome terrain id (40–43);
  - `places.json` has 5 villages, 6 prisoners, 3 chapels, 7 shrines, exactly one `start`;
  - every place tile is walkable (terrain ground not solid, see Step 3 list) and every village is reachable from the start by a 4-neighbour flood fill over walkable corners where a level change is allowed only on a ramp corner.

- [ ] **Step 3: Run it to see it fail** (`.venv/bin/python tools/world_design/check_export.py` → `FileNotFoundError`).

- [ ] **Step 4: Implement `export.py`.** Upscale ×4 from the 500 px design: sample zone and level at `(x/4 + j(x, y), y/4 + j(y, x))` where `j` is smooth noise of amplitude 1.5 design px, so borders don't step. Then map zones to terrain:

  | Zone / feature | Biome | Grounds used |
  |---|---|---|
  | Fen | swamp (1) | 0 base, 2 mud where noise > 0.6, 3 pools where > 0.85 |
  | The Long Field | battlefield (0) | 0, 1, 3 by noise as the noise world does |
  | Fallow fields | fallow (6) | 0 dry grass, 1 thistle, 2 furrows, 3 bare earth |
  | Dead woods | woods (7) | 0 litter, 1 moss, 2 roots; 3 thicket (solid) for wood cores (≥ 8 tiles inside) |
  | Court grounds | ruins (2) | as the noise world |
  | Frost pines | frozen (4) | as the noise world |
  | Bare mountain | mountain (8) | 3 crag (solid) everywhere, except 0 scree / 1 snow within 4 tiles of the Pass road |
  | Ashen Forest | ashen (3) | as the noise world |
  | Cinder peak | cinder (9) | 0 scorched, 1 ash, 2 cracked |
  | Deep water (sea, Mere, lakes) | water (10) | 0 deep (solid) |
  | Rivers (flow > 900) | water (10) | 1 river (solid), 4–8 tiles wide by flow |
  | Streams | water (10) | 3 stream (slow), 2 tiles wide |
  | Shallows within 2 tiles of shore | water (10) | 2 shallow (slow) |
  | Roads | road (11) | 0 dirt, 3 tiles wide; 1 cobbles within 40 tiles of the Old Court; 2 causeway over shallow/deep water; 3 bridge over rivers |

  Rasterise rivers, streams and roads from the smoothed polylines the design already draws. Ramp = 1 on both corners of every level edge the design's `edge_open` allows, and along roads. Write `places.json` from `landmarks.py`'s tables (tiles ×4).

- [ ] **Step 5: Run the check** → `export OK` with no assertion errors.

- [ ] **Step 6: Commit** `tools/world_design/` (not `out/`; add `tools/world_design/out/` to `.gitignore`).

### Task 2: Placeholder art and biome definitions

**Files:**
- Modify: `tools/gen_ground_hd.py` (`BIOMES`: add `fallow`, `woods`, `mountain`, `cinder`, `water`, `road`)
- Create: `tools/gen_cliffs_hd.py` → `art/tiles/cliffs/cliffs_hd.png`
- Modify: `godot/scripts/world/biomes.gd` (`LIST` entries 6–11)
- Modify: `godot/tools/build_tileset.gd` (also build `res://tiles/cliffs.tres`)
- Create: `godot/tools/world_check.gd` (headless checks, grows in later tasks)

**Interfaces:**
- Produces: `Biomes.LIST[6..11]` with `id` `fallow`, `woods`, `mountain`, `cinder`, `water`, `road`; each ground dict may carry `"solid": true`. Solid grounds: water 0, 1; woods 3; mountain 3. Slow grounds: water 2 and 3 `"speed": 0.6`. `name`: "Fallow Fields", "Dead Woods", "The White Teeth", "Cinder Peak", "" (water), "" (road).
- Produces: `res://tiles/cliffs.tres`, one atlas source, 64 px tiles, column = 4-bit mask of upper corners (bit order as `world.gd paint_tile`: top-left 1, top-right 2, bottom-left 4, bottom-right 8), row 0 cliff, row 1 ramp.

- [ ] **Step 1: Write the failing check** in `world_check.gd`: `Biomes.LIST.size() == 12`; every entry has 4 `grounds`, 4 `spawns`, 4 `decals`; `load("res://tiles/ground.tres").get_source_count() == 12`; `load("res://tiles/cliffs.tres")` has a tile at `(15, 1)`. Print `world_check OK` at the end, `FAIL <what>` on each failure.
- [ ] **Step 2: Run** `godot --headless --path godot -s tools/world_check.gd` → FAIL lines.
- [ ] **Step 3: Add the six ground specs** to `gen_ground_hd.py` using existing features and palette ramps (fallow: leather/rot ramps with `grass` and `strokes`; woods: void/rot with `blots`, thicket darkest; mountain: steel/ash with `stones`, `cracks`, snow from the lightest steel; cinder: void/ash/ember with `cracks`, `sparks`; water: void/steel with `ripples`; road: leather with `stones`, `flagstones` for cobbles, planks via `strokes` for bridge). Run it, copy the sheets to `godot/art/tiles/<id>/`.
- [ ] **Step 4: Write `gen_cliffs_hd.py`:** for each of 16 masks a 64 px tile; cliff row draws a rock face (steel/ash ramp, lit top-left) on the lower side of the boundary between upper and lower corners and a 2 px rim on other sides; ramp row draws stepped earth at the same boundary. Copy to `godot/art/tiles/cliffs/`.
- [ ] **Step 5: Add `Biomes.LIST` entries 6–11** with spawns (fallow: sparse `tree`, `stump`, `rocks`, `remains`, `crate`; woods: dense `tree` and `stump`, ground 3 `tree` 0.6; mountain: `boulder`, `rocks`, `cairn`; cinder: `charred_stump`, `rocks`, `embers`; water and road: none), decals from existing kinds, loot `{}`.
- [ ] **Step 6: Extend `build_tileset.gd`** to build `tiles/cliffs.tres` from `art/tiles/cliffs/cliffs_hd.png`; run it.
- [ ] **Step 7: Run** `world_check.gd` → `world_check OK`; `rune_check.gd` → `FAILS 0`; `check_art.py` on all new PNGs → clean. Dispatch the `art-reviewer` agent on the new sheets and fix what it fails.
- [ ] **Step 8: Commit.**

### Task 3: WorldMap and the baker

**Files:**
- Create: `godot/scripts/world/world_map.gd`
- Create: `godot/scripts/world/prop_marker.gd` (`@tool`, editor preview of a prop)
- Create: `godot/scripts/world/place_marker.gd` (`@tool`, editor label of a place)
- Create: `godot/tools/build_world.gd`
- Modify: `godot/scripts/world/terrain.gd`
- Output: `godot/world/regions/r_*.scn` (64), `godot/world/places.tscn`, `godot/world/swatches.tres` + `swatches.png`

**Interfaces:**
- Consumes: Task 1 export, Task 2 biomes.
- Produces (`class_name WorldMap extends RefCounted`):
  - `const SIZE := 2000`, `const REGION := 250`
  - `static var active: WorldMap` (null → noise world)
  - `static func from_export(dir: String) -> WorldMap` (reads the three PNGs; builder only)
  - `static func from_scenes() -> WorldMap` (lazy: regions load on first query; loads `places.tscn` at once)
  - `func terrain(vx: int, vy: int) -> int` (outside → 40, deep water)
  - `func level(vx: int, vy: int) -> int`, `func ramp(vx: int, vy: int) -> bool`
  - `func prop(tx: int, ty: int) -> Dictionary` (`{kind, variant, pos}` or `{}`)
  - `func places(kind := "") -> Array` (`[{kind, name, tile: Vector2i, start: bool}]`)
  - `func walkable(tx: int, ty: int) -> bool`: false if ≥ 2 of the tile's corners are on solid grounds, or its corners' levels differ and none is a ramp
  - `func reachable(a: Vector2i, b: Vector2i, limit: int) -> bool`: 4-neighbour BFS over `walkable` tiles, giving up after `limit` tiles
- Produces (`Terrain`): `terrain_at` returns `WorldMap.active.terrain()` when active (the village override stays); `prop_at` returns the village prop, else `WorldMap.active.prop()`; the old procedural body becomes `static func roll_prop(tx: int, ty: int) -> Dictionary`.
- Region scene layout: root `Node2D` named `Region`, children `Terrain`, `Level`, `Ramp` (`TileMapLayer` on `swatches.tres`, cell = corner, atlas coords `(value, row)`, rows 0 terrain / 1 level / 2 ramp, positioned −32 px so swatches sit on corners; `Level` and `Ramp` modulate alpha 0.4), and `Props` (`PropMarker` nodes: `@export var kind: String`, `@export var variant: int`, position in Godot px).
- `places.tscn`: root `Node2D`, `PlaceMarker` children: `@export var kind`, `@export var place_name`, `@export var start := false`, position = tile centre in Godot px.

- [ ] **Step 1: Extend `world_check.gd`** with WorldMap checks against the baked scenes: `WorldMap.from_scenes()`; `places("village").size() == 5`; the start village's tile is walkable; a tile 3 tiles east of Greywell on the King's Road is walkable; `terrain(-5, -5) == 40` and `walkable(-5, -5) == false`; the tile at the Long Field river crossing beside the crossroads (from `places.json` crossroads + the bridge found by scanning for road ground 3 within 20 tiles) is walkable while the river tile next to it is not; `reachable(start, start + Vector2i(30, 0), 4000)` is true; loading one region takes < 300 ms (`Time.get_ticks_msec` around the first `terrain()` call in a fresh region).
- [ ] **Step 2: Run** → FAIL (no `WorldMap`).
- [ ] **Step 3: Implement `world_map.gd`** with per-region `PackedByteArray`s (terrain, level, ramp) filled from images (`from_export`) or from the three layers (`from_scenes`, `get_cell_atlas_coords` per used cell, empty cell = value 0), and a per-region `{Vector2i tile: prop}` dictionary from the `Props` children.
- [ ] **Step 4: Implement `prop_marker.gd` and `place_marker.gd`** (`@tool`; in the editor `PropMarker` draws its sprite frame like `Prop.create` does, `PlaceMarker` draws its name).
- [ ] **Step 5: Implement `build_world.gd`** (run: `godot --headless --path godot -s tools/build_world.gd -- <abs path to tools/world_design/out>`): make `swatches.png` (terrain swatch = average colour of that ground's full tile in its HD sheet; level swatches an ash ramp; ramp swatch `gilt-2`) and `swatches.tres`; set `WorldMap.active = WorldMap.from_export(dir)`; for each region fill the three layers and add a `PropMarker` for every tile where `Terrain.roll_prop` returns a prop and no village is within 16 tiles; save each with `ResourceSaver.FLAG_COMPRESS`; write `places.tscn` from `places.json`.
- [ ] **Step 6: Switch `Terrain.terrain_at` / `prop_at`** to the active map as in Interfaces.
- [ ] **Step 7: Run the baker, then** `world_check.gd` → `world_check OK`; report the total size of `godot/world/`.
- [ ] **Step 8: Commit** (scripts and `godot/world/`).

### Task 4: Cliffs and water in play

**Files:**
- Modify: `godot/scripts/world/world.gd` (`_ready`, `load_chunk`, `unload_chunk`, `paint_tile`)
- Modify: `godot/scripts/world/terrain.gd` (`blocked`)

**Interfaces:**
- Consumes: `WorldMap.active`, `walkable`, `level`, `ramp`; `tiles/cliffs.tres`.
- Produces: `World._ready` sets `WorldMap.active = WorldMap.from_scenes()` when `biome == 0`, else null; a fifth `TileMapLayer` (`cliff_layer`, `z_index = -6`); per chunk one `StaticBody2D` with a 64 × 64 `RectangleShape2D` per tile where `walkable` is false, freed with the chunk; `Terrain.blocked(pos)` also returns true on a non-walkable tile.

- [ ] **Step 1: Extend `world_check.gd`:** instance `main.tscn`, put the player beside the river tile from Task 3, run 60 physics frames walking into it, assert the player didn't cross; same against a cliff tile next to Court Hill's base found by scanning `level` for a non-ramp edge; `Terrain.blocked()` is true on that cliff tile.
- [ ] **Step 2: Run** → FAIL (player crosses).
- [ ] **Step 3: Implement** the world changes: in `paint_tile` when the map is active and the tile's corner levels differ, set the cliff layer cell to `(mask of corners at the highest level, 1 if any corner is a ramp else 0)`; build the chunk's collision in `load_chunk`.
- [ ] **Step 4: Run** `world_check.gd` → OK; `rune_check.gd` → `FAILS 0`.
- [ ] **Step 5: Commit.**

### Task 5: Villages, start, spawning, titles, playtest tool

**Files:**
- Modify: `godot/scripts/world/villages.gd` (`centre_in`, `near`, `start_position`)
- Modify: `godot/scripts/world/world.gd` (`add_village`: use `village.name` when set)
- Modify: `godot/scripts/world/terrain.gd` (new `static func reachable(a: Vector2, b: Vector2) -> bool`, true when no map)
- Modify: `godot/scripts/main.gd` (`_physics_process` spawn check)
- Modify: `godot/scripts/ui/interface.gd` (`_process` zone title)
- Modify: `godot/tools/playtest.gd` (`village:` step, new `place:NAME:DX:DY` step, header comment)

**Interfaces:**
- Consumes: `WorldMap.places("village")`, `reachable`.
- Produces: with the map active, `Villages.near(seed, tx, ty, margin)` checks every authored village (not just the tile's cell) and returns `{tx, ty, key: Vector2i(tx, ty), seed: hash of name, name}`; `centre_in` returns the village whose centre lies in that cell, or `{}`; `start_position()` returns the start village's centre (Godot px) + `ARRIVAL`. Spawning rejects spots where `Terrain.reachable(at, player.position)` is false (BFS limit 1500 tiles).

- [ ] **Step 1: Extend `world_check.gd`:** `Villages.near` finds Greywell from a tile 10 tiles outside its centre in each direction; `Villages.start_position()` lies inside Greywell's walls; `Terrain.reachable()` is false between the two banks of the Long Field river 200 tiles away from any bridge, true between two fallow tiles 20 apart; `interface.next_zone("")` returns the current zone and `next_zone("Fallow Fields")` returns "Fallow Fields".
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** the files above; in `interface.gd` add `func next_zone(name: String) -> String` (the new name, or the current `zone` when empty) and use it in `_process`.
- [ ] **Step 4: Run** `world_check.gd` → OK; `rune_check.gd` → `FAILS 0`.
- [ ] **Step 5: Playtest** with `godot --path godot --script tools/playtest.gd -- --out <scratchpad>/world --steps "wait:2 shot:greywell place:crossroads:0:40 wait:1 shot:crossroads place:Court_Chapel:0:200 wait:1 shot:court place:Ashbarrow:0:300 wait:1 shot:causeway hold:d:2 shot:cliff"` and look at every shot: ground blends, cliff faces, bridge, causeway, villages whole, no holes at chunk edges. Fix what's wrong.
- [ ] **Step 6: Dispatch the `playtester` agent** on the fixed map (Greywell, a river, a cliff, the Pass road) and fix its findings that belong to this plan.
- [ ] **Step 7: Update `CLAUDE.md`** (Run/Layout: the world is now fixed; how to re-export, bake, and edit regions in the editor; enable the editor setting *FileSystem → On Save → Compress Binary Resources* so hand edits stay small).
- [ ] **Step 8: Commit.**
