class_name Barter

# Metal trades at a village stall (src/barter.js, offers from src/village.js). Rates drift slowly
# over time per village; the barterer takes a CUT. The panel draws on the 1x HUD.
const W := 176
const PAD := 6
const ROW_H := 12
const METALS := ["bronze", "silver", "gold"]
const SHIFT_TIMES := 10
const BASE_RATE := 10.0
const RATE_SWING := 0.25
const RATE_DRIFT_SECONDS := 300.0
const CUT := 0.1


static func rate(village: Dictionary, pair: int, time: float) -> float:
	var swing := (WorldNoise.value_noise(village.seed + pair, time / RATE_DRIFT_SECONDS, 0) * 2 - 1) * RATE_SWING
	return BASE_RATE * (1 + swing)


# [{give: [key, count], get: [key, count]}, ...]
static func offers(village: Dictionary, time: float) -> Array:
	var silver := rate(village, 1, time)
	var gold := rate(village, 2, time)
	return [
		{"give": ["bronze", ceili(silver / (1 - CUT))], "get": ["silver", 1]},
		{"give": ["silver", ceili(gold / (1 - CUT))], "get": ["gold", 1]},
		{"give": ["silver", 1], "get": ["bronze", floori(silver * (1 - CUT))]},
		{"give": ["gold", 1], "get": ["silver", floori(gold * (1 - CUT))]},
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


static func box(screen: Vector2, count: int) -> Rect2:
	var h := PAD * 2 + 32 + count * ROW_H + 12
	return Rect2(((screen - Vector2(W, h)) / 2).floor(), Vector2(W, h))


static func row_top(b: Rect2, i: int) -> float:
	return b.position.y + PAD + 32 + i * ROW_H


# Index of the offer under a HUD point, or -1.
static func offer_at(list: Array, p: Vector2, screen: Vector2) -> int:
	var b := box(screen, list.size())
	if p.x < b.position.x + PAD or p.x >= b.end.x - PAD:
		return -1
	for i in list.size():
		if p.y >= row_top(b, i) and p.y < row_top(b, i) + ROW_H - 1:
			return i
	return -1


static func draw(canvas: CanvasItem, inventory: Inventory, village: Dictionary, list: Array, mouse: Vector2, screen: Vector2) -> void:
	var b := box(screen, list.size())
	var x := b.position.x
	UiDraw.frame(canvas, x, b.position.y, W, b.size.y)
	PixelFont.draw(canvas, "Barterer of %s" % village.name, Vector2(x + PAD, b.position.y + PAD - 1), "bone-0", "void-0")
	for i in METALS.size():
		var mx := x + PAD + i * 56
		var count := inventory.count_of(METALS[i])
		Items.draw_icon(canvas, METALS[i], count, Vector2(mx, b.position.y + PAD + 8), 16)
		PixelFont.draw(canvas, "%dg" % count, Vector2(mx + 18, b.position.y + PAD + 14), "bone-1" if count else "ash-2")
	var hovered := offer_at(list, mouse, screen)
	for i in list.size():
		var offer: Dictionary = list[i]
		var y := row_top(b, i)
		var affordable: bool = inventory.count_of(offer.give[0]) >= offer.give[1]
		if i == hovered and affordable:
			UiDraw.rect(canvas, "void-3", x + PAD - 2, y - 2, W - PAD * 2 + 4, ROW_H - 1)
		var give := "%dg %s" % [offer.give[1], Items.info(offer.give[0]).name]
		var get := "%dg %s" % [offer.get[1], Items.info(offer.get[0]).name]
		var color := "bone-0" if affordable else "ash-2"
		PixelFont.draw(canvas, give, Vector2(x + PAD, y), color)
		PixelFont.draw(canvas, ">", Vector2(x + 76, y), "ash-3")
		PixelFont.draw(canvas, get, Vector2(b.end.x - PAD - PixelFont.width(get), y), color)
	var hint := "Click trade  Shift x10  E close"
	PixelFont.draw(canvas, hint, Vector2(x + floori((W - PixelFont.width(hint)) / 2.0), b.end.y - PAD - 5), "ash-3")
