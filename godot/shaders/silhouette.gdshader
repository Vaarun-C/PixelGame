shader_type canvas_item;

// Blends the sprite toward a flat color (hit flashes, dodge afterimages) and can ring it with a
// 1px outline (attack telegraphs).
uniform vec4 tint : source_color;
uniform float amount = 1.0;
uniform vec4 outline : source_color;
uniform float outline_amount = 0.0;

void fragment() {
	COLOR.rgb = mix(COLOR.rgb, tint.rgb, amount);
	if (outline_amount > 0.0 && COLOR.a == 0.0) {
		vec2 px = TEXTURE_PIXEL_SIZE;
		float near = texture(TEXTURE, UV + vec2(px.x, 0.0)).a + texture(TEXTURE, UV - vec2(px.x, 0.0)).a
			+ texture(TEXTURE, UV + vec2(0.0, px.y)).a + texture(TEXTURE, UV - vec2(0.0, px.y)).a;
		if (near > 0.0) {
			COLOR = vec4(outline.rgb, outline_amount);
		}
	}
}
