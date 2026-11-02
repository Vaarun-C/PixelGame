shader_type canvas_item;

// Low-opacity atmosphere over the world (ART_RULES §6): slow cloud shade drifting across the
// ground in world space, and a vignette. One flat palette color; only its opacity varies.
uniform vec2 view_origin;
uniform vec2 view_size;
uniform vec4 shade_color : source_color;
uniform float shade_strength = 0.4;
uniform float shade_scale = 900.0;
uniform vec2 drift = vec2(5.0, 2.0);
uniform float vignette_strength = 0.4;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float value_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	// Whole world pixels (2 sprite pixels), so the shade never cuts through a sprite pixel.
	vec2 world = floor((view_origin + UV * view_size) / 2.0) * 2.0;
	vec2 p = (world + TIME * drift) / shade_scale;
	float n = value_noise(p) * 0.65 + value_noise(p * 2.7 + 13.0) * 0.35;
	float shade = smoothstep(0.35, 0.75, n) * shade_strength;
	float edge = length((UV - 0.5) * vec2(1.0, view_size.y / view_size.x)) * 2.0;
	float vignette = smoothstep(0.55, 1.15, edge) * vignette_strength;
	COLOR = vec4(shade_color.rgb, 1.0 - (1.0 - shade) * (1.0 - vignette));
}
