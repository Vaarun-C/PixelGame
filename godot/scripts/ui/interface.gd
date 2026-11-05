extends CanvasLayer

# Interaction and HUD (the tick in src/main.js, src/ui.js): E searches a lootable prop, opens the
# talk box to question a villager (the dialogue model, see dialogue.gd), opens the barterer's stall, the smith or
# a rite place (the ledger, the fire, the road shrine: rite_panel.gd); I or Tab opens the bag, C the rune sheet, B his book (N writes in
# its margin); Esc closes. Story beats are written into the book (Journal). The HUD draws at native
# pixels: the keepsake, gothic lettering and gilt titles.
const TALK_RANGE := 56.0
const BARTER_RANGE := 80.0
const MESSAGE_LIFE := 2.0
# The rune's name he shouts, this far over his feet (screen px).
const SHOUT_Y := 170.0
const TITLE_LIFE := 3.0
const ZONE_SETTLE := 0.6
const CONTROLS := "WASD move  Click attack  Space dodge  1-5 speak a rune  E use  I bag  C runes  B book"
const PANEL := preload("res://scripts/ui/inventory_panel.gd")
const BARTER_PANEL := preload("res://scripts/ui/barter_panel.gd")
const RITE_PANEL := preload("res://scripts/ui/rite_panel.gd")
const KEEPSAKE := preload("res://scripts/ui/keepsake_hud.gd")
const TALK_BOX := preload("res://scripts/ui/talk_box.gd")
const TITLE_GILT := ["gilt-3", "gilt-3", "gilt-2", "gilt-1"]
# The lashed runes, bottom centre, one slot per key 1-5 (Utter.SOCKETS), over the controls line.
const RUNE_SLOT := 36
const RUNE_GAP := 6
const RUNE_BAR_Y := 64
const GEAR_AT := Vector2(52, 44)

var inventory := Inventory.new()
var hud := Node2D.new()
var titles := Node2D.new()
var keepsake := KEEPSAKE.new()
var panel := PANEL.new()
var barter_panel := BARTER_PANEL.new()
var rite_panel := RITE_PANEL.new()
var talk_box := TALK_BOX.new()
var talking = null
var writing := false
# Trackpad scroll adds up here into whole steps of the book.
var pan := 0.0
var barter := {}
# Who keeps the open stall: the barterer or the smith.
var keeper = null
var messages := []
var title := ""
var title_age := TITLE_LIFE
var zone := ""
var pending := ""
var pending_age := 0.0
var was_dead := false
var village := {}
var target = null

@onready var player = get_tree().get_first_node_in_group("player")
@onready var world = get_tree().get_first_node_in_group("world")


func _ready() -> void:
	layer = 5
	hud.draw.connect(draw_hud)
	add_child(hud)
	keepsake.position = Vector2(14, 10)
	add_child(keepsake)
	titles.material = ShaderMaterial.new()
	titles.material.shader = preload("res://shaders/title_ramp.gdshader")
	for i in TITLE_GILT.size():
		titles.material.set_shader_parameter("shade_%d" % i, Palette.color(TITLE_GILT[i]))
	titles.draw.connect(draw_title)
	add_child(titles)
	panel.inventory = inventory
	panel.player = player
	add_child(panel)
	barter_panel.inventory = inventory
	add_child(barter_panel)
	rite_panel.inventory = inventory
	rite_panel.player = player
	rite_panel.world = world
	add_child(rite_panel)
	player.said.connect(say)
	talk_box.text_submitted.connect(submitted)
	add_child(talk_box)
	player.inventory = inventory


func say(text: String, color: String) -> void:
	messages.append({"text": text, "color": color, "age": 0.0})


func show_title(text: String) -> void:
	title = text
	title_age = 0.0


func _input(event: InputEvent) -> void:
	if talking or writing:
		if event is InputEventKey and event.pressed and event.physical_keycode == KEY_ESCAPE:
			stop_talking()
			get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_E:
				interact()
				get_viewport().set_input_as_handled()
			KEY_I, KEY_TAB:
				inventory.open = not inventory.open
				panel.page = ""
				close_stalls()
				get_viewport().set_input_as_handled()
			KEY_C:
				open_page("sheet")
			KEY_B:
				open_page("book")
			KEY_N:
				if inventory.open and panel.page == "book":
					writing = true
					talk_box.open(screen_size(), "Write in the margin. Enter to write, Esc to stop.")
					get_viewport().set_input_as_handled()
			KEY_ESCAPE:
				inventory.open = false
				close_stalls()
	elif inventory.open and event is InputEventMouseButton and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
		if event.pressed:
			panel.scroll(1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else -1)
		get_viewport().set_input_as_handled()
	elif inventory.open and event is InputEventPanGesture:
		pan -= event.delta.y
		if absf(pan) >= 1:
			panel.scroll(int(pan))
			pan -= int(pan)
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if inventory.open:
			panel.click(event.position)
			get_viewport().set_input_as_handled()
		elif barter:
			barter_panel.click(event.position, Barter.SHIFT_TIMES if event.shift_pressed else 1)
			get_viewport().set_input_as_handled()
		elif rite_panel.place:
			rite_panel.click(event.position)
			get_viewport().set_input_as_handled()


# A page of the open panel, or back to the bag if it is already showing.
func open_page(page: String) -> void:
	panel.page = "" if inventory.open and panel.page == page else page
	panel.lines_back = 0
	inventory.open = true
	close_stalls()


func close_stalls() -> void:
	barter = {}
	rite_panel.place = null


func interact() -> void:
	if player.dead > 0:
		return
	if barter or rite_panel.place:
		close_stalls()
	elif target is Prop and target.def.get("rite", false):
		rite_panel.place = target
		inventory.open = false
	elif target is Prop:
		Journal.write("search_first")
		for line in world.search(target, inventory):
			say(line[0], line[1])
	elif target and target.role in ["barterer", "smith"]:
		if target.role == "barterer":
			Journal.write("barter_first")
		barter = village
		keeper = target
		barter_panel.shop = Smith if target.role == "smith" else Barter
		inventory.open = false
	elif target:
		Journal.write("talk_first")
		Journal.write("talk_%s_first" % target.role)
		talking = target
		talking.held = true
		talk_box.open(screen_size())


func submitted(text: String) -> void:
	text = text.strip_edges()
	if writing:
		if text:
			Journal.note(text)
		stop_talking()
	elif text:
		talking.ask(text)
	talk_box.clear()


func stop_talking() -> void:
	if is_instance_valid(talking):
		talking.held = false
	talking = null
	writing = false
	talk_box.close()


func now() -> float:
	return Time.get_ticks_msec() / 1000.0


func screen_size() -> Vector2:
	return get_viewport().get_visible_rect().size


func _process(dt: float) -> void:
	village = world.village_at(player.position)
	if village:
		player.respawn = village.centre + Villages.ARRIVAL
	target = world.nearest_rite_place(player.position) if village else null
	if not target and village:
		target = nearest_villager()
	if not target:
		target = world.nearest_lootable(player.position)
	if barter and keeper.position.distance_to(player.position) > BARTER_RANGE:
		barter = {}
	if rite_panel.place and (not is_instance_valid(rite_panel.place) or rite_panel.place.position.distance_to(player.position) > BARTER_RANGE):
		rite_panel.place = null
	if talking and (not is_instance_valid(talking) or talking.position.distance_to(player.position) > TALK_RANGE * 2 or player.dead > 0):
		stop_talking()
	barter_panel.village = barter
	player.ui_open = inventory.open or not barter.is_empty() or rite_panel.place != null or talking != null
	player.typing = talking != null or writing
	if writing and not inventory.open:
		stop_talking()

	var first_frame := Journal.corruption < 0
	Journal.track(player.corruption)
	if first_frame:
		Journal.write("three_winters")
	var name := settle_zone(next_zone(village.name if village else Terrain.biome_at(player.position).name), dt)
	if name != zone and player.dead <= 0:
		zone = name
		show_title(zone)
		if village:
			Journal.write_again("village", "village:" + name, name)
		else:
			Journal.write("biome:" + name.to_lower().replace(" ", "_"))
	if player.dead > 0 and not was_dead:
		show_title("You have fallen")
		close_stalls()
	if was_dead and player.dead <= 0:
		var once := "death:%d" % Journal.entries.size()
		# From the Whisper the dark gods send him back, not Wend (lore: Death).
		if player.corruption >= Journal.WHISPER:
			Journal.write("death_whisper", once)
		else:
			Journal.write_again("death", once)
	was_dead = player.dead > 0

	for m in messages:
		m.age += dt
	messages = messages.filter(func(m): return m.age < MESSAGE_LIFE)
	title_age += dt
	keepsake.update(dt, player.hp / player.max_hp, player.corruption)
	hud.queue_redraw()
	titles.queue_redraw()


# Roads and water have no name, so crossing them keeps the zone the player was in.
func next_zone(name: String) -> String:
	return name if name else zone


# A new zone counts once the player has been in it ZONE_SETTLE seconds, so walking along a ragged
# border doesn't flip the title back and forth.
func settle_zone(name: String, dt: float) -> String:
	if name == zone:
		pending = ""
		return zone
	if name != pending:
		pending = name
		pending_age = 0.0
	pending_age += dt
	return pending if pending_age >= ZONE_SETTLE else zone


# The barterer or smith first, then the closest villager within reach.
func nearest_villager():
	for v in [village.barterer, village.smith]:
		if v.position.distance_to(player.position) < TALK_RANGE:
			return v
	var best = null
	var best_distance := TALK_RANGE
	for v in village.villagers:
		var d: float = v.position.distance_to(player.position)
		if d < best_distance:
			best = v
			best_distance = d
	return best


# A world point on the screen.
func on_hud(pos: Vector2) -> Vector2:
	return (get_viewport().get_canvas_transform() * pos).floor()


func draw_hud() -> void:
	var size := screen_size()
	var feet := on_hud(player.position)
	GothicText.draw(hud, CONTROLS, Vector2(10, size.y - 22), "ash-3", GothicText.BODY, GothicText.SMALL_SIZE)
	for v in village.get("villagers", []) + ([village.barterer, village.smith] if village else []):
		if v.speech:
			draw_speech(v.speech, on_hud(v.position) - Vector2(0, 124))
	if player.shout:
		GothicText.centred(hud, player.shout, feet.x, feet.y - SHOUT_Y, "bone-0", GothicText.BODY, GothicText.TITLE_SIZE)
	for e in get_tree().get_nodes_in_group("enemies"):
		if e.get("shout"):
			var head := on_hud(e.position + Vector2(0, e.stats.bar * 2 - 12))
			GothicText.centred(hud, e.shout, head.x, head.y, "bone-0", GothicText.BODY, GothicText.TITLE_SIZE)
	draw_runes(size)
	draw_gear()
	if target and barter.is_empty() and not rite_panel.place and not talking and player.dead <= 0:
		draw_prompt(feet - Vector2(0, 118))
	draw_messages(feet - Vector2(0, 104))


# Strength and Armor under the keepsake's vial.
func draw_gear() -> void:
	var line := "Strength %d    Armor %d%%" % [inventory.forged.strength, roundi(player.armor() * 100)]
	GothicText.draw(hud, line, keepsake.position + GEAR_AT, "ash-4", GothicText.BODY, GothicText.SMALL_SIZE)


func draw_runes(size: Vector2) -> void:
	var w := Utter.SOCKETS.size() * (RUNE_SLOT + RUNE_GAP) - RUNE_GAP
	var x := floorf((size.x - w) / 2)
	var y := size.y - RUNE_BAR_Y
	for i in Utter.SOCKETS.size():
		var socket: Array = Utter.SOCKETS[i]
		var key = inventory.sockets[socket[0]][socket[1]]
		var at := Vector2(x + i * (RUNE_SLOT + RUNE_GAP), y)
		UiDraw.frame(hud, at.x, at.y, RUNE_SLOT, RUNE_SLOT)
		if key:
			Items.draw_icon(hud, key, 1, at + Vector2(2, 2))
		GothicText.centred(hud, str(i + 1), at.x + RUNE_SLOT / 2, at.y + RUNE_SLOT + 1, "ash-3", GothicText.BODY, GothicText.SMALL_SIZE)


# The E key in a small iron plate with gilt corners.
func draw_prompt(at: Vector2) -> void:
	var w := 15
	var h := 17
	var x := at.x - floori(w / 2.0)
	UiDraw.frame(hud, x, at.y, w, h)
	for corner in [Vector2(x, at.y), Vector2(x + w - 2, at.y), Vector2(x, at.y + h - 2), Vector2(x + w - 2, at.y + h - 2)]:
		UiDraw.rect(hud, "gilt-1", corner.x, corner.y, 2, 2)
	GothicText.centred(hud, "E", at.x + 1, at.y - 1, "bone-1")


# A dark plate with gilt edges and corners, and a small tail pointing at the speaker.
func draw_speech(text: String, at: Vector2) -> void:
	var w := GothicText.width(text) + 16
	var h := GothicText.height() + 6
	var x := floorf(at.x - w / 2)
	UiDraw.rect(hud, "void-0", x - 1, at.y - 1, w + 2, h + 2)
	UiDraw.rect(hud, "void-1", x, at.y, w, h)
	UiDraw.rect(hud, "gilt-1", x, at.y, w, 1)
	UiDraw.rect(hud, "gilt-0", x, at.y + h - 1, w, 1)
	for corner in [Vector2(x, at.y), Vector2(x + w - 3, at.y), Vector2(x, at.y + h - 3), Vector2(x + w - 3, at.y + h - 3)]:
		UiDraw.rect(hud, "gilt-2", corner.x, corner.y, 3, 3)
	for k in 3:
		UiDraw.rect(hud, "void-1", at.x - 2 + k, at.y + h + k, 5 - k * 2, 1)
	GothicText.draw(hud, text, Vector2(x + 8, at.y + 2), "bone-0")


# Pickup and status lines rising over the player and fading.
func draw_messages(at: Vector2) -> void:
	for i in messages.size():
		var m: Dictionary = messages[i]
		var y := at.y - (messages.size() - i) * 16 - floori(m.age * 12)
		GothicText.centred(hud, m.text, at.x, y, m.color, GothicText.BODY, GothicText.BODY_SIZE, false, minf(1.0, (MESSAGE_LIFE - m.age) * 2))


# The zone's name in gilt blackletter at the top of the screen over a gilt flourish, with "Safe"
# under it inside a village. Drawn white into `titles`, whose shader lights it like cast metal.
func draw_title() -> void:
	var cx := floorf(screen_size().x / 2)
	var y := 10.0
	var showing := title_age < TITLE_LIFE
	if showing:
		var alpha := minf(1.0, minf((TITLE_LIFE - title_age) * 2, title_age * 4))
		var font := GothicText.TITLE
		var size := GothicText.TITLE_SIZE
		titles.material.set_shader_parameter("top", y + font.get_ascent(size) * 0.25)
		titles.material.set_shader_parameter("height", font.get_ascent(size) * 0.8)
		GothicText.centred(titles, title, cx, y, "", font, size, true, alpha)
		if alpha > 0.5:
			GothicText.flourish(titles, cx, y + GothicText.height(font, size) + 4, floori(GothicText.width(title, font, size) / 2))
	if village:
		GothicText.centred(titles, "Safe", cx, y + (52 if showing else 0), "ash-4", GothicText.BODY, GothicText.SMALL_SIZE)
