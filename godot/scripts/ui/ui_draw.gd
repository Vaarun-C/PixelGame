class_name UiDraw

# Panel pieces from src/ui.js and src/inventory.js, drawn in whole pixels with palette names.
const RIVET_EVERY := 32
const CORNER := 16


static func rect(canvas: CanvasItem, color: String, x: float, y: float, w: float, h: float) -> void:
	canvas.draw_rect(Rect2(x, y, w, h), Palette.color(color))


static func bevel(canvas: CanvasItem, x: float, y: float, w: float, h: float, light: String, dark: String) -> void:
	rect(canvas, light, x, y, w, 1)
	rect(canvas, light, x, y, 1, h)
	rect(canvas, dark, x, y + h - 1, w, 1)
	rect(canvas, dark, x + w - 1, y, 1, h)


# The small HUD frame: dark iron with a lit top-left edge.
static func frame(canvas: CanvasItem, x: float, y: float, w: float, h: float) -> void:
	rect(canvas, "void-0", x - 1, y - 1, w + 2, h + 2)
	rect(canvas, "steel-1", x, y, w, h)
	rect(canvas, "steel-2", x, y, w - 1, 1)
	rect(canvas, "steel-2", x, y, 1, h - 1)
	rect(canvas, "void-1", x + 1, y + 1, w - 2, h - 2)


# A sunken panel or slot: dark fill with a bevel lit from the top-left.
static func inset(canvas: CanvasItem, x: float, y: float, w: float, h: float, fill: String) -> void:
	rect(canvas, fill, x, y, w, h)
	bevel(canvas, x, y, w, h, "void-0", "steel-1")


static func rule(canvas: CanvasItem, x: float, y: float, w: float) -> void:
	rect(canvas, "void-0", x, y, w, 1)
	rect(canvas, "steel-1", x, y + 1, w, 1)


static func outline(canvas: CanvasItem, color: String, x: float, y: float, w: float, h: float) -> void:
	rect(canvas, color, x, y, w, 1)
	rect(canvas, color, x, y + h - 1, w, 1)
	rect(canvas, color, x, y, 1, h)
	rect(canvas, color, x + w - 1, y, 1, h)


# Blackened iron band with rivets and gilt corner bosses, each holding a small bone skull.
static func iron_frame(canvas: CanvasItem, x: float, y: float, w: float, h: float) -> void:
	rect(canvas, "void-0", x - 2, y - 2, w + 4, h + 4)
	rect(canvas, "steel-0", x, y, w, h)
	bevel(canvas, x, y, w, h, "steel-2", "void-1")
	rect(canvas, "void-1", x + 6, y + 6, w - 12, h - 12)
	bevel(canvas, x + 6, y + 6, w - 12, h - 12, "void-0", "steel-1")
	for rx in range(int(x) + 24, int(x + w) - 20, RIVET_EVERY):
		for ry in [y + 2, y + h - 5]:
			rect(canvas, "ash-2", rx, ry, 2, 2)
			rect(canvas, "void-0", rx + 1, ry + 1, 1, 1)
	for corner in [Vector2(x, y), Vector2(x + w - CORNER, y), Vector2(x, y + h - CORNER), Vector2(x + w - CORNER, y + h - CORNER)]:
		corner_boss(canvas, corner.x, corner.y)


static func corner_boss(canvas: CanvasItem, x: float, y: float) -> void:
	rect(canvas, "gilt-0", x, y, CORNER, CORNER)
	bevel(canvas, x, y, CORNER, CORNER, "gilt-2", "void-0")
	rect(canvas, "gilt-1", x + 3, y + 3, 10, 10)
	rect(canvas, "bone-0", x + 5, y + 4, 6, 5)
	rect(canvas, "bone-0", x + 6, y + 9, 4, 2)
	rect(canvas, "bone-1", x + 5, y + 4, 6, 1)
	rect(canvas, "void-0", x + 6, y + 6, 1, 1)
	rect(canvas, "void-0", x + 9, y + 6, 1, 1)
	rect(canvas, "void-1", x + 7, y + 10, 2, 1)


static func disc(canvas: CanvasItem, color: String, cx: float, cy: float, r: int) -> void:
	for dy in range(-r, r + 1):
		var dx := floori(sqrt(r * r + r - dy * dy))
		rect(canvas, color, cx - dx, cy + dy, dx * 2 + 1, 1)


# A faceted gem in a rune tier's colours; dimmed tiers show only the dark facet.
static func tier_gem(canvas: CanvasItem, tier: String, cx: float, cy: float, lit: bool) -> void:
	for d in 5:
		rect(canvas, "void-0", cx - d - 1, cy - 5 + d, d * 2 + 3, 1)
		rect(canvas, "void-0", cx - d - 1, cy + 5 - d, d * 2 + 3, 1)
	for d in 4:
		rect(canvas, "rune-%s-%s" % [tier, "mid" if lit else "dark"], cx - d, cy - 4 + d, d * 2 + 1, 1)
		rect(canvas, "rune-%s-dark" % tier if lit else "void-3", cx - d, cy + 4 - d, d * 2 + 1, 1)
	if lit:
		rect(canvas, "rune-%s-core" % tier, cx - 1, cy - 2, 1, 1)


static func wrap(text: String, chars: int) -> Array:
	var lines := [""]
	for word in text.split(" "):
		var line: String = lines[-1]
		if line and line.length() + word.length() + 1 > chars:
			lines.append(word)
		else:
			lines[-1] = line + " " + word if line else word
	return lines
