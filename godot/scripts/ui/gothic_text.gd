class_name GothicText

# HUD lettering: Unifraktur Cook for titles, Grenze Gotisch for text, both OFL (art/fonts), imported
# with no anti-aliasing so they draw as hard-edged pixel fonts. Text gets a 1px void-0 outline.
const TITLE: FontFile = preload("res://art/fonts/UnifrakturCook-Bold.ttf")
const BODY: FontFile = preload("res://art/fonts/GrenzeGotisch.ttf")
const TITLE_SIZE := 28
const BODY_SIZE := 16
const SMALL_SIZE := 14
const AROUND := [Vector2(-1, -1), Vector2(0, -1), Vector2(1, -1), Vector2(-1, 0), Vector2(1, 0), Vector2(-1, 1), Vector2(0, 1), Vector2(1, 1)]


static func width(text: String, font := BODY, size := BODY_SIZE) -> float:
	return font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


static func height(font := BODY, size := BODY_SIZE) -> float:
	return font.get_ascent(size) + font.get_descent(size)


# at: the top-left of the text box. color: a palette name, or "" to draw the fill white (for a
# shader to colour, see the title ramp). alpha fades the whole line.
static func draw(canvas: CanvasItem, text: String, at: Vector2, color: String, font := BODY, size := BODY_SIZE, shadow := false, alpha := 1.0) -> void:
	var base := (at + Vector2(0, font.get_ascent(size))).round()
	var dark := Color(Palette.color("void-0"), alpha)
	if shadow:
		canvas.draw_string(font, base + Vector2(1, 2), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, dark)
	for offset in AROUND:
		canvas.draw_string(font, base + offset, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, dark)
	var fill := Color(1, 1, 1, alpha) if color.is_empty() else Color(Palette.color(color), alpha)
	canvas.draw_string(font, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, fill)


static func centred(canvas: CanvasItem, text: String, cx: float, y: float, color: String, font := BODY, size := BODY_SIZE, shadow := false, alpha := 1.0) -> void:
	draw(canvas, text, Vector2(floorf(cx - width(text, font, size) / 2), y), color, font, size, shadow, alpha)


# A gilt rule under a title: tapering arms and a small cross at the centre.
static func flourish(canvas: CanvasItem, cx: float, y: float, half: int) -> void:
	for i in half:
		var c := "gilt-2" if i < half * 0.6 else "gilt-1"
		UiDraw.rect(canvas, c, cx - 8 - i, y, 1, 1)
		UiDraw.rect(canvas, c, cx + 8 + i, y, 1, 1)
		if i < half * 0.3:
			UiDraw.rect(canvas, "gilt-0", cx - 8 - i, y + 1, 1, 1)
			UiDraw.rect(canvas, "gilt-0", cx + 8 + i, y + 1, 1, 1)
	UiDraw.rect(canvas, "void-0", cx - 1, y - 4, 3, 9)
	UiDraw.rect(canvas, "void-0", cx - 4, y - 1, 9, 3)
	UiDraw.rect(canvas, "gilt-3", cx, y - 3, 1, 7)
	UiDraw.rect(canvas, "gilt-3", cx - 3, y, 7, 1)
	UiDraw.rect(canvas, "bone-1", cx, y, 1, 1)
