class_name Decals

# Ground detail decals from art/props/decals_hd.png (tools/gen_decals_hd.py prints its row order).
# rows: one per variant. animated: plays the sheet's frames (tufts sway, embers flicker).
# tuft: grass-like, so it may also grow in front of a prop's base, using its short irregular
# base_rows there (tall even blades look like a comb stuck to the prop). Odds per ground: biomes.gd.
const SIZE := 32
const FEET := 28
const FRAMES := 4
# Same beat as the animated ground tiles (tools/build_tileset.gd FRAME_SECONDS).
const FRAME_MS := 250
# Tufts this far apart (Godot pixels) sway half a beat apart, so gusts roll across a field.
const WIND_WAVE := 160.0
const KINDS := {
	"grass_tuft": {"rows": [0, 1, 2], "base_rows": [1], "animated": true, "tuft": true},
	"dry_tuft": {"rows": [3, 4], "base_rows": [4], "animated": true, "tuft": true},
	"frost_tuft": {"rows": [5, 6], "base_rows": [6], "animated": true, "tuft": true},
	"burnt_tuft": {"rows": [7], "animated": true, "tuft": true},
	"reed_sprig": {"rows": [8], "animated": true, "tuft": true},
	"pebbles": {"rows": [9, 10, 11]},
	"frost_pebbles": {"rows": [12]},
	"twigs": {"rows": [13, 14]},
	"bone_chips": {"rows": [15, 16]},
	"blood_splat": {"rows": [17, 18]},
	"moss": {"rows": [19]},
	"mushrooms": {"rows": [20]},
	"straw": {"rows": [21]},
	"embers": {"rows": [22], "animated": true},
	"ash_pile": {"rows": [23]},
}

static var texture: Texture2D = load("res://art/props/decals_hd.png")


# A placed decal: {row, pos, phase}; phase -1 means it doesn't animate. at_base: tucked in front of a prop.
static func placed(kind: String, pick: int, at: Vector2, at_base := false) -> Dictionary:
	var def: Dictionary = KINDS[kind]
	var rows: Array = def.get("base_rows", def.rows) if at_base else def.rows
	var phase := -1
	if def.get("animated", false):
		phase = int(at.x / WIND_WAVE * 2) if def.get("tuft", false) else pick
	return {"row": rows[pick % rows.size()], "pos": at, "phase": phase}


static func frame_now() -> int:
	return Time.get_ticks_msec() / FRAME_MS


static func draw(canvas: CanvasItem, decal: Dictionary, offset := Vector2.ZERO) -> void:
	var frame: int = 0 if decal.phase < 0 else posmod(frame_now() + decal.phase, FRAMES)
	var at: Vector2 = decal.pos + offset - Vector2(SIZE / 2, FEET)
	canvas.draw_texture_rect_region(texture, Rect2(at, Vector2(SIZE, SIZE)), Rect2(frame * SIZE, decal.row * SIZE, SIZE, SIZE))
