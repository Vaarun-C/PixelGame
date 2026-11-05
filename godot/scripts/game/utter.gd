class_name Utter

# Uttering (lore: Uttering), the only magic: the Wanderer speaks a lashed rune through his blade
# (keys 1-5: the blade's three sockets, then the armour's two). Its soul burns as the spell
# (RuneBook.SPELLS), the stone shatters into shards, corruption rises, and the soul's hatred gets up
# nearby as a Hollow.
#
# A verb with cast art (signed off: art/characters/wanderer_hd/wanderer_hd_cast_<verb>.png) is a
# cast: he stops, moves into the spell's held pose (the sheet's in-betweens, the last frame the
# pose), shouts the rune's name, and the spell goes off with its effect (SpellFx); he holds the pose
# a moment, then eases back. A verb without art goes off at once.
const HOLLOW := preload("res://scenes/hollow.tscn")
const SOCKETS := [["blade", 0], ["blade", 1], ["blade", 2], ["armor", 0], ["armor", 1]]
const KNOCK := {"rend": 200.0, "break": 260.0, "sting": 120.0}
const RISE_TRIES := 8
const CAST_FPS := 12.0
const CAST_SIZE := Vector2i(160, 160)
# Rows of the cast canvas under his feet (ART_RULES: feet at y=143).
const CAST_FLOOR := 16
# Ticks he shouts before the spell goes off, and holds the pose after.
const SHOUT_TICKS := 4
const HOLD_TICKS := 4
# Ticks each in-between is held: Rend's rise is slow.
const SLOW := {"rend": 2}


static func cast_path(verb: String) -> String:
	return "res://art/characters/wanderer_hd/wanderer_hd_cast_%s.png" % verb


static func has_cast(verb: String) -> bool:
	return ResourceLoader.exists(cast_path(verb))


# The lashed stone in socket `index` if it can be spoken, else "" (with a line when it can't).
static func speakable(p, index: int) -> String:
	var key = p.inventory.sockets[SOCKETS[index][0]][SOCKETS[index][1]]
	if not key or key == Items.EMPTY_STONE:
		return ""
	if Items.info(key).tier == RuneBook.CRIMSON:
		p.said.emit("Not this one. Not yet.", "ash-3")
		return ""
	return key


# Starts speaking the stone in socket `index`. Returns the cast to play ({} if none: nothing to
# speak, or it went off at once). A fused stone plays its first verb's cast.
static func begin(p, index: int) -> Dictionary:
	var key := speakable(p, index)
	if not key:
		return {}
	var verb: String = Items.info(key).types[0]
	if not has_cast(verb):
		speak(p, index)
		return {}
	var frames: int = p.sheets["cast_" + verb].texture.get_width() / CAST_SIZE.x
	var ticks := []
	for f in frames:
		for _i in SLOW.get(verb, 1):
			ticks.append(f)
	var shout := ticks.size()
	for _i in SHOUT_TICKS + HOLD_TICKS:
		ticks.append(frames - 1)
	for f in range(frames - 2, -1, -1):
		ticks.append(f)
	return {"index": index, "key": key, "verb": verb, "ticks": ticks, "shout": shout, "fire": shout + SHOUT_TICKS, "t": 0.0}


# Plays a cast for a frame; false once it is over.
static func advance(p, cast: Dictionary, dt: float) -> bool:
	var before := floori(cast.t * CAST_FPS)
	cast.t += dt
	var tick := floori(cast.t * CAST_FPS)
	if tick >= cast.ticks.size():
		p.pose = {}
		return false
	p.pose = {"sheet": "cast_" + cast.verb, "frame": cast.ticks[tick]}
	p.shout = cast.verb.capitalize() + "!" if tick >= cast.shout and tick < cast.fire + HOLD_TICKS else ""
	if before < cast.fire and tick >= cast.fire:
		# The bag was open mid-cast: the stone may not be in its socket any more.
		if p.inventory.sockets[SOCKETS[cast.index][0]][SOCKETS[cast.index][1]] == cast.key:
			speak(p, cast.index)
		else:
			p.said.emit("The stone is gone from the steel.", "ash-3")
	return true


static func speak(p, index: int) -> void:
	var key := speakable(p, index)
	if not key:
		return
	var part: String = SOCKETS[index][0]
	var slot: int = SOCKETS[index][1]
	var info := Items.info(key)
	for t in info.types:
		cast(p, t, Runes.spell_value(t, info, p.corruption), info)
	p.inventory.sockets[part][slot] = null
	var shards: int = RuneBook.UTTER_SHARDS[info.tier - 1]
	if shards:
		p.inventory.add("shard", shards)
	p.inventory.save()
	if p.corruption < 1.0:
		p.corruption = minf(1.0, p.corruption + RuneBook.UTTER_CORRUPTION[info.tier - 1])
	raise_hatred(p, info.tier)
	Journal.write("utter_first")
	p.said.emit("+%d Rune Shard" % shards if shards else "The stone crumbles to dust.", info.color)


static func cast(p, type: String, value: float, info: Dictionary) -> void:
	var chest: Vector2 = p.global_position + Vector2(0, p.CHEST_Y)
	var tier: String = Items.TIERS[info.tier - 1]
	match type:
		"ward":
			p.shield = maxf(p.shield, value)
		"flee":
			p.invuln = maxf(p.invuln, value)
	for e in near(p, chest, RuneBook.SPELLS[type].radius):
		var angle: float = (e.global_position - p.global_position).angle()
		if type in KNOCK or type == "hunger":
			e.take_damage(value, angle, KNOCK.get(type, 0.0), type == "break")
		match type:
			"break":
				e.add_break(1.0)
			"sting":
				e.bleed(RuneBook.BLEED.dps, RuneBook.BLEED.time)
			"hunger":
				Runes.heal(p.runes, p, value, "spell")
			"still":
				e.hold(value)
			"sink":
				e.slow(RuneBook.SINK_SPELL_SLOW, value)
	if not SpellFx.play(p.get_parent(), p.position, type, tier):
		Effects.burst(chest, 0, 70, 200, TAU, ["rune-%s-mid" % tier, "ember-2", "ember-3"], 0.8, 2)
	Effects.shake(8 if type == "rend" else 6)
	Effects.hit_stop(0.06)


# Living foes within radius of the chest. (Rend's scythe sweeps through him, so it reaches all round
# too, not a cone toward the mouse.)
static func near(p, chest: Vector2, radius: float) -> Array:
	return p.get_tree().get_nodes_in_group("enemies").filter(func(e):
		var to: Vector2 = e.global_position + Vector2(0, -24) - chest
		return e.dying <= 0 and to.length() < radius)


# The burned soul's hatred climbs out of the ground nearby (lore: Hollows, hatred Hollows).
static func raise_hatred(p, tier: int) -> void:
	for i in RISE_TRIES:
		var at: Vector2 = p.position + Vector2.from_angle(randf() * TAU) * RuneBook.HATRED_RISE_DISTANCE
		if Terrain.blocked(at):
			continue
		var hollow := HOLLOW.instantiate()
		hollow.position = at
		hollow.hatred = tier
		p.get_parent().add_child(hollow)
		return
