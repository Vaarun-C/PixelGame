shader_type canvas_item;

// What corruption does to the world (LORE.md): in the Whisper colour drains in from the screen's
// edges (Hush's greying); at the Pull most of it is gone and the screen dims. A post effect over
// the world and the atmosphere; the HUD draws above it and keeps its colour.
uniform sampler2D screen : hint_screen_texture, filter_nearest;
uniform float corruption = 0.0;
uniform vec4 dark : source_color;

void fragment() {
	vec4 s = texture(screen, SCREEN_UV);
	float whisper = smoothstep(0.72, 0.8, corruption);
	float pull = step(1.0, corruption);
	float reach = mix(0.6, 0.25, pull);
	float strength = mix(0.7, 0.85, pull) * whisper;
	float edge = length((SCREEN_UV - 0.5) * 2.0);
	float drain = strength * clamp((edge - reach) / 0.6, 0.0, 1.0);
	float grey = dot(s.rgb, vec3(0.299, 0.587, 0.114));
	vec3 c = mix(s.rgb, vec3(grey), drain);
	COLOR = vec4(mix(c, dark.rgb, 0.4 * pull), 1.0);
}
