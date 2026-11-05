class_name Cliffs

# Which tall-wall tile (tiles/cliffs.tres, art/drafts/terrain/assemble.py) a tile of the fixed map
# shows. Corner states round the tile, relative to its highest corner: 1 upper, 2 wall top (a lower
# corner straight south of an upper one), 0 lower. The 4 x 4 window of states (255 in a pattern =
# any) picks the most specific matching pattern; failing that, the one that fits the tile's own
# corners and most of the ring. Ramps show no wall: the bare ground reads as the slope.
const CORE := [5, 6, 9, 10]
# Biomes without cliff art borrow another's.
const STAND_IN := {"village": "fallow", "road": "fallow", "water": "swamp"}

static var patterns: Array = JSON.parse_string(FileAccess.get_file_as_string("res://art/tiles/cliffs/tall_patterns.json"))


# [source id, atlas coords] for the tile, or [] when it shows no wall.
static func tile_for(map: WorldMap, tx: int, ty: int) -> Array:
	# The corners just north count too: under an edge the tile's own corners are all lower ground, yet
	# it shows the wall's lower half, unless the edge above is a ramp.
	var reach := [Vector2i(tx, ty), Vector2i(tx + 1, ty), Vector2i(tx, ty + 1), Vector2i(tx + 1, ty + 1), Vector2i(tx, ty - 1), Vector2i(tx + 1, ty - 1)]
	if reach.any(func(c): return map.ramp(c.x, c.y)):
		return []
	var top: int = reach.map(func(c): return map.level(c.x, c.y)).max()
	var near := []
	for y in range(ty - 1, ty + 3):
		for x in range(tx - 1, tx + 3):
			near.append(1 if map.level(x, y) >= top else 2 if map.level(x, y - 1) >= top else 0)
	if CORE.all(func(k): return near[k] == 1) or CORE.all(func(k): return near[k] == 0):
		return []
	var best := pick(near)
	if best < 0:
		return []
	var high: Vector2i = reach.filter(func(c): return map.level(c.x, c.y) == top)[0]
	return [source(map.terrain(high.x, high.y) / Terrain.GROUNDS), Vector2i(best, 0)]


static func pick(near: Array) -> int:
	var best := -1
	var score := -1
	for i in patterns.size():
		var p: Array = patterns[i]
		if range(16).all(func(k): return p[k] == 255 or p[k] == near[k]):
			var specific := p.filter(func(v): return v != 255).size()
			if specific > score:
				best = i
				score = specific
	if best >= 0:
		return best
	for i in patterns.size():
		var p: Array = patterns[i]
		if CORE.all(func(k): return p[k] == 255 or p[k] == near[k]):
			var ring := range(16).filter(func(k): return k not in CORE and p[k] == near[k]).size()
			if ring > score:
				best = i
				score = ring
	return best


static func source(biome: int) -> int:
	var id: String = STAND_IN.get(Biomes.LIST[biome].id, Biomes.LIST[biome].id)
	return Biomes.LIST.find_custom(func(b): return b.id == id)
