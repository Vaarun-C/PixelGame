extends Node

# Colors by name from art/palette/master.gpl, the only colors the game may use (ART_RULES.md).
var colors := {}


func _init() -> void:
	for line in FileAccess.get_file_as_string("res://art/palette/master.gpl").split("\n"):
		var parts := line.replace("\t", " ").split(" ", false)
		if parts.size() == 4 and parts[0].is_valid_int():
			colors[parts[3]] = Color8(int(parts[0]), int(parts[1]), int(parts[2]))


func color(name: String) -> Color:
	return colors[name]
