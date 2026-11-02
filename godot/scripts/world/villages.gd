class_name Villages

# src/village.js: where villages stand and how each is laid out. Tile coordinates.
const CELL := 64
const CHANCE := 0.2
const RADIUS := 8
const ROLES := ["peasant", "monk", "guard", "peasant"]
const NAME_START := ["Grey", "Hollow", "Black", "Thorn", "Grave", "Mire", "Cinder", "Frost", "Ash", "Raven"]
const NAME_END := ["well", "moor", "hold", "stead", "ford", "barrow", "gate", "fen"]
const FIRST_NAMES := ["Hild", "Aldo", "Bertram", "Edda", "Osric", "Maud", "Garrick", "Agna", "Ulf", "Gisla", "Bede", "Tilda", "Ham", "Ysolt", "Merek", "Wenna", "Cuthbert", "Elsa", "Jory", "Sabel"]
const SURNAMES := ["Vosk", "Carr", "Tull", "Brack", "Holt", "Marsh", "Pell", "Rusk", "Crane", "Ashby", "Grieve", "Stave"]
const LINES := {
	"peasant": ["The crows eat better than we do.", "Don't drink from the well after dark.", "My son went to the battlefield. The crows came back."],
	"monk": ["The runes remember what we forget.", "Pray if you like. Nothing listens.", "Every stone out there was once a promise."],
	"guard": ["Keep your blade low inside the walls.", "Walls won't hold forever. Neither will I.", "Seen worse than you come through that gate."],
}
const STALL := Vector2i(-3, -1)
const HUT_SLOTS := [Vector2i(-5, 3), Vector2i(5, -2), Vector2i(4, 4), Vector2i(-3, -5), Vector2i(5, -5), Vector2i(-5, -3), Vector2i(3, 6), Vector2i(3, -5)]
const FIREPIT_SLOTS := [Vector2i(2, 2), Vector2i(-2, 3), Vector2i(2, -3)]
const CRATE_SLOTS := [Vector2i(-1, -2), Vector2i(3, 0), Vector2i(-2, 2), Vector2i(-6, 0), Vector2i(6, 1)]
const HUT_VARIANTS := 5
const WALL_VARIANTS := 4
# A new game starts in a village (LORE.md, Villages): the spawn cell always holds one, at its middle.
const START := Vector2i(CELL / 2, CELL / 2)
# Where the Wanderer starts and comes back after death: south of the well, clear of the row the
# villagers spawn on (add_village), since overlapping bodies shove each other apart (Godot px).
const ARRIVAL := Vector2(0, 112)

static var layouts := {}
# Off for the prologue: no village on the last field.
static var enabled := true


# The village centre in a CELL-sized cell, or {} (most cells have none, the spawn cell always).
static func centre_in(world_seed: int, cx: int, cy: int) -> Dictionary:
	if not enabled:
		return {}
	var h := WorldNoise.hash32([world_seed, cx, cy, 32])
	if cx == 0 and cy == 0:
		return {"tx": START.x, "ty": START.y, "key": Vector2i.ZERO, "seed": h}
	if WorldNoise.random01([world_seed, cx, cy, 31]) > CHANCE:
		return {}
	return {"tx": cx * CELL + 16 + h % 32, "ty": cy * CELL + 16 + (h >> 8) % 32, "key": Vector2i(cx, cy), "seed": h}


static func start_position() -> Vector2:
	return (Vector2(START) * Terrain.TILE + Vector2(16, 16)) * Terrain.SCALE + ARRIVAL


static func reach(dx: float, dy: float) -> float:
	return maxf(absf(dx), absf(dy))


static func near(world_seed: int, tx: int, ty: int, margin := 1.0) -> Dictionary:
	var centre := centre_in(world_seed, floori(tx / float(CELL)), floori(ty / float(CELL)))
	return centre if centre and reach(tx - centre.tx, ty - centre.ty) < RADIUS + margin else {}


# A villager's name: first name and surname from their own seed.
static func villager_name(villager_seed: int) -> String:
	return FIRST_NAMES[villager_seed % FIRST_NAMES.size()] + " " + SURNAMES[(villager_seed >> 8) % SURNAMES.size()]


static func pick(village_seed: int, slot: Vector2i, n: int) -> int:
	return floori(WorldNoise.random01([village_seed, slot.x, slot.y, 5]) * n)


static func pick_slots(village_seed: int, salt: int, slots: Array, count: int) -> Array:
	var shuffled := slots.duplicate()
	shuffled.sort_custom(func(a, b): return WorldNoise.hash32([village_seed, salt, a.x, a.y]) < WorldNoise.hash32([village_seed, salt, b.x, b.y]))
	return shuffled.slice(0, count)


static func layout_for(centre: Dictionary) -> Dictionary:
	if layouts.has(centre.key):
		return layouts[centre.key]
	var s: int = centre.seed
	var layout := {Vector2i.ZERO: ["well", s % 3], STALL: ["stall", 0]}
	layout[pick_slots(s, 1, FIREPIT_SLOTS, 1)[0]] = ["firepit", 0]
	for slot in pick_slots(s, 2, HUT_SLOTS, 4 + s % 3):
		layout[slot] = ["hut", pick(s, slot, HUT_VARIANTS)]
	for slot in pick_slots(s, 3, CRATE_SLOTS, 2 + s % 2):
		layout[slot] = ["village_crate", pick(s, slot, 3)]
	layouts[centre.key] = layout
	return layout


# [kind, variant] at an offset from the centre tile, or []. The palisade rings the village with a
# gate in the middle of the top and bottom walls.
static func prop(centre: Dictionary, dx: int, dy: int) -> Array:
	if reach(dx, dy) == RADIUS:
		var side := absi(dx) == RADIUS
		var corner := side and absi(dy) == RADIUS
		if not side and dx == 0:
			return []
		if corner or (not side and absi(dx) == 1):
			return ["palisade", 6]
		var variant := WALL_VARIANTS + pick(centre.seed, Vector2i(dx, dy), 2) if side else pick(centre.seed, Vector2i(dx, dy), WALL_VARIANTS)
		return ["palisade", variant]
	return layout_for(centre).get(Vector2i(dx, dy), [])
