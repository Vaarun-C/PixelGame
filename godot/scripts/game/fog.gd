class_name Fog

# What the Wanderer has seen of the fixed map, for the map (map_panel.gd): one byte per 8 x 8 tile
# chunk, 255 seen and 0 not, kept on the Inventory and saved with it.
const CHUNK := 8
const SIZE := WorldMap.SIZE / CHUNK
# Chunks revealed round the one he stands in: what he could see from there, a few screens.
const RADIUS := 5


static func blank() -> PackedByteArray:
	var bytes := PackedByteArray()
	bytes.resize(SIZE * SIZE)
	return bytes


static func index(chunk: Vector2i) -> int:
	return chunk.y * SIZE + chunk.x if chunk.x >= 0 and chunk.y >= 0 and chunk.x < SIZE and chunk.y < SIZE else -1


static func seen(explored: PackedByteArray, tile: Vector2i) -> bool:
	var i := index(tile / CHUNK)
	return i >= 0 and explored[i] > 0


# Whether anything new was revealed.
static func reveal(explored: PackedByteArray, tile: Vector2i) -> bool:
	var centre := tile / CHUNK
	var changed := false
	for y in range(-RADIUS, RADIUS + 1):
		for x in range(-RADIUS, RADIUS + 1):
			var i := index(centre + Vector2i(x, y))
			if x * x + y * y <= RADIUS * RADIUS + 1 and i >= 0 and explored[i] == 0:
				explored[i] = 255
				changed = true
	return changed


static func pack(explored: PackedByteArray) -> String:
	return Marshalls.raw_to_base64(explored.compress(FileAccess.COMPRESSION_DEFLATE))


static func unpack(text: String) -> PackedByteArray:
	var packed := Marshalls.base64_to_raw(text)
	var bytes := packed.decompress(SIZE * SIZE, FileAccess.COMPRESSION_DEFLATE) if packed else PackedByteArray()
	return bytes if bytes.size() == SIZE * SIZE else blank()
