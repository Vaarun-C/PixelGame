shader_type canvas_item;

// Spell effects are drawn in the Pale tier's ramp; this swaps it for the uttered stone's (SpellFx).
uniform vec4 from_dark : source_color;
uniform vec4 from_mid : source_color;
uniform vec4 from_core : source_color;
uniform vec4 to_dark : source_color;
uniform vec4 to_mid : source_color;
uniform vec4 to_core : source_color;

bool same(vec3 a, vec3 b) {
	return distance(a, b) < 0.01;
}

void fragment() {
	if (same(COLOR.rgb, from_dark.rgb)) {
		COLOR.rgb = to_dark.rgb;
	} else if (same(COLOR.rgb, from_mid.rgb)) {
		COLOR.rgb = to_mid.rgb;
	} else if (same(COLOR.rgb, from_core.rgb)) {
		COLOR.rgb = to_core.rgb;
	}
}
