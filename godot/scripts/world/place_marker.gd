@tool
class_name PlaceMarker
extends Node2D

# A named place in world/places.tscn: a village (its centre tile), a shrine, a chapel, a Crimson
# prisoner and so on. WorldMap.places() lists them; the editor shows a pin and the name.
@export var kind := "village"
@export var place_name := ""
@export var start := false

# Autoloads don't run in the editor, so the marker keeps its own copy of the palette.
static var palette: Node


func _draw() -> void:
	if not Engine.is_editor_hint():
		return
	if not palette:
		palette = preload("res://scripts/palette.gd").new()
	draw_circle(Vector2.ZERO, 24, palette.color("gilt-2"))
	draw_string(ThemeDB.fallback_font, Vector2(30, 8), "%s (%s)" % [place_name, kind], HORIZONTAL_ALIGNMENT_LEFT, -1, 48, palette.color("bone-1"))
