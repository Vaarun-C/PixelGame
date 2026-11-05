extends SceneTree

# Bakes the fixed world's export (tools/world_design/export.py) into editable scenes: 64 region scenes
# (world/regions/r_<x>_<y>.scn) holding the Terrain, Level and Ramp paint layers and every prop as a
# PropMarker, and world/places.tscn with a PlaceMarker per place. One-off: hand edits to the scenes
# are the source of truth after this, so rerunning it overwrites them.
# Run: godot --headless --path godot -s tools/build_world.gd -- <absolute path to tools/world_design/out>
const SWATCH := 64
const SWATCH_PATH := "res://world/swatches.res"
const LEVEL_SWATCHES := ["void-3", "ash-0", "ash-1", "ash-2", "ash-3", "ash-4"]
# Tiles around a village centre left without props: Villages lays out its own.
const VILLAGE_CLEAR := 16

var palette: Node = preload("res://scripts/palette.gd").new()


func _initialize() -> void:
	var dir: String = OS.get_cmdline_user_args()[0]
	var map := WorldMap.from_export(dir)
	WorldMap.active = map
	Terrain.reset(Terrain.FIXED_SEED)
	DirAccess.make_dir_recursive_absolute("res://world/regions")
	var swatches := swatch_set()
	ResourceSaver.save(swatches, SWATCH_PATH, ResourceSaver.FLAG_COMPRESS)
	var villages: Array = map.places("village").map(func(p): return p.tile)
	for ry in WorldMap.REGIONS:
		for rx in WorldMap.REGIONS:
			var started := Time.get_ticks_msec()
			var root := region_scene(map, Vector2i(rx, ry), swatches, villages)
			var packed := PackedScene.new()
			packed.pack(root)
			ResourceSaver.save(packed, WorldMap.REGION_PATH % [rx, ry], ResourceSaver.FLAG_COMPRESS)
			print("region %d,%d: %d props, %d ms" % [rx, ry, root.get_node("Props").get_child_count(), Time.get_ticks_msec() - started])
			root.free()
	save_places(map)
	palette.free()
	quit()


# One swatch per value: row 0 terrain ids (each ground's average colour), row 1 levels, row 2 ramp.
func swatch_set() -> TileSet:
	var image := Image.create(Biomes.LIST.size() * Terrain.GROUNDS * SWATCH, 3 * SWATCH, false, Image.FORMAT_RGBA8)
	for id in Biomes.LIST.size() * Terrain.GROUNDS:
		image.fill_rect(Rect2i(id * SWATCH, 0, SWATCH, SWATCH), ground_colour(id))
	for i in LEVEL_SWATCHES.size():
		image.fill_rect(Rect2i(i * SWATCH, SWATCH, SWATCH, SWATCH), palette.color(LEVEL_SWATCHES[i]))
	image.fill_rect(Rect2i(SWATCH, 2 * SWATCH, SWATCH, SWATCH), palette.color("gilt-2"))
	var source := TileSetAtlasSource.new()
	source.texture = ImageTexture.create_from_image(image)
	source.texture_region_size = Vector2i(SWATCH, SWATCH)
	for y in 3:
		for x in image.get_width() / SWATCH:
			source.create_tile(Vector2i(x, y))
	var tile_set := TileSet.new()
	tile_set.tile_size = Vector2i(SWATCH, SWATCH)
	tile_set.add_source(source, 0)
	return tile_set


# The palette colour nearest a ground's full tile, averaged.
func ground_colour(id: int) -> Color:
	var biome: String = Biomes.LIST[id / Terrain.GROUNDS].id
	var sheet: Image = load("res://art/tiles/%s/%s_ground_hd.png" % [biome, biome]).get_image()
	var tile := sheet.get_region(Rect2i(15 * SWATCH, id % Terrain.GROUNDS * SWATCH, SWATCH, SWATCH))
	tile.resize(1, 1, Image.INTERPOLATE_BILINEAR)
	var average := tile.get_pixel(0, 0)
	var best := Color.BLACK
	for c in palette.colors.values():
		if Vector3(c.r - average.r, c.g - average.g, c.b - average.b).length() < Vector3(best.r - average.r, best.g - average.g, best.b - average.b).length():
			best = c
	return best


func region_scene(map: WorldMap, key: Vector2i, swatches: TileSet, villages: Array) -> Node2D:
	var root := Node2D.new()
	root.name = "Region"
	var layers := {}
	for layer in WorldMap.EMPTY:
		var tiles := TileMapLayer.new()
		tiles.name = layer
		tiles.tile_set = swatches
		tiles.position = -Vector2.ONE * SWATCH / 2
		tiles.modulate.a = 1.0 if layer == "Terrain" else 0.4
		root.add_child(tiles)
		tiles.owner = root
		layers[layer] = tiles
	var props := Node2D.new()
	props.name = "Props"
	root.add_child(props)
	props.owner = root
	var origin := key * WorldMap.REGION
	for vy in range(origin.y, origin.y + WorldMap.REGION):
		for vx in range(origin.x, origin.x + WorldMap.REGION):
			var cell := Vector2i(vx, vy)
			var values := {"Terrain": map.terrain(vx, vy), "Level": map.level(vx, vy), "Ramp": int(map.ramp(vx, vy))}
			for layer in values:
				if values[layer] != WorldMap.EMPTY[layer]:
					layers[layer].set_cell(cell, 0, Vector2i(values[layer], ["Terrain", "Level", "Ramp"].find(layer)))
			if on_edge(map, vx, vy) or wet(map, vx, vy) or villages.any(func(v): return v.distance_to(cell) < VILLAGE_CLEAR):
				continue
			var prop := Terrain.roll_prop(vx, vy)
			if prop:
				var marker := PropMarker.new()
				marker.kind = prop.kind
				marker.variant = prop.variant
				marker.position = prop.pos
				props.add_child(marker)
				marker.owner = root
	return root


# Tiles touching a river or deep water stay clear of props: they would stand half in the water.
func wet(map: WorldMap, tx: int, ty: int) -> bool:
	for c in [Vector2i(tx, ty), Vector2i(tx + 1, ty), Vector2i(tx, ty + 1), Vector2i(tx + 1, ty + 1)]:
		if map.terrain(c.x, c.y) in [WorldMap.DEEP, WorldMap.DEEP + 1]:
			return true
	return false


# Tiles on a level edge or a wall face stay clear of props.
func on_edge(map: WorldMap, tx: int, ty: int) -> bool:
	var levels := [map.level(tx, ty), map.level(tx + 1, ty), map.level(tx, ty + 1), map.level(tx + 1, ty + 1), map.level(tx, ty - 1), map.level(tx + 1, ty - 1)]
	return levels.min() != levels.max()


func save_places(map: WorldMap) -> void:
	var root := Node2D.new()
	root.name = "Places"
	for p in map.places():
		var marker := PlaceMarker.new()
		marker.name = p.name.validate_node_name().replace(" ", "_")
		marker.kind = p.kind
		marker.place_name = p.name
		marker.start = p.start
		marker.position = Vector2(p.tile) * Terrain.TILE * Terrain.SCALE + Vector2.ONE * Terrain.TILE
		root.add_child(marker)
		marker.owner = root
	var packed := PackedScene.new()
	packed.pack(root)
	ResourceSaver.save(packed, WorldMap.PLACES_PATH)
	root.free()
