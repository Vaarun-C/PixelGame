extends "res://scripts/hollow.gd"

# The Misborn (lore: Hollows): a man's loose soul in a dead warhorse, forced upright. Heavy: only a
# hard blow, a knockdown or Still staggers it, and it picks its blow by reach. Its sheets face south
# only for now, so it faces the camera whichever way it goes.
const MISBORN := {"hp": 90.0, "aggro": 320.0, "leash": 700.0, "stagger": 0.2, "knockdown": 0.9, "dying": 1.0, "bar": -64}
const POISE := 12.0
const BITE := {
	"sheet": "bite", "frames": 13, "impact": 6, "range": 60.0,
	"windup": 0.35, "strike": 0.12, "recover": 0.5, "lunge": 120.0, "damage": 10.0, "arc": 1.0,
}
const FLAIL := {
	"sheet": "flail", "frames": 14, "impact": 7, "range": 84.0,
	"windup": 0.5, "strike": 0.14, "recover": 0.6, "lunge": 160.0, "damage": 14.0, "arc": 1.3,
}
# The long ember-lit wind-up and slow recovery are the opening.
const HAMMER := {
	"sheet": "hammer", "frames": 8, "impact": 5, "range": 80.0,
	"windup": 0.9, "strike": 0.16, "recover": 1.1, "lunge": 200.0, "damage": 25.0, "arc": 1.4,
}
# Out of bite reach, the chance it rears for the hammer instead of the flail.
const HAMMER_ODDS := 0.4


func _ready() -> void:
	var dir := "res://art/enemies/misborn_hd/misborn_hd_%s.png"
	sheets = {
		"idle": sheet_entry(dir % "idle", Vector2i(128, 128), 1),
		"walk": sheet_entry(dir % "walk", Vector2i(128, 128), 1),
		"hammer": sheet_entry(dir % "hammer", Vector2i(160, 160), 1),
		"flail": sheet_entry(dir % "flail", Vector2i(160, 160), 1),
		"bite": sheet_entry(dir % "bite", Vector2i(160, 160), 1),
		"death": sheet_entry(dir % "death", Vector2i(160, 160), 1),
	}
	stats = MISBORN
	body_kind = "misborn_body"
	super._ready()


func staggered_by(damage: float, knockdown: bool) -> bool:
	return knockdown or damage >= POISE


func pick_move(dist: float) -> Dictionary:
	if dist < BITE.range:
		return BITE
	if dist < FLAIL.range:
		return HAMMER if randf() < HAMMER_ODDS else FLAIL
	return {}
