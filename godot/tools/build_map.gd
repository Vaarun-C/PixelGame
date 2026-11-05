extends SceneTree

# Draws the fixed world's region scenes as an inked parchment map, world/map.png (MapPanel): one
# pixel per 2 x 2 tiles in palette browns, water washed grey, cliffs and coasts as ink lines (ramps
# left open), roads dotted, woods and crags stippled. Rerun after editing the regions, then --import.
# Run: godot --headless --path godot -s tools/build_map.gd
const STEP := WorldMap.MAP_TILES
const LAND := ["bone-1", "bone-1", "bone-1", "bone-0", "bone-0", "bone-0"]
const DEEP := "ash-4"
const WASH := "ash-3"
const INK := "leather-1"
const ROAD := "leather-2"
const WOODS := "flesh-2"
const THICKET := "leather-3"
const CRAG := "ash-2"

var palette: Node = preload("res://scripts/palette.gd").new()
var water := biome("water")
var road := biome("road")
var woods := biome("woods")


func _initialize() -> void:
	var map := WorldMap.from_scenes()
	var terrain := whole(map, "terrain")
	var level := whole(map, "level")
	var ramp := whole(map, "ramp")
	var size := WorldMap.SIZE / STEP
	var image := Image.create(size, size, false, Image.FORMAT_RGB8)
	for py in size:
		for px in size:
			var at := (py * STEP + 1) * WorldMap.SIZE + px * STEP + 1
			image.set_pixel(px, py, palette.color(shade(terrain, level, ramp, at, px, py)))
	image.save_png(ProjectSettings.globalize_path(WorldMap.MAP_PATH))
	print("wrote %s (%d x %d)" % [WorldMap.MAP_PATH, size, size])
	palette.free()
	quit()


# A layer for the whole map, one byte per corner.
func whole(map: WorldMap, layer: String) -> PackedByteArray:
	var image := Image.create(WorldMap.SIZE, WorldMap.SIZE, false, Image.FORMAT_L8)
	for ry in WorldMap.REGIONS:
		for rx in WorldMap.REGIONS:
			var r := map.region(rx * WorldMap.REGION, ry * WorldMap.REGION)
			var part := Image.create_from_data(WorldMap.REGION, WorldMap.REGION, false, Image.FORMAT_L8, r[layer])
			image.blit_rect(part, Rect2i(0, 0, WorldMap.REGION, WorldMap.REGION), r.origin)
	return image.get_data()


func shade(terrain: PackedByteArray, level: PackedByteArray, ramp: PackedByteArray, at: int, px: int, py: int) -> String:
	var id := terrain[at]
	var right := at + STEP if px < WorldMap.SIZE / STEP - 1 else at
	var below := at + STEP * WorldMap.SIZE if py < WorldMap.SIZE / STEP - 1 else at
	if (level[right] != level[at] or level[below] != level[at]) and not (ramp[at] or ramp[right] or ramp[below]):
		return INK
	if (terrain[at] == WorldMap.DEEP) != (terrain[right] == WorldMap.DEEP) or (terrain[at] == WorldMap.DEEP) != (terrain[below] == WorldMap.DEEP):
		return INK
	var kind := id / Terrain.GROUNDS
	var mark := (px * 73856093 ^ py * 19349663) % 7
	if id == WorldMap.DEEP:
		return DEEP
	if kind == water:
		return WASH
	if kind == road and (px + py) % 2 == 0:
		return ROAD
	if WorldMap.SOLID[id] and mark < (3 if kind == woods else 1):
		return THICKET if kind == woods else CRAG
	if kind == woods and mark == 0:
		return WOODS
	return LAND[mini(level[at], LAND.size() - 1)]


func biome(id: String) -> int:
	return Biomes.LIST.find_custom(func(b): return b.id == id)
