class_name MapPanel
extends Node2D

# M: the fixed world as an inked parchment map (world/map.png, tools/build_map.gd) in the iron frame,
# centred on the Wanderer, each map pixel ZOOM screen pixels. Ground he hasn't seen (Fog) is blank
# parchment; villages, chapels and shrines are marked once seen. The Crimson prisoners never are.
const ZOOM := 2
const MARGIN := 40
const BORDER := 12
const BLANK := "leather-3"
const MARKED := ["village", "chapel", "shrine"]

var inventory: Inventory
var player: Node2D
var open := false
var sheet := Node2D.new()
var marks := Node2D.new()
var fog := ImageTexture.new()


func _ready() -> void:
	visible = false
	sheet.material = ShaderMaterial.new()
	sheet.material.shader = preload("res://shaders/map_fog.gdshader")
	sheet.material.set_shader_parameter("blank", Palette.color(BLANK))
	sheet.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sheet.draw.connect(draw_sheet)
	marks.draw.connect(draw_marks)
	add_child(sheet)
	add_child(marks)


func toggle() -> void:
	open = not open
	if open:
		fog.set_image(Image.create_from_data(Fog.SIZE, Fog.SIZE, false, Image.FORMAT_L8, inventory.explored))
		sheet.material.set_shader_parameter("fog", fog)


func _process(_dt: float) -> void:
	visible = open
	if open:
		queue_redraw()
		sheet.queue_redraw()
		marks.queue_redraw()


# The frame's outer rect and the map's top-left pixel showing at its inner corner.
func frame() -> Rect2:
	var screen := get_viewport().get_visible_rect().size
	var size := (screen - Vector2(MARGIN, MARGIN) * 2).min(Vector2.ONE * (WorldMap.SIZE / WorldMap.MAP_TILES * ZOOM + BORDER * 2))
	return Rect2(((screen - size) / 2).floor(), size.floor())


func inner() -> Rect2:
	return frame().grow(-BORDER)


func corner() -> Vector2:
	var view := (inner().size / ZOOM).floor()
	var at := Vector2(Terrain.tile_of(player.position)) / WorldMap.MAP_TILES - view / 2
	return at.clamp(Vector2.ZERO, Vector2.ONE * WorldMap.SIZE / WorldMap.MAP_TILES - view).floor()


func on_screen(tile: Vector2i) -> Vector2:
	return inner().position + ((Vector2(tile) / WorldMap.MAP_TILES - corner()) * ZOOM).floor()


func _draw() -> void:
	var f := frame()
	UiDraw.iron_frame(self, f.position.x, f.position.y, f.size.x, f.size.y)


func draw_sheet() -> void:
	var view := inner()
	var shown := (view.size / ZOOM).floor()
	sheet.draw_texture_rect_region(preload(WorldMap.MAP_PATH), Rect2(view.position, shown * ZOOM), Rect2(corner(), shown))


func draw_marks() -> void:
	var view := inner()
	for place in WorldMap.active.places():
		var at := on_screen(place.tile)
		if place.kind in MARKED and Fog.seen(inventory.explored, place.tile) and view.grow(-4).has_point(at):
			draw_place(place, at)
	var feet := on_screen(Terrain.tile_of(player.position))
	UiDraw.disc(marks, "void-1", feet.x, feet.y, 3)
	UiDraw.disc(marks, "blood-3", feet.x, feet.y, 2)
	GothicText.centred(marks, "The Wake", view.position.x + view.size.x / 2, view.position.y + 4, "bone-0", GothicText.TITLE, GothicText.TITLE_SIZE)


func draw_place(place: Dictionary, at: Vector2) -> void:
	if place.kind == "village":
		UiDraw.rect(marks, "void-1", at.x - 4, at.y - 4, 9, 9)
		UiDraw.rect(marks, "leather-2", at.x - 3, at.y - 3, 7, 7)
		# Inked straight on the parchment, without the HUD's outline.
		var font := GothicText.BODY
		var size := GothicText.SMALL_SIZE
		var left := floorf(at.x - GothicText.width(place.name, font, size) / 2)
		marks.draw_string(font, Vector2(left, at.y + 6 + font.get_ascent(size)).round(), place.name, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Palette.color("leather-0"))
		return
	var arm := 4 if place.kind == "chapel" else 3
	UiDraw.rect(marks, "leather-0", at.x, at.y - arm, 1, arm * 2 + 1)
	UiDraw.rect(marks, "leather-0", at.x - arm + 1, at.y - arm + 2, arm * 2 - 1, 1)
