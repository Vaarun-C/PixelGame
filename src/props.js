// Variant counts and sheet order must match tools/gen_placeholder_props.py (the *_hd sheets: art/drafts/props/assemble.py). Spawn odds live in biomes.js.
// The anchor is the prop's ground contact point, 4px above its sprite's bottom edge.
// solid: collision box [dx, dy, w, h] from the anchor, or one box per variant.
// area: interaction box for non-solid lootables. flat: drawn under characters.
// large: 64px, only placed on even tiles so they don't overlap. spentOffset: sheet column offset once looted.
// scale: 0.5 draws a 2x-resolution sheet at native pixels; feet: anchor row in the sheet (default size - 4).
export const PROPS = {
  // Battlefield
  weapon_stuck: { sheet: "weapons_stuck_hd", size: 64, scale: 0.5, variants: 4 },
  // A slain Hollow (2x art from art/drafts/hollow/assemble.py): one variant per facing. Also left by every Hollow you kill.
  body: { sheet: "hollow_bodies", size: 96, scale: 0.5, feet: 94, variants: 4, flat: true, loot: "body", area: [-18, -16, 36, 16], glint: 10 },
  rocks: { sheet: "rocks_hd", size: 64, scale: 0.5, variants: 2, flat: true },
  boulder: { sheet: "boulders_hd", size: 128, scale: 0.5, variants: 1, solid: [-17, -8, 34, 9], large: true },
  runestone: { sheet: "runestones", size: 32, variants: 2, solid: [-5, -4, 10, 5], loot: "runestone", spentOffset: 2, glint: 18 },
  stump: { sheet: "stumps_hd", size: 64, scale: 0.5, variants: 2, solid: [-7, -4, 14, 5] },
  tree: { sheet: "trees_hd", size: 128, scale: 0.5, variants: 3, solid: [[-6, -4, 12, 5], [-9, -7, 36, 8], [-6, -4, 12, 5]], large: true },
  shield: { sheet: "shields_hd", size: 64, scale: 0.5, variants: 1, solid: [-7, -4, 14, 5] },
  crate: { sheet: "crates_hd", size: 64, scale: 0.5, variants: 4, solid: [-7, -5, 14, 6], loot: "crate", glint: 14 },
  cart: { sheet: "carts_hd", size: 128, scale: 0.5, variants: 2, solid: [-18, -10, 36, 11], loot: "crate", large: true, glint: 22 },
  stake: { sheet: "stakes_hd", size: 64, scale: 0.5, variants: 2 },
  gibbet: { sheet: "gibbets_hd", size: 128, scale: 0.5, variants: 2, solid: [-6, -3, 12, 4], large: true },
  banner: { sheet: "banners_hd", size: 128, scale: 0.5, variants: 2, large: true },
  remains: { sheet: "remains_hd", size: 64, scale: 0.5, variants: 6, flat: true },
  // Rot swamp
  swamp_tree: { sheet: "swamp_trees_hd", size: 128, scale: 0.5, variants: 4, solid: [[-6, -4, 12, 5], [-6, -4, 12, 5], [-4, -4, 12, 5], [-6, -4, 12, 5]], large: true },
  reeds: { sheet: "reeds_hd", size: 64, scale: 0.5, variants: 2 },
  drowned_chest: { sheet: "drowned_chests_hd", size: 64, scale: 0.5, variants: 2, solid: [-8, -5, 16, 6], loot: "chest", glint: 22 },
  // Chapel ruins
  pillar: { sheet: "pillars_hd", size: 128, scale: 0.5, variants: 3, solid: [[-10, -6, 22, 7], [-10, -6, 22, 7], [-22, -8, 40, 8]], large: true },
  wall: { sheet: "walls_hd", size: 128, scale: 0.5, variants: 2, solid: [[-24, -8, 46, 9], [-23, -8, 48, 9]], large: true },
  statue: { sheet: "statues_hd", size: 128, scale: 0.5, variants: 2, solid: [-12, -7, 24, 8], large: true },
  reliquary: { sheet: "reliquaries_hd", size: 64, scale: 0.5, variants: 4, solid: [-9, -5, 18, 6], loot: "reliquary", spentOffset: 4, glint: 20 },
  rubble: { sheet: "rubble_hd", size: 64, scale: 0.5, variants: 2, solid: [-8, -4, 16, 5] },
  // Ashen forest
  charred_tree: { sheet: "charred_trees_hd", size: 128, scale: 0.5, variants: 3, solid: [[-6, -4, 12, 5], [-10, -4, 20, 5], [-6, -4, 12, 5]], large: true },
  charred_stump: { sheet: "charred_stumps_hd", size: 64, scale: 0.5, variants: 2, solid: [-7, -4, 14, 5] },
  embers: { sheet: "embers_hd", size: 64, scale: 0.5, variants: 2, flat: true },
  pyre: { sheet: "pyres_hd", size: 128, scale: 0.5, variants: 1, solid: [-18, -14, 36, 12], loot: "pyre", spentOffset: 1, glint: 26, large: true },
  // Frozen pass
  frozen_tree: { sheet: "frozen_trees_hd", size: 128, scale: 0.5, variants: 2, solid: [-6, -4, 12, 5], large: true },
  cairn: { sheet: "cairns_hd", size: 64, scale: 0.5, variants: 2, solid: [-6, -4, 12, 5] },
  ice_tomb: { sheet: "ice_tombs_hd", size: 64, scale: 0.5, variants: 2, solid: [-6, -4, 12, 5], loot: "tomb", spentOffset: 2, glint: 18 },
  ice_spike: { sheet: "ice_spikes_hd", size: 64, scale: 0.5, variants: 2, solid: [-5, -3, 10, 4] },
  // Village (placed by the village layout, not by spawn odds)
  hut: { sheet: "huts", size: 64, variants: 5, solid: [[-18, -10, 36, 11], [-16, -10, 32, 11], [-28, -10, 56, 11], [-18, -10, 36, 11], [-18, -10, 36, 11]] },
  palisade: {
    sheet: "palisade",
    size: 32,
    variants: 7,
    solid: [[-16, -6, 32, 8], [-16, -6, 32, 8], [-16, -6, 32, 8], [-16, -6, 32, 8], [-4, -28, 8, 32], [-4, -28, 8, 32], [-3, -6, 6, 8]],
  },
  village_crate: { sheet: "crates_hd", size: 64, scale: 0.5, variants: 4, solid: [-7, -5, 14, 6] },
  well: { sheet: "well", size: 32, variants: 1, solid: [-9, -5, 18, 7] },
  firepit: { sheet: "firepit", size: 32, variants: 1, flat: true },
  stall: { sheet: "stall", size: 64, variants: 1, solid: [-19, -8, 38, 9] },
};

export function solidBox(prop) {
  const { solid } = prop.def;
  return Array.isArray(solid?.[0]) ? solid[prop.variant] : solid;
}
