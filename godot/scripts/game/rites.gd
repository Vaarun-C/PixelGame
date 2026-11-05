class_name Rites

# The six rites (lore: The six rites). Every village has the three places: its ledger, its fire and
# its road shrine, each with a good god's rite and the dark rite that looks like the kind option.
# A soul goes free only at Wend's road, once the parts of its death it missed (Rites.needs) are
# finished in order. Dark rites consume the soul and cost corruption; only Wend's lowers it.
const PLACES := {
	"ledger": [
		{"god": "Ennick", "words": "Write his name", "need": "name", "done": "Written: %s."},
		{"god": "Hush", "words": "Scrape his name", "dark": "The name goes out of the ledger."},
	],
	"firepit": [
		{"god": "Gled", "words": "Give him to the fire", "need": "fire", "done": "He lets go of what he held."},
		{"god": "Grudge", "words": "Bank the coal", "dark": "The coal takes him. Past the wall, something gets up."},
	],
	"wayside_shrine": [
		{"god": "Wend", "words": "Leave him by the road", "need": "road", "done": "He walks on."},
		{"god": "Mortmain", "words": "Lay him in the niche", "whisper": "Keep him safe", "dark": "The grate shuts. He stays."},
	],
}
const NOT_DUE := {"name": "His name is already kept.", "fire": "He holds onto nothing.", "road": "He would not go."}


static func needs(id: int) -> Array:
	return RuneBook.NEEDS[(id >> 4) % RuneBook.NEEDS.size()] + ["road"]


# done: how many of each soul's needs are finished, by soul id (the bag's rites ledger).
static func next_need(id: int, done: Dictionary) -> String:
	var list := needs(id)
	return list[mini(int(done.get(str(id), 0)), list.size() - 1)]


# The rite's words as he reads them: the dark words read kinder in the Whisper.
static func words(rite: Dictionary, corruption: float) -> String:
	return rite.get("whisper", rite.words) if corruption >= Journal.WHISPER else rite.words


# At the Pull a good rite is said kneeling, and the withdrawal costs blood (lore: Corruption).
static func kneels(rite: Dictionary, corruption: float) -> bool:
	return not rite.has("dark") and corruption >= 1.0


# Gives the stone `key` from the bag to a rite. Returns [message, whether the stone is gone].
static func perform(rite: Dictionary, key: String, inventory: Inventory, p) -> Array:
	var info := Items.info(key)
	if info.tier == RuneBook.CRIMSON:
		return ["No rite reaches a Crimson stone.", false]
	if rite.has("dark"):
		inventory.remove(key, 1)
		p.corruption = minf(1.0, p.corruption + RuneBook.DARK_RITE_CORRUPTION[info.tier - 1])
		Journal.write("rite_" + rite.god.to_lower())
		return [rite.dark, true]
	if info.souls.any(func(s): return not s.read):
		return ["You don't know him yet. Read the stone first.", false]
	var due: Array = info.souls.filter(func(s): return next_need(s.id, inventory.rites) == rite.need)
	if due.is_empty() or rite.need == "road" and due.size() < info.souls.size():
		return [NOT_DUE[rite.need], false]
	if kneels(rite, p.corruption):
		p.hp = maxf(1, p.hp - RuneBook.KNEEL_BLOOD)
	Journal.write("rite_" + rite.god.to_lower())
	if rite.need == "road":
		inventory.remove(key, 1)
		p.corruption = maxf(0.0, p.corruption - RuneBook.FREE_CORRUPTION[info.tier - 1])
		return [rite.done, true]
	var names := []
	for s in due:
		inventory.rites[str(s.id)] = int(inventory.rites.get(str(s.id), 0)) + 1
		if rite.need == "name":
			names.append(Villages.villager_name(s.id))
			Journal.name_soul(names[-1])
	inventory.save()
	return [rite.done % " and ".join(names) if names else rite.done, false]
