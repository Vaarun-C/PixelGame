class_name WorldMap
extends RefCounted

# The fixed world (tools/world_design/export.py, baked by tools/build_world.gd): terrain id, level and
# ramp at every tile corner, the props and the places. Read from 8 x 8 region scenes, each loaded the
# first time something asks about it; outside the map is deep water. Corners and tiles share
# coordinates: tile (x, y) has the corners (x, y) to (x + 1, y + 1).
const SIZE := 2000
const REGION := 250
const REGIONS := SIZE / REGION
const DEEP := 40
const REGION_PATH := "res://world/regions/r_%d_%d.scn"
const PLACES_PATH := "res://world/places.tscn"
# Paint-layer value an empty cell stands for, by layer.
const EMPTY := {"Terrain": DEEP, "Level": 0, "Ramp": 0}

static var active: WorldMap

var regions := {}
var place_list := []
# Builder only: the export's images, sliced per region on demand.
var images := {}
# 1 for each terrain id nobody can walk on (Biomes grounds marked solid).
static var SOLID: PackedByteArray = solid_ids()


static func solid_ids() -> PackedByteArray:
	var ids := PackedByteArray()
	for biome in Biomes.LIST:
		for ground in biome.grounds:
			ids.append(1 if ground.get("solid", false) else 0)
	return ids


static func from_scenes() -> WorldMap:
	var map := WorldMap.new()
	var root: Node = load(PLACES_PATH).instantiate()
	for marker in root.get_children():
		map.place_list.append({"kind": marker.kind, "name": marker.place_name, "tile": Terrain.tile_of(marker.position), "start": marker.start})
	root.free()
	return map


static func from_export(dir: String) -> WorldMap:
	var map := WorldMap.new()
	for layer in ["terrain", "level", "ramp"]:
		var image := Image.load_from_file(dir.path_join(layer + ".png"))
		image.convert(Image.FORMAT_L8)
		map.images[layer] = image
	var places = JSON.parse_string(FileAccess.get_file_as_string(dir.path_join("places.json")))
	for p in places:
		map.place_list.append({"kind": p.kind, "name": p.name, "tile": Vector2i(p.tile[0], p.tile[1]), "start": p.start})
	return map


func places(kind := "") -> Array:
	return place_list.filter(func(p): return kind.is_empty() or p.kind == kind)


func region(vx: int, vy: int) -> Dictionary:
	var key := Vector2i(floori(float(vx) / REGION), floori(float(vy) / REGION))
	if key.x < 0 or key.y < 0 or key.x >= REGIONS or key.y >= REGIONS:
		return {}
	if not regions.has(key):
		regions[key] = from_image(key) if images else from_scene(key)
	return regions[key]


func from_image(key: Vector2i) -> Dictionary:
	var rect := Rect2i(key * REGION, Vector2i(REGION, REGION))
	return {
		"origin": key * REGION, "props": {}, "walk": blank(),
		"terrain": images.terrain.get_region(rect).get_data(),
		"level": images.level.get_region(rect).get_data(),
		"ramp": images.ramp.get_region(rect).get_data(),
	}


func from_scene(key: Vector2i) -> Dictionary:
	var root: Node = load(REGION_PATH % [key.x, key.y]).instantiate()
	var data := {"origin": key * REGION, "props": {}, "walk": blank()}
	for layer in EMPTY:
		var bytes := PackedByteArray()
		bytes.resize(REGION * REGION)
		bytes.fill(EMPTY[layer])
		var tiles: TileMapLayer = root.get_node(layer)
		for cell in tiles.get_used_cells():
			var local: Vector2i = cell - data.origin
			if local.x >= 0 and local.y >= 0 and local.x < REGION and local.y < REGION:
				bytes[local.y * REGION + local.x] = tiles.get_cell_atlas_coords(cell).x
		data[layer.to_lower()] = bytes
	for marker in root.get_node("Props").get_children():
		data.props[Terrain.tile_of(marker.position)] = {"kind": marker.kind, "variant": marker.variant, "pos": marker.position}
	root.free()
	return data


static func blank() -> PackedByteArray:
	var bytes := PackedByteArray()
	bytes.resize(REGION * REGION)
	return bytes


func value(layer: String, vx: int, vy: int, outside: int) -> int:
	var r := region(vx, vy)
	if r.is_empty():
		return outside
	return r[layer][(vy - r.origin.y) * REGION + vx - r.origin.x]


func terrain(vx: int, vy: int) -> int:
	return value("terrain", vx, vy, DEEP)


func level(vx: int, vy: int) -> int:
	return value("level", vx, vy, 0)


func ramp(vx: int, vy: int) -> bool:
	return value("ramp", vx, vy, 0) == 1


func prop(tx: int, ty: int) -> Dictionary:
	var r := region(tx, ty)
	return r.props.get(Vector2i(tx, ty), {}) if r else {}


func solid(vx: int, vy: int) -> bool:
	return SOLID[terrain(vx, vy)] == 1


# A tile can be walked unless half its corners are solid ground, it spans a level edge, or it is the
# face of a wall rising to the north (its top corners sit under higher ground); ramps open all three.
# Spawning asks often, so each region remembers its answers (0 not yet asked, 1 yes, 2 no).
func walkable(tx: int, ty: int) -> bool:
	var r := region(tx, ty)
	if r.is_empty():
		return false
	var i: int = (ty - r.origin.y) * REGION + tx - r.origin.x
	if r.walk[i] == 0:
		r.walk[i] = 1 if walkable_now(tx, ty) else 2
	return r.walk[i] == 1


func walkable_now(tx: int, ty: int) -> bool:
	if int(solid(tx, ty)) + int(solid(tx + 1, ty)) + int(solid(tx, ty + 1)) + int(solid(tx + 1, ty + 1)) >= 2:
		return false
	if ramp(tx, ty) or ramp(tx + 1, ty) or ramp(tx, ty + 1) or ramp(tx + 1, ty + 1):
		return true
	var here := level(tx, ty)
	if level(tx + 1, ty) != here or level(tx, ty + 1) != here or level(tx + 1, ty + 1) != here:
		return false
	return level(tx, ty - 1) <= here and level(tx + 1, ty - 1) <= here


# Whether b can be walked to from a, giving up after `limit` tiles.
func reachable(a: Vector2i, b: Vector2i, limit: int) -> bool:
	var seen := {a: true}
	var queue: Array[Vector2i] = [a]
	var next_at := 0
	while next_at < queue.size() and seen.size() < limit:
		var at := queue[next_at]
		next_at += 1
		if at == b:
			return true
		for step in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var next: Vector2i = at + step
			if not seen.has(next) and walkable(next.x, next.y):
				seen[next] = true
				queue.append(next)
	return false
