class_name Villages

# Where villages stand and how each is laid out (src/village.js, reshaped). Tile coordinates.
# Each village has its own outline: a closed ring of lobes around the well, walled by a palisade
# that follows it, with a gate north and south. Inside, a random number of buildings stand
# around the well, clear of the paths from the gates.
const CELL := 64
const CHANCE := 0.2
const NAME_START := ["Grey", "Hollow", "Black", "Thorn", "Grave", "Mire", "Cinder", "Frost", "Ash", "Raven"]
const NAME_END := ["well", "moor", "hold", "stead", "ford", "barrow", "gate", "fen"]
const FIRST_NAMES := ["Hild", "Aldo", "Bertram", "Edda", "Osric", "Maud", "Garrick", "Agna", "Ulf", "Gisla", "Bede", "Tilda", "Ham", "Ysolt", "Merek", "Wenna", "Cuthbert", "Elsa", "Jory", "Sabel"]
const SURNAMES := ["Vosk", "Carr", "Tull", "Brack", "Holt", "Marsh", "Pell", "Rusk", "Crane", "Ashby", "Grieve", "Stave"]
const LINES := {
	"peasant": ["The crows eat better than we do.", "Don't drink from the well after dark.", "My son went to the battlefield. The crows came back."],
	"monk": ["The runes remember what we forget.", "Pray if you like. Nothing listens.", "Every stone out there was once a promise."],
	"guard": ["Keep your blade low inside the walls.", "Walls won't hold forever. Neither will I.", "Seen worse than you come through that gate."],
}
# The outline: SHAPE_POINTS radii around the well, each straying up to BULGE from a mean radius
# drawn from SIZE (tiles). Centres sit at least EDGE tiles inside their CELL, so the largest outline
# (plus the Hollow barrier around it) stays in the cell.
const SHAPE_POINTS := 9
const EDGE := 20
const SIZE := [11.0, 14.5]
const BULGE := 0.2
# Tiles left open each side of a gate's middle.
const GATE_HALF := 1.6
const TORCH_ODDS := 0.08
const WALL_VARIANTS := 4
# Buildings: one longhouse at most, the first placed, then a mix drawn from BUILDINGS (repeats
# weight the draw); about one per TILES_PER_BUILDING tiles of ground, kept BUILDING_MARGIN tiles
# inside the wall, with a tile of ground between neighbours.
const CENTREPIECE := "longhouse"
const CENTREPIECE_TRIES := 60
const BUILDINGS := ["cottage", "cottage", "cottage", "barn", "shed", "shed"]
const TILES_PER_BUILDING := 28.0
const BUILDING_MARGIN := 1.2
const PLACE_TRIES := 300
const DEPTH_SHARE := 0.75
const CRATES := [2, 5]
# Villagers besides the barterer: one peasant at least, a monk at most.
const PEOPLE := [2, 6]
const EXTRA_ROLES := ["peasant", "peasant", "guard", "monk"]
const STALL := Vector2i(-3, -1)
# The smith stands across the well from the stall.
const SMITHY := Vector2i(3, -1)
# The three rite places (Rites): the fire and the ledger near the well, the road shrine beside the
# south gate's path, SHRINE_SIDE tiles off its middle.
const FIREPIT_SLOTS := [Vector2i(2, 2), Vector2i(-2, 3), Vector2i(2, -3), Vector2i(3, 1)]
const LEDGER_SLOTS := [Vector2i(-3, 2), Vector2i(3, -1), Vector2i(-2, -3), Vector2i(4, 2), Vector2i(-4, 0)]
const SHRINE_SIDE := 3
# A new game starts in a village (LORE.md, Villages): the spawn cell always holds one, at its middle.
const START := Vector2i(CELL / 2, CELL / 2)
# Where the Wanderer starts and comes back after death: south of the well, on ground kept clear
# (Godot px).
const ARRIVAL := Vector2(0, 112)

static var layouts := {}
static var authored_for: WorldMap
static var authored_list := []
# No village outline reaches further than this from its well (SIZE plus BULGE, rounded up).
const REACH := 20.0
static var shapes := {}
# Off for the prologue: no village on the last field.
static var enabled := true


# The village centre in a CELL-sized cell, or {} (most cells have none, the spawn cell always).
static func centre_in(world_seed: int, cx: int, cy: int) -> Dictionary:
	if WorldMap.active:
		var inside_cell := authored().filter(func(c): return floori(c.tx / float(CELL)) == cx and floori(c.ty / float(CELL)) == cy)
		return inside_cell[0] if inside_cell else {}
	if not enabled:
		return {}
	var h := WorldNoise.hash32([world_seed, cx, cy, 32])
	if cx == 0 and cy == 0:
		return {"tx": START.x, "ty": START.y, "key": Vector2i.ZERO, "seed": h}
	if WorldNoise.random01([world_seed, cx, cy, 31]) > CHANCE:
		return {}
	return {"tx": cx * CELL + EDGE + h % (CELL - 2 * EDGE), "ty": cy * CELL + EDGE + (h >> 8) % (CELL - 2 * EDGE), "key": Vector2i(cx, cy), "seed": h}


static func start_position() -> Vector2:
	var start := Vector2(START)
	if WorldMap.active:
		var home: Dictionary = authored().filter(func(c): return c.start)[0]
		start = Vector2(home.tx, home.ty)
	return (start * Terrain.TILE + Vector2(16, 16)) * Terrain.SCALE + ARRIVAL


# The fixed map's villages as centres (the shape the rest of this file uses), kept per map.
static func authored() -> Array:
	if authored_for != WorldMap.active:
		authored_for = WorldMap.active
		authored_list = WorldMap.active.places("village").map(func(p): return {
			"tx": p.tile.x, "ty": p.tile.y, "key": p.tile, "seed": WorldNoise.hash32([p.name.hash()]), "name": p.name, "start": p.start,
		})
	return authored_list


# The village whose ground (walls included, plus margin tiles) holds a tile, or {}.
static func near(world_seed: int, tx: float, ty: float, margin := 0.0) -> Dictionary:
	if WorldMap.active:
		for c in authored():
			if absf(tx - c.tx) < REACH and absf(ty - c.ty) < REACH and inside(c, tx - c.tx, ty - c.ty, margin):
				return c
		return {}
	var centre := centre_in(world_seed, floori(tx / CELL), floori(ty / CELL))
	return centre if centre and inside(centre, tx - centre.tx, ty - centre.ty, margin) else {}


static func shape(centre: Dictionary) -> Dictionary:
	if shapes.has(centre.key):
		return shapes[centre.key]
	var s: int = centre.seed
	var mean := lerpf(SIZE[0], SIZE[1], WorldNoise.random01([s, 40]))
	var radii := []
	for i in SHAPE_POINTS:
		radii.append(mean * (1.0 + BULGE * (WorldNoise.random01([s, 41, i]) * 2 - 1)))
	var gates := []
	for side in [-1, 1]:
		gates.append(PI / 2 * side + (WorldNoise.random01([s, 42, side]) - 0.5) * 0.8)
	shapes[centre.key] = {"mean": mean, "radii": radii, "gates": gates}
	return shapes[centre.key]


# The outline's distance from the well at an angle, eased between its points.
static func radius_at(outline: Dictionary, angle: float) -> float:
	var t := fposmod(angle / TAU, 1.0) * SHAPE_POINTS
	var i := floori(t)
	var f := t - i
	return lerpf(outline.radii[i % SHAPE_POINTS], outline.radii[(i + 1) % SHAPE_POINTS], f * f * (3 - 2 * f))


static func inside(centre: Dictionary, dx: float, dy: float, margin := 0.0) -> bool:
	return Vector2(dx, dy).length() < radius_at(shape(centre), atan2(dy, dx)) + margin


# Wall tiles: the village's own tiles that touch the outside, corners included, so the ring has no
# diagonal gaps.
static func is_wall(centre: Dictionary, dx: int, dy: int) -> bool:
	if not inside(centre, dx, dy):
		return false
	for n in [Vector2i(-1, -1), Vector2i(0, -1), Vector2i(1, -1), Vector2i(-1, 0), Vector2i(1, 0), Vector2i(-1, 1), Vector2i(0, 1), Vector2i(1, 1)]:
		if not inside(centre, dx + n.x, dy + n.y):
			return true
	return false


static func gate_points(centre: Dictionary) -> Array:
	var outline := shape(centre)
	return outline.gates.map(func(a): return Vector2.from_angle(a) * radius_at(outline, a))


static func is_gate(centre: Dictionary, dx: int, dy: int) -> bool:
	return gate_points(centre).any(func(p): return p.distance_to(Vector2(dx, dy)) < GATE_HALF)


static func pick(village_seed: int, slot: Vector2i, n: int) -> int:
	return floori(WorldNoise.random01([village_seed, slot.x, slot.y, 5]) * n)


static func villager_name(villager_seed: int) -> String:
	return FIRST_NAMES[villager_seed % FIRST_NAMES.size()] + " " + SURNAMES[(villager_seed >> 8) % SURNAMES.size()]


# Building footprint in tiles: as wide as its sprite. Rows of buildings sit DEPTH_SHARE of that apart,
# so a roof may rise over the yard behind it.
static func footprint(kind: String) -> int:
	var def: Dictionary = Props.LIST[kind]
	return ceili(def.size * def.get("scale", 1.0) / Terrain.TILE)


static func layout_for(centre: Dictionary) -> Dictionary:
	if layouts.has(centre.key):
		return layouts[centre.key]
	var s: int = centre.seed
	var outline := shape(centre)
	var layout := {Vector2i.ZERO: ["well", s % 3], STALL: ["stall", 0]}
	# Kept clear: around the well, stall and smith, where the Wanderer arrives, and the paths in.
	var taken := [Rect2i(-2, -2, 5, 4), Rect2i(STALL.x - 2, STALL.y - 1, 4, 3), Rect2i(SMITHY.x - 1, SMITHY.y - 1, 3, 3), Rect2i(-1, 1, 3, 3)]
	var paths := []
	for gate in gate_points(centre):
		for step in ceili(gate.length()):
			var p := Vector2i((gate * step / gate.length()).round())
			paths.append(Rect2i(p - Vector2i.ONE, Vector2i(3, 3)))
	claim(layout, taken, paths, FIREPIT_SLOTS, "firepit")
	claim(layout, taken, paths, LEDGER_SLOTS, "ledger")
	claim(layout, taken, paths, shrine_slots(centre), "wayside_shrine")

	var houses := []
	var wanted := roundi(PI * outline.mean * outline.mean / TILES_PER_BUILDING * lerpf(0.75, 1.25, WorldNoise.random01([s, 43])))
	for attempt in PLACE_TRIES:
		if houses.size() >= wanted:
			break
		var kind: String = CENTREPIECE if houses.is_empty() and attempt < CENTREPIECE_TRIES else BUILDINGS[floori(WorldNoise.random01([s, 44, attempt]) * BUILDINGS.size())]
		var size := footprint(kind)
		var at := Vector2i((Vector2.from_angle(WorldNoise.random01([s, 45, attempt]) * TAU) * outline.mean * sqrt(WorldNoise.random01([s, 46, attempt]))).round())
		var depth := ceili(size * DEPTH_SHARE)
		# The sprite is centred on its anchor tile, so it reaches half a tile past size / 2 each way.
		var rect := Rect2i(at.x - size / 2, at.y - depth + 1, size + 1, depth)
		var corners := [rect.position, rect.end - Vector2i.ONE, Vector2i(rect.position.x, rect.end.y - 1), Vector2i(rect.end.x - 1, rect.position.y)]
		if not corners.all(func(c): return inside(centre, c.x, c.y, -BUILDING_MARGIN)):
			continue
		if taken.any(func(r): return r.intersects(rect.grow(1))) or paths.any(func(r): return r.intersects(rect)):
			continue
		layout[at] = [kind, pick(s, at, Props.LIST[kind].variants)]
		taken.append(rect)
		houses.append(at)

	for i in floori(lerpf(CRATES[0], CRATES[1] + 1, WorldNoise.random01([s, 47]))):
		if houses.is_empty():
			break
		var house: Vector2i = houses[i % houses.size()]
		var by: Vector2i = house + Vector2i(footprint(layout[house][0]) / 2 + 1, 0)
		if inside(centre, by.x, by.y, -BUILDING_MARGIN) and not (taken + paths).any(func(r): return r.has_point(by)):
			layout[by] = ["village_crate", pick(s, by, 3)]
			taken.append(Rect2i(by, Vector2i.ONE))
	layout["houses"] = houses
	layouts[centre.key] = layout
	return layout


# Puts `kind` on the first slot clear of what is taken and of the paths, and takes the tiles around it.
static func claim(layout: Dictionary, taken: Array, paths: Array, slots: Array, kind: String) -> void:
	for slot in slots:
		if not (taken + paths).any(func(r): return r.has_point(slot)):
			layout[slot] = [kind, 0]
			taken.append(Rect2i(slot - Vector2i.ONE, Vector2i(3, 3)))
			return


# Beside the south gate's path, a few tiles in, either side; only those inside the wall.
static func shrine_slots(centre: Dictionary) -> Array:
	var gate: Vector2 = gate_points(centre)[1]
	var side := Vector2(-gate.y, gate.x).normalized() * SHRINE_SIDE
	var slots := []
	for step in [3, 4, 5, 6]:
		for s in [1, -1]:
			var p := Vector2i((gate - gate.normalized() * step + side * s).round())
			if inside(centre, p.x, p.y, -BUILDING_MARGIN):
				slots.append(p)
	return slots


# The villagers besides the barterer: [role, tile offset from the well], each near a house door.
static func people(centre: Dictionary) -> Array:
	var s: int = centre.seed
	var houses: Array = layout_for(centre).houses
	var count := floori(lerpf(PEOPLE[0], PEOPLE[1] + 1, WorldNoise.random01([s, 48])))
	var list := []
	var monk := false
	for i in count:
		var role: String = "peasant" if i == 0 else EXTRA_ROLES[floori(WorldNoise.random01([s, 49, i]) * EXTRA_ROLES.size())]
		if role == "monk":
			role = "peasant" if monk else role
			monk = true
		var home: Vector2i = houses[i % houses.size()] + Vector2i(0, 1) if houses else Vector2i(i - 1, 2)
		list.append([role, home])
	return list


# [kind, variant] at an offset from the centre tile, or [].
static func prop(centre: Dictionary, dx: int, dy: int) -> Array:
	if is_wall(centre, dx, dy):
		return wall_piece(centre, dx, dy)
	var placed = layout_for(centre).get(Vector2i(dx, dy), [])
	return placed if placed is Array else []


# Upright logs where the wall runs north-south, a lying row where it runs east-west or turns, and a
# torch post beside each gate and here and there along the ring.
static func wall_piece(centre: Dictionary, dx: int, dy: int) -> Array:
	if is_gate(centre, dx, dy):
		return []
	var beside_gate := [Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, -1), Vector2i(0, 1)].any(func(n): return is_gate(centre, dx + n.x, dy + n.y))
	var slot := Vector2i(dx, dy)
	if beside_gate or WorldNoise.random01([centre.seed, dx, dy, 6]) < TORCH_ODDS:
		return ["palisade", 6]
	var across := is_wall(centre, dx - 1, dy) or is_wall(centre, dx + 1, dy)
	var along := is_wall(centre, dx, dy - 1) and is_wall(centre, dx, dy + 1)
	if along and not across:
		return ["palisade", WALL_VARIANTS + pick(centre.seed, slot, 2)]
	return ["palisade", pick(centre.seed, slot, WALL_VARIANTS)]
