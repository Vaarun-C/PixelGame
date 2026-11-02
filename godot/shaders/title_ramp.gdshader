shader_type canvas_item;

// Lights white title lettering like cast metal: four palette shades from top to bottom of the line.
// Anything not white (the void outline and shadow) passes through unchanged.
uniform vec4 shade_0 : source_color;
uniform vec4 shade_1 : source_color;
uniform vec4 shade_2 : source_color;
uniform vec4 shade_3 : source_color;
uniform float top = 0.0;
uniform float height = 1.0;

varying vec2 local;

void vertex() {
	local = VERTEX;
}

void fragment() {
	if (COLOR.r > 0.9 && COLOR.g > 0.9 && COLOR.b > 0.9) {
		float k = clamp((local.y - top) / height, 0.0, 0.999);
		int band = int(k * 4.0);
		vec3 c = band == 0 ? shade_0.rgb : band == 1 ? shade_1.rgb : band == 2 ? shade_2.rgb : shade_3.rgb;
		COLOR.rgb = c;
	}
}
