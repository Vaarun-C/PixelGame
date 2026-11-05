@tool
class_name PropMarker
extends Node2D

# A prop placed in a region scene (world/regions). WorldMap reads kind and variant as data; the game
# builds the real Prop when its chunk loads. In the editor it shows the prop's sprite, feet on the node.
@export var kind := "":
	set(value):
		kind = value
		queue_redraw()
@export var variant := 0:
	set(value):
		variant = value
		queue_redraw()


func _draw() -> void:
	if not Engine.is_editor_hint() or not Props.LIST.has(kind):
		return
	var def: Dictionary = Props.LIST[kind]
	var texture: Texture2D = load("res://art/props/%s.png" % def.sheet)
	var size: int = def.size
	var scale: float = def.get("scale", 1.0) * Terrain.SCALE
	var feet := Vector2(size / 2, def.get("feet", size - 4)) * scale
	draw_texture_rect_region(texture, Rect2(-feet, Vector2(size, size) * scale), Rect2(variant * size, 0, size, size))
