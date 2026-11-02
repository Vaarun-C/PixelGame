extends SceneTree

# Builds tiles/ground.tres from the biome HD ground sheets (tools/gen_ground_hd.py): one atlas source per biome (source id =
# index in Biomes.LIST), one row per ground, columns = corner masks (see world.gd paint_tile).
# Each sheet holds FRAMES copies of its COLUMNS side by side; rows whose frames differ (water, embers) animate.
# Run: godot --headless --script tools/build_tileset.gd
const SIZE := 64
const COLUMNS := 19
const FRAMES := 4
const FRAME_SECONDS := 0.25


func _initialize() -> void:
	var tile_set := TileSet.new()
	tile_set.tile_size = Vector2i(SIZE, SIZE)
	for i in Biomes.LIST.size():
		var id: String = Biomes.LIST[i].id
		var source := TileSetAtlasSource.new()
		source.texture = load("res://art/tiles/%s/%s_ground_hd.png" % [id, id])
		source.texture_region_size = Vector2i(SIZE, SIZE)
		var image := source.texture.get_image()
		for y in source.get_atlas_grid_size().y:
			var animated := frame_of(image, y, 0) != frame_of(image, y, 1)
			for x in COLUMNS:
				var coords := Vector2i(x, y)
				source.create_tile(coords)
				if animated:
					source.set_tile_animation_separation(coords, Vector2i(COLUMNS - 1, 0))
					source.set_tile_animation_frames_count(coords, FRAMES)
					for f in FRAMES:
						source.set_tile_animation_frame_duration(coords, f, FRAME_SECONDS)
		tile_set.add_source(source, i)
	print(ResourceSaver.save(tile_set, "res://tiles/ground.tres"))
	quit()


# A row's full tiles (cols 15-18) in one frame. Overlay columns are left out: the importer recolours
# their transparent pixels from neighbouring frames, so they differ even when nothing visible does.
func frame_of(image: Image, row: int, frame: int) -> PackedByteArray:
	return image.get_region(Rect2i((frame * COLUMNS + 15) * SIZE, row * SIZE, 4 * SIZE, SIZE)).get_data()
