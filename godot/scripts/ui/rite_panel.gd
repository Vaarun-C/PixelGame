extends Node2D

# A rite place (Rites.PLACES) in the barter panel's style, at native pixels: the runes in the bag on
# the left, the chosen stone and the place's two rites on the right. Click a stone, then a rite.
const PANEL := Vector2(560, 320)
const STONES_W := 236
const COLS := 6
const SLOT := 36
const GAP := 2
const ICON := 32
const RITE_H := 38
const MESSAGE_SECONDS := 2.5
const LARGE := PixelFont.LARGE
const TITLES := {"ledger": "The Ledger", "firepit": "The Fire", "wayside_shrine": "The Road Shrine"}

var inventory: Inventory
var player: Node
var world: Node
var place: Prop = null
var chosen := ""
var message := ""
var message_at := -100.0


func _ready() -> void:
	visible = false


func _process(_dt: float) -> void:
	visible = place != null
	if not visible:
		chosen = ""
		return
	if chosen and not inventory.count_of(chosen):
		chosen = ""
	queue_redraw()


func now() -> float:
	return Time.get_ticks_msec() / 1000.0


func origin() -> Vector2:
	return ((get_viewport().get_visible_rect().size - PANEL) / 2).floor()


func stones() -> Array:
	return inventory.slots.filter(Inventory.is_rune).map(func(slot): return slot.key)


func stone_rects(o: Vector2, count: int) -> Array:
	return range(count).map(func(i): return Rect2(o + Vector2(28 + i % COLS * (SLOT + GAP), 62 + i / COLS * (SLOT + GAP)), Vector2(SLOT, SLOT)))


func rite_rects(o: Vector2) -> Array:
	var x := o.x + STONES_W + 34
	return range(2).map(func(i): return Rect2(x, o.y + PANEL.y - 120 + i * (RITE_H + 6), PANEL.x - STONES_W - 52, RITE_H))


func rites() -> Array:
	return Rites.PLACES[place.def_kind]


func click(p: Vector2) -> void:
	var o := origin()
	var list := stones()
	var i: int = stone_rects(o, list.size()).find_custom(func(r): return r.has_point(p))
	if i >= 0:
		chosen = "" if chosen == list[i] else list[i]
		return
	var j: int = rite_rects(o).find_custom(func(r): return r.has_point(p))
	if j < 0:
		return
	var rite: Dictionary = rites()[j]
	var result := Rites.perform(rite, chosen, inventory, player) if chosen else ["Choose a stone first.", false]
	if result[1] and rite.god == "Mortmain":
		world.grate(place)
	message = result[0]
	message_at = now()


func text(t: String, at: Vector2, color: String, shadow := "") -> void:
	PixelFont.draw(self, t, at, color, shadow, LARGE)


func _draw() -> void:
	var o := origin()
	var mouse := get_viewport().get_mouse_position()
	draw_rect(get_viewport().get_visible_rect(), Color(Palette.color("void-0"), 0.6))
	UiDraw.iron_frame(self, o.x, o.y, PANEL.x, PANEL.y)
	var title: String = TITLES[place.def_kind]
	text(title, Vector2(o.x + floori((PANEL.x - PixelFont.width(title, LARGE)) / 2.0), o.y + 14), "bone-0", "void-0")
	UiDraw.rule(self, o.x + 20, o.y + 28, PANEL.x - 40)
	draw_stones(o, mouse)
	draw_chosen(o)
	draw_rites(o, mouse)
	var hint := "Click a stone, then a rite    E  Close"
	text(hint, o + Vector2(PANEL.x - 20 - PixelFont.width(hint, LARGE), PANEL.y - 14), "ash-3")
	if now() - message_at < MESSAGE_SECONDS:
		text(message, o + Vector2(20, PANEL.y - 14), "bone-0")


func draw_stones(o: Vector2, mouse: Vector2) -> void:
	UiDraw.inset(self, o.x + 18, o.y + 38, STONES_W, PANEL.y - 70, "void-2")
	text("Stones you carry", o + Vector2(28, 48), "ash-3")
	var list := stones()
	if list.is_empty():
		text("No runes in the bag.", o + Vector2(28, 66), "ash-2")
	var rects := stone_rects(o, list.size())
	for i in list.size():
		var r: Rect2 = rects[i]
		UiDraw.inset(self, r.position.x, r.position.y, SLOT, SLOT, "void-0")
		var ring := "bone-0" if list[i] == chosen else "gilt-2" if r.has_point(mouse) else ""
		if ring:
			UiDraw.outline(self, ring, r.position.x - 1, r.position.y - 1, SLOT + 2, SLOT + 2)
		Items.draw_icon(self, list[i], 1, r.position + Vector2(2, 2), ICON)


func draw_chosen(o: Vector2) -> void:
	var x := o.x + STONES_W + 34
	var y := o.y + 48
	if not chosen:
		text("Choose a stone.", Vector2(x, y), "ash-3")
		return
	var info := Items.info(chosen)
	text(info.name, Vector2(x, y), info.color, "void-0")
	y += LARGE.line + 4
	for line in Runes.soul_lines(chosen, inventory.reading, inventory.rites):
		for part in UiDraw.wrap(line[0], 36):
			text(part, Vector2(x, y), line[1])
			y += LARGE.line


func draw_rites(o: Vector2, mouse: Vector2) -> void:
	var rects := rite_rects(o)
	for i in rects.size():
		var rite: Dictionary = rites()[i]
		var r: Rect2 = rects[i]
		var live := chosen != ""
		UiDraw.inset(self, r.position.x, r.position.y, r.size.x, r.size.y, "steel-0" if live and r.has_point(mouse) else "void-1")
		var kneel := Rites.kneels(rite, player.corruption)
		text(Rites.words(rite, player.corruption), r.position + Vector2(10, 9 if kneel else 15), "bone-0" if live else "ash-2")
		if kneel:
			text("Kneel. It costs blood.", r.position + Vector2(10, 23), "blood-4")
