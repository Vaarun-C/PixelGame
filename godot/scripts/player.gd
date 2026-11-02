extends Actor

# The wanderer: sword combo, dodge and taking hits (src/combat.js and hurtPlayer in src/main.js).
const DEG := PI / 180
const MAX_HP := 100.0
const HURT_INVULN := 0.7
const HURT_KNOCK := 320.0
const DEATH_SECONDS := 2.5
const BODY := Vector2i(96, 96)
const ATTACK_BODY := Vector2i(128, 144)

# The sword combo. Times in seconds, reach in px, lunge/knock in px/s, cone in degrees around the aim.
# Each swing hits once, at the start of its strike, everything within reach and inside the cone.
# anim picks the attack sheet.
const COMBO := [
	{"windup": 0.08, "strike": 0.07, "recover": 0.22, "anim": "light", "damage": 10.0, "reach": 68.0, "cone": 150.0, "lunge": 300.0, "knock": 260.0, "hitstop": 0.05, "shake": 2.0},
	{"windup": 0.06, "strike": 0.07, "recover": 0.22, "anim": "light", "damage": 12.0, "reach": 68.0, "cone": 150.0, "lunge": 300.0, "knock": 280.0, "hitstop": 0.05, "shake": 2.5},
	{"windup": 0.1, "strike": 0.06, "recover": 0.24, "anim": "light", "damage": 14.0, "reach": 88.0, "cone": 60.0, "lunge": 520.0, "knock": 360.0, "hitstop": 0.06, "shake": 3.0},
	{"windup": 0.32, "strike": 0.09, "recover": 0.45, "anim": "heavy", "damage": 34.0, "reach": 84.0, "cone": 170.0, "lunge": 420.0, "knock": 600.0, "knockdown": true, "hitstop": 0.13, "shake": 7.0},
]
# Attack sheet length and, per facing, the frame where the blade lands (see attack_frame).
const ATTACK_FRAMES := {
	"light": {"frames": 6, "impact": {"down": 3, "left": 2, "right": 2, "up": 4}},
	"heavy": {"frames": 8, "impact": {"down": 6, "left": 5, "right": 4, "up": 6}},
}
const REACH_PAD := 16.0
const CHAIN_AFTER := 0.06
const AIM_FROM_Y := -28.0
const CHEST_Y := -36.0
const DODGE := {"time": 0.32, "iframes": 0.24, "speed": 350.0, "cooldown": 0.45}
const GHOST_EVERY := 0.03
const GHOST_LIFE := 0.2
const GHOST_ALPHA := 0.35
const BASE_SPEED := 120.0
# No enemy this close (Godot px) counts as out of the fight, for Scab and crimson Hunger.
const CALM_RANGE := 240.0
const PASS_RANGE := 28.0
const STILL_SPEED := 5.0
const CHARACTERS_LAYER := 3

var max_hp := MAX_HP
var hp := MAX_HP
# Rune state (src/runes.js): stats from the socketed runes, recomputed every frame.
var inventory: Inventory
var runes := Runes.stats(Runes.empty_sockets())
var shield := 0.0
var rune_hits := 0
var riposte := false
var empower := 0.0
var guard := 0.0
var guard_time := 0.0
var still_time := 0.0
var dodge_speed := DODGE.speed
var passed := []
var since_hurt := 0.0
var self_bleed := 0.0
# A panel is open: clicks and Space belong to it, not to the sword.
var ui_open := false
# A cutscene holds him still: no moving, swinging or dodging.
var frozen := false
# A cutscene pose overrides the animation: {"sheet": name, "frame": n}.
var pose := {}
# The one meter (LORE.md, Corruption): 0..1. The Whisper from 0.75, the Pull at 1. Nothing raises or
# lowers it yet; he starts where the lore puts him.
var corruption := 0.30
var invuln := 0.0
var flash := 0.0
var dead := 0.0
var respawn := Vector2.ZERO
var move := -1
var phase := ""
var t := 0.0
var aim := 0.0
var queued := false
var dodge := 0.0
var dodge_cooldown := 0.0
var dodge_dir := Vector2.ZERO
var ghost_timer := 0.0
var ghost_material := ShaderMaterial.new()
var attack_pressed := false
var dodge_pressed := false


func _ready() -> void:
	var dir := "res://art/characters/wanderer_hd/wanderer_hd_%s.png"
	sheets = {
		"idle": sheet_entry(dir % "idle", BODY),
		"walk": sheet_entry(dir % "walk", BODY),
		"light": sheet_entry(dir % "light", ATTACK_BODY),
		"heavy": sheet_entry(dir % "heavy", ATTACK_BODY),
	}
	super._ready()
	position = Villages.start_position()
	respawn = position
	ghost_material.shader = tint_material.shader
	ghost_material.set_shader_parameter("tint", Palette.color("steel-1"))


func _unhandled_input(event: InputEvent) -> void:
	if ui_open or frozen:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		attack_pressed = true
	elif event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_SPACE:
		dodge_pressed = true


func _physics_process(dt: float) -> void:
	invuln -= dt
	flash -= dt
	if inventory:
		runes = Runes.stats(inventory.sockets)
	speed = BASE_SPEED * Runes.speed_factor(runes)
	if dead <= 0:
		Runes.update(runes, self, dt, calm())
	if dead > 0:
		dead -= dt
		if dead <= 0:
			respawn_now()
		update_movement(Vector2.ZERO, false, dt)
	elif frozen:
		update_movement(Vector2.ZERO, false, dt)
	else:
		var dir := Vector2(held(KEY_D, KEY_RIGHT) - held(KEY_A, KEY_LEFT), held(KEY_S, KEY_DOWN) - held(KEY_W, KEY_UP))
		var run := Input.is_physical_key_pressed(KEY_SHIFT)
		var mouse_aim := (get_global_mouse_position() - global_position - Vector2(0, AIM_FROM_Y)).angle()
		var step := update_combat(dir, run, mouse_aim, dt)
		update_movement(step.dir, step.run, dt, step.ground)
		still_time = still_time + dt if velocity.length() < STILL_SPEED and move < 0 and dodge <= 0 else 0.0
	attack_pressed = false
	dodge_pressed = false
	update_sprite()


func held(a: Key, b: Key) -> float:
	return 1.0 if Input.is_physical_key_pressed(a) or Input.is_physical_key_pressed(b) else 0.0


func calm() -> bool:
	return not get_tree().get_nodes_in_group("enemies").any(func(e): return e.dying <= 0 and e.position.distance_to(position) < CALM_RANGE)


# Back at the last village (or the start) with the Hollows that were hunting cleared away.
func respawn_now() -> void:
	position = respawn
	velocity = Vector2.ZERO
	hp = max_hp
	shield = 0.0
	for e in get_tree().get_nodes_in_group("enemies"):
		e.queue_free()


func dodge_invulnerable() -> bool:
	return dodge > DODGE.time - DODGE.iframes


func hurt(damage: float, angle: float, attacker = null) -> void:
	if dodge_invulnerable():
		Runes.on_dodged(runes, self)
	if dead > 0 or invuln > 0 or dodge_invulnerable():
		return
	var blow := Runes.take_hit(runes, self, damage, attacker)
	hp = maxf(0.0, hp - blow.hurt)
	invuln = HURT_INVULN
	flash = 0.12
	if blow.knockback:
		velocity = Vector2.from_angle(angle) * HURT_KNOCK
	cancel_combat()
	Effects.hit_stop(0.08)
	Effects.shake(4)
	Effects.burst(global_position + Vector2(0, -32), angle, 10, 240, 1.2, ["blood-2", "blood-3"], 0.4)
	if hp <= 0:
		dead = DEATH_SECONDS


func cancel_combat() -> void:
	move = -1
	phase = ""
	queued = false


func start_move(index: int, at: float) -> void:
	move = index
	phase = "windup"
	t = 0.0
	aim = at
	queued = false


# The movement to apply this frame: rooted while swinging, forced while dodging.
func update_combat(dir: Vector2, run: bool, mouse_aim: float, dt: float) -> Dictionary:
	dodge_cooldown -= dt
	if dodge_pressed and dodge_cooldown <= 0 and (move < 0 or phase == "recover"):
		dodge_dir = dir.normalized() if dir else Vector2.from_angle(mouse_aim)
		dodge = DODGE.time
		dodge_speed = DODGE.speed * Runes.dodge_factor(runes, self)
		dodge_cooldown = DODGE.time + DODGE.cooldown * Runes.dodge_cooldown_factor(runes)
		passed = []
		cancel_combat()
		Runes.on_dodge(runes, self)
	# Dodging rolls through other characters; only props stop it.
	set_collision_mask_value(CHARACTERS_LAYER, dodge <= 0)
	if dodge > 0:
		dodge -= dt
		ghost_timer -= dt
		if ghost_timer <= 0:
			ghost_timer = GHOST_EVERY
			spawn_ghost()
		for e in get_tree().get_nodes_in_group("enemies"):
			if e.dying <= 0 and e not in passed and e.position.distance_to(position) < PASS_RANGE:
				passed.append(e)
				Runes.on_through(runes, self, e)
		return {"dir": dodge_dir, "run": false, "ground": {"speed": dodge_speed / speed, "slide": 40.0}}

	if attack_pressed:
		if move < 0:
			start_move(0, mouse_aim)
		else:
			queued = true
	if move < 0:
		return {"dir": dir, "run": run, "ground": null}

	var m: Dictionary = COMBO[move]
	t += dt
	if phase == "windup" and t >= m.windup:
		phase = "strike"
		t -= m.windup
		velocity = Vector2.from_angle(aim) * m.lunge
		resolve_hits(m)
	if phase == "strike" and t >= m.strike:
		phase = "recover"
		t -= m.strike
	if phase == "recover":
		var last := move == COMBO.size() - 1
		if queued and not last and t >= CHAIN_AFTER:
			start_move(move + 1, mouse_aim)
		elif t >= m.recover:
			var again := queued
			cancel_combat()
			if again:
				start_move(0, mouse_aim)
	facing = facing_from_angle(aim)
	return {"dir": Vector2.ZERO, "run": false, "ground": null}


func resolve_hits(m: Dictionary) -> void:
	var chest := global_position + Vector2(0, CHEST_Y)
	var knockdown: bool = m.get("knockdown", false)
	var hit := false
	for e in get_tree().get_nodes_in_group("enemies"):
		if e.dying > 0:
			continue
		var to: Vector2 = e.global_position + Vector2(0, -24) - chest
		var angle := to.angle()
		if to.length() > m.reach + REACH_PAD or absf(angle_difference(aim, angle)) > m.cone / 2 * DEG:
			continue
		var damage := Runes.strike_damage(runes, self, e, m.damage)
		e.take_damage(damage, angle, m.knock, knockdown)
		var wound: Vector2 = e.global_position + Vector2(0, -28)
		if Runes.on_strike(runes, self, e, damage, knockdown):
			Effects.burst(wound, angle, 8, 120, 2.5, ["blood-1", "blood-2"], 0.6)
		if e.hp <= 0:
			Runes.on_kill(runes, self)
		Effects.burst(wound, angle, 22 if knockdown else 12, 280, 1.4, ["blood-2", "blood-3", "blood-4"], 0.45)
		Effects.burst(wound, angle + PI, 4, 180, 2.0, ["bone-1", "steel-3"], 0.15)
		hit = true
	if hit:
		Effects.hit_stop(m.hitstop)
		Effects.shake(m.shake)
	if knockdown:
		var impact := global_position + Vector2(cos(aim) * m.reach * 0.8, sin(aim) * m.reach * 0.6)
		Effects.burst(impact, 0, 26, 220, TAU, ["ash-2", "ash-3", "leather-2"], 0.4)
		Effects.shake(m.shake if hit else 3.0)


# The body, or the attack animation while swinging, leaning toward the aim.
func update_sprite() -> void:
	var blink := invuln > 0 and floori(invuln * 20) % 2 == 0
	modulate.a = 0.5 if blink else 1.0
	set_tint("bone-1", 1.0 if flash > 0 else 0.0)
	if pose:
		show_frame(pose.sheet, pose.frame)
		return
	if move < 0:
		show_frame(anim, walk_frame())
		return
	var m: Dictionary = COMBO[move]
	var attack: Dictionary = ATTACK_FRAMES[m.anim]
	var frame := attack_frame(phase, t, m, attack.frames, attack.impact[facing])
	var lean: float = {"windup": -1.0, "strike": 2.0, "recover": 1.0 - minf(1.0, t / m.recover)}[phase]
	show_frame(m.anim, frame, Vector2.from_angle(aim) * lean)


func spawn_ghost() -> void:
	var ghost: Sprite2D = sprite.duplicate()
	ghost.material = ghost_material
	ghost.modulate.a = GHOST_ALPHA
	get_parent().add_child(ghost)
	get_parent().move_child(ghost, get_index())
	ghost.global_position = sprite.global_position
	var fade := ghost.create_tween()
	fade.tween_property(ghost, "modulate:a", 0.0, GHOST_LIFE)
	fade.tween_callback(ghost.queue_free)
