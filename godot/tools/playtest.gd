extends SceneTree

# Scripted playtest: runs the game with a fixed seed, plays a list of steps, saves screenshots and
# logs the game state at each one. Run windowed (headless doesn't render):
#   godot --path godot --script tools/playtest.gd -- --seed 7 --biome 0 --out DIR \
#     --steps "wait:1 shot:start hold:d+shift:1.5 shot:ran click:800:270 record:swing:0.6:2"
# Steps:
#   wait:S                 let the game run S seconds
#   shot:NAME              save NAME.png and log the state
#   record:NAME:S:N        save every Nth frame for S seconds as NAME_000.png, NAME_001.png, ...
#   hold:KEYS:S            hold keys for S seconds; KEYS joined by +, from w a s d up down left right shift
#   click:X:Y              aim at screen pixel X,Y and left click (swing)
#   aim:X:Y                move the mouse to screen pixel X,Y
#   dodge                  tap Space
#   teleport:X:Y           move the player to world pixel X,Y
#   hollow:DX:DY           spawn a Hollow at an offset from the player, already chasing
#   misborn:DX:DY          the same for a Misborn; stammerer:DX:DY for a Stammerer
#   kill                   finish off the nearest living enemy (to see its death and body)
#   hurt:DAMAGE            hit the player from the right
#   zoom:STEPS             zoom the camera in (positive) or out (negative) by whole steps
#   tap:KEY                press and release a key: e i c b n m tab escape space shift 1-5
#   give:ITEM:COUNT        put items in the bag, e.g. give:rune_rend_3:1 give:shard:30
#   lash:ITEM:PART:I       put a rune straight into a socket, e.g. lash:rune_break_2:blade:0
#   lootable               stand just below the nearest lootable prop that still has loot
#   rite:KIND              stand just below the nearest rite place of a kind: ledger firepit wayside_shrine
#   village:DX:DY          teleport to the nearest village's centre plus an offset (world px)
#   place:NAME:DX:DY       teleport to a fixed-map place (world/places.tscn) plus an offset, e.g.
#                          place:Court_Chapel:0:200 (underscores for spaces, any case)
#   corruption:C           set the player's corruption, 0..1 (0.75 the Whisper, 1 the Pull)
# --scene: the scene to play, default res://scenes/main.tscn (res://scenes/prologue.tscn for the prologue).
# --biome: 0 = normal mix, 1-5 = one wild biome everywhere (see World.biome).
const KEYS := {
	"w": KEY_W, "a": KEY_A, "s": KEY_S, "d": KEY_D, "shift": KEY_SHIFT,
	"up": KEY_UP, "down": KEY_DOWN, "left": KEY_LEFT, "right": KEY_RIGHT,
	"e": KEY_E, "i": KEY_I, "c": KEY_C, "b": KEY_B, "n": KEY_N, "m": KEY_M, "tab": KEY_TAB, "escape": KEY_ESCAPE, "space": KEY_SPACE,
	"1": KEY_1, "2": KEY_2, "3": KEY_3, "4": KEY_4, "5": KEY_5,
}

const VIEW := Vector2i(960, 540)

var out := ""
var main: Node
var player: Node


func _initialize() -> void:
	var args := parse_args(OS.get_cmdline_user_args())
	out = args.get("out", OS.get_user_data_dir() + "/playtest")
	DirAccess.make_dir_recursive_absolute(out)
	seed(int(args.get("seed", "1")))
	# The game starts fullscreen; screenshots need the fixed 960x540 view. On macOS leaving
	# fullscreen lands in maximized, which ignores resizes, so keep asking until the size sticks.
	for i in 120:
		if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_WINDOWED:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		else:
			DisplayServer.window_set_size(VIEW * DisplayServer.screen_get_scale())
		await process_frame
		if Vector2i(root.get_texture().get_size()) == VIEW:
			break
	main = load(args.get("scene", "res://scenes/main.tscn")).instantiate()
	if args.has("biome"):
		main.get_node("World").biome = int(args.biome)
	root.add_child(main)
	current_scene = main
	player = main.get_node("Player")
	for step in args.get("steps", "wait:1 shot:start").split(" ", false):
		await run(step.split(":"))
	quit()


func parse_args(list: PackedStringArray) -> Dictionary:
	var args := {}
	for i in range(0, list.size() - 1, 2):
		args[list[i].trim_prefix("--")] = list[i + 1]
	return args


func run(step: PackedStringArray) -> void:
	match step[0]:
		"wait":
			await wait(float(step[1]))
		"shot":
			await save(step[1])
		"record":
			var frames := int(float(step[2]) * Engine.get_frames_per_second())
			for i in frames:
				await process_frame
				if i % int(step[3]) == 0:
					await save("%s_%03d" % [step[1], i / int(step[3])], false)
		"hold":
			var keys := Array(step[1].split("+")).map(func(k): return KEYS[k])
			for k in keys:
				key(k, true)
			await wait(float(step[2]))
			for k in keys:
				key(k, false)
		"click":
			root.warp_mouse(Vector2(float(step[1]), float(step[2])))
			var click := InputEventMouseButton.new()
			click.button_index = MOUSE_BUTTON_LEFT
			click.pressed = true
			click.position = Vector2(float(step[1]), float(step[2]))
			Input.parse_input_event(click)
			await physics_frame
		"aim":
			root.warp_mouse(Vector2(float(step[1]), float(step[2])))
		"dodge":
			key(KEY_SPACE, true)
			await physics_frame
			await physics_frame
			key(KEY_SPACE, false)
		"teleport":
			player.position = Vector2(float(step[1]), float(step[2]))
			player.velocity = Vector2.ZERO
		"hollow", "misborn", "stammerer":
			var hollow = load("res://scenes/%s.tscn" % step[0]).instantiate()
			hollow.position = player.position + Vector2(float(step[1]), float(step[2]))
			main.add_child(hollow)
			hollow.state = "chase"
		"kill":
			var foes: Array = get_nodes_in_group("enemies").filter(func(e): return e.dying <= 0)
			foes.sort_custom(func(a, b): return a.position.distance_to(player.position) < b.position.distance_to(player.position))
			if foes:
				foes[0].take_damage(foes[0].hp, 0.0, 0.0, false)
		"hurt":
			player.hurt(float(step[1]), PI)
		"zoom":
			main.zoom_by(int(step[1]))
		"corruption":
			player.corruption = float(step[1])
		"tap":
			key(KEYS[step[1]], true)
			await physics_frame
			key(KEYS[step[1]], false)
			await process_frame
		"give":
			main.get_node("Interface").inventory.add(step[1], int(step[2]))
		"lash":
			main.get_node("Interface").inventory.sockets[step[2]][int(step[3])] = step[1]
		"lootable":
			var world = main.get_node("World")
			var props := get_nodes_in_group("lootables").filter(func(p): return world.has_loot(p))
			props.sort_custom(func(a, b): return a.position.distance_to(player.position) < b.position.distance_to(player.position))
			if props:
				player.position = props[0].position + Vector2(0, 12)
				player.velocity = Vector2.ZERO
		"rite":
			var places := get_nodes_in_group("rite_places").filter(func(p): return p.def_kind == step[1])
			places.sort_custom(func(a, b): return a.position.distance_to(player.position) < b.position.distance_to(player.position))
			if places:
				player.position = places[0].position + Vector2(0, 14)
				player.velocity = Vector2.ZERO
		"place":
			var wanted := step[1].replace("_", " ").to_lower()
			var found: Array = WorldMap.active.places().filter(func(p): return p.name.to_lower() == wanted) if WorldMap.active else []
			if found:
				player.position = (Vector2(found[0].tile) * 32 + Vector2(16, 16)) * 2 + Vector2(float(step[2]), float(step[3]))
				player.velocity = Vector2.ZERO
			else:
				push_error("no place " + step[1])
		"village":
			if WorldMap.active:
				var all := Villages.authored().duplicate()
				all.sort_custom(func(a, b): return Vector2(a.tx, a.ty).distance_to(player.position / 64) < Vector2(b.tx, b.ty).distance_to(player.position / 64))
				player.position = Vector2(all[0].tx * 32 + 16, all[0].ty * 32 + 16) * 2 + Vector2(float(step[1]), float(step[2]))
				return
			for r in 12:
				var found := false
				for cy in range(-r, r + 1):
					for cx in range(-r, r + 1):
						var c := Villages.centre_in(Terrain.world_seed, cx, cy)
						if c and not found:
							player.position = Vector2(c.tx * 32 + 16, c.ty * 32 + 16) * 2 + Vector2(float(step[1]), float(step[2]))
							found = true
				if found:
					break
		_:
			push_error("unknown step " + step[0])


func key(code: Key, down: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = code
	event.pressed = down
	Input.parse_input_event(event)


func wait(seconds: float) -> void:
	await create_timer(seconds, true, false, true).timeout


func save(name: String, log_state := true) -> void:
	await process_frame
	root.get_texture().get_image().save_png("%s/%s.png" % [out, name])
	if log_state:
		print(name, " | ", state())


func state() -> String:
	var hollows := []
	for h in get_nodes_in_group("enemies"):
		hollows.append("%s hp=%d at %s" % [h.state, h.hp, (h.position - player.position).round()])
	return "player pos=%s hp=%d facing=%s sheet=%s frame=%d dead=%s | ground (biome/row)=%s | fps=%d | hollows: %s" % [
		player.position.round(), player.hp, player.facing, player.sheet, player.sprite.frame, player.dead > 0,
		"%s/%d" % [Terrain.biome_at(player.position).id, Terrain.nearest_corner(player.position) % Terrain.GROUNDS], Engine.get_frames_per_second(), hollows,
	]
