class_name Prop
extends Node2D

# A placed prop (drawProp in src/world.js): sprite, ground shadow, collision box, a loot glint, and
# a few grass tufts in front of its base so it sits in the ground rather than on it.
# The node sits on the prop's ground contact point so it y-sorts with the characters.
const GLINT_ARMS := [0, 1, 2, 1]
const GLINT_PERIOD := 2400
const GLINT_TIME := 320
# Light comes from the top-left (ART_RULES §2), so each prop's contact shadow hugs the bottom
# contour of its art and peeks out down and to the right. World pixels.
const SHADOW_SHIFT := 1
const SHADOW_DEPTH := 2
# Columns whose art reaches this close to the lowest row are standing on the ground (a tree's
# branches above don't cast a contact shadow). Flat props lie on the ground across their whole width.
const BASE_ROWS := 4
const MAX_TUFTS := 3

static var contours := {}

var def: Dictionary
var def_kind := ""
var variant := 0
var key := ""
# Searched and empty: shows the spent sprite (an opened chest, a burnt-out pyre) and no glint.
var spent := false:
	set(value):
		spent = value
		if sprite:
			sprite.frame = variant + (def.get("spentOffset", 0) if spent else 0)
		if glint:
			glint.visible = not spent
var sprite: Sprite2D
var glint: Node2D
var tufts := []
var front: Node2D
var shown_frame := -1


static func create(kind: String, variant: int, at: Vector2) -> Prop:
	var prop := Prop.new()
	prop.def = Props.LIST[kind]
	prop.def_kind = kind
	prop.variant = variant
	prop.position = at
	var def := prop.def
	var sprite_scale: float = def.get("scale", 1.0)
	var sprite := Sprite2D.new()
	sprite.texture = load("res://art/props/%s.png" % def.sheet)
	sprite.hframes = sprite.texture.get_width() / def.size
	sprite.frame = variant
	sprite.centered = false
	sprite.scale = Vector2.ONE * sprite_scale * Terrain.SCALE
	sprite.offset = -Vector2(def.size / 2, def.get("feet", def.size - 4))
	prop.add_child(sprite)
	prop.sprite = sprite

	var box := Props.solid_box(kind, variant)
	if box:
		prop.add_child(collision_body(box))
	if def.get("flat", false):
		prop.z_index = -1
	if def.get("rite", false):
		prop.add_to_group("rite_places")
	if def.has("loot"):
		prop.add_to_group("lootables")
		prop.glint = Node2D.new()
		prop.glint.draw.connect(prop.draw_glint)
		prop.add_child(prop.glint)
	if not def.get("flat", false):
		prop.tufts = base_tufts(def, variant, at)
	if prop.tufts:
		prop.front = Node2D.new()
		prop.front.draw.connect(func(): for tuft in prop.tufts: Decals.draw(prop.front, tuft, -at))
		prop.add_child(prop.front)
	return prop


# Tufts of whatever grows on the ground here, rooted just in front of the art's bottom edge.
static func base_tufts(def: Dictionary, variant: int, at: Vector2) -> Array:
	var kinds := Terrain.tufts_at(at)
	var base := contour(def, variant)
	if kinds.is_empty() or base.is_empty():
		return []
	var h := WorldNoise.hash32([Terrain.world_seed, int(at.x), int(at.y), 70])
	var found := []
	for i in h % (MAX_TUFTS + 1):
		var pick := WorldNoise.hash32([h, i])
		var point: Vector2i = base[pick % base.size()]
		found.append(Decals.placed(kinds[pick % kinds.size()], pick >> 8, at + Vector2(point.x, point.y + 1) * Terrain.SCALE, true))
	return found


static func collision_body(box: Array) -> StaticBody2D:
	var shape := CollisionShape2D.new()
	shape.shape = RectangleShape2D.new()
	shape.shape.size = Vector2(box[2], box[3]) * Terrain.SCALE
	shape.position = Vector2(box[0] + box[2] / 2.0, box[1] + box[3] / 2.0) * Terrain.SCALE
	var body := StaticBody2D.new()
	body.add_child(shape)
	return body


func _ready() -> void:
	set_process(glint != null or tufts.any(func(t): return t.phase >= 0))


func _process(_dt: float) -> void:
	if glint:
		glint.queue_redraw()
	if front and Decals.frame_now() != shown_frame:
		shown_frame = Decals.frame_now()
		front.queue_redraw()


# The bottom row of the art in each world-pixel column that touches the ground, relative to the
# anchor: [Vector2i(x, bottom), ...]. Measured once per sheet frame.
static func contour(def: Dictionary, variant: int) -> Array:
	var key := "%s:%d" % [def.sheet, variant]
	if contours.has(key):
		return contours[key]
	var size: int = def.size
	var per_world_px: float = 1.0 / def.get("scale", 1.0)
	var frame: Image = load("res://art/props/%s.png" % def.sheet).get_image().get_region(Rect2i(variant * size, 0, size, size))
	var anchor := Vector2(size / 2.0, def.get("feet", size - 4))
	var bottoms := {}
	for x in size:
		for y in range(size - 1, -1, -1):
			if frame.get_pixel(x, y).a > 0:
				var column := floori((x - anchor.x) / per_world_px)
				bottoms[column] = maxi(bottoms.get(column, -size), floori((y - anchor.y) / per_world_px))
				break
	var lowest: int = bottoms.values().max() if bottoms else 0
	var flat: bool = def.get("flat", false)
	var base := []
	for column in bottoms:
		if flat or bottoms[column] >= lowest - BASE_ROWS:
			base.append(Vector2i(column, bottoms[column]))
	contours[key] = base
	return base


# Behind the art's bottom edge, showing as a thin dark rim below it and to its right.
func _draw() -> void:
	var color := Color(Palette.color("void-0"), 0.5)
	var cells := {}
	for point in contour(def, variant):
		for dy in range(-SHADOW_DEPTH, SHADOW_DEPTH):
			cells[point + Vector2i(SHADOW_SHIFT, dy + 1)] = true
	for cell in cells:
		draw_rect(Rect2(Vector2(cell) * Terrain.SCALE, Vector2.ONE * Terrain.SCALE), color)


# A brief bone-white sparkle above lootable props, staggered by position.
func draw_glint() -> void:
	var p := position / Terrain.SCALE
	var phase := posmod(int(Time.get_ticks_msec() + p.x * 37 + p.y * 91), GLINT_PERIOD)
	if phase >= GLINT_TIME:
		return
	var arm: int = GLINT_ARMS[phase / 80]
	var at := Vector2(-2, -def.glint)
	dot(at - Vector2(arm, 0), Vector2(arm * 2 + 1, 1), "bone-0")
	dot(at - Vector2(0, arm), Vector2(1, arm * 2 + 1), "bone-0")
	dot(at, Vector2.ONE, "bone-1")


func dot(at: Vector2, size: Vector2, color: String) -> void:
	glint.draw_rect(Rect2(at * Terrain.SCALE, size * Terrain.SCALE), Palette.color(color))
