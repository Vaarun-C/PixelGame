extends Actor

# The Hollow (src/enemies.js): a husk of a dead soldier. Slow, telegraphs a lunging spear thrust
# with an ember flash. Times in seconds, distances in px, speeds in px/s. Other Hollow bodies (the
# Misborn, the Stammerer) extend this one and swap its stats, sheets, moves and body.
const HOLLOW := {"hp": 40.0, "aggro": 300.0, "leash": 660.0, "stagger": 0.28, "knockdown": 0.9, "dying": 0.72, "bar": -50}
# A move: its attack sheet, frame count and the frame where the blow lands (per facing, or one for a
# sheet drawn facing south only; see attack_frame), reach, phase times, lunge and blow.
const THRUST := {
	"sheet": "attack", "frames": 6, "impact": {"down": 3, "left": 4, "right": 3, "up": 3},
	"range": 52.0, "windup": 0.6, "strike": 0.14, "recover": 0.75, "lunge": 340.0, "damage": 15.0, "arc": 1.2,
}
const ATTACKING := ["windup", "strike", "recover"]
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
# A hatred Hollow (lore: Hollows) burns at the seams: ember sparks per second, and ash when it falls.
const EMBER_SPARKS := 16.0
# A hit jolts the sprite (not the body) back along the blow, in world px; it springs home at RETURN.
const RECOIL := {"hit": 3.0, "big": 6.0, "return": 14.0}
# Health bar over the head, in world px (its height is stats.bar). The lost part bleeds away after
# `hold` seconds at `drain` hp/s.
const BAR := {"w": 16, "h": 2, "hold": 0.35, "drain": 40.0}

# The tier of the uttered stone whose hatred walks this body; 0 for a loose soul's Hollow. A hatred
# Hollow is stronger by tier, has no name to bind, leaves no body and stays dead.
var hatred := 0
var stats := HOLLOW
var move: Dictionary = THRUST
# The prop left where it falls (world/props.gd); one variant per facing unless its death faces south only.
var body_kind := "body"
var power := 1.0
var max_hp: float = HOLLOW.hp
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
var recoil := Vector2.ZERO
var bled_hp: float = HOLLOW.hp
var bleed_hold := 0.0
var bar := Node2D.new()

@onready var player = get_tree().get_first_node_in_group("player")


func _ready() -> void:
	if sheets.is_empty():
		var dir := "res://art/enemies/hollow_hd/hollow_hd_%s.png"
		sheets = {
			"idle": sheet_entry(dir % "idle", Vector2i(64, 96)),
			"walk": sheet_entry(dir % "walk", Vector2i(64, 96)),
			"attack": sheet_entry(dir % "attack", Vector2i(128, 112)),
			"death": sheet_entry(dir % "death", Vector2i(96, 96)),
		}
	super._ready()
	base_speed = speed
	max_hp = stats.hp
	if hatred:
		max_hp = stats.hp * RuneBook.HATRED_HP[hatred - 1]
		power = RuneBook.HATRED_DAMAGE[hatred - 1]
		rising = RISE_TIME
		state = "chase"
	hp = max_hp
	bled_hp = max_hp
	bar.z_as_relative = false
	bar.z_index = 100
	bar.draw.connect(draw_bar)
	add_child(bar)


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
	return hp < max_hp


func take_damage(damage: float, angle: float, knock: float, knockdown: bool) -> void:
	hp -= damage
	flash = 0.12
	if damage > 0:
		var big := damage >= Effects.BIG_HIT
		recoil = Vector2.from_angle(angle) * (RECOIL.big if big else RECOIL.hit)
		bleed_hold = BAR.hold
		Effects.number(global_position + Vector2(0, stats.bar * 1.2), damage, big)
	if hp <= 0:
		dying = stats.dying
	if not staggered_by(damage, knockdown):
		return
	velocity = Vector2.from_angle(angle) * knock
	stagger = stats.knockdown if knockdown else stats.stagger
	knocked_down = knockdown
	# A staggering hit breaks the attack, so a staggered Hollow never holds its attack pose.
	if state in ATTACKING:
		state = "chase"


# Whether a blow staggers it (and breaks its attack). Any blow staggers a Hollow.
func staggered_by(_damage: float, _knockdown: bool) -> bool:
	return true


# The move to start at `dist` from the player, or {} while out of reach.
func pick_move(dist: float) -> Dictionary:
	return THRUST if dist < THRUST.range else {}


func _physics_process(dt: float) -> void:
	flash -= dt
	recoil = recoil.lerp(Vector2.ZERO, 1 - exp(-RECOIL.return * dt))
	bleed_hold -= dt
	if bleed_hold <= 0:
		bled_hp = maxf(hp, bled_hp - BAR.drain * dt)
	bar.queue_redraw()
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
			dying = stats.dying
		if randf() < dt * BLEED_DRIPS:
			Effects.burst(global_position + Vector2(0, -20), PI / 2, 1, 60, 0.6, ["blood-2"], 0.5)
	if hatred and dying <= 0 and randf() < dt * EMBER_SPARKS:
		Effects.burst(global_position + Vector2(randf_range(-10, 10), randf_range(-56, -12)), -PI / 2, 1, 40, 0.8, ["ember-2", "ember-3"], 0.6, 2)
	if dying > 0:
		dying -= dt
		if dying <= 0:
			if hatred:
				Effects.burst(global_position + Vector2(0, -20), -PI / 2, 24, 90, TAU, ["ash-2", "ash-3", "ember-1"], 0.7)
				queue_free()
			else:
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


# Dead, or inside a village: Hollows leave him be.
func player_safe() -> bool:
	return player.dead > 0 or not Terrain.village_at(player.position).is_empty()


# One step of the state machine; returns the movement input.
func think(dt: float) -> Vector2:
	var to_player: Vector2 = player.position - position
	var dist := to_player.length()
	var safe := player_safe()
	if stagger > 0:
		stagger -= dt
		return Vector2.ZERO
	knocked_down = false
	t += dt
	match state:
		"wander":
			if dist < stats.aggro and not safe:
				state = "chase"
			if target == null or t > 4:
				t = 0.0
				target = position + Vector2(randf() - 0.5, randf() - 0.5) * WANDER * 2
			if position.distance_to(target) < 12 or t < 1.5:
				return Vector2.ZERO
			return (target - position).normalized() * 0.5
		"chase":
			if dist > stats.leash or safe:
				state = "wander"
				return Vector2.ZERO
			var next := pick_move(dist)
			if next:
				move = next
				state = "windup"
				t = 0.0
				aim = to_player.angle()
				return Vector2.ZERO
			return to_player.normalized()
		"windup":
			if t >= move.windup:
				state = "strike"
				t = 0.0
				hit = false
				velocity = Vector2.from_angle(aim) * move.lunge
		"strike":
			var in_arc: bool = absf(angle_difference(aim, to_player.angle())) < move.arc
			if not hit and dist < move.range + HIT_PAD and in_arc:
				hit = true
				player.hurt(move.damage * power, aim, self)
			if t >= move.strike:
				state = "recover"
				t = 0.0
		_:
			if t >= move.recover:
				state = "chase"
				t = 0.0
	return Vector2.ZERO


func update_sprite() -> void:
	var lean := (Vector2(0, 3) if knocked_down else Vector2.ZERO) + recoil
	var telegraph := state == "windup" and stagger <= 0
	set_tint("bone-1", 1.0 if flash > 0 else 0.0)
	# ART_RULES §7: a glowing outline that heats from ember-2 to ember-3 as the thrust nears.
	# Steady, so it never strobes. The windup of the attack animation is the rest of the telegraph.
	set_outline("ember-3" if t > move.windup * TELEGRAPH_HOT else "ember-2", 1.0 if telegraph and flash <= 0 else 0.0)

	var deaths := frame_count("death")
	if dying > 0:
		# The collapse plays over the dying time; its last frame is the body left behind.
		show_frame("death", mini(deaths - 1, floori((1 - dying / stats.dying) * deaths)), lean)
	elif rising > 0:
		show_frame("death", mini(deaths - 1, floori(rising / RISE_TIME * deaths)))
	elif state in ATTACKING:
		var impact: int = move.impact[facing] if move.impact is Dictionary else move.impact
		show_frame(move.sheet, attack_frame(state, t, move, move.frames, impact), lean)
	else:
		show_frame(anim, walk_frame(), lean)


func frame_count(sheet_name: String) -> int:
	return sheets[sheet_name].texture.get_width() / sheets[sheet_name].size.x


# Whole world pixels (2 sprite pixels): a void frame, the health in blood-3 and the part just lost
# in blood-4, bleeding away. Hidden until wounded and once dying.
func draw_bar() -> void:
	if not wounded() or dying > 0:
		return
	var w: int = BAR.w
	var x := -w / 2
	var y: int = stats.bar
	var health := ceili(w * maxf(0.0, hp) / max_hp)
	var bled := ceili(w * maxf(0.0, bled_hp) / max_hp)
	for r in [[x - 1, y - 1, w + 2, BAR.h + 2, "void-0"], [x, y, w, BAR.h, "void-2"], [x, y, bled, BAR.h, "blood-4"], [x, y, health, BAR.h, "blood-3"]]:
		bar.draw_rect(Rect2(r[0] * 2, r[1] * 2, r[2] * 2, r[3] * 2), Palette.color(r[4]))


func leave_body() -> void:
	var world = get_tree().get_first_node_in_group("world")
	var variant := DIRS.find(facing) if sheets.death.rows > 1 else 0
	var body: Prop = world.add_prop(get_parent(), body_kind, variant, position.round(), "corpse:%d" % get_instance_id())
	body.add_to_group("bodies")
	var bodies := get_tree().get_nodes_in_group("bodies")
	if bodies.size() > MAX_BODIES:
		bodies[0].queue_free()
	queue_free()
