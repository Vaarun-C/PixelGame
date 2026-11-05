extends Node2D

# A village stall in the inventory's style A, at native pixels: what the Wanderer carries on the
# left, the shop's trades on the right (Barter or Smith offers). Click trades once, Shift-click ten
# times.
const PANEL := Vector2(560, 320)
const PURSE_W := 150
const ROW_H := 44
const ICON := 32
const MESSAGE_SECONDS := 2.5
const LARGE := PixelFont.LARGE
const ROWS_H := 250

var inventory: Inventory
var village := {}
var shop: GDScript = Barter
var message := ""
var message_at := -100.0


func _ready() -> void:
	visible = false


func _process(_dt: float) -> void:
	visible = not village.is_empty()
	if visible:
		queue_redraw()


func now() -> float:
	return Time.get_ticks_msec() / 1000.0


func origin() -> Vector2:
	return ((get_viewport().get_visible_rect().size - PANEL) / 2).floor()


func rows(o: Vector2, count: int) -> Array:
	var x := o.x + PURSE_W + 34
	var h := mini(ROW_H, floori(ROWS_H / float(count)))
	return range(count).map(func(i): return Rect2(x, o.y + 50 + i * h, PANEL.x - PURSE_W - 52, h - 6))


func click(p: Vector2, times: int) -> void:
	var list: Array = shop.offers(village, now(), inventory)
	var i: int = rows(origin(), list.size()).find_custom(func(r): return r.has_point(p))
	if i < 0:
		return
	var offer: Dictionary = list[i]
	if shop.trade(inventory, offer, times) == 0:
		var short: bool = inventory.count_of(offer.give[0]) < offer.give[1]
		if offer.get("full"):
			message = "It takes no more."
		elif short:
			message = "Not enough %s." % Items.info(offer.give[0]).name.to_lower()
		else:
			message = "No room in the bag."
	else:
		message = "Traded."
	message_at = now()


func text(t: String, at: Vector2, color: String, shadow := "") -> void:
	PixelFont.draw(self, t, at, color, shadow, LARGE)


func amount(key: String, count: int) -> String:
	var info := Items.info(key)
	return "%d%s %s" % [count, info.unit, info.name] if info.unit else ("%d %s" % [count, info.name] if count > 1 else info.name)


func _draw() -> void:
	var o := origin()
	var mouse := get_viewport().get_mouse_position()
	draw_rect(get_viewport().get_visible_rect(), Color(Palette.color("void-0"), 0.6))
	UiDraw.iron_frame(self, o.x, o.y, PANEL.x, PANEL.y)
	var title: String = shop.title(village)
	text(title, Vector2(o.x + floori((PANEL.x - PixelFont.width(title, LARGE)) / 2.0), o.y + 14), "bone-0", "void-0")
	UiDraw.rule(self, o.x + 20, o.y + 28, PANEL.x - 40)
	draw_purse(o + Vector2(18, 38))
	draw_offers(o, mouse)
	var hint := "Click trade    Shift x10    E  Close"
	text(hint, o + Vector2(PANEL.x - 20 - PixelFont.width(hint, LARGE), PANEL.y - 14), "ash-3")
	if now() - message_at < MESSAGE_SECONDS:
		text(message, o + Vector2(20, PANEL.y - 14), "bone-0")


func draw_purse(at: Vector2) -> void:
	UiDraw.inset(self, at.x, at.y, PURSE_W, PANEL.y - 70, "void-2")
	text("You carry", at + Vector2(10, 10), "ash-3")
	for i in shop.PURSE.size():
		var key: String = shop.PURSE[i]
		var count := inventory.count_of(key)
		var y: float = at.y + 28 + i * 42
		Items.draw_icon(self, key, maxi(count, 1), Vector2(at.x + 10, y), ICON)
		text("%d%s" % [count, Items.info(key).unit], Vector2(at.x + 50, y + 8), "bone-0" if count else "ash-2")
		text(Items.info(key).name, Vector2(at.x + 50, y + 20), "ash-3")
	for i in shop.NOTES.size():
		text(shop.NOTES[i], Vector2(at.x + 10, at.y + PANEL.y - 104 + i * 12), "ash-3")


func draw_offers(o: Vector2, mouse: Vector2) -> void:
	var list: Array = shop.offers(village, now(), inventory)
	var rects := rows(o, list.size())
	text("Trades", rects[0].position - Vector2(0, 12), "ash-3")
	for i in list.size():
		var offer: Dictionary = list[i]
		var r: Rect2 = rects[i]
		var affordable: bool = not offer.get("full") and inventory.count_of(offer.give[0]) >= offer.give[1]
		UiDraw.inset(self, r.position.x, r.position.y, r.size.x, r.size.y, "void-1")
		if affordable and r.has_point(mouse):
			UiDraw.outline(self, "gilt-2", r.position.x - 1, r.position.y - 1, r.size.x + 2, r.size.y + 2)
		var colour := "bone-0" if affordable else "ash-2"
		var mid := r.position.x + floori(r.size.x / 2)
		var y := r.position.y + floori((r.size.y - ICON) / 2)
		Items.draw_icon(self, offer.give[0], offer.give[1], Vector2(r.position.x + 6, y), ICON)
		text(amount(offer.give[0], offer.give[1]), Vector2(r.position.x + 44, y + 13), colour)
		draw_arrow(Vector2(mid - 6, y + 16))
		if offer.has("label"):
			text(offer.label, Vector2(mid + 12, y + 13), colour)
		else:
			Items.draw_icon(self, offer.get[0], offer.get[1], Vector2(mid + 12, y), ICON)
			text(amount(offer.get[0], offer.get[1]), Vector2(mid + 50, y + 13), colour)


# The pixel font has no arrow: a 9 px shaft with a 3-step head.
func draw_arrow(at: Vector2) -> void:
	UiDraw.rect(self, "ash-3", at.x, at.y, 9, 1)
	for k in 3:
		UiDraw.rect(self, "ash-3", at.x + 6 + k, at.y - 2 + k, 1, 5 - k * 2)
