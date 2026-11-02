class_name Items

# src/items.js: item definitions, rune keys, icons and loot tables.
# Keys: "bronze", "shard", "scrap_helm", ... or "rune_<types>_<tier 1-6>[_<notches>]", where <types> is
# one verb or a fused pair in RuneBook.ORDER ("rend-hunger").
const TIERS := ["pale", "azure", "violet", "venom", "gold", "crimson"]
const TIER_WEIGHTS := [700, 200, 70, 25, 4, 1]
# Metals are counted in grams; barter is priced by weight.
const LIST := {
	"shard": {"name": "Rune Shard", "desc": "Feeds a rune's growth.", "stack": 99, "icon": 0},
	"scrap_blade": {"name": "Rusted Blade", "desc": "Snapped near the hilt.", "stack": 20, "icon": 1},
	"scrap_helm": {"name": "Dented Helm", "desc": "Its owner didn't need it.", "stack": 20, "icon": 2},
	"scrap_plate": {"name": "Cracked Plate", "desc": "Pierced through the heart.", "stack": 20, "icon": 3},
	"bronze": {"name": "Bronze", "desc": "Common metal. Traded by weight.", "stack": 9999, "icon": 4, "unit": "g"},
	"silver": {"name": "Silver", "desc": "Prized metal. Traded by weight.", "stack": 9999, "icon": 7, "unit": "g"},
	"gold": {"name": "Gold", "desc": "Rare metal. A little goes far.", "stack": 9999, "icon": 10, "unit": "g"},
}
# Clump icons grow with weight: small below 10g, medium below 40g, then large.
const CLUMP_SIZES := [10, 40]
const METAL_DROPS := [[70, "bronze", 4, 30], [25, "silver", 2, 12], [5, "gold", 1, 5]]
const SCRAP := ["scrap_blade", "scrap_helm", "scrap_plate"]
# drops: [weight, kind, ...args]. kind shard: [min, max]; metal: [scale]; scrap; rune.
const LOOT_TABLES := {
	"body": {"empty": 0.2, "rolls": [1, 3], "nothing": "Nothing but rot.", "drops": [[35, "shard", 1, 3], [35, "metal", 1], [20, "scrap"], [10, "rune"]]},
	"crate": {"empty": 0.15, "rolls": [2, 4], "nothing": "Picked clean.", "drops": [[15, "shard", 1, 2], [40, "metal", 2], [40, "scrap"], [5, "rune"]]},
	"runestone": {"empty": 0.0, "rolls": [1, 1], "nothing": "", "drops": [[75, "shard", 2, 4], [25, "rune"]]},
	"chest": {"empty": 0.1, "rolls": [2, 3], "nothing": "Only black water.", "drops": [[20, "shard", 1, 3], [50, "metal", 3], [15, "scrap"], [15, "rune"]]},
	"reliquary": {"empty": 0.0, "rolls": [1, 2], "nothing": "", "drops": [[50, "shard", 2, 5], [50, "rune"]]},
	"pyre": {"empty": 0.25, "rolls": [1, 3], "nothing": "Ash and bone.", "drops": [[40, "shard", 1, 4], [45, "metal", 2], [15, "rune"]]},
	"tomb": {"empty": 0.1, "rolls": [1, 3], "nothing": "The ice kept nothing.", "drops": [[30, "shard", 1, 3], [45, "metal", 2], [10, "scrap"], [15, "rune"]]},
}
# Biome loot modifiers that scale a drop kind's weight.
const BONUSES := {"rune": "runeBonus", "shard": "shardBonus"}

static var icons := {
	16: {"items": load("res://art/items/item_icons.png"), "runes": load("res://art/runes/rune_icons.png")},
	32: {"items": load("res://art/items/item_icons_hd.png"), "runes": load("res://art/runes/rune_icons_hd.png")},
}


static func rune_key(types: Array, tier: int, notches := 0) -> String:
	return "rune_%s_%d%s" % ["-".join(types), tier, "_%d" % notches if notches else ""]


# Icon row (art/drafts/ui/icons.py): the single verbs in ORDER, then every pair in ORDER; -1 if unknown.
static func rune_row(types: String) -> int:
	var order := RuneBook.ORDER
	if types in order:
		return order.find(types)
	var row := order.size()
	for i in order.size():
		for j in range(i + 1, order.size()):
			if types == order[i] + "-" + order[j]:
				return row
			row += 1
	return -1


# {name, desc, stack, unit, color, sheet, col, row} plus {tier, types, notches} for runes; {} if unknown.
static func info(key: String) -> Dictionary:
	var parts := key.split("_")
	if parts[0] == "rune" and parts.size() >= 3 and parts[2].to_int() >= 1 and parts[2].to_int() <= TIERS.size():
		var tier := parts[2].to_int()
		var types := Array(parts[1].split("-"))
		var row := rune_row(parts[1])
		if row < 0:
			return {}
		var tier_name: String = TIERS[tier - 1]
		var kind: Dictionary = RuneBook.KINDS.get(parts[1], {})
		return {
			"name": "%s Rune of %s" % [tier_name.capitalize(), "the " + kind.name if kind else parts[1].capitalize()],
			"desc": kind.desc if kind else RuneBook.SUBTYPES[parts[1]].desc,
			"stack": 1, "unit": "", "color": "rune-%s-mid" % tier_name,
			"tier": tier, "types": types, "notches": parts[3].to_int() if parts.size() > 3 else 0,
			"sheet": "runes", "col": tier - 1, "row": row,
		}
	if not LIST.has(key):
		return {}
	var item: Dictionary = LIST[key]
	return {"unit": item.get("unit", ""), "color": "bone-1", "sheet": "items", "col": item.icon, "row": 0, "name": item.name, "desc": item.desc, "stack": item.stack}


# size 16 draws the HUD icon; 32 the 2x-resolution one.
static func draw_icon(canvas: CanvasItem, key: String, count: int, at: Vector2, size := 32) -> void:
	var item := info(key)
	var clump := CLUMP_SIZES.filter(func(grams): return count >= grams).size() if item.unit else 0
	var source := Rect2((item.col + clump) * size, item.row * size, size, size)
	canvas.draw_texture_rect_region(icons[size][item.sheet], Rect2(at, Vector2(size, size)), source)


static func weighted(weights: Array) -> int:
	var r: float = randf() * weights.reduce(func(a, b): return a + b, 0.0)
	for i in weights.size():
		r -= weights[i]
		if r < 0:
			return i
	return weights.size() - 1


# Rolls a loot table: [{key, count}, ...]. mods: the biome's loot modifiers (biomes.gd loot).
static func roll_loot(table_name: String, mods := {}) -> Array:
	var table: Dictionary = LOOT_TABLES[table_name]
	if randf() < table.empty:
		return []
	var weights: Array = table.drops.map(func(d): return d[0] * mods.get(BONUSES.get(d[1], ""), 1.0))
	var loot := []
	for i in randi_range(table.rolls[0], table.rolls[1]):
		var drop := make_drop(table.drops[weighted(weights)], mods)
		var same = loot.filter(func(item): return item.key == drop.key)
		if same:
			same[0].count += drop.count
		else:
			loot.append(drop)
	return loot


static func make_drop(drop: Array, mods: Dictionary) -> Dictionary:
	match drop[1]:
		"shard":
			return {"key": "shard", "count": randi_range(drop[2], drop[3])}
		"metal":
			var metal: Array = METAL_DROPS[weighted(mods.get("metals", METAL_DROPS.map(func(m): return m[0])))]
			return {"key": metal[1], "count": randi_range(metal[2] * drop[2], metal[3] * drop[2])}
		"scrap":
			return {"key": SCRAP.pick_random(), "count": 1}
	var type: String = mods.runeType if mods.has("runeType") and randf() < 0.6 else RuneBook.ORDER.pick_random()
	return {"key": "rune_%s_%d" % [type, weighted(TIER_WEIGHTS) + 1], "count": 1}
