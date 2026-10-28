const ICON = 16;
export const RUNE_TYPES = {
  rend: "Sharpens the edge.",
  ward: "Hardens the flesh.",
  hunger: "Drinks from the wounded.",
};
export const TIERS = ["pale", "azure", "violet", "venom", "gold", "crimson"];
// Fused runes carry two types; their icon rows follow the three single types in this order.
export const FUSIONS = ["rend-ward", "rend-hunger", "ward-hunger"];
const TIER_WEIGHTS = [700, 200, 70, 25, 4, 1];
// Metals are counted in grams; barter will be priced by weight.
const ITEMS = {
  shard: { name: "Rune Shard", desc: "Feeds a rune's growth.", stack: 99, icon: 0 },
  scrap_blade: { name: "Rusted Blade", desc: "Snapped near the hilt.", stack: 20, icon: 1 },
  scrap_helm: { name: "Dented Helm", desc: "Its owner didn't need it.", stack: 20, icon: 2 },
  scrap_plate: { name: "Cracked Plate", desc: "Pierced through the heart.", stack: 20, icon: 3 },
  bronze: { name: "Bronze", desc: "Common metal. Traded by weight.", stack: 9999, icon: 4, unit: "g" },
  silver: { name: "Silver", desc: "Prized metal. Traded by weight.", stack: 9999, icon: 7, unit: "g" },
  gold: { name: "Gold", desc: "Rare metal. A little goes far.", stack: 9999, icon: 10, unit: "g" },
};
// Clump icons grow with weight: small below 10g, medium below 40g, then large.
const CLUMP_SIZES = [10, 40];
const METAL_DROPS = [[70, "bronze", 4, 30], [25, "silver", 2, 12], [5, "gold", 1, 5]];

const capitalize = (s) => s[0].toUpperCase() + s.slice(1);
const randInt = (min, max) => min + Math.floor(Math.random() * (max - min + 1));
const pick = (list) => list[Math.floor(Math.random() * list.length)];

function weighted(weights) {
  let r = Math.random() * weights.reduce((a, b) => a + b, 0);
  return weights.findIndex((w) => (r -= w) < 0);
}

// Keys: "bronze", "shard", "scrap_helm", ... or "rune_<types>_<tier 1-6>[_<notches>]", where <types> is
// one type or a fused pair from FUSIONS ("rend-hunger").
export const runeKey = (types, tier, notches = 0) => `rune_${types.join("-")}_${tier}${notches ? `_${notches}` : ""}`;

export function itemInfo(key) {
  const [kind, type, tier, notches = "0"] = key.split("_");
  if (kind === "rune" && TIERS[tier - 1]) {
    const types = type.split("-");
    const row = types.length > 1 ? FUSIONS.indexOf(type) + (FUSIONS.includes(type) ? 3 : -1) : Object.keys(RUNE_TYPES).indexOf(type);
    if (row < 0) return null;
    const tierName = TIERS[tier - 1];
    return {
      name: `${capitalize(tierName)} Rune of ${types.map(capitalize).join(" and ")}`,
      desc: types.map((t) => RUNE_TYPES[t]).join(" "),
      stack: 1,
      unit: "",
      color: `rune-${tierName}-mid`,
      tier: Number(tier),
      types,
      notches: Number(notches),
      sheet: "runes",
      col: tier - 1,
      row,
    };
  }
  const item = ITEMS[key];
  return item && { unit: "", ...item, color: "bone-1", sheet: "items", col: item.icon, row: 0 };
}

// size 16 draws the HUD icon; 32 draws the 2x-resolution icon from the *_hd sheet.
export function drawIcon(ctx, images, key, count, x, y, size = ICON) {
  const { sheet, col, row, unit } = itemInfo(key);
  const clump = unit ? CLUMP_SIZES.filter((grams) => count >= grams).length : 0;
  const img = images[size === ICON ? sheet : `${sheet}_hd`];
  ctx.drawImage(img, (col + clump) * size, row * size, size, size, x, y, size, size);
}

// Drop factories take the biome's loot modifiers (see biomes.js).
const tagged = (kind, make) => Object.assign(make, { kind });
const shards = (min, max) => tagged("shard", () => ({ key: "shard", count: randInt(min, max) }));
const metal = (scale) => (mods) => {
  const weights = mods.metals ?? METAL_DROPS.map(([w]) => w);
  const [, key, min, max] = METAL_DROPS[weighted(weights)];
  return { key, count: randInt(min * scale, max * scale) };
};
const scrap = () => ({ key: pick(["scrap_blade", "scrap_helm", "scrap_plate"]), count: 1 });
const rune = tagged("rune", (mods) => {
  const type = mods.runeType && Math.random() < 0.6 ? mods.runeType : pick(Object.keys(RUNE_TYPES));
  return { key: `rune_${type}_${weighted(TIER_WEIGHTS) + 1}`, count: 1 };
});
const BONUSES = { rune: "runeBonus", shard: "shardBonus" };

export const LOOT_TABLES = {
  body: { empty: 0.2, rolls: [1, 3], nothing: "Nothing but rot.", drops: [[35, shards(1, 3)], [35, metal(1)], [20, scrap], [10, rune]] },
  crate: { empty: 0.15, rolls: [2, 4], nothing: "Picked clean.", drops: [[15, shards(1, 2)], [40, metal(2)], [40, scrap], [5, rune]] },
  runestone: { empty: 0, rolls: [1, 1], nothing: "", drops: [[75, shards(2, 4)], [25, rune]] },
  chest: { empty: 0.1, rolls: [2, 3], nothing: "Only black water.", drops: [[20, shards(1, 3)], [50, metal(3)], [15, scrap], [15, rune]] },
  reliquary: { empty: 0, rolls: [1, 2], nothing: "", drops: [[50, shards(2, 5)], [50, rune]] },
  pyre: { empty: 0.25, rolls: [1, 3], nothing: "Ash and bone.", drops: [[40, shards(1, 4)], [45, metal(2)], [15, rune]] },
  tomb: { empty: 0.1, rolls: [1, 3], nothing: "The ice kept nothing.", drops: [[30, shards(1, 3)], [45, metal(2)], [10, scrap], [15, rune]] },
};

export function rollLoot(tableName, mods = {}) {
  const { empty, rolls, drops } = LOOT_TABLES[tableName];
  if (Math.random() < empty) return [];
  const weights = drops.map(([w, make]) => w * (mods[BONUSES[make.kind]] ?? 1));
  const loot = [];
  for (let i = randInt(...rolls); i > 0; i--) {
    const drop = drops[weighted(weights)][1](mods);
    const same = loot.find((item) => item.key === drop.key);
    if (same) same.count += drop.count;
    else loot.push(drop);
  }
  return loot;
}
