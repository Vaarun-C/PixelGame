class_name Biomes

# src/biomes.js. Ground rows match each biome's tile sheet, base first.
# speed: movement multiplier. slide: how quickly you can change direction (default 20; low = icy).
# dust: what a footfall kicks up (dust, grit, splashes, sparks), a shade or two lighter than the
# ground so it shows against it.
# spawns: chance per tile of each prop (see props.gd), one map per ground. Large props only roll on
# 1 in 4 tiles, so their odds are higher.
# loot: metals = bronze/silver/gold weights, runeType = favoured rune, runeBonus/shardBonus scale those drops.
# decals: average count per tile of each ground decal (see decals.gd), one map per ground.
const LIST := [
	{
		"id": "battlefield",
		"name": "The Battlefield",
		"loot": {},
		"grounds": [{"dust": ["ash-1", "ash-2"]}, {"dust": ["leather-2", "leather-3"]}, {"dust": ["rot-2", "rot-3"]}, {"dust": ["blood-2", "blood-1"]}],
		"spawns": [
			{"weapon_stuck": 0.035, "body": 0.012, "remains": 0.012, "shield": 0.01, "rocks": 0.015, "stake": 0.006, "crate": 0.004, "boulder": 0.016, "cart": 0.012, "gibbet": 0.008},
			{"rocks": 0.04, "boulder": 0.1, "runestone": 0.004, "crate": 0.008, "weapon_stuck": 0.02, "body": 0.008, "remains": 0.01, "cart": 0.02},
			{"tree": 0.16, "stump": 0.025, "rocks": 0.015, "boulder": 0.04, "weapon_stuck": 0.008, "body": 0.008, "remains": 0.012, "runestone": 0.002, "banner": 0.02},
			{"body": 0.08, "stake": 0.04, "weapon_stuck": 0.07, "remains": 0.03, "shield": 0.025, "gibbet": 0.04, "banner": 0.04},
		],
		"decals": [
			{"pebbles": 0.5, "bone_chips": 0.15, "blood_splat": 0.15, "twigs": 0.1, "dry_tuft": 0.25},
			{"pebbles": 0.3, "twigs": 0.2, "blood_splat": 0.1, "dry_tuft": 0.15},
			{"grass_tuft": 2.0, "pebbles": 0.1, "bone_chips": 0.05},
			{"blood_splat": 0.6, "bone_chips": 0.2, "pebbles": 0.1},
		],
	},
	{
		"id": "swamp",
		"name": "Rot Swamp",
		"loot": {"metals": [80, 17, 3], "runeType": "hunger"},
		"grounds": [{"dust": ["rot-1", "rot-2"]}, {"dust": ["rot-2", "rot-3"]}, {"speed": 0.65, "dust": ["steel-2", "steel-1"]}, {"speed": 0.45, "dust": ["steel-1", "steel-2"]}],
		"spawns": [
			{"swamp_tree": 0.14, "reeds": 0.03, "body": 0.01, "remains": 0.008, "stump": 0.01, "drowned_chest": 0.004, "boulder": 0.016},
			{"swamp_tree": 0.2, "reeds": 0.02, "stump": 0.02, "rocks": 0.01},
			{"reeds": 0.08, "drowned_chest": 0.01, "body": 0.01},
			{"reeds": 0.02, "drowned_chest": 0.008},
		],
		"decals": [
			{"moss": 0.4, "mushrooms": 0.15, "reed_sprig": 0.3, "grass_tuft": 0.3},
			{"grass_tuft": 1.8, "mushrooms": 0.1, "reed_sprig": 0.2},
			{"reed_sprig": 0.3},
			{},
		],
	},
	{
		"id": "ruins",
		"name": "Chapel Ruins",
		"loot": {"runeType": "ward", "runeBonus": 2.5},
		"grounds": [{"dust": ["ash-2", "ash-3"]}, {"dust": ["ash-2", "ash-1"]}, {"dust": ["rot-2", "rot-3"]}, {"dust": ["ash-0", "ash-1"]}],
		"spawns": [
			{"rubble": 0.05, "pillar": 0.08, "wall": 0.06, "boulder": 0.04, "reliquary": 0.005, "runestone": 0.006, "body": 0.006},
			{"pillar": 0.14, "statue": 0.04, "rubble": 0.03, "reliquary": 0.008, "weapon_stuck": 0.01},
			{"rubble": 0.03, "tree": 0.08, "stump": 0.015, "pillar": 0.06},
			{"rubble": 0.06, "remains": 0.02},
		],
		"decals": [
			{"pebbles": 0.6, "grass_tuft": 0.2, "bone_chips": 0.05},
			{"moss": 0.2, "pebbles": 0.2, "grass_tuft": 0.2},
			{"grass_tuft": 1.8, "pebbles": 0.1},
			{"pebbles": 0.5, "bone_chips": 0.1},
		],
	},
	{
		"id": "ashen",
		"name": "Ashen Forest",
		"loot": {"runeType": "rend", "shardBonus": 1.5},
		"grounds": [{"dust": ["ash-2", "ash-3"]}, {"dust": ["ash-0", "ash-1"]}, {"dust": ["leather-1", "ash-1"]}, {"dust": ["ember-0", "ember-1"]}],
		"spawns": [
			{"charred_tree": 0.2, "charred_stump": 0.03, "remains": 0.01, "embers": 0.015, "pyre": 0.02, "body": 0.006},
			{"charred_tree": 0.24, "charred_stump": 0.04, "embers": 0.03},
			{"charred_tree": 0.16, "charred_stump": 0.02},
			{"embers": 0.08, "pyre": 0.04, "remains": 0.02},
		],
		"decals": [
			{"ash_pile": 0.3, "twigs": 0.3, "burnt_tuft": 0.2, "embers": 0.05},
			{"twigs": 0.3, "embers": 0.1},
			{"burnt_tuft": 1.4, "twigs": 0.1},
			{"embers": 0.5},
		],
	},
	{
		"id": "frozen",
		"name": "Frozen Pass",
		"loot": {"metals": [50, 42, 8]},
		"grounds": [{"speed": 0.85, "dust": ["ash-2", "steel-3"]}, {"dust": ["ash-2", "steel-2"]}, {"slide": 2.0, "dust": ["steel-2", "steel-3"]}, {"speed": 0.9, "dust": ["leather-2", "steel-2"]}],
		"spawns": [
			{"frozen_tree": 0.12, "cairn": 0.01, "ice_tomb": 0.006, "boulder": 0.08, "ice_spike": 0.01, "body": 0.005},
			{"boulder": 0.16, "rocks": 0.05, "cairn": 0.015, "ice_spike": 0.01},
			{"ice_spike": 0.03, "ice_tomb": 0.008},
			{"frozen_tree": 0.1, "rocks": 0.03, "remains": 0.01},
		],
		"decals": [
			{"frost_tuft": 0.5, "frost_pebbles": 0.3},
			{"frost_pebbles": 0.6, "frost_tuft": 0.2},
			{"frost_pebbles": 0.1},
			{"frost_tuft": 0.3, "twigs": 0.2, "frost_pebbles": 0.2},
		],
	},
	{
		"id": "village",
		"name": "Village",
		"loot": {},
		"grounds": [{"dust": ["leather-2", "leather-3"]}, {"dust": ["rot-2", "rot-3"]}, {"dust": ["leather-3", "ash-2"]}, {"speed": 0.8, "dust": ["steel-2", "steel-1"]}],
		"spawns": [{}, {}, {}, {}],
		"decals": [{"pebbles": 0.3, "straw": 0.3, "twigs": 0.1}, {"grass_tuft": 1.8}, {"straw": 0.8}, {}],
	},
]
const WILD := 5
const VILLAGE := 5
