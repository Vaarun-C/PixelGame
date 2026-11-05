class_name Journal
extends RefCounted

# The Wanderer's office book (lore: The Wanderer's book): his entries at story beats (journal.json),
# the roll of names and echoes at the back, and the player's margin notes. Saved apart from the bag,
# so it comes back with him after death. Entries keep the corruption they were written at.
# Entry: {kind: "his" | "margin" | "name" | "echo", text, corruption, beat?, verb?}
const SAVE_PATH := "user://journal.json"
const WHISPER := 0.75

static var lines := {}
static var entries := []
static var seen := {}
# -1 until the first frame of a scene, so a scene's starting corruption is not a crossing.
static var corruption := -1.0
# The prologue writes its own pages at its end; nothing else is written while it plays.
static var paused := false
static var loaded := false


static func load_saved() -> void:
	if loaded:
		return
	loaded = true
	lines = JSON.parse_string(FileAccess.get_file_as_string("res://scripts/game/journal.json"))
	var saved = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH)) if FileAccess.file_exists(SAVE_PATH) else null
	if saved is Dictionary:
		entries = saved.get("entries", [])
		seen = saved.get("seen", {})


static func save() -> void:
	FileAccess.open(SAVE_PATH, FileAccess.WRITE).store_string(JSON.stringify({"entries": entries, "seen": seen}))


static func add(entry: Dictionary) -> void:
	load_saved()
	entry.corruption = corruption
	entries.append(entry)
	save()


# A beat's entry, written once per `once` key. Repeated beats (a key per village) cycle the variants.
static func write(beat: String, once := beat, name := "") -> bool:
	load_saved()
	var variants: Array = lines.get(beat, [])
	if paused or seen.has(once) or variants.is_empty():
		return false
	seen[once] = true
	var n := entries.filter(func(e): return e.get("beat") == beat).size()
	add({"kind": "his", "beat": beat, "text": variants[n % variants.size()].format({"name": name})})
	return true


# beat + "_first" the first time, then beat itself; either way `once` is spent.
static func write_again(beat: String, once: String, name := "") -> void:
	if write(beat + "_first", beat + "_first", name):
		seen[once] = true
		save()
	else:
		write(beat, once, name)


static func echo(verb: String, text: String) -> void:
	add({"kind": "echo", "verb": verb, "text": text})


static func name_soul(name: String) -> void:
	add({"kind": "name", "text": name})


static func note(text: String) -> void:
	add({"kind": "margin", "text": text})


# Called each frame with the Wanderer's corruption; writes on crossing into the Whisper, out of it
# and into the Pull.
static func track(c: float) -> void:
	var was := corruption
	corruption = c
	if paused or was < 0 or was == c:
		return
	if c >= 1.0 and was < 1.0:
		write("pull")
	elif c >= WHISPER and was < WHISPER:
		write("whisper")
	elif c < WHISPER and was >= WHISPER:
		write("whisper_leave")
