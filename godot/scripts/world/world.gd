extends Node2D

# Streams the procedural world around the player in chunks: ground tiles into stacked TileMapLayers
# (dual-grid: terrain is sampled at tile corners and each tile draws every terrain touching it,
# lowest id first, the rest as corner masks over it), ground decals, and props and villages as
# y-sorted nodes.
const GROUND := preload("res://tiles/ground.tres")
const VILLAGER := preload("res://scenes/villager.tscn")
const DECAL_LAYER := preload("res://scripts/world/decal_layer.gd")
const LAYERS := 4
const FULL_TILES := [15, 16, 17, 18]
const CHUNK := 8
const LOAD_RADIUS := 2
const KEEP_RADIUS := 3
const CHUNKS_PER_FRAME := 2
# Chunks this close always load at once, so the view (under 1 chunk to each side) never shows a hole.
const VISIBLE_RADIUS := 1
const VILLAGE_GROUNDS_LAYER := 2
# How close the feet must be to a lootable prop's box to search it (Godot px).
const LOOT_RANGE := 20.0

# Fill the whole world with one biome, e.g. to look at its tiles and props.
@export_enum("All", "The Battlefield", "Rot Swamp", "Chapel Ruins", "Ashen Forest", "Frozen Pass") var biome := 0
@export var with_villages := true

var layers: Array[TileMapLayer] = []
var chunks := {}
# Loaded villages by key: {name, seed, centre, villagers, barterer, chunk}.
var villages := {}
# What is left in each searched prop, by prop key; unsearched props aren't here yet.
var loot := {}

@onready var player: Node2D = get_tree().get_first_node_in_group("player")


func _ready() -> void:
	add_to_group("world")
	Villages.enabled = with_villages
	Terrain.reset(randi(), biome - 1)
	for i in LAYERS:
		var layer := TileMapLayer.new()
		layer.tile_set = GROUND
		layer.z_index = -10 + i
		add_child(layer)
		layers.append(layer)
	_process(0)


func _process(_dt: float) -> void:
	var centre := chunk_of(player.position)
	var budget := CHUNKS_PER_FRAME
	for chunk in chunks_around(centre, LOAD_RADIUS):
		if chunks.has(chunk):
			continue
		var in_view := maxi(absi(chunk.x - centre.x), absi(chunk.y - centre.y)) <= VISIBLE_RADIUS
		if in_view or budget > 0:
			load_chunk(chunk)
			budget -= 0 if in_view else 1
	for chunk in chunks.keys():
		if maxi(absi(chunk.x - centre.x), absi(chunk.y - centre.y)) > KEEP_RADIUS:
			unload_chunk(chunk)


func chunk_of(pos: Vector2) -> Vector2i:
	return Vector2i((Vector2(Terrain.tile_of(pos)) / CHUNK).floor())


# Nearest first, so the ground under the player fills in before the edges.
func chunks_around(centre: Vector2i, radius: int) -> Array[Vector2i]:
	var found: Array[Vector2i] = []
	for y in range(-radius, radius + 1):
		for x in range(-radius, radius + 1):
			found.append(centre + Vector2i(x, y))
	found.sort_custom(func(a, b): return (a - centre).length_squared() < (b - centre).length_squared())
	return found


func chunk_tiles(chunk: Vector2i) -> Array[Vector2i]:
	var tiles: Array[Vector2i] = []
	for y in CHUNK:
		for x in CHUNK:
			tiles.append(chunk * CHUNK + Vector2i(x, y))
	return tiles


func load_chunk(chunk: Vector2i) -> void:
	var holder := Node2D.new()
	holder.y_sort_enabled = true
	add_child(holder)
	chunks[chunk] = holder
	var decals := []
	for tile in chunk_tiles(chunk):
		paint_tile(tile)
		decals.append_array(Terrain.decals_at(tile.x, tile.y))
		var prop := Terrain.prop_at(tile.x, tile.y)
		if prop:
			add_prop(holder, prop.kind, prop.variant, prop.pos, "%d,%d" % [tile.x, tile.y])
		var village := Villages.near(Terrain.world_seed, tile.x, tile.y)
		if village and village.tx == tile.x and village.ty == tile.y:
			add_village(holder, village, chunk)
	holder.add_child(DECAL_LAYER.new(decals))


func unload_chunk(chunk: Vector2i) -> void:
	for tile in chunk_tiles(chunk):
		for layer in layers:
			layer.erase_cell(tile)
	chunks[chunk].queue_free()
	chunks.erase(chunk)
	for key in villages.keys():
		if villages[key].chunk == chunk:
			villages.erase(key)


# key: names the prop in `loot`, so a searched prop stays spent when its chunk loads again.
func add_prop(parent: Node, kind: String, variant: int, at: Vector2, key: String) -> Prop:
	var prop := Prop.create(kind, variant, at)
	prop.key = key
	prop.spent = not has_loot(prop)
	parent.add_child(prop)
	return prop


func has_loot(prop: Prop) -> bool:
	return prop.def.has("loot") and loot.get(prop.key, [null]).size() > 0


# The lootable prop whose box (solid, or its loot area) is nearest the feet, within reach; or null.
func nearest_lootable(feet: Vector2) -> Prop:
	var best: Prop = null
	var best_distance := LOOT_RANGE
	for prop in get_tree().get_nodes_in_group("lootables"):
		if not has_loot(prop):
			continue
		var box: Array = Props.solid_box(prop.def_kind, prop.variant)
		if box.is_empty():
			box = prop.def.area
		var rect := Rect2(prop.position + Vector2(box[0], box[1]) * Terrain.SCALE, Vector2(box[2], box[3]) * Terrain.SCALE)
		var gap := Vector2(maxf(maxf(rect.position.x - feet.x, 0), feet.x - rect.end.x), maxf(maxf(rect.position.y - feet.y, 0), feet.y - rect.end.y))
		if gap.length() < best_distance:
			best = prop
			best_distance = gap.length()
	return best


# Rolls (once) and takes a prop's loot into the bag. Returns the pickup messages: [[text, colour], ...].
func search(prop: Prop, inventory: Inventory) -> Array:
	var found: Array = loot[prop.key] if loot.has(prop.key) else Items.roll_loot(prop.def.loot, Terrain.biome_at(prop.position).loot)
	var said := []
	if found.is_empty():
		said.append([Items.LOOT_TABLES[prop.def.loot].nothing, "ash-3"])
	var left := []
	for item in found:
		var rest := inventory.add(item.key, item.count)
		var info := Items.info(item.key)
		if rest < item.count:
			said.append(["+%d%s %s" % [item.count - rest, info.unit, info.name], info.color])
		if rest:
			left.append({"key": item.key, "count": rest})
	if left:
		said.append(["Inventory full.", "blood-4"])
	loot[prop.key] = left
	prop.spent = left.is_empty()
	return said


# The loaded village whose walls enclose a point, or {}.
func village_at(pos: Vector2) -> Dictionary:
	var centre := Terrain.village_at(pos)
	return villages.get(centre.key, {}) if centre else {}


func paint_tile(tile: Vector2i) -> void:
	var corners := [
		Terrain.terrain_at(tile.x, tile.y), Terrain.terrain_at(tile.x + 1, tile.y),
		Terrain.terrain_at(tile.x, tile.y + 1), Terrain.terrain_at(tile.x + 1, tile.y + 1),
	]
	var ids := []
	for id in corners:
		if id not in ids:
			ids.append(id)
	ids.sort()
	var full: int = FULL_TILES[(WorldNoise.hash32([Terrain.world_seed, tile.x, tile.y]) >> 4) % FULL_TILES.size()]
	for i in ids.size():
		var mask := 0
		for bit in corners.size():
			if corners[bit] == ids[i]:
				mask |= 1 << bit
		var column := full if i == 0 or mask == 15 else mask
		layers[i].set_cell(tile, ids[i] / Terrain.GROUNDS, Vector2i(column, ids[i] % Terrain.GROUNDS))


# Villagers, the barterer and an invisible wall around the grounds that only Hollows bump into
# (createVillage in src/village.js, inVillageGrounds in src/world.js).
func add_village(holder: Node2D, village: Dictionary, chunk: Vector2i) -> void:
	var centre := Vector2(village.tx * Terrain.TILE + 16, village.ty * Terrain.TILE + 16)
	var h := WorldNoise.hash32([Terrain.world_seed, village.tx, village.ty, 33])
	var villagers := []
	for i in 2 + h % 3:
		var villager := VILLAGER.instantiate()
		villager.role = Villages.ROLES[i]
		villager.wait = 1.0 + i
		villager.position = (centre + Vector2((i - 1) * 24, 40)) * Terrain.SCALE
		holder.add_child(villager)
		villagers.append(villager)
	var barterer := VILLAGER.instantiate()
	barterer.role = "barterer"
	barterer.position = (centre + Vector2(Villages.STALL) * Terrain.TILE - Vector2(0, 2)) * Terrain.SCALE
	holder.add_child(barterer)
	villages[village.key] = {
		"name": Villages.NAME_START[h % Villages.NAME_START.size()] + Villages.NAME_END[(h >> 8) % Villages.NAME_END.size()],
		"seed": h, "centre": centre * Terrain.SCALE, "villagers": villagers, "barterer": barterer, "chunk": chunk,
	}

	var span := (Villages.RADIUS + 1) * 2 + 1
	var grounds := Prop.collision_body([-(Villages.RADIUS + 1) * Terrain.TILE, -(Villages.RADIUS + 1) * Terrain.TILE, span * Terrain.TILE, span * Terrain.TILE])
	grounds.collision_layer = 1 << (VILLAGE_GROUNDS_LAYER - 1)
	grounds.position = Vector2(village.tx, village.ty) * Terrain.TILE * Terrain.SCALE
	holder.add_child(grounds)
