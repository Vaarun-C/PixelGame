class_name Runes

# Runes lashed to the wanderer's blade (3) and armor (2). Numbers live in RuneBook. Each verb gives a
# passive by tier; a fused rune's kind adds a trait; sets of verbs in one part form resonances.
const SOCKETS := {"blade": 3, "armor": 2}
const MAX_ARMOR := 0.75
const MAX_NOTCHES := RuneBook.MAX_NOTCHES

static var echoes := {}


static func empty_sockets() -> Dictionary:
	var sockets := {}
	for part in SOCKETS:
		sockets[part] = []
		sockets[part].resize(SOCKETS[part])
	return sockets


static func fits(key: String, part: String) -> bool:
	if key == Items.EMPTY_STONE:
		return part == "blade"
	return Items.info(key).types.any(func(t): return RuneBook.SUBTYPES[t].part == part)


static func share(info: Dictionary) -> float:
	return RuneBook.FUSED_SHARE if info.types.size() > 1 else 1.0


static func strength(info: Dictionary) -> float:
	return 1 + info.notches * RuneBook.NOTCH_BONUS


# A per-tier value for one verb of a stone, scaled by its notches, its fused share and whether that
# verb is read.
static func scaled(tiers: Array, type: String, info: Dictionary) -> float:
	var read: bool = info.souls[info.types.find(type)].read
	return tiers[info.tier - 1] * strength(info) * share(info) * (1.0 if read else RuneBook.UNREAD_POWER)


static func tier_value(type: String, info: Dictionary) -> float:
	return scaled(RuneBook.SUBTYPES[type].tiers, type, info)


static func spell_value(type: String, info: Dictionary, corruption: float) -> float:
	return scaled(RuneBook.SPELLS[type].tiers, type, info) * (RuneBook.PULL_POWER if corruption >= 1.0 else 1.0)


# Mortmain's grip on one verb of a forced rune; Crimson's burden is its prisoner's instead.
static func grip_value(type: String, info: Dictionary) -> float:
	return 0.0 if info.tier == RuneBook.CRIMSON else RuneBook.GRIPS[type].tiers[info.tier - 1] * share(info)


static func grip_text(type: String, value: float) -> String:
	return RuneBook.GRIPS[type].text % roundi(value)


# The soul's echo: fixed per stone, chosen by its soul id (echoes.json). "" for stones from older saves.
static func echo(verb: String, id: int) -> String:
	if echoes.is_empty():
		echoes = JSON.parse_string(FileAccess.get_file_as_string("res://scripts/game/echoes.json"))
	var lines: Array = echoes.get(verb, [])
	return lines[id % lines.size()] if id and lines else ""


static func kind(info: Dictionary) -> Dictionary:
	return RuneBook.KINDS.get("-".join(info.types), {})


# percent: the verb's value as a tier list holds it (Still's in hundredths of a second).
static func verb_text(type: String, percent: float) -> String:
	return RuneBook.SUBTYPES[type].text % (percent / 100 if type == "still" else roundi(percent))


static func passive_lines(key: String) -> Array:
	var info := Items.info(key)
	var lines := [" and ".join(info.types.map(func(t): return RuneBook.FAMILIES[RuneBook.SUBTYPES[t].family].grade))]
	for t in info.types:
		lines.append(verb_text(t, tier_value(t, info)))
	if kind(info):
		lines.append(kind(info).desc)
	if info.tier != RuneBook.CRIMSON:
		for t in info.types:
			lines.append("Spoken: " + RuneBook.SPELLS[t].text % spell_value(t, info, 0.0))
	return lines


# [text, colour] per verb: its grip, then how far it is read, or what its echo says and what part of
# its death it still needs (Rites). done: the bag's rites ledger.
static func soul_lines(key: String, reading: Dictionary, done: Dictionary) -> Array:
	var info := Items.info(key)
	var lines := []
	for i in info.types.size():
		var t: String = info.types[i]
		var soul: Dictionary = info.souls[i]
		if grip_value(t, info):
			lines.append([grip_text(t, grip_value(t, info)), "blood-4"])
		if soul.read and echo(t, soul.id):
			lines.append(["Echo: " + echo(t, soul.id), "ash-4"])
		if soul.read and info.tier != RuneBook.CRIMSON:
			lines.append([RuneBook.NEED_TEXT[Rites.next_need(soul.id, done)], "ash-3"])
		elif not soul.read:
			lines.append(["Unread %d/%d" % [reading.get(str(soul.id), 0), RuneBook.READ_USES[info.tier - 1]], "ash-3"])
	return lines


static func carve_cost(key: String) -> int:
	return RuneBook.CARVE_COST[Items.info(key).notches]


# "" when a and b may fuse, else why not.
static func fuse_error(a: String, b: String) -> String:
	var x := Items.info(a)
	var y := Items.info(b)
	if x.tier == RuneBook.CRIMSON or y.tier == RuneBook.CRIMSON:
		return "There's no room in a Crimson stone."
	if x.types.size() > 1 or y.types.size() > 1:
		return "Two souls already share that stone."
	if x.types[0] == y.types[0]:
		return "Only runes of different verbs can fuse."
	return ""


static func fuse_cost(a: String, b: String) -> int:
	return RuneBook.FUSE_COST_PER_TIER * maxi(Items.info(a).tier, Items.info(b).tier)


static func carved(key: String) -> String:
	var info := Items.info(key)
	return Items.rune_key(info.types, info.tier, info.notches + 1, info.souls)


# Both souls keep their ids and what has been read of them, in verb order.
static func fused(a: String, b: String) -> String:
	var souls := [Items.info(a).souls[0], Items.info(b).souls[0]]
	souls.sort_custom(func(p, q): return RuneBook.ORDER.find(p.verb) < RuneBook.ORDER.find(q.verb))
	return Items.rune_key(souls.map(func(s): return s.verb), maxi(Items.info(a).tier, Items.info(b).tier), 0, souls)


# Doing what a lashed rune names reads it: its soul's uses count up in the bag's reading ledger, and
# at the tier's count the stone gives full power and its echo.
static func practise(p, verb: String) -> void:
	for part in SOCKETS:
		var lashed: Array = p.inventory.sockets[part]
		for i in lashed.size():
			if not lashed[i] or lashed[i] == Items.EMPTY_STONE:
				continue
			var info := Items.info(lashed[i])
			var j: int = info.types.find(verb)
			if j < 0 or info.souls[j].read:
				continue
			if p.inventory.practise(info.souls[j].id) < RuneBook.READ_USES[info.tier - 1]:
				continue
			info.souls[j].read = true
			lashed[i] = Items.rune_key(info.types, info.tier, info.notches, info.souls)
			p.inventory.save()
			var line := echo(verb, info.souls[j].id)
			p.said.emit("Echo: " + line if line else "The stone answers.", "bone-0")
			if line:
				Journal.write("read_first")
				Journal.echo(verb, line)


# Everything the sockets do, recomputed whenever they change. Verb values are fractions (Still's in
# seconds); kinds are the fused runes' traits with their power. strength and armor come from the
# smith's work on his gear (Smith), not from runes.
static func stats(sockets: Dictionary, forged := {}) -> Dictionary:
	var result := {"cursed": {}, "resonances": [], "kinds": [], "grip": {}, "strength": Smith.bonus(forged, "strength"), "armor": Smith.bonus(forged, "armor")}
	for t in RuneBook.ORDER:
		result[t] = 0.0
		result.grip[t] = 0.0
	for part in SOCKETS:
		var infos: Array = sockets[part].filter(func(k): return k and k != Items.EMPTY_STONE).map(func(k): return Items.info(k))
		for info in infos:
			for t in info.types:
				result[t] += tier_value(t, info) / 100
				result.grip[t] += grip_value(t, info)
				if info.tier == RuneBook.CRIMSON:
					result.cursed[t] = true
			if kind(info):
				result.kinds.append(kind(info).merged({"power": RuneBook.KIND_POWER[info.tier - 1] * strength(info)}))
		for r in RuneBook.RESONANCES.filter(func(r): return r.part == part):
			var formers := infos.filter(func(info): return info.types.any(func(t): return r.needs.has(t)))
			var met: bool = r.needs.keys().all(func(t): return formers.filter(func(info): return t in info.types).size() >= r.needs[t])
			if not met:
				continue
			var cursed := formers.any(func(info): return info.tier == RuneBook.CRIMSON)
			var weakest: int = formers.map(func(info): return mini(info.tier, RuneBook.CRIMSON - 1)).min()
			result.resonances.append(r.merged({"power": (0.6 + 0.2 * weakest) * (2 if cursed else 1), "cursed": cursed}))
	return result


static func resonance(s: Dictionary, name: String) -> Dictionary:
	for r in s.resonances:
		if r.name == name:
			return r
	return {}


static func kinds(s: Dictionary, when: String, does := "") -> Array:
	return s.kinds.filter(func(k): return k.when == when and (not does or k.do == does))


static func amount(k: Dictionary) -> float:
	return k.get("amount", 0.0) * k.power


# Whether a kind's `if` holds. p is the player, e the foe (null if none).
static func met(k: Dictionary, p, e) -> bool:
	match k.get("if", ""):
		"attacking":
			return p.move >= 0
		"still":
			return p.still_time >= RuneBook.STILL_AFTER
		"bleeding":
			return e != null and e.bleed_time > 0
		"held":
			return e != null and e.hold_time > 0
		"slowed":
			return e != null and e.slow_time > 0
		"wounded":
			return e != null and e.wounded()
	return true


static func fire(s: Dictionary, when: String, p, e = null) -> void:
	for k in kinds(s, when).filter(func(k): return met(k, p, e)):
		match k.do:
			"heal":
				heal(s, p, amount(k), "kind")
			"empower":
				p.empower += amount(k)
			"guard":
				if k.has("time"):
					p.guard = amount(k)
					p.guard_time = k.time
		if e == null:
			continue
		match k.do:
			"bleed":
				e.bleed(k.dps * k.power, k.time)
			"hold":
				hold(s, p, e, k.time * k.power)
			"slow":
				e.slow(amount(k) / 100, k.time)
			"knockdown":
				e.knock_down()
			"break":
				break_foe(s, p, e, amount(k))
			"hurt":
				e.take_damage(amount(k), (e.position - p.position).angle(), 0.0, false)


static func hold(s: Dictionary, p, e, time: float) -> void:
	e.hold(time)
	fire(s, "held", p, e)


static func break_foe(s: Dictionary, p, e, amount_: float) -> void:
	if e.add_break(amount_ / RuneBook.BREAK_FULL):
		fire(s, "broken", p, e)


# Combat hooks. p is the player (hp, max_hp, shield, rune_hits, riposte, empower, guard, guard_time,
# still_time, since_hurt, self_bleed, move).
static func strike_damage(s: Dictionary, p, e, base: float) -> float:
	var mult: float = (1 + s.rend + s.strength) * (2.0 if p.riposte else 1.0) * (1 + p.empower / 100) * (1 - s.grip.flee / 100)
	for k in kinds(s, "strike", "damage").filter(func(k): return met(k, p, e)):
		mult *= 1 + amount(k) / 100
	p.riposte = false
	p.empower = 0.0
	return base * mult


static func heal(s: Dictionary, p, amount_: float, source: String) -> void:
	var gorge := resonance(s, "Gorge")
	if gorge and gorge.cursed and source != "Gorge":
		return
	if source != "hunger":
		amount_ *= 1 - s.grip.hunger / 100
	var room: float = p.max_hp - p.hp
	p.hp += minf(room, amount_)
	if amount_ <= room:
		return
	var cap := 0.0
	var leech := resonance(s, "Leech-shell")
	if leech:
		cap = RuneBook.SHIELD_MAX * leech.power
	for k in kinds(s, "heal_over"):
		cap = maxf(cap, amount(k))
	p.shield = minf(cap, p.shield + amount_ - room)


# After a hit lands on foe e for `damage`; returns whether the hit opened a bleed.
static func on_strike(s: Dictionary, p, e, damage: float, finisher: bool) -> bool:
	# The kinds read the foe as it was before this hit's own hold and slow.
	fire(s, "strike", p, e)
	if finisher:
		fire(s, "finisher", p, e)
	p.rune_hits += 1
	for t in ["rend", "break", "still", "sink", "hunger"]:
		if s[t]:
			practise(p, t)
	if s.hunger:
		heal(s, p, damage * s.hunger, "hunger")
	if s.break:
		break_foe(s, p, e, s.break * 100)
	if s.still:
		hold(s, p, e, s.still)
	if s.sink:
		e.slow(s.sink, RuneBook.SINK_TIME)
	var bloodlet := resonance(s, "Bloodletting")
	if bloodlet and e.bleed_time > 0:
		heal(s, p, RuneBook.BLOODLET_HEAL * bloodlet.power, "Bloodletting")
	if p.rune_hits % RuneBook.BLEED.every:
		return false
	var flay := resonance(s, "Flay")
	if flay:
		e.bleed(RuneBook.BLEED.dps * flay.power, RuneBook.BLEED.time)
		if flay.cursed:
			p.self_bleed = RuneBook.BLEED.time
	elif bloodlet:
		e.bleed(RuneBook.BLEED.light_dps * bloodlet.power, RuneBook.BLEED.light_time)
	return not flay.is_empty() or not bloodlet.is_empty()


static func on_kill(s: Dictionary, p) -> void:
	p.hp = maxf(1, p.hp - s.grip.rend)
	var gorge := resonance(s, "Gorge")
	if gorge:
		heal(s, p, p.max_hp * RuneBook.GORGE_HEAL * gorge.power, "Gorge")


# A Hollow killed with an empty stone lashed to the blade goes into the stone instead of walking again:
# a forced Pale rune of a verb it died doing. Binding is trapping, so it costs corruption. Returns the
# bound rune's key, or "".
static func bind(sockets: Dictionary, p) -> String:
	var slot: int = sockets.blade.find(Items.EMPTY_STONE)
	if slot < 0:
		return ""
	var verb: String = RuneBook.ORDER.pick_random()
	var key := Items.rune_key([verb], 1, 0, Items.new_souls([verb]))
	sockets.blade[slot] = key
	p.corruption = minf(1.0, p.corruption + RuneBook.BIND_CORRUPTION)
	return key


# A dodged blow arms Riposte.
static func on_dodged(s: Dictionary, p) -> void:
	if resonance(s, "Riposte"):
		p.riposte = true


static func on_dodge(s: Dictionary, p) -> void:
	fire(s, "dodge", p)
	if s.flee:
		practise(p, "flee")


# The dodge passes foe e.
static func on_through(s: Dictionary, p, e) -> void:
	fire(s, "through", p, e)


static func dodge_factor(s: Dictionary, p) -> float:
	var bonus := 0.0
	for k in kinds(s, "always", "dodge").filter(func(k): return met(k, p, null)):
		bonus += amount(k)
	return (1 + s.flee + bonus / 100) * (1 - s.grip.sink / 100)


static func dodge_cooldown_factor(s: Dictionary) -> float:
	var quick := 0.0
	for k in kinds(s, "always", "quick"):
		quick += amount(k)
	return maxf(0.3, 1 - quick / 100) * (1 + s.grip.still / 100)


# Damage the player actually takes from a blow by `attacker` (may be null), after shields:
# {hurt, knockback}. Sting and its kinds hurt the attacker back.
static func take_hit(s: Dictionary, p, damage: float, attacker = null) -> Dictionary:
	var guard: float = p.guard if p.guard_time > 0 else 0.0
	for k in s.kinds.filter(func(k): return k.do == "guard" and not k.has("time") and met(k, p, attacker)):
		guard += amount(k)
	var bulwark := resonance(s, "Bulwark")
	var cursed_sets: int = s.resonances.filter(func(r): return r.cursed and r.name != "Flay" and r.name != "Gorge").size()
	var hurt: float = damage * (1 - minf(MAX_ARMOR, s.ward + s.armor + guard / 100)) * pow(RuneBook.CURSED_DAMAGE_TAKEN, cursed_sets) * (1 + s.grip.break / 100)
	if s.ward:
		practise(p, "ward")
	if s.cursed.has("rend"):
		hurt += RuneBook.CRIMSON_HURT
	if bulwark:
		hurt = maxf(1, hurt - RuneBook.BULWARK_BLOCK * bulwark.power)
	var absorbed := minf(p.shield, hurt)
	p.shield -= absorbed
	p.since_hurt = 0.0
	if attacker:
		var reflect: float = s.sting
		for k in kinds(s, "always", "reflect"):
			reflect += amount(k) / 100
		if reflect > 0:
			var back := damage * reflect
			attacker.take_damage(back, (attacker.position - p.position).angle(), 0.0, false)
			p.hp = maxf(1, p.hp - back * s.grip.sting / 100)
			if s.sting:
				practise(p, "sting")
			for k in kinds(s, "reflect", "heal"):
				heal(s, p, back * amount(k) / 100, "kind")
		fire(s, "hurt", p, attacker)
	var steady := not kinds(s, "always", "steady").is_empty()
	return {"hurt": hurt - absorbed, "knockback": bulwark.is_empty() and not steady}


# Per frame: Scab regeneration, crimson Hunger starvation, Flay's self-bleed, timed guard.
# calm: no enemy near.
static func update(s: Dictionary, p, dt: float, calm: bool) -> void:
	p.since_hurt += dt
	p.guard_time -= dt
	var scab := resonance(s, "Scab")
	if scab and calm and p.since_hurt > RuneBook.SCAB.after:
		heal(s, p, RuneBook.SCAB.regen * scab.power * dt, "Scab")
	if s.cursed.has("hunger") and calm:
		p.hp = maxf(1, p.hp - RuneBook.CRIMSON_STARVE * dt)
	if p.self_bleed > 0:
		p.self_bleed -= dt
		p.hp = maxf(1, p.hp - dt)


static func speed_factor(s: Dictionary) -> float:
	return (RuneBook.CRIMSON_SLOW if s.cursed.has("ward") else 1.0) * (1 + s.flee) * (1 - s.grip.ward / 100)
