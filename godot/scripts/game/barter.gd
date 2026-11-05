class_name Barter

# Trades at a village stall (src/barter.js, offers from src/village.js): metal for metal, and empty
# stones for silver. Rates drift slowly over time per village; the barterer takes a CUT. Drawn by
# barter_panel.gd.
const SHIFT_TIMES := 10
# Grams of silver an empty stone costs at the base rate; it drifts with the village's rates.
const STONE_PRICE := 15.0
const BASE_RATE := 10.0
const RATE_SWING := 0.25
const RATE_DRIFT_SECONDS := 300.0
const CUT := 0.1
const PURSE := ["bronze", "silver", "gold", Items.EMPTY_STONE]
const NOTES := ["He keeps a tenth.", "Rates drift."]


static func title(village: Dictionary) -> String:
	return "Barterer of %s" % village.name


static func rate(village: Dictionary, pair: int, time: float) -> float:
	var swing := (WorldNoise.value_noise(village.seed + pair, time / RATE_DRIFT_SECONDS, 0) * 2 - 1) * RATE_SWING
	return BASE_RATE * (1 + swing)


# [{give: [key, count], get: [key, count]}, ...]
static func offers(village: Dictionary, time: float, _inventory: Inventory = null) -> Array:
	var silver := rate(village, 1, time)
	var gold := rate(village, 2, time)
	return [
		{"give": ["bronze", ceili(silver / (1 - CUT))], "get": ["silver", 1]},
		{"give": ["silver", ceili(gold / (1 - CUT))], "get": ["gold", 1]},
		{"give": ["silver", 1], "get": ["bronze", floori(silver * (1 - CUT))]},
		{"give": ["gold", 1], "get": ["silver", floori(gold * (1 - CUT))]},
		{"give": ["silver", ceili(STONE_PRICE * rate(village, 3, time) / BASE_RATE)], "get": [Items.EMPTY_STONE, 1]},
	]


# Trades as many times as asked and affordable. Returns how many went through.
static func trade(inventory: Inventory, offer: Dictionary, times: int) -> int:
	var done := 0
	while done < times and inventory.count_of(offer.give[0]) >= offer.give[1]:
		inventory.remove(offer.give[0], offer.give[1])
		var left := inventory.add(offer.get[0], offer.get[1])
		if left:
			inventory.remove(offer.get[0], offer.get[1] - left)
			inventory.add(offer.give[0], offer.give[1])
			break
		done += 1
	return done
