extends Node2D

# The 2x-resolution inventory panel (src/inventory.js, style A): bag, wanderer with rune sockets,
# item detail with carve and fuse, metal and rune summary. C swaps the bag and detail for the rune
# sheet: what the lashed runes add up to. B opens his book over the whole top: his entries and the
# margin notes on the left page, the roll of names and echoes on the right. Drawn at native pixels on a CanvasLayer.
const SLOT := 36
const GAP := 4
const ICON := 32
const PANEL := Vector2(640, 360)
const BAG := Vector2(196, 52)
const SIDE_W := 160
const SECTION_H := 228
const SOCKET_R := 13
const SOCKET_STEP := 32
const BUTTON := Vector2(78, 20)
const MESSAGE_SECONDS := 2.5
const SHEET_VALUE_X := 90
const LARGE := PixelFont.LARGE
const WANDERER := preload("res://art/characters/wanderer_hd/wanderer_hd_idle.png")

var inventory: Inventory
var player: Node
# "" the bag, "sheet" the rune sheet, "book" his book.
var page := ""
# How far the book is turned back from its newest lines, and how many lines a page holds.
var lines_back := 0
var page_lines := 1
var message := ""
var message_at := -100.0


func _process(_dt: float) -> void:
	visible = inventory.open
	if visible:
		queue_redraw()


func now() -> float:
	return Time.get_ticks_msec() / 1000.0


# Panel geometry, shared by drawing and clicks.
func layout() -> Dictionary:
	var screen := get_viewport().get_visible_rect().size
	var origin := ((screen - PANEL) / 2).floor()
	var bag := []
	for i in Inventory.COLS * Inventory.ROWS:
		bag.append(Rect2(origin + BAG + Vector2(i % Inventory.COLS, i / Inventory.COLS) * (SLOT + GAP), Vector2(SLOT, SLOT)))
	var side := origin + Vector2(18, 38)
	var sockets := []
	var row := 0
	for part in Runes.SOCKETS:
		for i in Runes.SOCKETS[part]:
			var centre := side + Vector2(73 + i * SOCKET_STEP, 141 + row * SOCKET_STEP)
			sockets.append({"part": part, "i": i, "centre": centre, "rect": Rect2(centre - Vector2.ONE * SOCKET_R, Vector2.ONE * (SOCKET_R * 2 + 1))})
		row += 1
	var detail := Rect2(origin + Vector2(PANEL.x - 194, 38), Vector2(SIDE_W + 16, SECTION_H))
	var sheet_rect := Rect2(origin + Vector2(BAG.x, 38), Vector2(detail.end.x - origin.x - BAG.x, SECTION_H))
	var book := Rect2(origin + Vector2(18, 38), Vector2(PANEL.x - 36, SECTION_H))
	var turn_y := book.end.y - BUTTON.y - 6
	var turn := {
		"back": Rect2(Vector2(book.position.x + 8, turn_y), BUTTON),
		"on": Rect2(Vector2(book.end.x - 8 - BUTTON.x, turn_y), BUTTON),
	}
	var by := detail.end.y - BUTTON.y - 8
	var buttons := {
		"carve": Rect2(Vector2(detail.position.x + 8, by), BUTTON),
		"fuse": Rect2(Vector2(detail.end.x - 8 - BUTTON.x, by), BUTTON),
	}
	return {"origin": origin, "bag": bag, "side": side, "sockets": sockets, "detail": detail, "buttons": buttons, "sheet": sheet_rect, "book": book, "turn": turn}


# A left click at screen point p while the panel is open.
func click(p: Vector2) -> void:
	var l := layout()
	var text := ""
	var bag_index: int = l.bag.find_custom(func(r): return r.has_point(p))
	var socket = l.sockets.filter(func(s): return s.rect.has_point(p))
	if page == "book":
		if l.turn.back.has_point(p):
			lines_back += page_lines
		elif l.turn.on.has_point(p):
			lines_back = maxi(0, lines_back - page_lines)
		return
	if page == "sheet" and bag_index >= 0:
		return
	if bag_index >= 0:
		text = inventory.click_bag(bag_index)
	elif socket and not player.calm():
		text = "No time to lash a stone. Not with the dead this close."
	elif socket:
		text = inventory.click_socket(socket[0].part, socket[0].i)
	elif inventory.selected_rune() and l.buttons.carve.has_point(p):
		text = inventory.carve()
	elif inventory.selected_rune() and l.buttons.fuse.has_point(p):
		text = inventory.toggle_fusing()
	elif not l.detail.has_point(p):
		inventory.deselect()
	if text:
		message = text
		message_at = now()


func text(t: String, at: Vector2, color: String, shadow := "") -> void:
	PixelFont.draw(self, t, at, color, shadow, LARGE)


func centred(t: String, x: float, w: float, y: float, color: String, shadow := "") -> void:
	text(t, Vector2(x + floori((w - PixelFont.width(t, LARGE)) / 2.0), y), color, shadow)


func _draw() -> void:
	var l := layout()
	var o: Vector2 = l.origin
	var mouse := get_viewport().get_mouse_position()
	draw_rect(get_viewport().get_visible_rect(), Color(Palette.color("void-0"), 0.6))
	UiDraw.iron_frame(self, o.x, o.y, PANEL.x, PANEL.y)
	centred("Office Book" if page == "book" else "Inventory", o.x, PANEL.x, o.y + 14, "bone-0", "void-0")
	UiDraw.rule(self, o.x + 20, o.y + 28, PANEL.x - 40)
	var hovered_socket = draw_character(l, mouse) if page != "book" else null
	if page == "book":
		draw_book(l.book)
	elif page == "sheet":
		draw_sheet(l.sheet)
	else:
		var hovered_bag = draw_bag(l, mouse)
		var shown = inventory.slots[inventory.selected] if inventory.selected >= 0 else hovered_bag if hovered_bag else hovered_socket
		draw_detail(l, shown, mouse)
	draw_summary(o + Vector2(18, PANEL.y - 82))
	var close := "C  %s    B  %s    I  Close" % ["Bag" if page == "sheet" else "Rune sheet", "Bag" if page == "book" else "Book"]
	if page == "book":
		close = "N  Write in the margin    " + close
	text(close, o + Vector2(PANEL.x - 20 - PixelFont.width(close, LARGE), PANEL.y - 14), "ash-3")
	if now() - message_at < MESSAGE_SECONDS:
		text(message, o + Vector2(20, PANEL.y - 14), "bone-0")


func draw_bag(l: Dictionary, mouse: Vector2):
	var hovered = null
	text("Bag", l.bag[0].position - Vector2(0, 12), "ash-3")
	for i in inventory.slots.size():
		var r: Rect2 = l.bag[i]
		var slot = inventory.slots[i]
		UiDraw.inset(self, r.position.x, r.position.y, SLOT, SLOT, "void-0")
		var ring := "bone-0" if i == inventory.selected else "rune-pale-dark" if inventory.fusing and Inventory.is_rune(slot) else "gilt-2" if r.has_point(mouse) and slot else ""
		if ring:
			UiDraw.outline(self, ring, r.position.x - 1, r.position.y - 1, SLOT + 2, SLOT + 2)
		if not slot:
			continue
		if r.has_point(mouse):
			hovered = slot
		Items.draw_icon(self, slot.key, slot.count, r.position + Vector2(2, 2), ICON)
		draw_notches(slot.key, r.position + Vector2(3, SLOT - 4))
		if slot.count > 1:
			var count := str(slot.count)
			text(count, r.position + Vector2(SLOT - 2 - PixelFont.width(count, LARGE), SLOT - 9), "bone-1", "void-0")
	return hovered


# Carved notches as small marks in the rune's tier colour along the slot's bottom edge.
func draw_notches(key: String, at: Vector2) -> void:
	var info := Items.info(key)
	for n in info.get("notches", 0):
		UiDraw.rect(self, "rune-%s-mid" % Items.TIERS[info.tier - 1], at.x + n * 3, at.y, 2, 2)


func draw_character(l: Dictionary, mouse: Vector2):
	var side: Vector2 = l.side
	UiDraw.inset(self, side.x, side.y, SIDE_W, SECTION_H, "void-2")
	centred("Wanderer", side.x, SIDE_W, side.y + 8, "ash-3")
	draw_texture_rect_region(WANDERER, Rect2(side + Vector2((SIDE_W - 96) / 2, 22), Vector2(96, 96)), Rect2(0, 0, 96, 96))
	var key := inventory.selected_lashable()
	var hovered = null
	for s in l.sockets:
		var c: Vector2 = s.centre
		if s.i == 0:
			text(s.part, Vector2(side.x + 10, c.y - 3), "ash-4")
		UiDraw.disc(self, "gilt-2" if key and Runes.fits(key, s.part) else "void-0", c.x, c.y, SOCKET_R)
		UiDraw.disc(self, "void-2", c.x, c.y, SOCKET_R - 2)
		var rune = inventory.sockets[s.part][s.i]
		if rune:
			Items.draw_icon(self, rune, 1, c - Vector2(16, 16), ICON)
			if s.rect.has_point(mouse):
				hovered = {"key": rune, "count": 1}
		else:
			UiDraw.disc(self, "void-3", c.x, c.y, 2)
	var names: Array = player.runes.resonances.map(func(r): return [r.name, "rune-crimson-mid" if r.cursed else "bone-0"])
	if names.is_empty():
		names.append(["No resonance", "ash-3"])
	for i in mini(3, names.size()):
		centred(names[i][0], side.x, SIDE_W, side.y + 192 + i * LARGE.line, names[i][1], "void-0")
	return hovered


func draw_detail(l: Dictionary, slot, mouse: Vector2) -> void:
	var d: Rect2 = l.detail
	var x := d.position.x
	var y := d.position.y
	var w := d.size.x
	UiDraw.inset(self, x, y, w, d.size.y, "void-2")
	if not slot:
		if player.runes.resonances.is_empty():
			centred("Pick an item", x, w, y + 104, "ash-3")
			return
		var ly := y + 12
		for r in player.runes.resonances:
			text(r.name, Vector2(x + 10, ly), "rune-crimson-mid" if r.cursed else "bone-0")
			var lines := UiDraw.wrap(r.desc, 26)
			for i in lines.size():
				text(lines[i], Vector2(x + 10, ly + 12 + i * LARGE.line), "ash-4")
			ly += 16 + lines.size() * LARGE.line
		return
	var info := Items.info(slot.key)
	UiDraw.inset(self, x + floori((w - 40) / 2), y + 10, 40, 40, "void-0")
	Items.draw_icon(self, slot.key, slot.count, Vector2(x + floori((w - ICON) / 2), y + 14), ICON)
	var name := UiDraw.wrap(info.name, 26)
	for i in name.size():
		centred(name[i], x, w, y + 56 + i * LARGE.line, info.color, "void-0")
	var ly := y + 60 + name.size() * LARGE.line
	UiDraw.rule(self, x + 16, ly, w - 32)
	ly += 8
	var rune: bool = info.has("types")
	var lines := []
	for line in Runes.passive_lines(slot.key) if rune else [info.desc]:
		lines += UiDraw.wrap(line, 26)
	for i in lines.size():
		text(lines[i], Vector2(x + 10, ly + i * LARGE.line), "bone-0" if rune else "ash-4")
	ly += lines.size() * LARGE.line + 6
	if rune:
		for line in Runes.soul_lines(slot.key, inventory.reading, inventory.rites):
			for part in UiDraw.wrap(line[0], 26):
				text(part, Vector2(x + 10, ly), line[1])
				ly += LARGE.line
		ly += 4
	if info.unit:
		text("Weight: %d%s" % [slot.count, info.unit], Vector2(x + 10, ly), "ash-3")
	if not rune:
		return
	for i in Items.TIERS.size():
		UiDraw.tier_gem(self, Items.TIERS[i], x + 15 + i * 14, ly + 5, i < info.tier)
	var notches := "%d/%d" % [info.notches, Runes.MAX_NOTCHES]
	text(notches, Vector2(x + w - 10 - PixelFont.width(notches, LARGE), ly + 2), "ash-3")
	var desc := UiDraw.wrap(info.desc, 26)
	for i in desc.size():
		text(desc[i], Vector2(x + 10, ly + 16 + i * LARGE.line), "ash-3")

	if inventory.selected < 0 or slot != inventory.slots[inventory.selected]:
		return
	if inventory.fusing:
		centred("Pick a rune to fuse", x, w, l.buttons.carve.position.y - 14, "rune-pale-mid")
	var labels := {
		"carve": "Carve %d" % Runes.carve_cost(slot.key) if info.notches < Runes.MAX_NOTCHES else "Carved",
		"fuse": "Cancel" if inventory.fusing else "Fuse",
	}
	for id in l.buttons:
		var b: Rect2 = l.buttons[id]
		var hot := b.has_point(mouse)
		UiDraw.inset(self, b.position.x, b.position.y, b.size.x, b.size.y, "steel-0" if hot else "void-1")
		centred(labels[id], b.position.x, b.size.x, b.position.y + 7, "bone-1" if hot else "bone-0")


# Two columns: the Wanderer's numbers and the lashed verbs; then fused kinds and resonances.
# A row is [text, colour] or [label, colour, value].
func draw_sheet(r: Rect2) -> void:
	UiDraw.inset(self, r.position.x, r.position.y, r.size.x, r.size.y, "void-2")
	var s: Dictionary = player.runes
	var hits: Array = player.COMBO.map(func(m): return m.damage)
	var bulwark := Runes.resonance(s, "Bulwark")
	var left := [
		["Wanderer", "ash-3"],
		["Health", "ash-4", "%d / %d" % [ceili(player.hp), player.max_hp]],
		["Attack", "ash-4", "%d - %d" % [roundi(hits.min() * (1 + s.rend + s.strength)), roundi(hits.max() * (1 + s.rend + s.strength))]],
		["Strength", "ash-4", "%d / %d" % [inventory.forged.strength, Smith.MAX.strength]],
		["Armor", "ash-4", "%d%%" % roundi(player.armor() * 100) + (" +%d block" % roundi(RuneBook.BULWARK_BLOCK * bulwark.power) if bulwark else "")],
		["Speed", "ash-4", str(roundi(player.speed))],
		["Dodge reach", "ash-4", str(roundi(player.DODGE.speed * player.DODGE.time * Runes.dodge_factor(s, player)))],
		["Shield", "ash-4", "%d" % ceili(player.shield)],
		["Corruption", "ash-4", "%d%%" % roundi(player.corruption * 100)],
		["", "ash-3"],
		["Lashed", "ash-3"],
	]
	for t in RuneBook.ORDER:
		if s[t]:
			left.append([Runes.verb_text(t, s[t] * 100), "bone-0"])
	for t in s.cursed:
		left.append([RuneBook.CRIMSON_TEXT.get(t, "%s: cursed" % t.capitalize()), "rune-crimson-mid"])
	if not s.kinds and not s.cursed and RuneBook.ORDER.all(func(t): return not s[t]):
		left.append(["Nothing lashed", "ash-3"])
	var gripped := RuneBook.ORDER.filter(func(t): return s.grip[t])
	if gripped:
		left += [["", "ash-3"], ["Grip", "ash-3"]]
		for t in gripped:
			left.append([Runes.grip_text(t, s.grip[t]), "blood-4"])
	var right := [["Kinds", "ash-3"]]
	for k in s.kinds:
		right.append(["%s  x%.1f" % [k.name, k.power], "bone-1"])
		for line in UiDraw.wrap(k.desc, 32):
			right.append([line, "ash-4"])
	if s.kinds.is_empty():
		right.append(["None", "ash-3"])
	right += [["", "ash-3"], ["Resonances", "ash-3"]]
	for res in s.resonances:
		right.append(["%s  x%.1f" % [res.name, res.power], "rune-crimson-mid" if res.cursed else "bone-1"])
		for line in UiDraw.wrap(res.desc, 32):
			right.append([line, "ash-4"])
	if s.resonances.is_empty():
		right.append(["None", "ash-3"])
	var half := floori(r.size.x / 2)
	for c in 2:
		var column: Array = [left, right][c]
		for i in mini(column.size(), floori((r.size.y - 16) / LARGE.line)):
			var at := r.position + Vector2(10 + c * half, 10 + i * LARGE.line)
			text(column[i][0], at, column[i][1])
			if column[i].size() > 2:
				text(column[i][2], at + Vector2(SHEET_VALUE_X, 0), "bone-0")


func scroll(lines: int) -> void:
	lines_back = maxi(0, lines_back + lines * 3)


# His hand in the body blackletter; margin notes and headings in the plain pixel hand.
# A row is [text, colour, "hand" | "plain", indent].
func draw_book(r: Rect2) -> void:
	UiDraw.inset(self, r.position.x, r.position.y, r.size.x, r.size.y, "void-2")
	var half := floori(r.size.x / 2)
	UiDraw.rect(self, "void-0", r.position.x + half, r.position.y + 6, 1, r.size.y - 12)
	var room := half - 24
	var hand := func(t): return GothicText.width(t, GothicText.BODY, GothicText.SMALL_SIZE)
	var left := []
	var right := [["Names", "ash-3", "plain", 0]]
	var echoes := [["", "ash-3", "plain", 0], ["Echoes", "ash-3", "plain", 0]]
	for e in Journal.entries:
		match e.kind:
			"his":
				left += UiDraw.wrap(e.text, room, hand).map(func(t): return [t, "bone-1", "hand", 0]) + [["", "ash-3", "plain", 0]]
			"margin":
				left += UiDraw.wrap(e.text, floori((room - 12) / 6.0)).map(func(t): return [t, "ash-4", "plain", 12]) + [["", "ash-3", "plain", 0]]
			"name":
				right.append([e.text, "bone-0", "hand", 0])
			"echo":
				echoes.append([e.verb.capitalize(), "bone-1", "plain", 0])
				echoes += UiDraw.wrap(e.text, room - 8, hand).map(func(t): return [t, "ash-4", "hand", 8])
	if left.is_empty():
		left.append(["The pages are blank.", "ash-3", "hand", 0])
	if right.size() == 1:
		right.append(["None yet", "ash-3", "hand", 0])
	right += echoes if echoes.size() > 2 else echoes + [["None yet", "ash-3", "hand", 0]]
	var row_h := ceili(GothicText.height(GothicText.BODY, GothicText.SMALL_SIZE))
	var shown := floori((r.size.y - 16 - BUTTON.y - 6) / row_h)
	var most := maxi(0, maxi(left.size(), right.size()) - shown)
	page_lines = shown
	lines_back = mini(lines_back, most)
	draw_turn(get_viewport().get_mouse_position(), "back", "< Earlier", lines_back < most)
	draw_turn(get_viewport().get_mouse_position(), "on", "Later >", lines_back > 0)
	for c in 2:
		var column: Array = [left, right][c]
		var first := maxi(0, column.size() - shown - lines_back)
		for i in range(first, mini(column.size(), first + shown)):
			var row: Array = column[i]
			var at := r.position + Vector2(12 + c * half + row[3], 8 + (i - first) * row_h)
			if row[2] == "hand":
				GothicText.draw(self, row[0], at, row[1], GothicText.BODY, GothicText.SMALL_SIZE)
			else:
				text(row[0], at + Vector2(0, 5), row[1])


# A page-turn button, dim when there is no page that way.
func draw_turn(mouse: Vector2, id: String, label: String, live: bool) -> void:
	var b: Rect2 = layout().turn[id]
	var hot := live and b.has_point(mouse)
	UiDraw.inset(self, b.position.x, b.position.y, b.size.x, b.size.y, "steel-0" if hot else "void-1")
	centred(label, b.position.x, b.size.x, b.position.y + 7, "bone-1" if hot else "bone-0" if live else "ash-2")


func draw_summary(at: Vector2) -> void:
	UiDraw.inset(self, at.x, at.y, PANEL.x - 36, 64, "void-2")
	var lx := at.x + 14
	for metal in [["bronze", "g"], ["silver", "g"], ["gold", "g"], ["shard", ""]]:
		var count := inventory.count_of(metal[0])
		Items.draw_icon(self, metal[0], maxi(count, 1), Vector2(lx, at.y + 16), ICON)
		var label := "%d%s" % [count, metal[1]]
		text(label, Vector2(lx + 36, at.y + 28), "ash-4" if count else "ash-2")
		lx += 36 + PixelFont.width(label, LARGE) + 22
	text("Runes", Vector2(lx + 6, at.y + 12), "ash-3")
	for i in Items.TIERS.size():
		var count: int = inventory.slots.reduce(func(n, s): return n + (s.count if s and Items.info(s.key).get("tier", 0) == i + 1 else 0), 0)
		var tx := lx + 6 + i * 30
		UiDraw.tier_gem(self, Items.TIERS[i], tx + 5, at.y + 34, count > 0)
		text(str(count), Vector2(tx + 14, at.y + 31), "ash-4" if count else "ash-2")
