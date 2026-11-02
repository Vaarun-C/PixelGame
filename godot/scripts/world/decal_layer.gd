extends Node2D

# One chunk's ground decals, drawn flat under everything that stands (z -2: below bodies and
# other flat props). Redraws only when the animation frame changes, and only if something animates.
var decals := []
var animated := false
var shown_frame := -1


func _init(list: Array) -> void:
	decals = list
	animated = decals.any(func(d): return d.phase >= 0)
	z_index = -2


func _ready() -> void:
	set_process(animated)


func _process(_dt: float) -> void:
	if Decals.frame_now() != shown_frame:
		shown_frame = Decals.frame_now()
		queue_redraw()


func _draw() -> void:
	for decal in decals:
		Decals.draw(self, decal)
