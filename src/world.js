import { hash, random01, valueNoise } from "./noise.js";
import { PROPS, solidBox } from "./props.js";
import { BIOMES, WILD_BIOMES, VILLAGE_BIOME } from "./biomes.js";
import { villageNear, villageProp, createVillage, insideWalls } from "./village.js";
import { drawShadow, SHADOW_WIDTH } from "./actor.js";

const TILE = 32;
const GROUNDS = 4;
const FULL_TILES = [15, 16, 17, 18];
const BIOME_CELL = 48;
const LOOT_RANGE = 10;
const FEET = [-5, -3, 10, 4];
const SAFE_RADIUS = 1;
const GLINT_ARMS = [0, 1, 2, 1];
const CACHE_LIMIT = 50000;
const MAX_CORPSES = 40;
const CORPSE_FACINGS = ["down", "left", "right", "up"];

export function createWorld(images) {
  return { seed: hash(Date.now(), Math.random() * 1e9), images, loot: new Map(), villages: new Map(), terrain: new Map(), corpses: [] };
}

// Wild biome at a tile corner: nearest jittered cell centre, with the coordinates warped so borders are organic
// and a little high-frequency warp so neighbouring biomes mix in a band along the border. Spawn cell is the battlefield.
function wildBiomeAt(seed, vx, vy) {
  const wx = vx + (valueNoise(seed + 20, vx / 9, vy / 9) - 0.5) * 18 + (valueNoise(seed + 21, vx / 2.5, vy / 2.5) - 0.5) * 5;
  const wy = vy + (valueNoise(seed + 22, vx / 9, vy / 9) - 0.5) * 18 + (valueNoise(seed + 23, vx / 2.5, vy / 2.5) - 0.5) * 5;
  const cx0 = Math.floor(wx / BIOME_CELL + 0.5);
  const cy0 = Math.floor(wy / BIOME_CELL + 0.5);
  let best = 0;
  let bestDist = Infinity;
  for (let cy = cy0 - 1; cy <= cy0 + 1; cy++) {
    for (let cx = cx0 - 1; cx <= cx0 + 1; cx++) {
      const spawn = cx === 0 && cy === 0;
      const px = cx * BIOME_CELL + (spawn ? 0 : (random01(seed, cx, cy, 24) - 0.5) * 0.6 * BIOME_CELL);
      const py = cy * BIOME_CELL + (spawn ? 0 : (random01(seed, cx, cy, 25) - 0.5) * 0.6 * BIOME_CELL);
      const dist = (wx - px) ** 2 + (wy - py) ** 2;
      if (dist < bestDist) {
        bestDist = dist;
        best = spawn ? 0 : hash(seed, cx, cy, 26) % WILD_BIOMES;
      }
    }
  }
  return best;
}

// Terrain id at a tile corner: biome * GROUNDS + ground. Higher ids draw on top of lower ones.
function terrainAt(world, vx, vy) {
  const key = `${vx},${vy}`;
  let id = world.terrain.get(key);
  if (id !== undefined) return id;

  const { seed } = world;
  const biome = villageNear(seed, vx, vy, 0.5 + valueNoise(seed + 30, vx / 2, vy / 2)) ? VILLAGE_BIOME : wildBiomeAt(seed, vx, vy);
  const n = valueNoise(seed + 2, vx / 7, vy / 7) * 0.7 + valueNoise(seed + 3, vx / 3, vy / 3) * 0.3;
  const ground = valueNoise(seed + 1, vx / 4, vy / 4) > 0.86 ? 3 : n > 0.6 ? 2 : n < 0.38 ? 1 : 0;
  id = biome * GROUNDS + ground;

  if (world.terrain.size > CACHE_LIMIT) world.terrain.clear();
  world.terrain.set(key, id);
  return id;
}

const nearestCorner = (world, x, y) => terrainAt(world, Math.round(x / TILE), Math.round(y / TILE));

// Movement effect of the ground under a point: { speed, slide }.
export function groundAt(world, x, y) {
  const id = nearestCorner(world, x, y);
  return BIOMES[Math.floor(id / GROUNDS)].grounds[id % GROUNDS];
}

export function biomeAt(world, x, y) {
  return BIOMES[Math.floor(nearestCorner(world, x, y) / GROUNDS)];
}

function forTiles(tx0, ty0, tx1, ty1, fn) {
  for (let ty = ty0; ty <= ty1; ty++) {
    for (let tx = tx0; tx <= tx1; tx++) fn(tx, ty);
  }
}

function forVisibleTiles(camX, camY, w, h, margin, fn) {
  const t = (v) => Math.floor(v / TILE);
  forTiles(t(camX) - margin, t(camY) - margin, t(camX + w) + margin, t(camY + h) + margin, fn);
}

function forTilesAround(x, y, radius, fn) {
  const tx = Math.floor(x / TILE);
  const ty = Math.floor(y / TILE);
  forTiles(tx - radius, ty - radius, tx + radius, ty + radius, fn);
}

export function drawGround(ctx, world, camX, camY, w, h) {
  forVisibleTiles(camX, camY, w, h, 0, (tx, ty) => {
    const corners = [terrainAt(world, tx, ty), terrainAt(world, tx + 1, ty), terrainAt(world, tx, ty + 1), terrainAt(world, tx + 1, ty + 1)];
    const r = hash(world.seed, tx, ty);
    [...new Set(corners)].sort((a, b) => a - b).forEach((id, i) => {
      const mask = corners.reduce((m, c, bit) => (c === id ? m | (1 << bit) : m), 0);
      const col = i === 0 || mask === 15 ? FULL_TILES[(r >>> 4) % 4] : mask;
      const img = world.images[`${BIOMES[Math.floor(id / GROUNDS)].id}_ground`];
      ctx.drawImage(img, col * TILE, (id % GROUNDS) * TILE, TILE, TILE, tx * TILE - camX, ty * TILE - camY, TILE, TILE);
    });
  });
}

function makeProp(kind, variant, key, x, y) {
  return { kind, def: PROPS[kind], key, variant, x, y };
}

function propAt(world, tx, ty) {
  const { seed } = world;
  const village = villageNear(seed, tx, ty);
  if (village) {
    const placed = villageProp(village, tx - village.tx, ty - village.ty);
    return placed && makeProp(placed[0], placed[1], `${tx},${ty}`, tx * TILE + 16, ty * TILE + 28);
  }
  if (Math.abs(tx) <= SAFE_RADIUS && Math.abs(ty) <= SAFE_RADIUS) return null;

  const id = terrainAt(world, tx, ty);
  let r = random01(seed, tx, ty, 7);
  const spawns = Object.entries(BIOMES[Math.floor(id / GROUNDS)].spawns[id % GROUNDS]);
  const kind = spawns.find(([, chance]) => (r -= chance) < 0)?.[0];
  const def = PROPS[kind];
  if (!def || (def.large && (tx & 1 || ty & 1))) return null;

  const v = hash(seed, tx, ty, 9);
  const jitter = def.large ? 4 : 16;
  return makeProp(kind, v % def.variants, `${tx},${ty}`,
    tx * TILE + 16 - jitter / 2 + ((v >>> 2) % jitter),
    ty * TILE + 16 - jitter / 2 + ((v >>> 6) % jitter));
}

export function visibleProps(world, camX, camY, w, h) {
  const props = world.corpses.filter((c) => c.x > camX - TILE && c.x < camX + w + TILE && c.y > camY - TILE && c.y < camY + h + TILE);
  forVisibleTiles(camX, camY, w, h, 2, (tx, ty) => {
    const prop = propAt(world, tx, ty);
    if (prop) props.push(prop);
  });
  return props;
}

// Slain enemies leave a searchable body, using the body loot table.
// A slain Hollow's body: the last frame of its death collapse, one sheet column per facing.
export function addCorpse(world, x, y, id, facing) {
  world.corpses.push(makeProp("body", CORPSE_FACINGS.indexOf(facing), `corpse:${id}`, Math.round(x), Math.round(y)));
  if (world.corpses.length > MAX_CORPSES) world.corpses.shift();
}

// Village grounds, walls included: enemies never spawn or walk here.
export function inVillageGrounds(world, x, y) {
  return Boolean(villageNear(world.seed, Math.floor(x / TILE), Math.floor(y / TILE), 1.5));
}

const toBox = (prop, [dx, dy, w, h]) => ({ x: prop.x + dx, y: prop.y + dy, w, h });

function overlaps(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

export function blocked(world, x, y) {
  const feet = { x: x + FEET[0], y: y + FEET[1], w: FEET[2], h: FEET[3] };
  let hit = false;
  forTilesAround(x, y, 2, (tx, ty) => {
    const prop = propAt(world, tx, ty);
    const solid = prop && solidBox(prop);
    if (solid && overlaps(feet, toBox(prop, solid))) hit = true;
  });
  return hit;
}

const hasLoot = (world, prop) => Boolean(prop.def.loot) && (world.loot.get(prop.key)?.length ?? 1) > 0;

function distanceToBox(x, y, b) {
  return Math.hypot(Math.max(b.x - x, 0, x - (b.x + b.w)), Math.max(b.y - y, 0, y - (b.y + b.h)));
}

export function nearestLootable(world, x, y) {
  const props = [...world.corpses];
  forTilesAround(x, y, 2, (tx, ty) => props.push(propAt(world, tx, ty)));
  let best = null;
  let bestDist = LOOT_RANGE;
  for (const prop of props) {
    if (!prop || !hasLoot(world, prop)) continue;
    const dist = distanceToBox(x, y, toBox(prop, solidBox(prop) ?? prop.def.area));
    if (dist < bestDist) {
      best = prop;
      bestDist = dist;
    }
  }
  return best;
}

// Villages within reach of a point, created on first approach.
export function nearbyVillages(world, x, y) {
  const found = [];
  const seen = new Set();
  forTilesAround(x, y, 24, (tx, ty) => {
    if ((tx & 7) || (ty & 7)) return;
    const centre = villageNear(world.seed, tx, ty, 30);
    if (!centre || seen.has(centre.key)) return;
    seen.add(centre.key);
    if (!world.villages.has(centre.key)) world.villages.set(centre.key, createVillage(world.seed, centre, world.images));
    found.push(world.villages.get(centre.key));
  });
  return found;
}

export const villageAt = (villages, x, y) => villages.find((v) => insideWalls(v, x, y)) ?? null;

export function drawProp(ctx, world, prop, camX, camY, time, colors) {
  const { def } = prop;
  const x = prop.x - camX;
  const y = prop.y - camY;
  const looted = !hasLoot(world, prop);
  const col = prop.variant + (looted && def.spentOffset ? def.spentOffset : 0);
  const scale = def.scale ?? 1;
  const size = def.size * scale;
  const top = y - (def.feet ?? def.size - 4) * scale;
  if (!def.flat) drawShadow(ctx, x, y, ((solidBox(prop)?.[2] ?? size / 2) + 4) / SHADOW_WIDTH, colors);
  ctx.drawImage(world.images[def.sheet], col * def.size, 0, def.size, def.size, x - size / 2, top, size, size);
  if (!def.loot || looted) return;

  const phase = (time * 1000 + prop.x * 37 + prop.y * 91) % 2400;
  if (phase >= 320) return;
  const arm = GLINT_ARMS[Math.floor(phase / 80)];
  const gx = x - 2;
  const gy = y - def.glint;
  ctx.fillStyle = colors["bone-0"];
  ctx.fillRect(gx - arm, gy, arm * 2 + 1, 1);
  ctx.fillRect(gx, gy - arm, 1, arm * 2 + 1);
  ctx.fillStyle = colors["bone-1"];
  ctx.fillRect(gx, gy, 1, 1);
}
