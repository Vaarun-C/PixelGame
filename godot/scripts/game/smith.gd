class_name Smith

# The village smith: melts scrap down to bronze by weight, or hammers it into the Wanderer's own
# gear. Blades worked into his sword raise Strength, helms and plates worked into his armour raise
# Armor, each up to MAX levels. Levels are kept in Inventory.forged; drawn by barter_panel.gd.
const PURSE := ["scrap_blade", "scrap_helm", "scrap_plate", "bronze"]
const NOTES := ["Scrap melts by weight.", "Gear takes only so much."]
const MELT := {"scrap_blade": 6, "scrap_helm": 9, "scrap_plate": 14}
const FORGE := {"scrap_blade": "strength", "scrap_helm": "armor", "scrap_plate": "armor"}
# Per level: strength adds to damage dealt, armor takes from damage taken (with Ward, capped at 75%).
const STEP := {"strength": 0.05, "armor": 0.03}
const MAX := {"strength": 10, "armor": 8}


static func title(village: Dictionary) -> String:
	return "Smith of %s" % village.name


static func bonus(forged: Dictionary, stat: String) -> float:
	return STEP[stat] * forged.get(stat, 0)


# Pieces of scrap the next level costs: 1, 1, 2, 2, 3, ...
static func cost(level: int) -> int:
	return 1 + level / 2


static func offers(_village: Dictionary, _time: float, inventory: Inventory) -> Array:
	var list := []
	for key in MELT:
		list.append({"give": [key, 1], "get": ["bronze", MELT[key]]})
	for key in FORGE:
		var stat: String = FORGE[key]
		var level: int = inventory.forged[stat]
		var full: bool = level >= MAX[stat]
		var label := "%s at its limit" % stat.capitalize() if full else "%s %d > %d" % [stat.capitalize(), level, level + 1]
		list.append({"give": [key, cost(level)], "stat": stat, "full": full, "label": label})
	return list


static func trade(inventory: Inventory, offer: Dictionary, times: int) -> int:
	if not offer.has("stat"):
		return Barter.trade(inventory, offer, times)
	var stat: String = offer.stat
	var done := 0
	while done < times and inventory.forged[stat] < MAX[stat] and inventory.count_of(offer.give[0]) >= cost(inventory.forged[stat]):
		inventory.forged[stat] += 1
		inventory.remove(offer.give[0], cost(inventory.forged[stat] - 1))
		done += 1
	return done
