extends SceneTree

# Checks the fixed world's pieces. Run: godot --headless --path godot -s tools/world_check.gd
const CLIFF_MASKS := 16
const TALL_TILES := 25
const CLIFF_BIOMES := ["battlefield", "swamp", "ruins", "ashen", "frozen", "fallow", "woods", "mountain", "cinder"]

var fails := 0


func _initialize() -> void:
	run()


func run() -> void:
	check_biomes()
	check_world_map()
	await check_collision()
	print("world_check OK" if fails == 0 else "world_check FAILS %d" % fails)
	quit(1 if fails else 0)


func expect(ok: bool, what: String) -> void:
	if not ok:
		fails += 1
		print("FAIL ", what)


func check_biomes() -> void:
	expect(Biomes.LIST.size() == 12, "Biomes.LIST has %d entries, want 12" % Biomes.LIST.size())
	for biome in Biomes.LIST:
		for key in ["grounds", "spawns", "decals"]:
			expect(biome[key].size() == 4, "%s has %d %s" % [biome.id, biome[key].size(), key])
	var ground: TileSet = load("res://tiles/ground.tres")
	expect(ground.get_source_count() == 12, "ground.tres has %d sources" % ground.get_source_count())
	var cliffs = load("res://tiles/cliffs.tres") if ResourceLoader.exists("res://tiles/cliffs.tres") else null
	expect(cliffs != null, "tiles/cliffs.tres missing")
	if not cliffs:
		return
	expect(cliffs.get_source_count() == CLIFF_BIOMES.size(), "cliffs.tres has %d sources" % cliffs.get_source_count())
	for id in CLIFF_BIOMES:
		var i := Biomes.LIST.find_custom(func(b): return b.id == id)
		var source: TileSetAtlasSource = cliffs.get_source(i) if cliffs.has_source(i) else null
		expect(source != null and source.has_tile(Vector2i(TALL_TILES - 1, 0)) and source.has_tile(Vector2i(CLIFF_MASKS - 1, 1)), "cliffs.tres lacks %s's wall or ramp tiles" % id)
	var patterns = JSON.parse_string(FileAccess.get_file_as_string("res://art/tiles/cliffs/tall_patterns.json"))
	expect(patterns is Array and patterns.size() == TALL_TILES, "tall_patterns.json should list %d patterns" % TALL_TILES)


const BRIDGE := 47
const WATER_BIOME := 10
const RIVER := 41


func check_world_map() -> void:
	var started := Time.get_ticks_msec()
	var map := WorldMap.from_scenes()
	var villages := map.places("village")
	expect(villages.size() == 5, "%d villages" % villages.size())
	var start: Array = villages.filter(func(p): return p.start)
	expect(start.size() == 1, "%d start villages" % start.size())
	if start.is_empty():
		return
	var home: Vector2i = start[0].tile
	expect(map.walkable(home.x, home.y), "the start village's tile is not walkable")
	var loaded := Time.get_ticks_msec() - started
	expect(loaded < 300, "loading the start region took %d ms" % loaded)
	expect(map.terrain(-5, -5) == 40 and not map.walkable(-5, -5), "off the map should be deep water")
	expect(map.reachable(home, home + Vector2i(30, 0), 4000), "30 tiles east of the start can't be reached")
	# Spawning runs this every 0.35 s: a search that never finds its target must stay well under a frame.
	map.reachable(home, Vector2i(-50, -50), Terrain.REACH_LIMIT)
	var timed := Time.get_ticks_usec()
	for i in 10:
		map.reachable(home + Vector2i(i, 0), Vector2i(-50, -50), Terrain.REACH_LIMIT)
	var each := (Time.get_ticks_usec() - timed) / 10000.0
	expect(each < 4.0, "an unreachable spawn search takes %.1f ms" % each)
	var cross: Vector2i = map.places("crossroads")[0].tile
	var wet_props: Array = map.region(cross.x, cross.y).props.keys().filter(func(t): return touches_deep_water(map, t))
	expect(wet_props.is_empty(), "%d props stand on river or deep water near the crossroads, e.g. %s" % [wet_props.size(), wet_props.slice(0, 3)])
	var bridge := find_near(map, cross, 60, func(x, y): return map.terrain(x, y) == BRIDGE)
	expect(bridge != Vector2i(-1, -1), "no bridge within 60 tiles of the crossroads")
	if bridge != Vector2i(-1, -1):
		expect(map.walkable(bridge.x, bridge.y), "the bridge at %s is not walkable" % bridge)
		var river := find_near(map, bridge, 6, func(x, y): return map.terrain(x, y) == RIVER and map.terrain(x + 1, y) == RIVER and map.terrain(x, y + 1) == RIVER and map.terrain(x + 1, y + 1) == RIVER)
		expect(river != Vector2i(-1, -1) and not map.walkable(river.x, river.y), "the river beside the bridge is walkable or missing")


func find_near(map: WorldMap, at: Vector2i, radius: int, test: Callable) -> Vector2i:
	for r in radius:
		for y in range(at.y - r, at.y + r + 1):
			for x in range(at.x - r, at.x + r + 1):
				if maxi(absi(x - at.x), absi(y - at.y)) == r and test.call(x, y):
					return Vector2i(x, y)
	return Vector2i(-1, -1)


# In the running game, a river and a wall face block and the bridge beside the river does not.
func check_collision() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	var map := WorldMap.active
	expect(map != null, "main.tscn did not open the fixed map")
	if not map:
		return
	var cross: Vector2i = map.places("crossroads")[0].tile
	var bridge := find_near(map, cross, 60, func(x, y): return map.terrain(x, y) == BRIDGE and map.walkable(x, y))
	var river := find_near(map, bridge, 6, func(x, y): return not map.walkable(x, y) and map.terrain(x, y) == RIVER)
	var wall := find_near(map, cross, 200, func(x, y): return Cliffs.tile_for(map, x, y) and not map.walkable(x, y))
	# The row under a south-facing edge is the lower half of the wall: it must draw, not just block.
	var face := find_near(map, cross, 300, func(x, y): return wall_face(map, x, y))
	expect(face != Vector2i(-1, -1) and not Cliffs.tile_for(map, face.x, face.y).is_empty(), "the wall face at %s has no wall tile" % face)
	# Water stays water: no wall tile on a tile whose corners are all water (seen off the Ashholm causeway).
	var gate: Vector2i = map.places("village").filter(func(p): return p.name == "Ashbarrow")[0].tile
	var wet_wall := find_near(map, gate, 80, func(x, y): return all_water(map, x, y) and not Cliffs.tile_for(map, x, y).is_empty())
	expect(wet_wall == Vector2i(-1, -1), "a wall tile stands in open water at %s" % wet_wall)
	var player: Node2D = main.get_node("Player")
	for tile in [bridge, river, wall]:
		player.position = centre(tile)
		for i in 10:
			await physics_frame
		var hits := solid_at(main, centre(tile))
		var want: bool = tile != bridge
		expect(hits == want, "%s at %s: solid %s, want %s" % [["bridge", "river", "wall"][[bridge, river, wall].find(tile)], tile, hits, want])
	expect(Terrain.blocked(centre(river)), "Terrain.blocked() misses the river")
	check_villages(map, main)
	main.free()


# Authored villages, the start, reachability for spawning and zone titles, in the running game.
func check_villages(map: WorldMap, main: Node) -> void:
	var home: Dictionary = map.places("village").filter(func(p): return p.start)[0]
	for step in [Vector2i(10, 0), Vector2i(-10, 0), Vector2i(0, 10), Vector2i(0, -10)]:
		var tile: Vector2i = home.tile + step
		var found := Villages.near(Terrain.world_seed, tile.x, tile.y)
		expect(found.get("name", "") == home.name, "Villages.near misses %s from %s" % [home.name, step])
	var arrived := Terrain.village_at(Villages.start_position())
	expect(arrived.get("name", "") == home.name, "the start position is not inside %s" % home.name)
	expect(Terrain.reachable(centre(home.tile), centre(home.tile + Vector2i(0, 12))), "12 tiles south of %s can't be reached" % home.name)
	var river := find_near(map, map.places("crossroads")[0].tile, 400, func(x, y): return map.terrain(x, y) == RIVER and not near_bridge(map, Vector2i(x, y)))
	var west := river
	while not map.walkable(west.x, west.y):
		west.x -= 1
	var east := river
	while not map.walkable(east.x, east.y):
		east.x += 1
	expect(not Terrain.reachable(centre(west), centre(east)), "the banks of the river at %s join within reach" % river)
	var interface: Node = main.get_node("Interface")
	interface.zone = "Fallow Fields"
	expect(interface.next_zone("") == "Fallow Fields", "crossing a road changes the zone title")
	expect(interface.next_zone("Dead Woods") == "Dead Woods", "entering the woods keeps the old zone title")
	# A ragged border must not flip the title back and forth: a new zone shows once it has lasted.
	expect(interface.settle_zone("Dead Woods", 0.1) == "Fallow Fields", "one step into the woods already changes the title")
	expect(interface.settle_zone("Fallow Fields", 0.1) == "Fallow Fields", "stepping back out changes the title")
	interface.settle_zone("Dead Woods", 0.4)
	expect(interface.settle_zone("Dead Woods", 0.4) == "Dead Woods", "staying in the woods never changes the title")


func near_bridge(map: WorldMap, at: Vector2i) -> bool:
	return find_near(map, at, 40, func(x, y): return map.terrain(x, y) == BRIDGE) != Vector2i(-1, -1)


func centre(tile: Vector2i) -> Vector2:
	return (Vector2(tile) + Vector2(0.5, 0.5)) * Terrain.TILE * Terrain.SCALE


func solid_at(main: Node, at: Vector2) -> bool:
	var query := PhysicsPointQueryParameters2D.new()
	query.position = at
	query.collide_with_areas = false
	var hits: Array = main.get_world_2d().direct_space_state.intersect_point(query)
	return hits.any(func(h): return h.collider is StaticBody2D and h.collider.get_parent().get("def_kind") == null)


# A tile wholly on one level, under higher ground to the north, with no ramp: the lower half of a wall.
func wall_face(map: WorldMap, x: int, y: int) -> bool:
	var corners := [Vector2i(x, y), Vector2i(x + 1, y), Vector2i(x, y + 1), Vector2i(x + 1, y + 1)]
	var level := map.level(x, y)
	if corners.any(func(c): return map.level(c.x, c.y) != level or map.ramp(c.x, c.y)):
		return false
	return map.level(x, y - 1) > level and map.level(x + 1, y - 1) > level and not map.ramp(x, y - 1)


func all_water(map: WorldMap, x: int, y: int) -> bool:
	for c in [Vector2i(x, y), Vector2i(x + 1, y), Vector2i(x, y + 1), Vector2i(x + 1, y + 1)]:
		if map.terrain(c.x, c.y) / Terrain.GROUNDS != WATER_BIOME:
			return false
	return true


func touches_deep_water(map: WorldMap, t: Vector2i) -> bool:
	for c in [t, t + Vector2i(1, 0), t + Vector2i(0, 1), t + Vector2i(1, 1)]:
		if map.terrain(c.x, c.y) in [WorldMap.DEEP, RIVER]:
			return true
	return false
