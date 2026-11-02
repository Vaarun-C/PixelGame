extends SceneTree

# Checks every rune key, the fuse rules and each fused kind's trait against a Hollow, and prints what
# each kind did. Run after tuning game/rune_book.gd: godot --headless --path godot -s tools/rune_check.gd

class FakePlayer:
	var hp := 50.0
	var max_hp := 100.0
	var shield := 0.0
	var rune_hits := 0
	var riposte := false
	var empower := 0.0
	var guard := 0.0
	var guard_time := 0.0
	var still_time := 0.0
	var since_hurt := 0.0
	var self_bleed := 0.0
	var move := -1
	var position := Vector2.ZERO

func _initialize() -> void:
	var fails := 0
	for t in RuneBook.ORDER:
		for tier in range(1, 7):
			var k := Items.rune_key([t], tier)
			if Items.info(k).is_empty(): fails += 1; print("bad ", k)
	var pairs := 0
	for i in RuneBook.ORDER.size():
		for j in range(i + 1, RuneBook.ORDER.size()):
			var a := Items.rune_key([RuneBook.ORDER[i]], 2)
			var b := Items.rune_key([RuneBook.ORDER[j]], 3)
			var f := Runes.fused(b, a)
			var info := Items.info(f)
			if info.is_empty() or not RuneBook.KINDS.has("-".join(info.types)): fails += 1; print("bad fuse ", f)
			pairs += 1
			if info.row != 8 + pairs - 1: fails += 1; print("row ", f, " ", info.row)
	print("pairs ", pairs)
	print(Items.info("rune_rend-hunger_3").name, " | ", Runes.passive_lines("rune_rend-hunger_3"))
	print(Items.info("rune_still_2").name, " | ", Runes.passive_lines("rune_still_2"))
	print("crimson: ", Runes.fuse_error("rune_rend_6", "rune_ward_2"))
	print("fused again: ", Runes.fuse_error("rune_rend-ward_2", "rune_flee_2"))
	print("same: ", Runes.fuse_error("rune_rend_1", "rune_rend_2"))
	print("ok: '", Runes.fuse_error("rune_rend_1", "rune_flee_2"), "'")
	# Each kind alone, its hooks fired against a held, slowed, bleeding Hollow.
	var hollow_scene = load("res://scripts/hollow.gd")
	var p := FakePlayer.new()
	for key in RuneBook.KINDS:
		var sockets := Runes.empty_sockets()
		var part: String = RuneBook.SUBTYPES[key.split("-")[0]].part
		sockets[part][0] = "rune_%s_2" % key
		var s := Runes.stats(sockets)
		var e = hollow_scene.new()
		e.player = p
		e.position = Vector2(10, 0)
		e.base_speed = 100
		p.hp = 50; p.move = 0; p.still_time = 1.0
		e.hold(0.5); e.slow(0.3, 2.0); e.bleed(1.0, 2.0)
		var dmg := Runes.strike_damage(s, p, e, 10.0)
		Runes.on_strike(s, p, e, dmg, true)
		Runes.on_dodge(s, p)
		Runes.on_through(s, p, e)
		var blow := Runes.take_hit(s, p, 15.0, e)
		Runes.heal(s, p, 80.0, "test")
		print("%-10s dmg %.1f hurt %.1f knock %s hp %.0f shield %.0f empower %.0f guard %.0f foe hp %.1f held %.2f slow %.2f broken %.2f dodge x%.2f cd x%.2f" % [RuneBook.KINDS[key].name, dmg, blow.hurt, blow.knockback, p.hp, p.shield, p.empower, p.guard, e.hp, e.hold_time, e.slow_amount, e.broken, Runes.dodge_factor(s, p), Runes.dodge_cooldown_factor(s)])
		p.shield = 0; p.empower = 0; p.guard = 0; p.guard_time = 0
		e.free()
	print("FAILS ", fails)
	quit()
