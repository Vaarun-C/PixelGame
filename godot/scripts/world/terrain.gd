class_name Terrain

# The procedural world from src/world.js: biome regions, ground types and prop placement, all pure
# functions of the seed. Positions in and out are Godot pixels; the maths runs in the JS world's
# pixels (SCALE times smaller) so it stays comparable with the JS.
const SCALE := 2
const TILE := 32
const GROUNDS := 4
const BIOME_CELL := 48
# Props gather in clusters with clearings between: a slow noise mask (one blob per CLUSTER_SIZE
# tiles) scales the spawn odds from 0 at CLEARING to 2 * DENSITY at GROVE, about DENSITY on average.
const DENSITY := 0.5
const CLUSTER_SIZE := 5.0
const CLEARING := 0.3
const GROVE := 0.7
# Large props only stand on every LARGE_GRID-th tile each way, so they never crowd each other.
const LARGE_GRID := 3
# Up to this far off their tile centre, so the grid doesn't show as rows (world pixels).
const LARGE_JITTER := 24
# Decal spots rolled per tile; the decal odds per ground in biomes.gd add up to at most this.
const DECAL_TRIES := 3
const FEET := [-5, -3, 10, 4]
const CACHE_LIMIT := 50000

static var world_seed := 0
# A wild biome index to fill the whole world with, or -1 for the normal mix.
static var only_biome := -1
static var cache := {}


static func reset(new_seed: int, biome := -1) -> void:
	world_seed = new_seed
	only_biome = biome
	cache.clear()
	Villages.layouts.clear()


# Wild biome at a tile corner: nearest jittered cell centre, with the coordinates warped so borders
# are organic and a little high-frequency warp so neighbouring biomes mix in a band along the border.
# The spawn cell is the battlefield.
static func wild_biome_at(vx: int, vy: int) -> int:
	if only_biome >= 0:
		return only_biome
	var s := world_seed
	var wx := vx + (WorldNoise.value_noise(s + 20, vx / 9.0, vy / 9.0) - 0.5) * 18 + (WorldNoise.value_noise(s + 21, vx / 2.5, vy / 2.5) - 0.5) * 5
	var wy := vy + (WorldNoise.value_noise(s + 22, vx / 9.0, vy / 9.0) - 0.5) * 18 + (WorldNoise.value_noise(s + 23, vx / 2.5, vy / 2.5) - 0.5) * 5
	var cx0 := floori(wx / BIOME_CELL + 0.5)
	var cy0 := floori(wy / BIOME_CELL + 0.5)
	var best := 0
	var best_dist := INF
	for cy in range(cy0 - 1, cy0 + 2):
		for cx in range(cx0 - 1, cx0 + 2):
			var spawn := cx == 0 and cy == 0
			var px := cx * BIOME_CELL + (0.0 if spawn else (WorldNoise.random01([s, cx, cy, 24]) - 0.5) * 0.6 * BIOME_CELL)
			var py := cy * BIOME_CELL + (0.0 if spawn else (WorldNoise.random01([s, cx, cy, 25]) - 0.5) * 0.6 * BIOME_CELL)
			var dist := (wx - px) ** 2 + (wy - py) ** 2
			if dist < best_dist:
				best_dist = dist
				best = 0 if spawn else WorldNoise.hash32([s, cx, cy, 26]) % Biomes.WILD
	return best


# Terrain id at a tile corner: biome * GROUNDS + ground. Higher ids draw on top of lower ones.
static func terrain_at(vx: int, vy: int) -> int:
	var key := Vector2i(vx, vy)
	if cache.has(key):
		return cache[key]
	var s := world_seed
	var margin := 0.5 + WorldNoise.value_noise(s + 30, vx / 2.0, vy / 2.0)
	var biome := Biomes.VILLAGE if Villages.near(s, vx, vy, margin) else wild_biome_at(vx, vy)
	var n := WorldNoise.value_noise(s + 2, vx / 7.0, vy / 7.0) * 0.7 + WorldNoise.value_noise(s + 3, vx / 3.0, vy / 3.0) * 0.3
	var ground := 3 if WorldNoise.value_noise(s + 1, vx / 4.0, vy / 4.0) > 0.86 else 2 if n > 0.6 else 1 if n < 0.38 else 0
	if cache.size() > CACHE_LIMIT:
		cache.clear()
	cache[key] = biome * GROUNDS + ground
	return cache[key]


static func nearest_corner(pos: Vector2) -> int:
	var corner := (pos / (SCALE * TILE)).round()
	return terrain_at(int(corner.x), int(corner.y))


# Movement effect of the ground under a point: {speed, slide}.
static func ground_at(pos: Vector2) -> Dictionary:
	var id := nearest_corner(pos)
	return Biomes.LIST[id / GROUNDS].grounds[id % GROUNDS]


static func biome_at(pos: Vector2) -> Dictionary:
	return Biomes.LIST[nearest_corner(pos) / GROUNDS]


# The prop on a tile: {kind, variant, pos}, or {}.
static func prop_at(tx: int, ty: int) -> Dictionary:
	var s := world_seed
	var village := Villages.near(s, tx, ty)
	if village:
		var placed := Villages.prop(village, tx - village.tx, ty - village.ty)
		return placed_prop(placed[0], placed[1], tx * TILE + 16, ty * TILE + 28) if placed else {}

	var id := terrain_at(tx, ty)
	var density := prop_density(tx, ty)
	if density <= 0:
		return {}
	var r := WorldNoise.random01([s, tx, ty, 7]) / density
	var large_odds := LARGE_GRID * LARGE_GRID / 4.0
	var kind := ""
	var spawns: Dictionary = Biomes.LIST[id / GROUNDS].spawns[id % GROUNDS]
	for k in spawns:
		# The tables assume large props roll on 1 tile in 4; they now roll on 1 in LARGE_GRID².
		r -= spawns[k] * (large_odds if Props.LIST[k].get("large", false) else 1.0)
		if r < 0:
			kind = k
			break
	if not kind:
		return {}
	var def: Dictionary = Props.LIST[kind]
	var large: bool = def.get("large", false)
	if large and (posmod(tx, LARGE_GRID) or posmod(ty, LARGE_GRID)):
		return {}
	var v := WorldNoise.hash32([s, tx, ty, 9])
	var jitter := LARGE_JITTER if large else 16
	return placed_prop(kind, v % def.variants, tx * TILE + 16 - jitter / 2 + (v >> 2) % jitter, ty * TILE + 16 - jitter / 2 + (v >> 6) % jitter)


# The decals on a tile: up to DECAL_TRIES spots, each taking its kind from the ground right under it,
# so grass grows on the grass side of a border. [{row, pos, phase}, ...] (see Decals.placed).
static func decals_at(tx: int, ty: int) -> Array:
	var found := []
	for i in DECAL_TRIES:
		var h := WorldNoise.hash32([world_seed, tx, ty, 50 + i])
		var at := Vector2(tx * TILE + h % TILE, ty * TILE + (h >> 8) % TILE) * SCALE
		var id := nearest_corner(at)
		var odds: Dictionary = Biomes.LIST[id / GROUNDS].decals[id % GROUNDS]
		var r := WorldNoise.random01([world_seed, tx, ty, 60 + i]) * DECAL_TRIES
		for kind in odds:
			r -= odds[kind]
			if r < 0:
				found.append(Decals.placed(kind, h >> 16, at))
				break
	return found


# The grass-like decal kinds that grow on the ground at a point, for tucking around prop bases.
static func tufts_at(pos: Vector2) -> Array:
	var id := nearest_corner(pos)
	var odds: Dictionary = Biomes.LIST[id / GROUNDS].decals[id % GROUNDS]
	return odds.keys().filter(func(kind): return Decals.KINDS[kind].get("tuft", false))


static func prop_density(tx: int, ty: int) -> float:
	var n := WorldNoise.value_noise(world_seed + 40, tx / CLUSTER_SIZE, ty / CLUSTER_SIZE)
	return DENSITY * 2 * smoothstep(CLEARING, GROVE, n)


static func placed_prop(kind: String, variant: int, x: int, y: int) -> Dictionary:
	return {"kind": kind, "variant": variant, "pos": Vector2(x, y) * SCALE}


static func tile_of(pos: Vector2) -> Vector2i:
	return Vector2i((pos / (SCALE * TILE)).floor())


# Whether feet at this point would stand inside a prop's collision box.
static func blocked(pos: Vector2) -> bool:
	var feet := Rect2(pos / SCALE + Vector2(FEET[0], FEET[1]), Vector2(FEET[2], FEET[3]))
	var tile := tile_of(pos)
	for ty in range(tile.y - 2, tile.y + 3):
		for tx in range(tile.x - 2, tile.x + 3):
			var prop := prop_at(tx, ty)
			var box := Props.solid_box(prop.kind, prop.variant) if prop else []
			if box and feet.intersects(Rect2(prop.pos / SCALE + Vector2(box[0], box[1]), Vector2(box[2], box[3]))):
				return true
	return false


# Village grounds, walls included: enemies never spawn or walk here.
static func in_village_grounds(pos: Vector2) -> bool:
	var tile := tile_of(pos)
	return not Villages.near(world_seed, tile.x, tile.y, 1.5).is_empty()


# The village whose walls enclose a point, or {}.
static func village_at(pos: Vector2) -> Dictionary:
	var tile := tile_of(pos)
	var village := Villages.near(world_seed, tile.x, tile.y)
	if village.is_empty():
		return {}
	var p := pos / SCALE
	var inside := Villages.reach(p.x - (village.tx * TILE + 16), p.y - (village.ty * TILE + 16)) < (Villages.RADIUS - 0.5) * TILE
	return village if inside else {}
