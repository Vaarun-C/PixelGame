class_name WorldNoise

# src/noise.js: 32-bit FNV-style hash and value noise, kept bit-for-bit like the JS.
const MASK := 0xFFFFFFFF


# Math.imul: the low 32 bits of a * b, without overflowing 64-bit ints.
static func imul(a: int, b: int) -> int:
	a &= MASK
	b &= MASK
	return ((((a >> 16) * b) & 0xFFFF) << 16) + (a & 0xFFFF) * b & MASK


static func hash32(values: Array) -> int:
	var h := 2166136261
	for v in values:
		h = imul(h ^ (int(v) & MASK), 16777619)
	h ^= h >> 15
	return imul(h, 2246822507)


static func random01(values: Array) -> float:
	return hash32(values) / 4294967296.0


static func value_noise(noise_seed: int, x: float, y: float) -> float:
	var x0 := floori(x)
	var y0 := floori(y)
	var sx := smoothstep(0.0, 1.0, x - x0)
	var sy := smoothstep(0.0, 1.0, y - y0)
	var top := lerpf(random01([noise_seed, x0, y0]), random01([noise_seed, x0 + 1, y0]), sx)
	var bottom := lerpf(random01([noise_seed, x0, y0 + 1]), random01([noise_seed, x0 + 1, y0 + 1]), sx)
	return lerpf(top, bottom, sy)
