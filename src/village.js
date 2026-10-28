import { hash, random01, valueNoise } from "./noise.js";
import { createActor, updateActor } from "./actor.js";

const TILE = 32;
const CELL = 64;
const CHANCE = 0.2;
export const RADIUS = 8;
const WANDER_RADIUS = (RADIUS - 2) * TILE;
const VILLAGER_SPEED = 22;
const TALK_RANGE = 28;
const SPEECH_SECONDS = 3.5;

const NAME_START = ["Grey", "Hollow", "Black", "Thorn", "Grave", "Mire", "Cinder", "Frost", "Ash", "Raven"];
const NAME_END = ["well", "moor", "hold", "stead", "ford", "barrow", "gate", "fen"];
const ROLES = ["peasant", "monk", "guard", "peasant"];
const LINES = {
  peasant: ["The crows eat better than we do.", "Don't drink from the well after dark.", "My son went to the battlefield. The crows came back."],
  monk: ["The runes remember what we forget.", "Pray if you like. Nothing listens.", "Every stone out there was once a promise."],
  guard: ["Keep your blade low inside the walls.", "Walls won't hold forever. Neither will I.", "Seen worse than you come through that gate."],
};

// Interior layout by tile offset from the centre. Every village has the well and the stall; the rest is picked
// per village from these slots. Hut slots are 2+ tiles apart and keep the gate column (dx = 0) clear.
const STALL = [-3, -1];
const HUT_SLOTS = [[-5, 3], [5, -2], [4, 4], [-3, -5], [5, -5], [-5, -3], [3, 6], [3, -5]];
const FIREPIT_SLOTS = [[2, 2], [-2, 3], [2, -3]];
const CRATE_SLOTS = [[-1, -2], [3, 0], [-2, 2], [-6, 0], [6, 1]];
const HUT_VARIANTS = 5;
const WALL_VARIANTS = 4;
const layouts = new Map();

// Barter: base exchange is 10 bronze per silver and 10 silver per gold, drifting ±25% per village over minutes.
const BASE_RATE = 10;
const RATE_SWING = 0.25;
const RATE_DRIFT_SECONDS = 300;
const CUT = 0.1;

// Village centre tile for a village grid cell, or null. No village in the spawn cell.
function centreIn(seed, cx, cy) {
  if ((cx === 0 && cy === 0) || random01(seed, cx, cy, 31) > CHANCE) return null;
  const h = hash(seed, cx, cy, 32);
  return { tx: cx * CELL + 16 + (h % 32), ty: cy * CELL + 16 + ((h >>> 8) % 32), key: `${cx},${cy}`, seed: h };
}

// Square distance: villages are square stockades.
const reach = (dx, dy) => Math.max(Math.abs(dx), Math.abs(dy));

// The village whose grounds (walls included, plus a margin) cover this tile.
export function villageNear(seed, tx, ty, margin = 1) {
  const centre = centreIn(seed, Math.floor(tx / CELL), Math.floor(ty / CELL));
  return centre && reach(tx - centre.tx, ty - centre.ty) < RADIUS + margin ? centre : null;
}

// [kind, variant] for a tile at offset (dx, dy) from the centre, or null.
// Seeded choice of 0..n-1 for a tile; uses the whole hash, as its low bits repeat between neighbours.
const pick = (seed, [dx, dy], n) => Math.floor(random01(seed, dx, dy, 5) * n);

// Picks `count` slots in a seeded order, so a village always looks the same.
function pickSlots(seed, salt, slots, count) {
  return [...slots].sort((a, b) => hash(seed, salt, ...a) - hash(seed, salt, ...b)).slice(0, count);
}

function layoutFor(centre) {
  if (layouts.has(centre.key)) return layouts.get(centre.key);
  const { seed } = centre;
  const layout = { "0,0": ["well", seed % 3], [STALL.join()]: ["stall", 0] };
  layout[pickSlots(seed, 1, FIREPIT_SLOTS, 1)[0].join()] = ["firepit", 0];
  for (const slot of pickSlots(seed, 2, HUT_SLOTS, 4 + (seed % 3))) layout[slot.join()] = ["hut", pick(seed, slot, HUT_VARIANTS)];
  for (const slot of pickSlots(seed, 3, CRATE_SLOTS, 2 + (seed % 2))) layout[slot.join()] = ["village_crate", pick(seed, slot, 3)];
  layouts.set(centre.key, layout);
  return layout;
}

// Walls on the square ring: varied log rows top and bottom, log lines on the sides, torch posts at the
// corners and either side of the one-tile north and south gates.
export function villageProp(centre, dx, dy) {
  if (reach(dx, dy) === RADIUS) {
    const side = Math.abs(dx) === RADIUS;
    const corner = side && Math.abs(dy) === RADIUS;
    if (!side && dx === 0) return null;
    if (corner || (!side && Math.abs(dx) === 1)) return ["palisade", 6];
    return ["palisade", side ? WALL_VARIANTS + pick(centre.seed, [dx, dy], 2) : pick(centre.seed, [dx, dy], WALL_VARIANTS)];
  }
  return layoutFor(centre)[`${dx},${dy}`] ?? null;
}

export function createVillage(seed, centre, images) {
  const h = hash(seed, centre.tx, centre.ty, 33);
  const x = centre.tx * TILE + 16;
  const y = centre.ty * TILE + 16;
  const villagers = ROLES.slice(0, 2 + (h % 3)).map((role, i) => {
    const actor = createActor(images[role], x + (i - 1) * 24, y + 40, VILLAGER_SPEED);
    return Object.assign(actor, { role, home: { x, y }, wait: 1 + i, target: null, lastLine: -1 });
  });
  const barterer = createActor(images.barterer, x + STALL[0] * TILE, y + STALL[1] * TILE - 2);
  barterer.role = "barterer";
  return {
    key: centre.key,
    name: NAME_START[h % NAME_START.length] + NAME_END[(h >>> 8) % NAME_END.length],
    x,
    y,
    seed: h,
    villagers,
    barterer,
  };
}

export const insideWalls = (village, x, y) => reach(x - village.x, y - village.y) < (RADIUS - 0.5) * TILE;

export function updateVillage(village, dt, groundAt, blocked) {
  updateActor(village.barterer, { x: 0, y: 0 }, dt, {}, () => true);
  for (const v of village.villagers) {
    if (v.speech && (v.speech.age += dt) > SPEECH_SECONDS) v.speech = null;
    let input = { x: 0, y: 0 };
    if (v.speech || v.wait > 0) {
      v.wait -= dt;
    } else if (!v.target) {
      const angle = Math.random() * Math.PI * 2;
      const dist = Math.random() * WANDER_RADIUS;
      v.target = { x: v.home.x + Math.cos(angle) * dist, y: v.home.y + Math.sin(angle) * dist, time: 6 };
    } else {
      const dx = v.target.x - v.x;
      const dy = v.target.y - v.y;
      v.target.time -= dt;
      if (Math.hypot(dx, dy) < 4 || v.target.time < 0) {
        v.target = null;
        v.wait = 1 + Math.random() * 4;
      } else {
        input = { x: Math.abs(dx) > 2 ? Math.sign(dx) : 0, y: Math.abs(dy) > 2 ? Math.sign(dy) : 0 };
      }
    }
    updateActor(v, input, dt, groundAt(v.x, v.y), blocked);
  }
}

// The barterer wins when in range, so villagers loitering at the stall don't get in the way of trade.
export function nearestVillager(village, x, y) {
  const { barterer } = village;
  if (Math.hypot(barterer.x - x, barterer.y - y) < TALK_RANGE) return barterer;
  let best = null;
  let bestDist = TALK_RANGE;
  for (const v of village.villagers) {
    const dist = Math.hypot(v.x - x, v.y - y);
    if (dist < bestDist) {
      best = v;
      bestDist = dist;
    }
  }
  return best;
}

export function talk(villager) {
  const lines = LINES[villager.role];
  villager.lastLine = (villager.lastLine + 1) % lines.length;
  villager.speech = { text: lines[villager.lastLine], age: 0 };
  villager.target = null;
}

// Grams of the cheaper metal per gram of the dearer one, drifting over time.
function rate(village, pair, time) {
  const swing = (valueNoise(village.seed + pair, time / RATE_DRIFT_SECONDS, 0) * 2 - 1) * RATE_SWING;
  return BASE_RATE * (1 + swing);
}

// Each offer: give `give` grams of one metal to receive `get` grams of another. The barterer keeps CUT.
export function offers(village, time) {
  const silver = rate(village, 1, time);
  const gold = rate(village, 2, time);
  return [
    { give: ["bronze", Math.ceil(silver / (1 - CUT))], get: ["silver", 1] },
    { give: ["silver", Math.ceil(gold / (1 - CUT))], get: ["gold", 1] },
    { give: ["silver", 1], get: ["bronze", Math.floor(silver * (1 - CUT))] },
    { give: ["gold", 1], get: ["silver", Math.floor(gold * (1 - CUT))] },
  ];
}
