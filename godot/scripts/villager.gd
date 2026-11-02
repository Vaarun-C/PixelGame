extends Actor

# Villagers wander around their home; the barterer keeps to the stall (src/village.js).
const WANDER_RADIUS := 384.0
const TARGET_SECONDS := 6.0
const SPEECH_SECONDS := 3.5

@export_enum("peasant", "monk", "guard", "barterer") var role := "peasant"
@export var wait := 1.0

var home := Vector2.ZERO
var target = null
var target_time := 0.0
var speech := ""
var speech_age := 0.0
var last_line := -1


func _ready() -> void:
	var dir := "res://art/characters/%s/%s_hd_" % [role, role]
	sheets = {
		"idle": sheet_entry(dir + "idle.png", Vector2i(64, 96)),
		"walk": sheet_entry(dir + "walk.png", Vector2i(64, 96)),
	}
	super._ready()
	home = position


func _physics_process(dt: float) -> void:
	speech_age += dt
	if speech and speech_age > SPEECH_SECONDS:
		speech = ""
	update_movement(wander(dt), false, dt)
	show_frame(anim, walk_frame())


func wander(dt: float) -> Vector2:
	if role == "barterer":
		return Vector2.ZERO
	if speech or wait > 0:
		wait -= dt
		return Vector2.ZERO
	if target == null:
		target = home + Vector2.from_angle(randf() * TAU) * randf() * WANDER_RADIUS
		target_time = TARGET_SECONDS
		return Vector2.ZERO
	var to: Vector2 = target - position
	target_time -= dt
	if to.length() < 8 or target_time < 0:
		target = null
		wait = 1 + randf() * 4
		return Vector2.ZERO
	return Vector2(signf(to.x) if absf(to.x) > 4 else 0.0, signf(to.y) if absf(to.y) > 4 else 0.0)


# The next of this role's lines (src/village.js talk); they stop to say it.
func talk() -> void:
	var lines: Array = Villages.LINES[role]
	last_line = (last_line + 1) % lines.size()
	speech = lines[last_line]
	speech_age = 0.0
	target = null
