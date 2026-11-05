shader_type canvas_item;

// The parchment map (map_panel.gd): ground he hasn't seen shows as blank parchment. fog covers the
// whole map like the map texture, one texel per chunk, red > 0 where seen.
uniform sampler2D fog : filter_nearest;
uniform vec4 blank : source_color;

void fragment() {
	if (texture(fog, UV).r < 0.5) {
		COLOR = blank;
	}
}
