// Ground rows match each biome's tile sheet (tools/gen_placeholder_terrain.py), base first.
// speed: movement multiplier. slide: how quickly you can change direction (default 20; low = icy).
// spawns: chance per tile of each prop (see props.js), one map per ground. Large props only roll on
// 1 in 4 tiles, so their odds are higher.
// loot: metals = bronze/silver/gold weights, runeType = favoured rune, runeBonus/shardBonus scale those drops.
export const BIOMES = [
  {
    id: "battlefield",
    name: "The Battlefield",
    grounds: [{}, {}, {}, {}],
    spawns: [
      { weapon_stuck: 0.035, body: 0.012, remains: 0.012, shield: 0.01, rocks: 0.015, stake: 0.006, crate: 0.004, boulder: 0.016, cart: 0.012, gibbet: 0.008 },
      { rocks: 0.04, boulder: 0.1, runestone: 0.004, crate: 0.008, weapon_stuck: 0.02, body: 0.008, remains: 0.01, cart: 0.02 },
      { tree: 0.16, stump: 0.025, rocks: 0.015, boulder: 0.04, weapon_stuck: 0.008, body: 0.008, remains: 0.012, runestone: 0.002, banner: 0.02 },
      { body: 0.08, stake: 0.04, weapon_stuck: 0.07, remains: 0.03, shield: 0.025, gibbet: 0.04, banner: 0.04 },
    ],
    loot: {},
  },
  {
    id: "swamp",
    name: "Rot Swamp",
    grounds: [{}, {}, { speed: 0.65 }, { speed: 0.45 }],
    spawns: [
      { swamp_tree: 0.14, reeds: 0.03, body: 0.01, remains: 0.008, stump: 0.01, drowned_chest: 0.004, boulder: 0.016 },
      { swamp_tree: 0.2, reeds: 0.02, stump: 0.02, rocks: 0.01 },
      { reeds: 0.08, drowned_chest: 0.01, body: 0.01 },
      { reeds: 0.02, drowned_chest: 0.008 },
    ],
    loot: { metals: [80, 17, 3], runeType: "hunger" },
  },
  {
    id: "ruins",
    name: "Chapel Ruins",
    grounds: [{}, {}, {}, {}],
    spawns: [
      { rubble: 0.05, pillar: 0.08, wall: 0.06, boulder: 0.04, reliquary: 0.005, runestone: 0.006, body: 0.006 },
      { pillar: 0.14, statue: 0.04, rubble: 0.03, reliquary: 0.008, weapon_stuck: 0.01 },
      { rubble: 0.03, tree: 0.08, stump: 0.015, pillar: 0.06 },
      { rubble: 0.06, remains: 0.02 },
    ],
    loot: { runeType: "ward", runeBonus: 2.5 },
  },
  {
    id: "ashen",
    name: "Ashen Forest",
    grounds: [{}, {}, {}, {}],
    spawns: [
      { charred_tree: 0.2, charred_stump: 0.03, remains: 0.01, embers: 0.015, pyre: 0.02, body: 0.006 },
      { charred_tree: 0.24, charred_stump: 0.04, embers: 0.03 },
      { charred_tree: 0.16, charred_stump: 0.02 },
      { embers: 0.08, pyre: 0.04, remains: 0.02 },
    ],
    loot: { runeType: "rend", shardBonus: 1.5 },
  },
  {
    id: "frozen",
    name: "Frozen Pass",
    grounds: [{ speed: 0.85 }, {}, { slide: 2 }, { speed: 0.9 }],
    spawns: [
      { frozen_tree: 0.12, cairn: 0.01, ice_tomb: 0.006, boulder: 0.08, ice_spike: 0.01, body: 0.005 },
      { boulder: 0.16, rocks: 0.05, cairn: 0.015, ice_spike: 0.01 },
      { ice_spike: 0.03, ice_tomb: 0.008 },
      { frozen_tree: 0.1, rocks: 0.03, remains: 0.01 },
    ],
    loot: { metals: [50, 42, 8] },
  },
  {
    id: "village",
    name: "Village",
    grounds: [{}, {}, {}, { speed: 0.8 }],
    spawns: [{}, {}, {}, {}],
    loot: {},
  },
];

export const WILD_BIOMES = 5;
export const VILLAGE_BIOME = 5;
