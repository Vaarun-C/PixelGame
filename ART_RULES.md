# Art Rules

The art rulebook for the game. Every sprite, tile, icon, effect and UI element must follow it. Human artists and review agents both check work against this file. If a rule needs to change, change it here first, then change the art.

**The game:** a dark fantasy online pixel RPG. Players find, trade, upgrade and combine runes scattered across a ruined world. The tone is heavy, grim and violent: lone warriors, oversized steel, monsters that used to be people, and a world that has already lost.

---

## 1. Pillars

1. **The world is dead; runes are alive.** The world is desaturated (ash, iron, dried blood, rot). Runes are the *only* source of saturated color and true light. If something glows in a vivid color, it is a rune or rune-touched. This is both the mood and the core gameplay signal.
2. **Weight.** Weapons are too big, armor is too thick, monsters are too large. Silhouettes are heavy and grounded. Nothing floats or bounces cheerfully.
3. **Readable in the dark.** The mood is dark, but gameplay must never be hard to read. Characters, enemies, telegraphs and loot must separate from the background by value, not only by hue.
4. **Grim, not gory-for-its-own-sake.** Violence is implied through wear, scars, blood stains and posture. Blood is stylized and limited (see §8).

---

## 2. Technical spec

| Item | Rule |
|---|---|
| Perspective | Top-down 3/4 (camera ~45° above). Front faces and tops of objects are both visible. |
| Tile grid | **32×32 px**. All environment art snaps to this grid. |
| Player / humanoid canvas | **32×48 px**. Feet sit on the bottom 4 px; body height is ~40 px. |
| Player canvas (2× art) | **96×96 px**. Body ~88 px tall, centered; the extra width holds the oversized greatsword. Approved concept: `art/drafts/wanderer/approved/`. |
| Player attack canvas (2× art) | **128×144 px**. The 96×96 body sits bottom-centered (feet at y=142) with room above and beside it for the swing. |
| Fodder enemy canvas (2× art) | **64×96 px** (feet at y=94); attack sheets **128×112 px** with the body bottom-centered (feet at y=110). |
| Large enemy canvas | 64×64 px. |
| Boss canvas | 96×96 or 128×128 px. |
| Rune icon canvas | **16×16 px** (inventory), 32×32 px (detail/inspect view). |
| Item icon canvas | **16×16 px** (inventory), 32×32 px (detail/inspect view). |
| Scaling | Integer scaling only (2×, 3×, 4×), nearest-neighbor. Never rotate or scale sprites at non-integer factors in-engine. |
| Light direction | Key light from **top-left**. Shadows fall bottom-right. Exception: local light from runes and fire. |
| Ground shadow | Every character/enemy/prop has a flat elliptical shadow in `void-0` at 50% opacity (the only permitted alpha besides effects). |
| Pixel rules | No mixed pixel sizes. No sub-pixel or half-pixel art. No anti-aliasing against transparency (sprite edges are hard). No orphan pixels. No pillow shading. No banding. |
| Dithering | Allowed only in large backgrounds and skies (checker or ordered, 2 colors). Not on sprites smaller than 64×64. |
| Colors | Only colors from the master palette (§3), `art/palette/master.gpl`. No pure black `#000000`, no pure white `#FFFFFF`. |

### Outlines

- **Exterior outline:** 1 px `void-1` on characters, enemies and items.
- **Interior lines:** use the darkest shade of the local color ramp, never the exterior outline color.
- **Selective outlining:** on the lit (top-left) edge, the outline may switch to a dark tone of the local ramp so the form reads as lit.
- **Rim light:** player characters and enemies get a broken 1 px rim highlight on top-left edges (`bone-0`, `steel-3` or `ash-4` depending on material) so they separate from dark ground.
- **Tiles have no exterior outline.** Only props that stand up from the ground (rocks, pillars, corpses, chests) get one.

---

## 3. Palette

The master palette has **44 world colors** and **18 reserved rune colors**. The Aseprite/GIMP file is `art/palette/master.gpl`. Ramps go dark to light.

### World colors (desaturated)

| Ramp | 0 | 1 | 2 | 3 | 4 | Use |
|---|---|---|---|---|---|---|
| `void` | `#0B0A0D` | `#16141A` | `#221E26` | `#2F2A33` | | Outlines, deepest shadow, night, pits |
| `ash` | `#3D3840` | `#554E55` | `#6F676C` | `#8C8386` | `#AAA0A0` | Stone, ruins, cloth, ground, fog |
| `bone` | `#C9BCAE` | `#E3D7C3` | | | | Bone, teeth, highest highlights, parchment |
| `flesh` | `#5A3F3A` | `#7D5A4F` | `#A07B68` | `#C09C84` | | Skin (pale, tired, bruised) |
| `blood` | `#2A0F10` | `#4A1416` | `#6E1C1C` | `#922A22` | `#B0402C` | Blood, rust, red cloth, raw meat |
| `leather` | `#2B2220` | `#3F3029` | `#574234` | `#725A44` | | Leather, wood, straps, dirt |
| `rot` | `#1F2419` | `#2F3825` | `#465134` | `#5F6A45` | | Moss, swamp, decay, corrupted flesh |
| `steel` | `#2A3038` | `#3A4450` | `#5A6878` | `#8495A6` | | Armor, blades, chains, cold light |
| `ember` | `#7A3410` | `#C0601A` | `#E89A3A` | `#FFD9A0` | | Fire, torches, sparks, **enemy attack telegraphs** |
| `gilt` | `#4A3A18` | `#7A6226` | `#A88A3C` | `#CDB46A` | | Gold metal: currency clumps, gilded trim. Matte, never glowing |
| `bronze` | `#3E2616` | `#6A4226` | `#93613A` | `#B98657` | | Bronze and copper metal: currency clumps, fittings |

### Reserved rune colors (saturated, glowing)

The glow hue shows the rune's **tier**. These colors may appear **only** on runes, rune-infused gear, rune effects, rune UI and rune-corrupted creatures. Never use them for ordinary props, clothing or environment.

| Tier | Name | Dark | Mid | Core | Meaning |
|---|---|---|---|---|---|
| 1 | Pale | `#6F8A8F` | `#A9C6C8` | `#E6F4F2` | Common, barely awake |
| 2 | Azure | `#1E4F7A` | `#3D8FD1` | `#9FD8FF` | Uncommon |
| 3 | Violet | `#4A1F6E` | `#8A3FD1` | `#D6A6FF` | Rare |
| 4 | Venom | `#2F5A12` | `#7FD12A` | `#D9FF8A` | Epic |
| 5 | Gold | `#7A5410` | `#E0A82A` | `#FFF1B0` | Legendary |
| 6 | Crimson | `#5A0010` | `#E0103A` | `#FF8A9A` | Cursed / mythic. Powerful with a cost |

Gold rune yellow is bright and glowing; `gilt` metal gold is dull and matte. Silver metal uses `steel` with `bone` highlights.

Crimson rune red is bright and glowing; `blood` is dull and matte. Never put them next to each other without a `void` separation pixel.

### Saturation and value budget

- Each environment screen is ≥ 90% world colors. Rune color is a reward and should feel rare.
- Ground and floor tiles stay in `void-2` … `ash-2`. The `ash-3`, `ash-4` and `bone` values are kept for characters, highlights and points of interest, so actors are always the brightest things on a tile.
- Firelight (`ember`) is warm and local: a small radius around torches and braziers. Runes give the cold or colored light.

---

## 4. Characters

### Proportions and silhouette

- **~4.5 heads tall** within the 40 px body: grounded and adult, not chibi.
- Broad shoulders, thick limbs and visible armor bulk. Weapons may be **as tall as the character or taller** (greatswords, cleavers, poleaxes).
- Each class or archetype must be recognizable **from silhouette alone** at 1× scale.
- Faces are mostly shadowed: 1–2 px for eyes, often hidden by helmets, hoods or hair. No big expressive anime eyes.
- Wear and damage: chipped armor edges, torn cloaks, bandages, scars. Nothing looks new.

### Facings

- **4 directions:** down, up, left, right.
- **Do not mirror** left/right if the sprite has asymmetric gear (weapon hand, pauldron, scar, cape). Draw both. Mirroring is allowed only for symmetric enemies.
- All facings of one character share the exact same palette indices, proportions and foot baseline.

### Animation

| Animation | Frames | Timing | Notes |
|---|---|---|---|
| Idle | 4 | 150–200 ms | Breathing and a slight weapon sway. Heavy, slow. |
| Walk | 6 | 100 ms | Feet hit the ground on the baseline. Weapon lags behind body. |
| Run | 6 | 80 ms | Forward lean. |
| Attack (heavy) | 6–8 | variable | **Anticipation frame held 2–3× longer.** Big wind-up, fast swing, 1–2 smear frames, recovery. |
| Attack (light) | 4–5 | variable | Shorter wind-up; still has one anticipation frame. |
| Hit | 2 | 80 ms | Recoil plus a 1-frame white flash (`bone-1` silhouette fill). |
| Death | 6 | 120 ms | Collapses with weight; last frame holds. |

- **Smear frames** use the weapon's material color stretched along the arc. Rune-infused weapons smear in their rune tier color.
- Hit-stop (1–3 frame freeze on impact) is an engine effect. Do not draw it into sprites.

---

## 5. Runes (core item)

Runes are the heart of the game and must be the most polished art in it.

### Anatomy of a rune icon (16×16)

1. **Base stone:** a carved fragment (shard, disc, tablet or tooth) in `ash`, `void`, `bone` or `steel`. The base shape suggests the rune's origin region.
2. **Glyph:** the carved symbol, 1 px strokes, **angular and chiseled** (straight cuts and sharp angles, no smooth curves). **Max 6 strokes** in the 16×16 icon. The glyph is filled with the tier's `mid` color, with `core` on 1–3 key pixels.
3. **Glow:** a broken 1 px halo in the tier's `dark` color outside the stone outline. Tier 1 has no halo.
4. Leave 1 px of transparent padding on all sides.

### What changes and what stays the same

| Property | Communicates |
|---|---|
| **Glyph shape** | Rune *type* / effect school. Each type's glyph is unique and must stay recognizable at 16×16 in silhouette. |
| **Glow color** | *Tier* (§3). |
| **Upgrade level** | Notches carved along the stone edge (1 notch per level, max 5) and cracks that fill with light at higher levels. |
| **Combined runes** | Both parent glyphs fused into one symbol on a single stone, joined by a crack of light. The higher parent tier sets the glow. A fusion must still read as one symbol, not two stickers. |
| **Cursed (Crimson)** | The stone looks wrong: weeping cracks, bone or flesh growing into it, glyph strokes slightly uneven. |

### Rune animation

- Inventory/world pickup: 4-frame pulse (glow `dark` → `mid` → `core` on key pixels → `mid`), 150 ms per frame.
- World drop: the rune lights a 1-tile radius on the ground in its `dark` tier color. This is the only world light besides fire.
- Upgrade/combine VFX: shards and sparks in the tier color with a final flash on `core`. Effects can be bright here; this is the payoff moment.

### Rune-infused gear

Gear with a socketed rune shows **only small accents** in the tier color: an engraved line, a gem socket, a glowing edge on the blade. Keep the rest of the gear in world colors.

---

## 6. Environments

- **Setting:** ruined kingdoms, battlefields that never got cleared, gibbet roads, chapel ruins, swamp villages, apostate cathedrals, mountain fortresses, caverns with ancient rune walls.
- **Tiles** must tile seamlessly on the 32×32 grid. Every ground tileset needs at least 3 variants of the base tile so the ground doesn't repeat visibly.
- **Storytelling props:** broken weapons, corpses (bones, armor heaps, not graphic gore), impaled stakes, abandoned camps, faded banners, shrines with dead or faintly glowing rune slots.
- **Depth:** use value to show depth. Things farther from the action are darker and lower contrast. Foreground occluders (branches, pillars) are near-silhouette `void-1/2`.
- **Fog and atmosphere:** overlay layers in `ash` / `void` at low opacity. Effect layers are the only place besides ground shadows where alpha is allowed.
- **Rune walls/shrines** in the world use the `Pale` tier unless they are a quest or boss focal point.
- **Collision honesty:** anything that looks solid blocks movement. Walkable areas must read clearly as walkable.

---

## 7. Enemies and bosses

- **Monsters were once human or animal.** Body horror is welcome: too many teeth, fused limbs, stretched skin, armor grown into flesh. Keep it readable at sprite scale.
- **Size classes:** fodder (32×48), elite (64×64), boss (96–128 px). Bigger is more dangerous; never draw a deadly enemy small without a clear visual tell.
- **Rune-corrupted enemies** carry their rune tier color in their eyes, veins or a visible embedded rune. This tells players the enemy will drop a rune of that tier.
- **Attack telegraphs** use `ember-2` / `ember-3`: a glowing outline flash on the attacking limb or weapon, plus ground warning areas in `ember-1` at low opacity. Telegraphs must be visible against every tileset.
- **Boss phases:** phase 2 must look different, not just recolored: armor breaks off, flesh splits, a rune awakens, or the silhouette grows.
- Enemies get the same hit flash and death collapse rules as characters (§4).

---

## 8. VFX, blood and gore

- Blood splatter is pixel clusters of 2–4 px in `blood-2/3/4`. Ground decals fade out over ~10 s.
- No exposed organs or detailed dismemberment on screen. Severing can be shown with a dark silhouette and a blood burst.
- Weapon trails and impacts: steel → `steel-3` + `bone-1` spark; fire → `ember`; rune → tier color.
- Screen shake and flashes are engine effects. Keep flashes under 3 frames and never strobe (accessibility).

---

## 9. UI

- **Frame material:** dark iron and stone (`void`, `steel`, `ash`) with rivets and chipped corners. No rounded "cozy" panels.
- **Font:** pixel font only, sized to the integer scale. Body text in `bone-0` on `void-1/2`. Minimum contrast ratio 4.5:1.
- **Rune tier colors in UI** must exactly match §3 (item borders, tooltips, rarity labels). Never use rune colors for non-rune UI meaning, e.g. no green "confirm" buttons. Use `bone`/`ash` for neutral actions and `blood-4` for destructive ones.
- Health uses `blood-3/4`. Stamina uses `ash-3/4`. Resource bars must not use any rune color, so players don't confuse them with rune tiers.
- Icons are 1 px outlined in `void-1`, lit from the top-left, with the same rules as sprites.

---

## 10. Originality

The inspiration is the *tone* of dark manga and grimdark fantasy (Berserk, Dark Souls, Blasphemous). **Do not copy protected designs:**

- No recreations of named characters, the Brand of Sacrifice symbol, the Dragonslayer sword, the Skull Knight, the God Hand, Behelits, or other recognizable iconography.
- No traced or lightly edited frames from existing games or manga.
- Rune glyphs are invented for this game. Don't copy real-world runic alphabets (Elder Futhark etc.) one-to-one. Draw new glyphs that only feel ancient.

---

## 11. AI-assisted workflow rules

AI tools may generate art, but a human approves every design:

1. **Base designs are human-approved.** Every character, enemy, rune base and key prop starts from a base sprite that a human picked on a review page. It can be AI-generated (PixelLab via `tools/pixellab.py`) or hand-drawn. Approved bases live in `art/drafts/<name>/approved/` until they ship.
2. AI may produce base sprites, extra facings, animation frames, tile variants and concepts.
3. **All AI output is cleaned up before commit:**
   - Snapped to the master palette (no stray colors) with `tools/snap_palette.py`.
   - Snapped to the pixel grid at 1× (no blurry, mixed-size or half pixels).
   - Outline and rim-light rules re-applied.
   - Compared side by side with the base sprite: same proportions, palette indices, baseline and gear placement.
4. AI-generated art that fails any item in §12 does not ship.

---

## 12. Review checklist

Run this on every asset or screenshot. Mark each item **PASS** / **FAIL** / **N/A**, and note the location of every FAIL.

**Technical**
- [ ] Canvas size matches §2 for its asset type.
- [ ] Integer scale only; no blur, no mixed pixel sizes, no half pixels.
- [ ] Every color is in `master.gpl`; no `#000000` or `#FFFFFF`.
- [ ] Hard edges against transparency; no anti-aliased fringe.
- [ ] No orphan pixels, banding or pillow shading.
- [ ] Light from the top-left; shadows bottom-right.
- [ ] Exterior outline `void-1` (characters/items); interior lines use the local ramp.
- [ ] Ground shadow present (characters, enemies, standing props).

**Color and mood**
- [ ] Rune colors appear only on rune-related things.
- [ ] The scene is ≥ 90% world palette.
- [ ] Actors are the highest-value elements on screen; ground stays within `void-2` … `ash-2`.
- [ ] Crimson rune red and `blood` are separated by `void`.

**Readability**
- [ ] The subject is recognizable from silhouette at 1×.
- [ ] Characters and enemies separate from the background (rim light present).
- [ ] Enemy telegraphs are visible against the current tileset.
- [ ] A rune's tier (color) and type (glyph) are readable at 16×16.

**Consistency**
- [ ] All facings share proportions, palette indices and foot baseline.
- [ ] Asymmetric gear is not mirrored.
- [ ] Animation frame counts and anticipation holds follow §4.
- [ ] Matches the tone: worn, heavy, grim, not cute.

**Originality**
- [ ] No protected designs or symbols (§10).

---

## 13. Files and naming

```
art/
  palette/master.gpl
  characters/<name>/<name>_<anim>.png            e.g. wanderer_walk.png
  enemies/<name>/<name>_<anim>.png
  bosses/<name>/<name>_<phase>_<anim>.png
  runes/rune_icons.png                            rows = rune type, cols = tier 1-6
  items/item_icons.png                            one row of 16×16 icons
  tiles/<biome>/<biome>_ground.png                one row per ground type, base first (layout in its generator)
  props/<name>.png                                one row of 32×32 or 64×64 variants (shared across biomes); <name>_hd.png: 2x versions (64×64, large props 128×128)
  ui/
  vfx/
```

- Animation sheets: frames laid out horizontally, one row per direction (down, left, right, up), no spacing.
- Keep source files (`.aseprite`) next to the exported `.png`.
- File names: lowercase snake_case, no spaces.
