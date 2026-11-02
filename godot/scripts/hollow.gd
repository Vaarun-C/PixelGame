extends Actor

# The Hollow (src/enemies.js): a husk of a dead soldier. Slow, telegraphs a lunging spear thrust
# with an ember flash. Times in seconds, distances in px, speeds in px/s.
const HOLLOW := {
	"hp": 40.0, "aggro": 300.0, "leash": 660.0, "range": 52.0, "windup": 0.6, "strike": 0.14, "recover": 0.75,
	"lunge": 340.0, "damage": 15.0, "arc": 1.2, "stagger": 0.28, "knockdown": 0.9, "dying": 0.72,
}
# Spear thrust sheet: frame count and, per facing, the frame where the spear lands (see attack_frame).
const THRUST := {"frames": 6, "impact": {"down": 3, "left": 4, "right": 3, "up": 3}}
const ATTACKING := ["windup", "strike", "recover"]
const DEATH_FRAMES := 6
const HIT_PAD := 16.0
const SPACING := 28.0
const WANDER := 160.0
const DESPAWN := 1600.0
const MAX_BODIES := 40
# Blood drops per second from a bleeding Hollow.
const BLEED_DRIPS := 8.0
const TELEGRAPH_HOT := 0.6
# Climbing up out of a corpse: the death animation played backwards, slowly.
const RISE_TIME := 1.8

var hp: float = HOLLOW.hp
var state := "wander"
var t := 0.0
var aim := 0.0
var target = null
var hit := false
var flash := 0.0
var stagger := 0.0
var knocked_down := false
var dying := 0.0
var rising := 0.0
var bleed_time := 0.0
var bleed_dps := 0.0
# Rune effects from the player's strikes (game/runes.gd).
var hold_time := 0.0
var slow_time := 0.0
var slow_amount := 0.0
var broken := 0.0
var base_speed := 0.0

@onready var player = get_tree().get_first_node_in_group("player")


func _ready() -> void:
	var dir := "res://art/enemies/hollow_hd/hollow_hd_%s.png"
	sheets = {
		"idle": sheet_entry(dir % "idle", Vector2i(64, 96)),
		"walk": sheet_entry(dir % "walk", Vector2i(64, 96)),
		"attack": sheet_entry(dir % "attack", Vector2i(128, 112)),
		"death": sheet_entry(dir % "death", Vector2i(96, 96)),
	}
	super._ready()
	base_speed = speed


# Opened by Flay or Bloodletting runes: hp drains for `time` seconds, dripping blood.
func bleed(dps: float, time: float) -> void:
	bleed_dps = dps
	bleed_time = time


# Still: frozen in place, the attack broken off.
func hold(time: float) -> void:
	hold_time = maxf(hold_time, time)
	stagger = maxf(stagger, time)
	if state in ATTACKING:
		state = "chase"


# Sink: moves at (1 - amount) speed for `time` seconds.
func slow(amount: float, time: float) -> void:
	slow_amount = maxf(slow_amount if slow_time > 0 else 0.0, amount)
	slow_time = maxf(slow_time, time)


func knock_down() -> void:
	take_damage(0.0, (position - player.position).angle(), 120.0, true)


# Break builds toward a knockdown; returns true when it lands.
func add_break(amount: float) -> bool:
	broken += amount
	if broken < 1:
		return false
	broken = 0.0
	knock_down()
	return true


func wounded() -> bool:
	return hp < HOLLOW.hp


func take_damage(damage: float, angle: float, knock: float, knockdown: bool) -> void:
	hp -= damage
	flash = 0.12
	velocity = Vector2.from_angle(angle) * knock
	stagger = HOLLOW.knockdown if knockdown else HOLLOW.stagger
	knocked_down = knockdown
	# Any hit breaks the attack, so a staggered Hollow never holds its thrust pose.
	if state in ATTACKING:
		state = "chase"
	if hp <= 0:
		dying = HOLLOW.dying


func _physics_process(dt: float) -> void:
	flash -= dt
	hold_time -= dt
	slow_time -= dt
	speed = base_speed * (1 - slow_amount if slow_time > 0 else 1.0)
	if position.distance_to(player.position) > DESPAWN:
		queue_free()
		return
	if bleed_time > 0 and dying <= 0:
		bleed_time -= dt
		hp -= bleed_dps * dt
		if hp <= 0:
			dying = HOLLOW.dying
		if randf() < dt * BLEED_DRIPS:
			Effects.burst(global_position + Vector2(0, -20), PI / 2, 1, 60, 0.6, ["blood-2"], 0.5)
	if dying > 0:
		dying -= dt
		if dying <= 0:
			leave_body()
			return
		update_movement(Vector2.ZERO, false, dt)
		update_sprite()
		return
	if rising > 0:
		rising -= dt
		update_movement(Vector2.ZERO, false, dt)
		update_sprite()
		return

	var intent := think(dt)
	var dir := intent
	for o in get_tree().get_nodes_in_group("enemies"):
		var d := position.distance_to(o.position)
		if o != self and d < SPACING and d > 0:
			dir += (position - o.position) / d
	var kept := facing
	update_movement(dir, false, dt)
	# Face where the Hollow means to go, not where crowding shoves it.
	facing = facing_for(intent, kept) if intent else kept
	if state == "windup" or state == "strike":
		facing = facing_from_angle(aim)
	update_sprite()


# One step of the state machine; returns the movement input.
func think(dt: float) -> Vector2:
	var to_player: Vector2 = player.position - position
	var dist := to_player.length()
	var player_safe: bool = player.dead > 0 or not Terrain.village_at(player.position).is_empty()
	if stagger > 0:
		stagger -= dt
		return Vector2.ZERO
	knocked_down = false
	t += dt
	match state:
		"wander":
			if dist < HOLLOW.aggro and not player_safe:
				state = "chase"
			if target == null or t > 4:
				t = 0.0
				target = position + Vector2(randf() - 0.5, randf() - 0.5) * WANDER * 2
			if position.distance_to(target) < 12 or t < 1.5:
				return Vector2.ZERO
			return (target - position).normalized() * 0.5
		"chase":
			if dist > HOLLOW.leash or player_safe:
				state = "wander"
				return Vector2.ZERO
			if dist < HOLLOW.range:
				state = "windup"
				t = 0.0
				aim = to_player.angle()
				return Vector2.ZERO
			return to_player.normalized()
		"windup":
			if t >= HOLLOW.windup:
				state = "strike"
				t = 0.0
				hit = false
				velocity = Vector2.from_angle(aim) * HOLLOW.lunge
		"strike":
			var in_arc := absf(angle_difference(aim, to_player.angle())) < HOLLOW.arc
			if not hit and dist < HOLLOW.range + HIT_PAD and in_arc:
				hit = true
				player.hurt(HOLLOW.damage, aim, self)
			if t >= HOLLOW.strike:
				state = "recover"
				t = 0.0
		_:
			if t >= HOLLOW.recover:
				state = "chase"
				t = 0.0
	return Vector2.ZERO


func update_sprite() -> void:
	var lean := Vector2(0, 3) if knocked_down else Vector2.ZERO
	var telegraph := state == "windup" and stagger <= 0
	set_tint("bone-1", 1.0 if flash > 0 else 0.0)
	# ART_RULES §7: a glowing outline that heats from ember-2 to ember-3 as the thrust nears.
	# Steady, so it never strobes. The windup of the attack animation is the rest of the telegraph.
	set_outline("ember-3" if t > HOLLOW.windup * TELEGRAPH_HOT else "ember-2", 1.0 if telegraph and flash <= 0 else 0.0)

	if dying > 0:
		# The collapse plays over the dying time; its last frame is the body left behind.
		show_frame("death", mini(DEATH_FRAMES - 1, floori((1 - dying / HOLLOW.dying) * DEATH_FRAMES)), lean)
	elif rising > 0:
		show_frame("death", mini(DEATH_FRAMES - 1, floori(rising / RISE_TIME * DEATH_FRAMES)))
	elif state in ATTACKING:
		show_frame("attack", attack_frame(state, t, HOLLOW, THRUST.frames, THRUST.impact[facing]), lean)
	else:
		show_frame(anim, walk_frame(), lean)


func leave_body() -> void:
	var world = get_tree().get_first_node_in_group("world")
	var body: Prop = world.add_prop(get_parent(), "body", DIRS.find(facing), position.round(), "corpse:%d" % get_instance_id())
	body.add_to_group("bodies")
	var bodies := get_tree().get_nodes_in_group("bodies")
	if bodies.size() > MAX_BODIES:
		bodies[0].queue_free()
	queue_free()
