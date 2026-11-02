extends Node2D

# The Wanderer's health and corruption, at native pixels: his keepsake stone in an iron ring, a worn
# gilt-bound vial of blood, and iron wire wound onto a rod. Corruption greys the stone (Hush), winds
# wire round it (Mortmain), cracks it with a coal behind in the Whisper (Grudge) and grates it at the
# Pull. Painted into images (PixelImage): the stone and rod when corruption changes, the vial as the
# blood moves.
const WHISPER := 0.75
const VIAL := Vector2i(52, 12)
const VIAL_SIZE := Vector2i(190, 10)
const ROD := Vector2i(52, 32)
const ROD_H := 6
const PERCENT := Vector2(270, 28)
# Recent damage lingers this long as dark blood, then drains at LAG_DRAIN of the vial per second.
const LAG_HOLD := 0.6
const LAG_DRAIN := 0.5
const SLOSH_FPS := 6.0
const DRIP_GRAVITY := 160.0
# Stone shades by corruption: clean bone, through grey, to near black at the Pull (Hush's greying).
const STONE_RAMPS := [
	[0.35, ["bone-1", "bone-0", "ash-4", "ash-3"]],
	[0.60, ["ash-4", "ash-3", "ash-2", "ash-1"]],
	[0.75, ["ash-3", "ash-2", "ash-1", "ash-0"]],
	[1.00, ["ash-2", "ash-1", "ash-0", "void-3"]],
	[9.99, ["ash-0", "void-3", "void-2", "void-2"]],
]
const CRACK := [[0, -12], [1, -11], [1, -10], [0, -9], [-1, -8], [-1, -7], [0, -6], [1, -5], [1, -4], [0, -3], [0, -2], [1, -1], [2, 0], [1, 1]]
const WOBBLE := [0, -1, -1, 0, 1, 0, -1, 0, 0, -1, 0, 1]

var emblem := PixelImage.new(Vector2i(44, 46))
var vial := PixelImage.new(VIAL_SIZE + Vector2i(12, 18))
var rod := PixelImage.new(Vector2i(VIAL_SIZE.x + 6, ROD_H + 10))
var textures := {}
var corruption := -1.0
var hp := 1.0
var lag := 1.0
var lag_hold := 0.0
var slosh_step := -1
var drips := []
var tremble := Vector2.ZERO


# hp and c in 0..1, every frame.
func update(dt: float, hp_now: float, c: float) -> void:
	var moved := hp_now != hp or lag != hp_now
	if hp_now < hp:
		lag = maxf(lag, hp)
		lag_hold = LAG_HOLD
		drips.append({"pos": Vector2(VIAL.x + VIAL_SIZE.x * hp_now - 1, VIAL.y + VIAL_SIZE.y + 2), "vy": 0.0, "life": 0.8})
	hp = hp_now
	lag_hold -= dt
	if lag_hold <= 0:
		lag = move_toward(lag, hp, LAG_DRAIN * dt)
	lag = maxf(lag, hp)
	if absf(c - corruption) > 0.004:
		corruption = c
		paint_keepsake(c)
		paint_rod(c)
		textures.emblem = emblem.texture()
		textures.rod = rod.texture()
	var step := int(Time.get_ticks_msec() / 1000.0 * SLOSH_FPS)
	if step != slosh_step or moved:
		slosh_step = step
		paint_vial(step)
		textures.vial = vial.texture()
	for d in drips:
		d.vy += DRIP_GRAVITY * dt
		d.pos.y += d.vy * dt
		d.life -= dt
	drips = drips.filter(func(d): return d.life > 0)
	# At the Pull the whole piece trembles.
	tremble = Vector2(randi_range(0, 1), randi_range(0, 1)) if c >= 1 and step % 2 == 0 else Vector2.ZERO
	queue_redraw()


func _draw() -> void:
	if textures.is_empty():
		return
	draw_texture(textures.emblem, tremble)
	draw_texture(textures.vial, Vector2(VIAL - Vector2i(4, 8)) + tremble)
	draw_texture(textures.rod, Vector2(ROD - Vector2i(3, 5)) + tremble)
	for d in drips:
		draw_rect(Rect2(d.pos.round() + tremble, Vector2(2, 3)), Color(Palette.color("blood-3"), minf(1.0, d.life * 2)))
	var c := "ash-4" if corruption < WHISPER else "ash-3"
	GothicText.draw(self, "%d%%" % roundi(corruption * 100), PERCENT + tremble, c, GothicText.BODY, GothicText.SMALL_SIZE)


func paint_keepsake(c: float) -> void:
	var p := emblem
	p.clear()
	var cx := 21
	var cy := 22
	var ring := 20
	# Iron ring: dark outline, lit top-left, shadowed bottom-right, four rivets.
	for yy in range(-ring - 1, ring + 2):
		for xx in range(-ring - 1, ring + 2):
			var d := Vector2(xx, yy).length()
			if d <= ring + 1 and d > ring - 4:
				var col := "void-0"
				if d <= ring and d > ring - 3:
					var light := (-xx - yy) / maxf(1, d)
					col = "steel-2" if light > 0.45 else "steel-0" if light < -0.45 else "steel-1"
				p.dot(cx + xx, cy + yy, col)
			elif d <= ring - 3:
				p.dot(cx + xx, cy + yy, "void-1")
	for a in [45, 135, 225, 315]:
		var r := deg_to_rad(a)
		var rx := cx + roundi(sin(r) * (ring - 1.5))
		var ry := cy - roundi(cos(r) * (ring - 1.5))
		p.dot(rx, ry, "ash-3")
		p.dot(rx + 1, ry + 1, "void-0")
	# The stone: broad at the shoulder, tapering to a blunt point, shaded in four bands from the top-left.
	var ramp: Array = STONE_RAMPS.filter(func(r): return c < r[0])[0][1]
	var half_w := 10
	var half_h := 13
	var stone := {}
	for dy in range(-half_h, half_h + 1):
		var v := float(dy) / half_h
		var w := half_w * (1 - 0.6 * pow(maxf(0, v), 1.3)) * (1 - 0.12 * pow(maxf(0, -v), 3))
		for dx in range(-half_w, half_w + 1):
			if pow(dx / (w + 0.5), 2) + pow(dy / (half_h + 0.5), 4) <= 1:
				stone[Vector2i(cx + dx, cy + dy)] = true
	p.outline(stone)
	for pt in stone:
		var u := float(pt.x - cx) / half_w
		var v := float(pt.y - cy) / half_h
		var light := -(u + v) * 0.7 + (1 - (u * u + v * v)) * 0.6
		p.dot(pt.x, pt.y, ramp[0 if light > 0.75 else 1 if light > 0.25 else 2 if light > -0.35 else 3])
	if c < WHISPER:
		p.rect(cx - 5, cy - 8, 2, 2, "bone-1" if c < 0.35 else ramp[0])
	# Iron wire: neat parallel wraps from the top down, each lit on top with a shadow below.
	var wraps := 6 if c >= 1 else roundi(c * 6)
	for i in wraps:
		var top := cy - 10 + i * 4
		for dx in range(-half_w - 1, half_w + 2):
			var yy := top + floori((dx + half_w) / 7.0)
			var here := Vector2i(cx + dx, yy)
			var edge := absi(dx) >= half_w - 1 and (stone.has(here + Vector2i.LEFT) or stone.has(here + Vector2i.RIGHT))
			if stone.has(here) or edge:
				p.dot(here.x, here.y, "steel-2" if dx < 0 else "steel-1")
				if stone.has(here + Vector2i.DOWN):
					p.dot(here.x, here.y + 1, "void-0")
	# The Whisper: a crack down the stone with Grudge's coal glowing in it.
	if c >= WHISPER:
		for step in CRACK:
			p.dot(cx + step[0], cy + step[1], "void-0")
			p.dot(cx + step[0] + 1, cy + step[1], ramp[3])
		p.rect(cx, cy - 5, 2, 2, "ember-1")
		p.dot(cx, cy - 5, "ember-2")
		p.dot(cx - 1, cy - 8, "ember-0")
		p.dot(cx + 1, cy - 1, "ember-0")
		if c >= 1:
			p.dot(cx + 1, cy - 4, "ember-3")
	# The Pull: an iron grate over the ring's opening.
	if c >= 1:
		for bx in range(-12, 13, 5):
			for yy in range(-16, 17):
				if Vector2(bx, yy).length() <= ring - 3 and Vector2(bx + 1, yy).length() <= ring - 3:
					p.dot(cx + bx, cy + yy, "steel-2")
					p.dot(cx + bx + 1, cy + yy, "steel-1")
					p.dot(cx + bx + 2, cy + yy, "void-0")
		for xx in range(-15, 16):
			p.dot(cx + xx, cy - 1, "steel-1")
			p.dot(cx + xx, cy, "steel-0")
			p.dot(cx + xx, cy + 1, "void-0")


# The vial: worn chipped gilt, dark glass, and blood moving in slow currents (smooth 1D noise, so
# light and dark form streaks and pools), clots low, bubbles high, a wobbling surface and a drip.
func paint_vial(step: int) -> void:
	var p := vial
	p.clear()
	var x := 4
	var y := 8
	var w := VIAL_SIZE.x
	var h := VIAL_SIZE.y
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	p.rect(x - 3, y - 3, w + 6, h + 6, "void-0")
	for i in range(-2, w + 2):
		for row in [[-2, "gilt-2"], [-1, "gilt-1"], [h, "gilt-1"], [h + 1, "gilt-0"]]:
			var r := rng.randf()
			var col: String = "gilt-3" if row[1] == "gilt-2" and r < 0.25 else "gilt-0" if r < 0.12 else "void-0" if r < 0.03 else row[1]
			p.dot(x + i, y + row[0], col)
	for side in [x - 2, x - 1, x + w, x + w + 1]:
		p.rect(side, y, 1, h, "gilt-1" if side == x - 1 or side == x + w else "gilt-0")
	for k in 4:
		var nick := x + rng.randi_range(4, w - 4)
		p.dot(nick, y - 2, "void-0")
		p.dot(nick + 1, y - 2, "gilt-0")
	p.rect(x, y, w, h, "void-1")
	for k in w / 30:
		p.rect(x + rng.randi_range(0, w - 6), y + rng.randi_range(0, h - 2), rng.randi_range(3, 6), 1, "void-2")
	var lattice := []
	for k in w / 4 + 3:
		lattice.append(rng.randf())
	var drift := step * 0.5
	var fill := roundi(w * hp)
	var trail := roundi(w * lag)
	for j in h:
		var end: int = fill + WOBBLE[(j + step) % WOBBLE.size()] - (2 if j == 0 else 0)
		var tail: int = trail + WOBBLE[(j + 5) % WOBBLE.size()]
		for i in maxi(end, tail):
			var col := "blood-1"
			if i >= end:
				if j >= h - 2 and wave(lattice, i, 40) > 0.6:
					col = "void-1"
			else:
				var n := wave(lattice, i, j * 2.5 + drift)
				if j <= 1:
					col = "blood-4" if n > 0.45 else "blood-3"
				elif j >= h - 3:
					col = "blood-1" if n > 0.7 else "blood-2"
				else:
					col = "blood-2" if n < 0.28 else "blood-4" if n > 0.85 and j < h / 2 else "blood-3"
			p.dot(x + i, y + j, col)
		if end > 0 and end < w:
			p.dot(x + end - 1, y + j, "blood-4" if j < h / 2 else "blood-3")
	for k in w / 30:
		var bx := x + rng.randi_range(4, maxi(5, fill - 6))
		var by := y + rng.randi_range(3, 5)
		if bx < x + fill - 5:
			p.rect(bx, by, 2, 2, "blood-4")
			p.dot(bx, by, "bone-0")
	for k in w / 24:
		var clot := x + rng.randi_range(2, maxi(3, fill - 6))
		if clot < x + fill - 5:
			p.rect(clot, y + h - 3, rng.randi_range(3, 5), 2, "blood-1")
			p.dot(clot + 1, y + h - 4, "blood-1")
	for k in 2:
		var sx := x + rng.randi_range(4, w - 8)
		p.rect(sx, y + 1, 3, 1, "bone-0" if sx < x + fill - 4 else "steel-0")
	if fill > 3:
		p.rect(x + fill - 2, y + h + 2, 2, 2, "blood-3")
		p.dot(x + fill - 2, y + h + 4, "blood-2")
	# Thorns: uneven barbs, curved, top and bottom.
	var tx := x + rng.randi_range(2, 8)
	while tx < x + w - 4:
		var up := rng.randf() < 0.55
		var size := rng.randi_range(3, 5)
		var lean := 1 if rng.randf() < 0.5 else -1
		for k in size:
			var yy := y - 4 - k if up else y + h + 3 + k
			var bx := tx + lean * (k / 2)
			p.dot(bx - 1, yy, "void-0")
			p.dot(bx + 1 + (1 if k < 2 else 0), yy, "void-0")
			p.dot(bx, yy, "leather-1" if k < 2 else "leather-0")
			if k < 2:
				p.dot(bx + 1, yy, "leather-0")
		p.dot(tx + lean * (size / 2), (y - 4 - size) if up else (y + h + 3 + size), "void-0")
		tx += rng.randi_range(6, 14)
	p.rect(x + w + 2, y - 2, 1, h + 4, "gilt-0")


func wave(lattice: Array, i: float, shift: float) -> float:
	var f := (i + shift) / 4.0
	var k := floori(f)
	var t := f - k
	t = t * t * (3 - 2 * t)
	return lerpf(lattice[posmod(k, lattice.size())], lattice[posmod(k + 1, lattice.size())], t)


# Corruption: iron wire wound unevenly onto a rod up to c, rust coming through, a notch at the Whisper.
func paint_rod(c: float) -> void:
	var p := rod
	p.clear()
	var x := 3
	var y := 5
	var w := VIAL_SIZE.x
	var h := ROD_H
	p.rect(x - 2, y - 2, w + 4, h + 4, "void-0")
	p.rect(x - 1, y - 1, w + 2, h + 2, "steel-0")
	p.rect(x, y, w, h, "void-1")
	var fill := roundi(w * c)
	var rng := RandomNumberGenerator.new()
	rng.seed = 9
	var i := 0
	while i < fill:
		var step: int = [3, 3, 4, 4, 5][rng.randi_range(0, 4)]
		for k in h:
			for t in step:
				if i + t >= fill:
					break
				var lit := (t + k) % step == 0
				p.dot(x + i + t, y + k, "steel-2" if lit else "steel-1" if (t + k) % step == 1 else "steel-0")
		if rng.randf() < 0.35:
			p.dot(x + i + 1, y + rng.randi_range(1, h - 2), "bronze-1" if rng.randf() < 0.6 else "blood-1")
		i += step
	for k in range(0, fill, 2):
		if rng.randf() < 0.6:
			p.dot(x + k, y, "steel-3" if c < 1 else "steel-1")
	var notch := x + roundi(w * WHISPER)
	p.rect(notch - 1, y - 4, 3, h + 8, "void-0")
	p.rect(notch, y - 3, 1, h + 6, "bone-0" if c < WHISPER else "ash-3")
