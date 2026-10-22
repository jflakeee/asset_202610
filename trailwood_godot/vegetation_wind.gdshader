shader_type spatial;
render_mode cull_back;

uniform sampler2D palette_texture : source_color, filter_nearest, repeat_disable;
uniform float plant_height = 1.0;
uniform float max_sway = 0.08;
uniform float strength : hint_range(0.0, 1.0) = 0.4;
uniform float wind_phase = 0.0;
uniform float instance_phase = 0.0;

void vertex() {
	float height = max(plant_height, 0.001);
	float h = clamp(VERTEX.y / height, 0.0, 1.0);
	float phase = wind_phase + instance_phase;
	float xwave = sin(phase);
	float zwave = 0.35 * sin(2.0 * phase + 0.7);
	float amplitude = max_sway * strength;
	float derivative = 2.0 * h / height;
	// Inverse-transpose of the height-dependent shear keeps normals coherent.
	NORMAL = normalize(vec3(NORMAL.x, NORMAL.y - amplitude * derivative *
		(xwave * NORMAL.x + zwave * NORMAL.z), NORMAL.z));
	VERTEX.x += amplitude * h * h * xwave;
	VERTEX.z += amplitude * h * h * zwave;
}

void fragment() {
	ALBEDO = texture(palette_texture, UV).rgb;
	ROUGHNESS = 0.85;
	METALLIC = 0.0;
}
