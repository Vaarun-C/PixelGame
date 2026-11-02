extends Node

# The prologue (lore: The Wanderer, round 38): the last field, three winters before the game. He is
# at the Pull and starving. He takes a Rend stone from a dead man's hand, cuts with it until it
# reads, and the name he once spoke wakes him. Then the game proper starts in a village.
# It opens on a cutscene: letterboxed, the camera drifting across the field to him while he tells
# how he came here. Space or Esc skips it. Taking the stone is a second one: he kneels, the stone
# and then the hilt fill the screen as he sets it, and the dead around him rise as Hollows.
# Only a new game plays it: with a saved bag it hands straight over to the main scene.
const MAIN := "res://scenes/main.tscn"
const STONE := "rune_rend_1"
# Placeholder until the lore names him; the lore says it is an exact game string.
const NAME := "Aldric Venn"
const READ_HITS := 8
const HOLLOWS := 3
# Withdrawal: health drains while he isn't fighting, down to a floor; it never kills by itself.
const STARVE := 2.0
const STARVE_FLOOR := 30.0
const DEAD_MAN := Vector2(150, -60)
# Where he kneels, from the dead man, so he faces right into the one kneeling animation.
const KNEEL_SPOT := Vector2(-40, 6)
const KNEEL_FRAMES := 8
const KNEEL_TIME := 1.4
const KNEEL_HOLD := 0.8
const CLOSE_ZOOM := 2
# The dead lying around the dead man, who rise when the stone is set (offsets and facing rows).
const RISEN := [[Vector2(-210, 110), 2], [Vector2(190, 130), 1], [Vector2(30, -170), 0]]
const RISE_EVERY := 0.6
const HOLLOW_SCRIPT := preload("res://scripts/hollow.gd")
const CLOSEUP_TIME := 5.0
const DIM := 0.85
# The stone close-up: two frames, its light low and high, swapped slowly. Drawn at a whole scale.
const STONE_ART := preload("res://art/cutscenes/stone_closeup.png")
const STONE_SCALE := 2
const PULSE := 0.7
# The hilt close-up: frames of the stone being lashed to the ricasso, and where the stone sits in them.
const HILT_ART := preload("res://art/cutscenes/hilt_closeup.png")
const HILT_FRAMES := 12
const LASH_TIME := 9.0
const WOUND := 7.5
const HILT_SCALE := 2
const LASHED := Vector2(397, 48)
const LINE_TIME := 4.0
const FADE_TIME := 2.0
const INTRO_LINE_TIME := 4.5
const BARS := 64.0
const BARS_TIME := 1.0
# Where the camera starts, from its rest above the Wanderer; it eases back to him over the intro.
const DRIFT_FROM := Vector2(-560, -120)
const INTRO := [
	"A king died and said two words: Not him.",
	"His sons each swore it meant the other. We fought a generation over it.",
	"I was a chaplain. I knelt by the dying and said their names, and the short rite.",
	"The war had no time for the long one.",
	"Thousands. I did not count them.",
	"The dead did not stay down.",
	"Then the war did not end. It ran out.",
	"And something in me went wrong.",
	"The colour went out of things first.",
	"Then the long words. I knew them by heart, and they would not come.",
	"I was hungry, and food did not help.",
	"I wanted to kneel again. I did not know to whom.",
]
const OPENING := ["The last field. No one came to say it was over."]
const TAKEN := ["A shriving hand holds no stone.", "I hold it anyway."]
const WAKING := ["The stone reads. It says nothing."]
const FIGHT := ["Click to strike. Space to dodge."]

var beat := "intro"
var lines: Array = INTRO.duplicate()
var line_time := INTRO_LINE_TIME
var line_age := 0.0
var beat_age := 0.0
var black := 1.0
var bars := 1.0
var dim := 0.0
var dead_man: Prop
var risen := []
var screen := Node2D.new()

@onready var main = get_parent()
@onready var player = main.get_node("Player")
@onready var world = main.get_node("World")
@onready var interface: CanvasLayer = main.get_node("Interface")
@onready var inventory: Inventory = interface.inventory
@onready var camera: Camera2D = player.get_node("Camera")
@onready var camera_rest: Vector2 = camera.position


func _ready() -> void:
	if FileAccess.file_exists(Inventory.SAVE_PATH):
		get_tree().change_scene_to_file.call_deferred(MAIN)
		return
	player.corruption = 1.0
	player.sheets["kneel"] = Actor.sheet_entry("res://art/characters/wanderer_hd/wanderer_hd_kneel.png", player.BODY, 1)
	cutscene(true)
	camera.position = camera_rest + DRIFT_FROM
	var at: Vector2 = player.position + DEAD_MAN
	world.loot["prologue"] = [{"key": STONE, "count": 1}]
	dead_man = world.add_prop(world, "dead_man", 0, at, "prologue")
	for i in RISEN.size():
		var key := "risen:%d" % i
		world.loot[key] = []
		risen.append(world.add_prop(world, "body", RISEN[i][1], at + RISEN[i][0], key))
	var layer := CanvasLayer.new()
	layer.layer = 6
	screen.draw.connect(draw_screen)
	layer.add_child(screen)
	add_child(layer)


func _process(dt: float) -> void:
	line_age += dt
	beat_age += dt
	if line_age > line_time and lines.size() > 1:
		lines.pop_front()
		line_age = 0.0
	if not player.frozen and player.dead <= 0 and player.calm():
		player.hp = maxf(minf(player.hp, STARVE_FLOOR), player.hp - STARVE * dt)
	bars = move_toward(bars, 1.0 if player.frozen else 0.0, dt / BARS_TIME)
	dim = move_toward(dim, DIM if beat in ["stone", "lash"] else 0.0, dt * 2)
	match beat:
		"intro":
			black = maxf(0.0, black - dt / FADE_TIME)
			var drift := ease(minf(1.0, beat_age / (INTRO.size() * INTRO_LINE_TIME)), -2.0)
			camera.position = camera_rest + DRIFT_FROM * (1.0 - drift)
			if drift >= 1.0:
				end_intro()
		"opening":
			if inventory.count_of(STONE):
				kneel()
		"kneel":
			player.pose = {"sheet": "kneel", "frame": mini(KNEEL_FRAMES - 1, floori(beat_age / KNEEL_TIME * KNEEL_FRAMES))}
			if beat_age > KNEEL_TIME + KNEEL_HOLD:
				start("stone", [TAKEN[0]])
		"stone":
			if beat_age > CLOSEUP_TIME:
				set_stone()
		"lash":
			if beat_age > LASH_TIME:
				rise()
		"rise":
			var due := floori(beat_age / RISE_EVERY)
			for i in mini(due, risen.size()):
				if is_instance_valid(risen[i]):
					raise(risen[i])
			if beat_age > RISE_EVERY * risen.size() + HOLLOW_SCRIPT.RISE_TIME:
				fight()
		"reading":
			if player.rune_hits >= READ_HITS:
				wake()
		"waking":
			if beat_age > LINE_TIME:
				start("name", [])
		"name":
			if beat_age > LINE_TIME:
				start("after", ["I know this name. I said it."])
		"after":
			if beat_age > LINE_TIME:
				black = minf(1.0, black + dt / FADE_TIME)
			if black >= 1.0:
				start("card", ["Three winters later."])
		"card":
			if beat_age > LINE_TIME:
				get_tree().change_scene_to_file(MAIN)
	screen.queue_redraw()


func start(next: String, next_lines: Array) -> void:
	beat = next
	beat_age = 0.0
	lines = next_lines
	line_time = LINE_TIME
	line_age = 0.0


func _unhandled_input(event: InputEvent) -> void:
	if beat == "intro" and event is InputEventKey and event.pressed and event.physical_keycode in [KEY_SPACE, KEY_ESCAPE]:
		get_viewport().set_input_as_handled()
		end_intro()


# Letterbox, HUD and controls: the bars follow `frozen` (see _process).
func cutscene(on: bool) -> void:
	player.frozen = on
	interface.visible = not on
	interface.process_mode = Node.PROCESS_MODE_DISABLED if on else Node.PROCESS_MODE_INHERIT


func end_intro() -> void:
	black = 0.0
	camera.position = camera_rest
	cutscene(false)
	start("opening", OPENING.duplicate())


# He kneels by the dead man, facing him, and the camera closes in.
func kneel() -> void:
	cutscene(true)
	player.position = dead_man.position + KNEEL_SPOT
	player.velocity = Vector2.ZERO
	player.facing = "right"
	camera.zoom = Vector2.ONE * CLOSE_ZOOM
	start("kneel", [])


# Mad, he breaks the rule he kept for twenty years and lashes the stone to his blade himself.
func set_stone() -> void:
	inventory.remove(STONE, 1)
	inventory.sockets.blade[0] = STONE
	inventory.save()
	start("lash", [TAKEN[1]])


func rise() -> void:
	player.pose = {}
	camera.zoom = Vector2.ONE
	Effects.shake(4)
	start("rise", [])


# A dead man climbs up out of the ground as a Hollow, where his body lay and facing as it lay.
func raise(body: Prop) -> void:
	var hollow = main.HOLLOW.instantiate()
	hollow.position = body.position
	hollow.facing = Actor.DIRS[body.variant]
	hollow.rising = HOLLOW_SCRIPT.RISE_TIME
	hollow.state = "chase"
	main.add_child(hollow)
	body.queue_free()
	Effects.shake(3)
	Effects.burst(hollow.global_position + Vector2(0, -8), -PI / 2, 24, 160, 2.4, ["ash-2", "ash-3", "leather-1"], 0.6)


func fight() -> void:
	cutscene(false)
	player.rune_hits = 0
	main.hollows = HOLLOWS
	start("reading", FIGHT.duplicate())


# The stone reads. At the Pull its echo can't reach him, but the name comes back: he said it.
func wake() -> void:
	main.hollows = 0
	for e in get_tree().get_nodes_in_group("enemies"):
		if e.dying <= 0:
			e.take_damage(e.hp, player.position.angle_to_point(e.position), 200, true)
	Effects.hit_stop(0.3)
	Effects.shake(6)
	Effects.burst(player.global_position + Vector2(0, -40), 0, 40, 200, TAU, ["rune-pale-mid", "rune-pale-core"], 0.8)
	start("waking", WAKING.duplicate())


func draw_screen() -> void:
	var size := get_viewport().get_visible_rect().size
	if black > 0:
		screen.draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.color("void-0"), black))
	if dim > 0:
		screen.draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.color("void-0"), dim))
		match beat:
			"stone":
				draw_stone(size)
			"lash":
				draw_lash(size)
	if bars > 0:
		var h := roundf(BARS * bars)
		screen.draw_rect(Rect2(0, 0, size.x, h), Palette.color("void-0"))
		screen.draw_rect(Rect2(0, size.y - h, size.x, h), Palette.color("void-0"))
	if beat == "name":
		var alpha := minf(1.0, beat_age)
		GothicText.centred(screen, NAME, size.x / 2, size.y * 0.3, "rune-pale-core", GothicText.TITLE, GothicText.TITLE_SIZE, true, alpha)
	if lines:
		var alpha := minf(1.0, minf(line_age * 2, (line_time - line_age) * 2)) if lines.size() > 1 or beat != "card" else minf(1.0, line_age)
		var y := size.y - BARS + 20 if bars > 0 else size.y - 80
		GothicText.centred(screen, lines[0], size.x / 2, y, "bone-1", GothicText.BODY, GothicText.BODY_SIZE, true, maxf(alpha, 0.0))


# The stone in his palm, its light slowly rising and falling, named under it.
func draw_stone(size: Vector2) -> void:
	var frame := floori(beat_age / PULSE) % 2
	var art := Vector2(STONE_ART.get_width() / 2.0, STONE_ART.get_height())
	var at := ((size - art * STONE_SCALE) / 2).floor() - Vector2(0, 24)
	screen.draw_texture_rect_region(STONE_ART, Rect2(at, art * STONE_SCALE), Rect2(Vector2(art.x * frame, 0), art), Color(1, 1, 1, dim / DIM))
	var info := Items.info(STONE)
	var below := at.y + art.y * STONE_SCALE + 6
	GothicText.centred(screen, info.name, size.x / 2, below, info.color, GothicText.TITLE, GothicText.BODY_SIZE + 4, true, dim / DIM)
	GothicText.centred(screen, info.desc, size.x / 2, below + 26, "ash-4", GothicText.BODY, GothicText.BODY_SIZE, true, dim / DIM)


# The hilt across the screen while he threads the wire round it; the stone flares once it's tight.
func draw_lash(size: Vector2) -> void:
	var art := Vector2(HILT_ART.get_width() / HILT_FRAMES, HILT_ART.get_height())
	var at := ((size - art * HILT_SCALE) / 2).floor()
	var alpha := dim / DIM
	var frame := mini(HILT_FRAMES - 1, floori(beat_age / WOUND * HILT_FRAMES))
	screen.draw_texture_rect_region(HILT_ART, Rect2(at, art * HILT_SCALE), Rect2(Vector2(frame * art.x, 0), art), Color(1, 1, 1, alpha))
	var flare := beat_age - WOUND
	if flare > 0 and flare < 0.6:
		var r := 8 + flare * 120
		screen.draw_arc(at + LASHED * HILT_SCALE, r, 0, TAU, 32, Color(Palette.color("rune-pale-core"), (0.6 - flare) / 0.6 * alpha), 2)
