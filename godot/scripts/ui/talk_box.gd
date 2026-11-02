extends LineEdit

# The line the Wanderer types a question into while speaking with a villager: a dark plate with a
# gilt edge at the bottom of the screen. Enter asks, Esc leaves.
const WIDTH := 420
const FROM_BOTTOM := 64


func _ready() -> void:
	visible = false
	max_length = 200
	placeholder_text = "Speak. Esc to leave."
	add_theme_font_override("font", GothicText.BODY)
	add_theme_font_size_override("font_size", GothicText.BODY_SIZE)
	add_theme_color_override("font_color", Palette.color("bone-0"))
	add_theme_color_override("font_placeholder_color", Palette.color("ash-3"))
	add_theme_color_override("caret_color", Palette.color("gilt-2"))
	add_theme_color_override("selection_color", Palette.color("void-0"))
	var plate := StyleBoxFlat.new()
	plate.bg_color = Palette.color("void-1")
	plate.border_color = Palette.color("gilt-1")
	plate.set_border_width_all(1)
	plate.set_content_margin_all(6)
	for style in ["normal", "focus", "read_only"]:
		add_theme_stylebox_override(style, plate)
	size = Vector2(WIDTH, 0)


func open(screen: Vector2) -> void:
	position = Vector2(floorf((screen.x - WIDTH) / 2), screen.y - FROM_BOTTOM)
	visible = true
	clear()
	grab_focus()


func close() -> void:
	visible = false
	release_focus()
