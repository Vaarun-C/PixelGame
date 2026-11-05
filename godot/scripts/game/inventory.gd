class_name Inventory
extends RefCounted

# The bag and the rune sockets (src/inventory.js), saved between runs. Slots hold {key, count} or null.
# selected: bag index shown in the panel's detail; fusing: waiting for a second rune to fuse with.
const COLS := 6
const ROWS := 4
const SAVE_PATH := "user://inventory.json"

var slots := []
var sockets := Runes.empty_sockets()
# Uses toward reading each soul not yet read, by soul id (Runes.practise).
var reading := {}
# How many of each soul's needs the rites have finished, by soul id (Rites.next_need).
var rites := {}
# Levels the smith has hammered into his gear (Smith).
var forged := {"strength": 0, "armor": 0}
var selected := -1
var fusing := false
var open := false
# The game builds more than one Inventory; the playtest bag is handed out once per launch.
static var rune_bag_given := false


func _init() -> void:
	slots.resize(COLS * ROWS)
	load_saved()
	# Playtesting runes: godot --path godot -- --rune-bag
	if "--rune-bag" in OS.get_cmdline_user_args() and not rune_bag_given:
		rune_bag_given = true
		for verb in RuneBook.ORDER:
			add(Items.rune_key([verb], 2, 0, Items.new_souls([verb])), 1)
		add("shard", 200)


func load_saved() -> void:
	var saved = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH)) if FileAccess.file_exists(SAVE_PATH) else null
	if not saved is Dictionary:
		return
	# Items that no longer exist are dropped; everything else is kept.
	var bag: Array = saved.get("slots", [])
	if bag.size() == slots.size():
		for i in bag.size():
			var slot = bag[i]
			slots[i] = {"key": slot.key, "count": int(slot.count)} if slot is Dictionary and Items.info(slot.key) and slot.count > 0 else null
	for part in Runes.SOCKETS:
		var held: Array = saved.get("sockets", {}).get(part, [])
		for i in mini(held.size(), sockets[part].size()):
			var key = held[i]
			sockets[part][i] = key if key is String and lashable(key) and Runes.fits(key, part) else null
	var ledger = saved.get("reading", {})
	reading = ledger if ledger is Dictionary else {}
	var finished = saved.get("rites", {})
	rites = finished if finished is Dictionary else {}
	var gear = saved.get("forged", {})
	for stat in forged:
		forged[stat] = clampi(int(gear.get(stat, 0)), 0, Smith.MAX[stat]) if gear is Dictionary else 0


func save() -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify({"slots": slots, "sockets": sockets, "reading": reading, "rites": rites, "forged": forged}))


# Returns how many didn't fit.
func add(key: String, count: int) -> int:
	var stack: int = Items.info(key).stack
	if Items.info(key).get("tier", 0) == RuneBook.CRIMSON:
		Journal.write("crimson_first")
	for slot in slots:
		if slot and slot.key == key:
			var n := mini(count, stack - slot.count)
			slot.count += n
			count -= n
	for i in slots.size():
		if count <= 0:
			break
		if not slots[i]:
			var n := mini(count, stack)
			slots[i] = {"key": key, "count": n}
			count -= n
	save()
	return count


func count_of(key: String) -> int:
	return slots.reduce(func(sum, slot): return sum + (slot.count if slot and slot.key == key else 0), 0)


# Removes up to `count`; returns how many were removed.
func remove(key: String, count: int) -> int:
	var removed := 0
	for i in slots.size():
		var slot = slots[i]
		if not slot or slot.key != key or removed == count:
			continue
		var n := mini(slot.count, count - removed)
		slot.count -= n
		removed += n
		if not slot.count:
			slots[i] = null
	save()
	return removed


# One more use toward reading soul `id`; returns the count so far.
func practise(id: int) -> int:
	reading[str(id)] = reading.get(str(id), 0) + 1
	return reading[str(id)]


static func is_rune(slot) -> bool:
	return slot != null and Items.info(slot.key).has("types")


static func lashable(key: String) -> bool:
	return key == Items.EMPTY_STONE or Items.info(key).has("types")


# The selected bag item if it can be lashed (a rune or an empty stone), else "".
func selected_lashable() -> String:
	return slots[selected].key if selected >= 0 and slots[selected] and lashable(slots[selected].key) else ""


func selected_rune() -> String:
	return slots[selected].key if selected >= 0 and is_rune(slots[selected]) else ""


func deselect() -> void:
	selected = -1
	fusing = false


# Clicks from the panel. Each returns a message to show, or "".
func click_bag(i: int) -> String:
	if fusing and i != selected:
		return fuse(i)
	selected = -1 if selected == i or not slots[i] else i
	fusing = false
	return ""


func click_socket(part: String, i: int) -> String:
	var current = sockets[part][i]
	var key := selected_lashable()
	if key:
		if not Runes.fits(key, part):
			return "%s won't sit in the %s." % [Items.info(key).name, part]
		var left: int = slots[selected].count - 1
		var free := slots.find(null)
		if left and current and free < 0:
			return "Bag is full."
		slots[selected] = {"key": key, "count": left} if left else {"key": current, "count": 1} if current else null
		if left and current:
			slots[free] = {"key": current, "count": 1}
		sockets[part][i] = key
		deselect()
	elif current:
		var free := slots.find(null)
		if free < 0:
			return "Bag is full."
		slots[free] = {"key": current, "count": 1}
		sockets[part][i] = null
	save()
	return ""


func carve() -> String:
	var key := selected_rune()
	var notches: int = Items.info(key).notches
	if notches >= Runes.MAX_NOTCHES:
		return "No room for another notch."
	var cost := Runes.carve_cost(key)
	if count_of("shard") < cost:
		return "Carving needs %d shards." % cost
	remove("shard", cost)
	slots[selected] = {"key": Runes.carved(key), "count": 1}
	save()
	Journal.write("carve_first")
	return "Notch %d carved." % (notches + 1)


func toggle_fusing() -> String:
	var info := Items.info(selected_rune())
	if info.tier == RuneBook.CRIMSON:
		return "There's no room in a Crimson stone."
	if info.types.size() > 1:
		return "Two souls already share that stone."
	fusing = not fusing
	return ""


func fuse(i: int) -> String:
	var a := selected_rune()
	var b: String = slots[i].key if is_rune(slots[i]) else ""
	if not b:
		return "Pick a rune to fuse with."
	var error := Runes.fuse_error(a, b)
	if error:
		return error
	var cost := Runes.fuse_cost(a, b)
	if count_of("shard") < cost:
		return "Fusing needs %d shards." % cost
	var key := Runes.fused(a, b)
	slots[i] = null
	slots[selected] = {"key": key, "count": 1}
	remove("shard", cost)
	fusing = false
	selected = slots.find_custom(func(s): return s and s.key == key)
	save()
	Journal.write("fuse_first")
	return "Fused: %s." % Items.info(key).name
