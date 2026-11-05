extends Node2D

# Keeps Hollows spawning in a ring around the player, off screen (updateEnemies in src/enemies.js),
# draws the atmosphere and corruption's greying over the world, darkens the screen while the player
# is dead, and handles
# zoom and fullscreen.
const HOLLOW := preload("res://scenes/hollow.tscn")
# Rarer Hollow bodies by biome: [scene, chance a spawn there is one].
const RARE := {
	"battlefield": [[preload("res://scenes/misborn.tscn"), 1.0 / 12], [preload("res://scenes/stammerer.tscn"), 0.08]],
	"ruins": [[preload("res://scenes/stammerer.tscn"), 0.15]],
}
const SPAWN_MIN := 600.0
const SPAWN_MAX := 920.0
const SPAWN_EVERY := 0.35
const DEATH_FADE := 0.75
const DEATH_FADE_SPEED := 0.6
# Whole steps only, so every sprite pixel stays the same size on screen (ART_RULES §2).
const MIN_ZOOM := 1
const MAX_ZOOM := 4
const PAN_PER_STEP := 3.0
const PINCH_PER_STEP := 1.3

@export var hollows := 10

var timer := 0.0
var zoom_gesture := 0.0
var fade := ColorRect.new()
var atmosphere := ColorRect.new()
var corruption := ColorRect.new()

@onready var player: Node2D = $Player


func _ready() -> void:
	atmosphere.material = ShaderMaterial.new()
	atmosphere.material.shader = preload("res://shaders/atmosphere.gdshader")
	atmosphere.material.set_shader_parameter("shade_color", Palette.color("void-0"))
	add_overlay(atmosphere)
	corruption.material = ShaderMaterial.new()
	corruption.material.shader = preload("res://shaders/corruption.gdshader")
	corruption.material.set_shader_parameter("dark", Palette.color("void-0"))
	add_overlay(corruption)
	fade.color = Color(Palette.color("void-0"), 0.0)
	add_overlay(fade)


# A full-screen rect above the world, stacked in the order added.
func add_overlay(rect: ColorRect) -> void:
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var layer := CanvasLayer.new()
	layer.layer = get_children().filter(func(c): return c is CanvasLayer).size() + 1
	layer.add_child(rect)
	add_child(layer)


# Scroll (mouse wheel or trackpad), pinch or +/- to zoom, F11 to toggle fullscreen.
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom_by(1)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom_by(-1)
	# Trackpads send a stream of small scroll and pinch deltas; add them up into whole zoom steps.
	elif event is InputEventPanGesture:
		zoom_gesture -= event.delta.y / PAN_PER_STEP
	elif event is InputEventMagnifyGesture:
		zoom_gesture += log(event.factor) / log(PINCH_PER_STEP)
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_EQUAL, KEY_KP_ADD:
				zoom_by(1)
			KEY_MINUS, KEY_KP_SUBTRACT:
				zoom_by(-1)
			KEY_F11:
				var fullscreen := DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
				DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if fullscreen else DisplayServer.WINDOW_MODE_FULLSCREEN)


func zoom_by(step: int) -> void:
	var camera: Camera2D = player.get_node("Camera")
	camera.zoom = Vector2.ONE * clampi(int(camera.zoom.x) + step, MIN_ZOOM, MAX_ZOOM)


func _process(_dt: float) -> void:
	var to_world := get_viewport().get_canvas_transform().affine_inverse()
	atmosphere.material.set_shader_parameter("view_origin", to_world.origin)
	atmosphere.material.set_shader_parameter("view_size", to_world.basis_xform(get_viewport().get_visible_rect().size))
	corruption.visible = player.corruption >= 0.72
	corruption.material.set_shader_parameter("corruption", player.corruption)
	if absf(zoom_gesture) >= 1:
		zoom_by(int(signf(zoom_gesture)))
		zoom_gesture = 0.0
	var dead_for: float = player.DEATH_SECONDS - player.dead
	fade.color.a = minf(DEATH_FADE, dead_for * DEATH_FADE_SPEED) if player.dead > 0 else 0.0


func _physics_process(dt: float) -> void:
	timer -= dt
	if timer > 0 or get_tree().get_nodes_in_group("enemies").size() >= hollows:
		return
	timer = SPAWN_EVERY
	var at := player.position + Vector2.from_angle(randf() * TAU) * randf_range(SPAWN_MIN, SPAWN_MAX)
	if Terrain.blocked(at) or Terrain.in_village_grounds(at) or not Terrain.reachable(at, player.position):
		return
	var scene: PackedScene = HOLLOW
	for rare in RARE.get(Terrain.biome_at(at).id, []):
		if randf() < rare[1]:
			scene = rare[0]
			break
	var hollow := scene.instantiate()
	hollow.position = at
	add_child(hollow)
