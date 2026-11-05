extends Node2D

# Game feel from src/effects.js: hit-stop, screen shake, particles and damage numbers, plus ground
# puffs (dust kicked up by feet) drawn on the ground under the characters.
const SHAKE_DECAY := 18.0
const PARTICLE_DRAG := 5.0
const PUFF_ALPHA := 0.6
# Damage at or above this is a big hit: a longer freeze, a harder shake, a bigger number.
const BIG_HIT := 25.0
# A number pops out at `pop` scale, settles to `scale`, leaps, falls and fades. Speeds in px/s.
const NUMBER := {"life": 0.75, "fade": 0.25, "pop": 0.07, "leap": 300.0, "drift": 60.0, "gravity": 1100.0}

var freeze_until := 0
var shake_amount := 0.0
var last_tick := Time.get_ticks_msec()
var particles: Array[Dictionary] = []
var puffs: Array[Dictionary] = []
var numbers: Array[Dictionary] = []
var ground := Node2D.new()


func _ready() -> void:
	z_index = 100
	ground.z_as_relative = false
	ground.z_index = -1
	ground.draw.connect(draw_puffs)
	add_child(ground)


# A soft round puff that drifts, swells from `from` to `to` world pixels across and fades out.
func puff(at: Vector2, velocity: Vector2, color: String, from: float, to: float, life: float) -> void:
	puffs.append({"pos": at, "vel": velocity, "color": Palette.color(color), "from": from, "to": to, "life": life, "age": 0.0})


# Freezes gameplay time; shake and the freeze itself run on real time.
func hit_stop(seconds: float) -> void:
	freeze_until = maxi(freeze_until, Time.get_ticks_msec() + int(seconds * 1000))
	Engine.time_scale = 0.0


func shake(amount: float) -> void:
	shake_amount = maxf(shake_amount, amount)


# A burst of particles flying out around `angle`, e.g. blood away from the blow. size: world pixels.
func burst(at: Vector2, angle: float, count: int, speed: float, spread: float, names: Array, life: float, size := 1) -> void:
	for i in count:
		var a := angle + (randf() - 0.5) * spread
		particles.append({
			"pos": at,
			"vel": Vector2.from_angle(a) * speed * (0.4 + randf() * 0.6),
			"life": life * (0.6 + randf() * 0.4),
			"color": Palette.color(names[i % names.size()]),
			"size": size,
		})


func number(at: Vector2, damage: float, big: bool) -> void:
	numbers.append({
		"pos": at, "age": 0.0, "text": str(maxi(1, roundi(damage))), "big": big,
		"vel": Vector2((randf() * 2 - 1) * NUMBER.drift, -NUMBER.leap * (1.25 if big else 1.0)),
	})


func _process(dt: float) -> void:
	var now := Time.get_ticks_msec()
	var real_dt := minf((now - last_tick) / 1000.0, 0.1)
	last_tick = now
	if Engine.time_scale == 0.0 and now >= freeze_until:
		Engine.time_scale = 1.0

	shake_amount = maxf(0.0, shake_amount - SHAKE_DECAY * real_dt)
	var camera := get_viewport().get_camera_2d()
	if camera:
		camera.offset = Vector2(shake_offset(), shake_offset())

	for p in particles:
		p.pos += p.vel * dt
		p.vel -= p.vel * PARTICLE_DRAG * dt
		p.life -= dt
	particles = particles.filter(func(p): return p.life > 0)
	for p in puffs:
		p.pos += p.vel * dt
		p.vel -= p.vel * PARTICLE_DRAG * dt
		p.age += dt
	puffs = puffs.filter(func(p): return p.age < p.life)
	for n in numbers:
		n.pos += n.vel * dt
		n.vel.y += NUMBER.gravity * dt
		n.age += dt
	numbers = numbers.filter(func(n): return n.age < NUMBER.life)
	ground.queue_redraw()
	queue_redraw()


# Whole world pixels, which are 2 sprite pixels.
func shake_offset() -> float:
	return roundf((randf() * 2 - 1) * shake_amount) * 2


func _draw() -> void:
	for p in particles:
		draw_rect(Rect2((p.pos / 2).round() * 2, Vector2.ONE * 2 * p.size), p.color)
	for n in numbers:
		var scale := (4 if n.big else 3) if n.age < NUMBER.pop else (3 if n.big else 2)
		var alpha := minf(1.0, (NUMBER.life - n.age) / NUMBER.fade)
		var at: Vector2 = (n.pos / 2).round() * 2 - Vector2(PixelFont.width(n.text, PixelFont.LARGE, scale) / 2, 0)
		PixelFont.draw(self, n.text, at.round(), "blood-4" if n.big else "bone-0", "void-0", PixelFont.LARGE, scale, alpha)


# Each puff is a disc of whole world pixels, so it sits on the same grid as the art.
func draw_puffs() -> void:
	for p in puffs:
		var k: float = p.age / p.life
		var r := lerpf(p.from, p.to, k) / 2
		var color := Color(p.color as Color, PUFF_ALPHA * (1 - k))
		var centre: Vector2 = (p.pos / 2).round()
		for dy in range(-ceili(r), ceili(r) + 1):
			var half := floori(sqrt(maxf(0.0, r * r + r - dy * dy)))
			ground.draw_rect(Rect2((centre + Vector2(-half, dy)) * 2, Vector2(half * 2 + 1, 1) * 2), color)
