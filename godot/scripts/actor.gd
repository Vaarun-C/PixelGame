class_name Actor
extends CharacterBody2D

# Movement and animation shared by the player, villagers and Hollows (src/actor.js). Distances are
# the sprites' native pixels, which are the JS world's pixels times 2 (it draws 2x sheets at scale 0.5).
const RUN_MULT := 1.7
const ACCEL := 20.0
const DIRS := ["down", "left", "right", "up"]
const ANIMS := {"idle": {"frames": 4, "ms": 180}, "walk": {"frames": 6, "ms": 100}}
const MIN_FRAME_TIME := 0.04
const SHADOW_ROWS := [8, 14, 16, 14, 8]
const SHADOW_WIDTH := 16
# A walk is a series of steps, not a glide. Each facing's walk has two contact frames, read from
# the art (see contacts()). Speed drops by LURCH as a foot plants and surges between steps, the
# body sinks STEP_DIP world px on the contact and the ground kicks up a little of whatever it is
# made of (biomes.gd dust).
const LURCH := 0.35
# Rows at the bottom of a frame where its feet are measured.
const FEET_ROWS := 6
const STEP_DIP := 1
# The floor under the feet on sheets that aren't measured (attacks, poses: blades and bodies can
# reach the bottom edge), as ART_RULES §2 specifies.
const FEET_PAD := 2
# Two puffs roll out sideways from the planted foot, low along the ground; running kicks bigger ones.
const DUST_SPEED := 40.0
const DUST_LIFE := 0.45
const DUST_SIZE := [1.0, 3.0]
const RUN_DUST := 1.5

@export var speed := 120.0

# name -> {texture, size}, filled by each actor before _ready.
var sheets := {}
# Idle and walk frame counts and timing; an actor whose sheets differ sets its own before _ready.
var anims := ANIMS
var facing := "down"
var anim := "idle"
var anim_time := 0.0
var sheet := ""
var tint_material := ShaderMaterial.new()
var last_walk_frame := -1

static var contact_cache := {}
static var floor_cache := {}

@onready var sprite: Sprite2D = $Sprite


func _ready() -> void:
	tint_material.shader = preload("res://shaders/silhouette.gdshader")
	sprite.material = tint_material
	set_tint("bone-1", 0.0)
	show_frame("idle", 0)


# rows: 1 for a sheet drawn for one facing only (a cutscene pose); it shows whatever the facing.
# floor: rows of the canvas under the feet, for a sheet whose canvas leaves more than FEET_PAD.
static func sheet_entry(path: String, size: Vector2i, rows := DIRS.size(), floor := FEET_PAD) -> Dictionary:
	return {"texture": load(path), "size": size, "rows": rows, "floor": floor}


# ground: {speed, slide} overrides the ground under the feet (Terrain.ground_at). An override is
# a forced move (a dodge), so it glides instead of stepping.
func update_movement(dir: Vector2, run: bool, dt: float, ground = null) -> void:
	var striding: bool = ground == null
	if striding:
		ground = Terrain.ground_at(position)
	var moving := dir != Vector2.ZERO
	var lurch := 1.0 - LURCH * cos(PI * minf(1.0, step_distance() / 1.5)) if striding and anim == "walk" else 1.0
	var target: Vector2 = dir.normalized() * speed * (RUN_MULT if moving and run else 1.0) * ground.get("speed", 1.0) * lurch
	velocity += (target - velocity) * minf(1.0, ground.get("slide", ACCEL) * dt)
	move_and_slide()

	var next := "walk" if moving else "idle"
	if next != anim:
		anim = next
		anim_time = 0.0
	anim_time += dt * (maxf(0.5, velocity.length() / speed) if moving else 1.0)
	if moving:
		facing = facing_for(dir, facing)
	var walk := walk_frame() if anim == "walk" and striding else -1
	if walk != last_walk_frame and walk in contacts():
		footfall(ground, run)
	last_walk_frame = walk


# The two walk frames of the current facing where a foot is planted: where the body sits lowest
# and the feet are spread widest, a pair roughly half a cycle apart.
func contacts() -> Array:
	var texture: Texture2D = sheets.walk.texture
	var row := DIRS.find(facing) if sheets.walk.rows > 1 else 0
	var key := "%s:%d" % [texture.resource_path, row]
	if not contact_cache.has(key):
		var size: Vector2i = sheets.walk.size
		var frames: int = anims.walk.frames
		var image := texture.get_image()
		var scores := []
		for f in frames:
			var frame := image.get_region(Rect2i(f * size.x, row * size.y, size.x, size.y))
			var used := frame.get_used_rect()
			var feet := frame.get_region(Rect2i(0, used.end.y - FEET_ROWS, size.x, FEET_ROWS)).get_used_rect()
			scores.append(used.position.y + feet.size.x / 10.0)
		var first: int = scores.find(scores.max())
		var opposite := range(first + 2, first + frames - 1).map(func(f): return f % frames)
		var second: int = opposite.reduce(func(best, f): return f if scores[f] > scores[best] else best)
		contact_cache[key] = [first, second]
	return contact_cache[key]


# Walk frames from the current moment to the nearest contact, either way round.
func step_distance() -> float:
	var frames: int = anims.walk.frames
	var now := fposmod(anim_time * 1000 / anims.walk.ms, frames)
	return contacts().map(func(c): return minf(absf(now - c), frames - absf(now - c))).min()


func footfall(ground: Dictionary, run: bool) -> void:
	if not ground.has("dust"):
		return
	var grow: float = RUN_DUST if run else 1.0
	for side in [-1, 1]:
		var at := global_position + Vector2(side * randf_range(4, 10), randf_range(-2, 2))
		var drift := Vector2(side * DUST_SPEED * randf_range(0.6, 1.0), -DUST_SPEED * 0.2) * grow
		Effects.puff(at, drift, ground.dust[randi() % ground.dust.size()], DUST_SIZE[0], DUST_SIZE[1] * grow, DUST_LIFE)


# Near-diagonals keep the current facing, so analog input (enemy steering) doesn't flip it every frame.
static func facing_for(dir: Vector2, current: String) -> String:
	var horizontal := "left" if dir.x < 0 else "right"
	var vertical := "up" if dir.y < 0 else "down"
	if absf(dir.x) > absf(dir.y) * 2:
		return horizontal
	if absf(dir.y) > absf(dir.x) * 2:
		return vertical
	return current if current == horizontal or current == vertical else horizontal


static func facing_from_angle(angle: float) -> String:
	var dir := Vector2.from_angle(angle)
	if absf(dir.x) > absf(dir.y):
		return "left" if dir.x < 0 else "right"
	return "up" if dir.y < 0 else "down"


# Attack sheet frame for a moment of an attack. times: {windup, strike, recover} in seconds.
# The frames before impact play during the windup (short windups skip the earliest so each lasts
# MIN_FRAME_TIME), the impact frame holds through the strike, the rest play during recovery.
static func attack_frame(phase: String, t: float, times: Dictionary, frames: int, impact: int) -> int:
	var k := minf(0.999, t / times[phase])
	if phase == "windup":
		var shown := maxi(1, mini(impact, floori(times.windup / MIN_FRAME_TIME)))
		return impact - shown + floori(k * shown)
	if phase == "strike":
		return impact
	return impact + ceili(k * (frames - 1 - impact))


func walk_frame() -> int:
	return floori(anim_time * 1000 / anims[anim].ms) % anims[anim].frames


# lean: sprite offset toward a blow, in world pixels.
func show_frame(next: String, frame: int, lean := Vector2.ZERO) -> void:
	if next != sheet:
		sheet = next
		var s: Dictionary = sheets[next]
		sprite.texture = s.texture
		sprite.hframes = s.texture.get_width() / s.size.x
		sprite.vframes = s.rows
		queue_redraw()
	var row := DIRS.find(facing) if sprite.vframes > 1 else 0
	sprite.offset = Vector2(-sheets[next].size.x / 2, floor_gap(next, row) - sheets[next].size.y)
	sprite.frame_coords = Vector2i(frame, row)
	var dip := STEP_DIP if next == "walk" and frame in contacts() else 0
	sprite.position = (lean.round() + Vector2(0, dip)) * 2


# Empty rows under the lowest foot in a sheet's row, so the feet stand on the actor's position
# whatever floor the art left under them. Only idle and walk frames show the true foot line.
func floor_gap(name: String, row: int) -> int:
	if name not in anims:
		return sheets[name].floor
	var s: Dictionary = sheets[name]
	var key := "%s:%d" % [s.texture.resource_path, row]
	if not floor_cache.has(key):
		var image: Image = s.texture.get_image()
		var gaps := []
		for f in s.texture.get_width() / s.size.x:
			var used := image.get_region(Rect2i(f * s.size.x, row * s.size.y, s.size.x, s.size.y)).get_used_rect()
			if used.has_area():
				gaps.append(s.size.y - used.end.y)
		floor_cache[key] = gaps.min() if gaps else 0
	return floor_cache[key]


func set_tint(color: String, amount: float) -> void:
	tint_material.set_shader_parameter("tint", Palette.color(color))
	tint_material.set_shader_parameter("amount", amount)


func set_outline(color: String, amount: float) -> void:
	tint_material.set_shader_parameter("outline", Palette.color(color))
	tint_material.set_shader_parameter("outline_amount", amount)


# Flat ellipse in void-0 at 50% (ART_RULES §2), as wide as the JS one for the current sheet.
func _draw() -> void:
	var width_scale: float = sheets[sheet].size.x / 32.0
	for i in SHADOW_ROWS.size():
		var w: float = SHADOW_ROWS[i] * width_scale
		draw_rect(Rect2(-w / 2, (i - 2) * 2, w, 2), Color(Palette.color("void-0"), 0.5))
