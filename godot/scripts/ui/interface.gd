extends CanvasLayer

# Interaction and HUD (the tick in src/main.js, src/ui.js): E searches a lootable prop, opens the
# talk box to question a villager (the dialogue model, see dialogue.gd) or opens the barterer's stall; I or Tab opens the bag; Esc closes. The HUD draws at native
# pixels: the keepsake, gothic lettering and gilt titles. The barter panel still draws at the JS
# game's 1x, scaled by BARTER_SCALE.
const BARTER_SCALE := 2
const TALK_RANGE := 56.0
const BARTER_RANGE := 80.0
const MESSAGE_LIFE := 2.0
const TITLE_LIFE := 3.0
const CONTROLS := "WASD move  Click attack  Space dodge  E use  I bag"
const PANEL := preload("res://scripts/ui/inventory_panel.gd")
const KEEPSAKE := preload("res://scripts/ui/keepsake_hud.gd")
const TALK_BOX := preload("res://scripts/ui/talk_box.gd")
const TITLE_GILT := ["gilt-3", "gilt-3", "gilt-2", "gilt-1"]

var inventory := Inventory.new()
var hud := Node2D.new()
var titles := Node2D.new()
var barter_hud := Node2D.new()
var keepsake := KEEPSAKE.new()
var panel := PANEL.new()
var talk_box := TALK_BOX.new()
var talking = null
var barter := {}
var messages := []
var title := ""
var title_age := TITLE_LIFE
var zone := ""
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
	barter_hud.scale = Vector2.ONE * BARTER_SCALE
	barter_hud.draw.connect(draw_barter)
	add_child(barter_hud)
	panel.inventory = inventory
	panel.player = player
	add_child(panel)
	talk_box.text_submitted.connect(ask)
	add_child(talk_box)
	player.inventory = inventory


func say(text: String, color: String) -> void:
	messages.append({"text": text, "color": color, "age": 0.0})


func show_title(text: String) -> void:
	title = text
	title_age = 0.0


func _input(event: InputEvent) -> void:
	if talking:
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
				barter = {}
				get_viewport().set_input_as_handled()
			KEY_ESCAPE:
				inventory.open = false
				barter = {}
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if inventory.open:
			panel.click(event.position)
			get_viewport().set_input_as_handled()
		elif barter:
			var list := Barter.offers(barter, now())
			var i := Barter.offer_at(list, event.position / BARTER_SCALE, barter_size())
			if i >= 0 and not Barter.trade(inventory, list[i], Barter.SHIFT_TIMES if event.shift_pressed else 1):
				say("Not enough metal.", "ash-3")
			get_viewport().set_input_as_handled()


func interact() -> void:
	if player.dead > 0:
		return
	if barter:
		barter = {}
	elif target is Prop:
		for line in world.search(target, inventory):
			say(line[0], line[1])
	elif target and target.role == "barterer":
		barter = village
		inventory.open = false
	elif target:
		talking = target
		talking.held = true
		talk_box.open(screen_size())


func ask(question: String) -> void:
	if question.strip_edges():
		talking.ask(question.strip_edges())
	talk_box.clear()


func stop_talking() -> void:
	if is_instance_valid(talking):
		talking.held = false
	talking = null
	talk_box.close()


func now() -> float:
	return Time.get_ticks_msec() / 1000.0


func screen_size() -> Vector2:
	return get_viewport().get_visible_rect().size


func barter_size() -> Vector2:
	return (screen_size() / BARTER_SCALE).floor()


func _process(dt: float) -> void:
	village = world.village_at(player.position)
	if village:
		player.respawn = village.centre + Villages.ARRIVAL
	target = nearest_villager() if village else null
	if not target:
		target = world.nearest_lootable(player.position)
	if barter and barter.barterer.position.distance_to(player.position) > BARTER_RANGE:
		barter = {}
	if talking and (not is_instance_valid(talking) or talking.position.distance_to(player.position) > TALK_RANGE * 2 or player.dead > 0):
		stop_talking()
	player.ui_open = inventory.open or not barter.is_empty() or talking != null
	player.typing = talking != null

	var name: String = village.name if village else Terrain.biome_at(player.position).name
	if name != zone and player.dead <= 0:
		zone = name
		show_title(zone)
	if player.dead > 0 and not was_dead:
		show_title("You have fallen")
		barter = {}
	was_dead = player.dead > 0
	for m in messages:
		m.age += dt
	messages = messages.filter(func(m): return m.age < MESSAGE_LIFE)
	title_age += dt
	keepsake.update(dt, player.hp / player.max_hp, player.corruption)
	hud.queue_redraw()
	titles.queue_redraw()
	barter_hud.queue_redraw()


# The barterer first, then the closest villager within reach.
func nearest_villager():
	if village.barterer.position.distance_to(player.position) < TALK_RANGE:
		return village.barterer
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
	for v in village.get("villagers", []) + ([village.barterer] if village else []):
		if v.speech:
			draw_speech(v.speech, on_hud(v.position) - Vector2(0, 124))
	if target and barter.is_empty() and not talking and player.dead <= 0:
		draw_prompt(feet - Vector2(0, 118))
	draw_messages(feet - Vector2(0, 104))


func draw_barter() -> void:
	if barter:
		Barter.draw(barter_hud, inventory, barter, Barter.offers(barter, now()), get_viewport().get_mouse_position() / BARTER_SCALE, barter_size())


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
