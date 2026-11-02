extends Actor

# Villagers wander around their home; the barterer keeps to the stall (src/village.js).
const WANDER_RADIUS := 384.0
const TARGET_SECONDS := 6.0
const SPEECH_SECONDS := 3.5
const SECONDS_PER_WORD := 0.4
const HISTORY := 2

@export_enum("peasant", "monk", "guard", "barterer") var role := "peasant"
@export var wait := 1.0

var home := Vector2.ZERO
var target = null
var target_time := 0.0
var speech := ""
var speech_age := 0.0
var last_line := -1
var villager_name := ""
var village_name := ""
var persona_seed := 0
var history := []
var waiting := false
# Held in place while the Wanderer is speaking with them.
var held := false


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
	if speech and not waiting and speech_age > SPEECH_SECONDS + speech.split(" ").size() * SECONDS_PER_WORD:
		speech = ""
	update_movement(wander(dt), false, dt)
	show_frame(anim, walk_frame())


func wander(dt: float) -> Vector2:
	if role == "barterer":
		return Vector2.ZERO
	if held or speech or waiting or wait > 0:
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


# The next of this role's scripted lines (src/village.js talk); they stop to say it.
func talk() -> void:
	var lines: Array = Villages.LINES[role]
	last_line = (last_line + 1) % lines.size()
	say(lines[last_line])


# A typed question for the dialogue model; the scripted line stands in when it can't answer.
func ask(question: String) -> void:
	if waiting:
		return
	waiting = true
	say("...")
	var request := {"role": role, "name": villager_name, "village": village_name, "seed": persona_seed, "history": history, "question": question}
	Dialogue.ask(request, func(reply: String):
		waiting = false
		if reply.is_empty():
			talk()
			return
		say(reply)
		history = (history + [[question, reply]]).slice(-HISTORY))


func say(text: String) -> void:
	speech = text
	speech_age = 0.0
	target = null
