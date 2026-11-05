extends "res://scripts/hollow.gd"

# The Stammerer (lore: Hollows): the corpse of an old reader of souls, rune stones nailed into his
# body. He keeps his distance and stammers a stone's name; hit him mid-word and it chokes. Finished,
# the word lands where you stood when he began it, as a weak spell, the stone burns and its hatred
# rises beside him. His sheets face south only for now.
const STAMMERER := {"hp": 55.0, "aggro": 320.0, "leash": 660.0, "stagger": 0.28, "knockdown": 0.9, "dying": 0.96, "bar": -46}
const KEEP := [140.0, 200.0]
const WORD := 1.4
const RELEASE := 0.5
const CHOKE := 0.9
const REST := 3.0
const STONES := [3, 5]
const VERBS := ["rend", "break", "sting"]
# His word hits at this share of a Pale stone's spell, within this share of its reach.
const WEAK := 0.5
# Cast sheet frames: the hands rise and the jaw stammers through the word, then the release.
const WORD_FRAMES := 15
const RELEASE_FRAMES := 6
const CHOKE_FRAMES := 9

var stones := 0
var rest := 0.0
var verb := ""
var spot := Vector2.ZERO
# What he is saying, drawn over his head like the Wanderer's shout (interface.gd).
var shout := ""


func _ready() -> void:
	var dir := "res://art/enemies/stammerer_hd/stammerer_hd_%s.png"
	sheets = {
		"idle": sheet_entry(dir % "idle", Vector2i(96, 96), 1),
		"walk": sheet_entry(dir % "walk", Vector2i(96, 96), 1),
		"cast": sheet_entry(dir % "cast", Vector2i(96, 96), 1, 1),
		"choke": sheet_entry(dir % "choke", Vector2i(96, 96), 1, 1),
		"death": sheet_entry(dir % "death", Vector2i(96, 96), 1, 1),
	}
	anims = {"idle": {"frames": 4, "ms": 200}, "walk": {"frames": 7, "ms": 130}}
	stats = STAMMERER
	body_kind = "stammerer_body"
	stones = randi_range(STONES[0], STONES[1])
	super._ready()


func take_damage(damage: float, angle: float, knock: float, knockdown: bool) -> void:
	var stammering := state == "stammer"
	super.take_damage(damage, angle, knock, knockdown)
	if stammering and damage > 0 and dying <= 0:
		choke()


func hold(time: float) -> void:
	if state == "stammer":
		choke()
	super.hold(time)


# The word breaks off in his throat; the stone isn't spent. The choke plays instead of a stagger.
func choke() -> void:
	state = "choke"
	t = 0.0
	stagger = 0.0


func think(dt: float) -> Vector2:
	if stagger > 0 or state == "wander":
		return super.think(dt)
	t += dt
	var to_player: Vector2 = player.position - position
	var dist := to_player.length()
	match state:
		"stammer":
			if t >= WORD:
				speak()
				state = "release"
				t = 0.0
		"release", "choke":
			if t >= (RELEASE if state == "release" else CHOKE):
				state = "chase"
				rest = REST
		_:
			if dist > stats.leash or player_safe():
				state = "wander"
				return Vector2.ZERO
			rest -= dt
			# Out of stones he only keeps his distance: what he becomes then isn't decided yet.
			if stones > 0 and rest <= 0 and dist < KEEP[1] + 40:
				state = "stammer"
				t = 0.0
				verb = VERBS.pick_random()
				spot = player.position
				return Vector2.ZERO
			if dist < KEEP[0]:
				return -to_player.normalized()
			if dist > KEEP[1]:
				return to_player.normalized()
	return Vector2.ZERO


func speak() -> void:
	var spell: Dictionary = RuneBook.SPELLS[verb]
	SpellFx.play(get_parent(), spot, verb, "pale")
	Effects.shake(4)
	var to: Vector2 = player.position - spot
	if to.length() < spell.radius * WEAK:
		player.hurt(spell.tiers[0] * WEAK, to.angle(), self)
	Utter.raise_hatred(self, 1)
	stones -= 1


# The name comes out in pieces as the word goes on ("R-", "R- R-", "R- R- Re-"), whole once it
# lands, and strangled when he chokes.
func say_word() -> String:
	var word := verb[0].to_upper() + verb.substr(1)
	var pieces := [word[0] + "-", word[0] + "-", word.substr(0, 2) + "-"]
	match state:
		"stammer":
			return " ".join(pieces.slice(0, mini(pieces.size(), floori(t / WORD * pieces.size()) + 1)))
		"release":
			return word + "!"
		"choke":
			return pieces[0] + " kkh"
	return ""


func update_sprite() -> void:
	shout = say_word() if dying <= 0 and verb else ""
	if dying > 0 or rising > 0 or state not in ["stammer", "release", "choke"]:
		super.update_sprite()
		return
	set_tint("bone-1", 1.0 if flash > 0 else 0.0)
	# ART_RULES §7: his word is the telegraph, heating from ember-2 to ember-3 as it nears its end.
	set_outline("ember-3" if t > WORD * TELEGRAPH_HOT else "ember-2", 1.0 if state == "stammer" and flash <= 0 else 0.0)
	match state:
		"stammer":
			show_frame("cast", mini(WORD_FRAMES - 1, floori(t / WORD * WORD_FRAMES)), recoil)
		"release":
			show_frame("cast", WORD_FRAMES + mini(RELEASE_FRAMES - 1, floori(t / RELEASE * RELEASE_FRAMES)), recoil)
		_:
			show_frame("choke", mini(CHOKE_FRAMES - 1, floori(t / CHOKE * CHOKE_FRAMES)), recoil)
