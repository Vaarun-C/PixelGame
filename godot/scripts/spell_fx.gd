class_name SpellFx
extends Node2D

# A spoken rune's effect (art/vfx/spell_<verb>_hd.png, built by art/drafts/spells/build.py): row 0
# plays under the characters, row 1 over them, both on the caster's feet where the spell went off.
# The sheet's Pale glow takes the uttered stone's tier.
const FPS := 12.0
const STAGE := Vector2i(320, 256)
const FEET := Vector2(160, 176)
const SWAP := preload("res://shaders/tier_swap.gdshader")
const RAMP := ["dark", "mid", "core"]

var t := 0.0
var frames := 1
var layers: Array[Sprite2D] = []


static func path(verb: String) -> String:
	return "res://art/vfx/spell_%s_hd.png" % verb


# Plays the verb's effect at `at`; false if it has none.
static func play(parent: Node, at: Vector2, verb: String, tier: String) -> bool:
	if not ResourceLoader.exists(path(verb)):
		return false
	var fx := SpellFx.new()
	fx.position = at
	var texture: Texture2D = load(path(verb))
	fx.frames = texture.get_width() / STAGE.x
	var swap := ShaderMaterial.new()
	swap.shader = SWAP
	for shade in RAMP:
		swap.set_shader_parameter("from_" + shade, Palette.color("rune-pale-" + shade))
		swap.set_shader_parameter("to_" + shade, Palette.color("rune-%s-%s" % [tier, shade]))
	for row in 2:
		var layer := Sprite2D.new()
		layer.texture = texture
		layer.hframes = fx.frames
		layer.vframes = 2
		layer.frame = row * fx.frames
		layer.centered = false
		layer.offset = -FEET
		layer.material = swap
		layer.z_index = -1 if row == 0 else 1
		fx.add_child(layer)
		fx.layers.append(layer)
	parent.add_child(fx)
	return true


func _process(dt: float) -> void:
	t += dt
	var frame := floori(t * FPS)
	if frame >= frames:
		queue_free()
		return
	for row in layers.size():
		layers[row].frame = row * frames + frame
