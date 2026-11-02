class_name PixelImage
extends RefCounted

# Paints pixel art into an Image by palette name, for HUD pieces that are redrawn as one texture.
var image: Image


func _init(size: Vector2i) -> void:
	image = Image.create_empty(size.x, size.y, false, Image.FORMAT_RGBA8)


func clear() -> void:
	image.fill(Color(0, 0, 0, 0))


func dot(x: int, y: int, color: String) -> void:
	if x >= 0 and y >= 0 and x < image.get_width() and y < image.get_height():
		image.set_pixel(x, y, Palette.color(color))


func rect(x: int, y: int, w: int, h: int, color: String) -> void:
	if w > 0 and h > 0:
		image.fill_rect(Rect2i(x, y, w, h), Palette.color(color))


func disc(cx: int, cy: int, r: int, color: String) -> void:
	for dy in range(-r, r + 1):
		var dx := int(sqrt(maxf(0, r * r + r - dy * dy)))
		rect(cx - dx, cy + dy, dx * 2 + 1, 1, color)


# A 1px ring around a set of points (Vector2i keys).
func outline(points: Dictionary, color := "void-0") -> void:
	for p in points:
		for step in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.DOWN, Vector2i.UP]:
			if not points.has(p + step):
				dot(p.x + step.x, p.y + step.y, color)


func texture() -> ImageTexture:
	return ImageTexture.create_from_image(image)
