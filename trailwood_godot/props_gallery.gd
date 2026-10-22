extends Node3D

var failures: Array[String] = []
var props: Array[StaticBody3D] = []
var wind_materials: Array[ShaderMaterial] = []
var wind_phase: float = 0.0
var wind_strength: float = 0.4
var wind_paused: bool = false
var wind_label: Label
var theme_label: Label
var theme_textures: Dictionary = {}
var theme_materials: Dictionary = {}
var selected_theme: String = "MOSS_01"
const WindShader = preload("res://vegetation_wind.gdshader")

func source_point(point: Array) -> Vector3:
	return Vector3(point[0], point[2], -float(point[1]))

func _ready() -> void:
	var catalog: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/props_catalog.json"))
	for i in range(catalog["assets"].size()):
		var entry: Dictionary = catalog["assets"][i]
		var body := StaticBody3D.new()
		body.name = entry["asset_id"]
		body.position = Vector3((i % 4 - 1.5) * 2.6, 0, (floori(i / 4.0) - 2.0) * 2.8)
		body.set_meta("solid", entry["collider"] != null)
		body.set_meta("collider_spec", entry["collider"])
		add_child(body)
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		if document.append_from_file("res://" + str(entry["file"]), state) != OK:
			failures.append("GLB load " + str(entry["asset_id"]))
		else:
			var model := document.generate_scene(state)
			body.add_child(model)
			if model.find_children("*", "MeshInstance3D", true, false).is_empty():
				failures.append("Missing mesh " + str(entry["asset_id"]))
			if entry["collider"] == null:
				attach_wind(model, str(entry["asset_id"]), float(i))
		if entry["collider"] != null:
			var parts: Array = entry["collider"].get("parts", [entry["collider"]])
			for part in parts:
				var shape := ConvexPolygonShape3D.new()
				var points := PackedVector3Array()
				for point in part["points_m"]:
					points.append(source_point(point))
				shape.points = points
				var node := CollisionShape3D.new()
				node.shape = shape
				body.add_child(node)
		props.append(body)
	var camera := Camera3D.new()
	add_child(camera)
	camera.position = Vector3(13, 14, 18)
	camera.look_at(Vector3(0, 0.3, 0))
	camera.current = true
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	add_child(sun)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("d8ded4")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color.WHITE
	env.environment.ambient_light_energy = 0.6
	add_child(env)
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := VBoxContainer.new()
	panel.position = Vector2(20, 20)
	layer.add_child(panel)
	var title := Label.new()
	title.text = "Trailwood | 20 props\nRows: stump/log | vegetation | signs/crates | paving/stairs | benches/tables"
	panel.add_child(title)
	theme_label = Label.new()
	panel.add_child(theme_label)
	var theme_buttons := HBoxContainer.new()
	panel.add_child(theme_buttons)
	for theme in ["MOSS_01", "DRY_01", "DUSK_01"]:
		var button := Button.new()
		button.text = theme.trim_suffix("_01")
		button.custom_minimum_size = Vector2(115, 48)
		button.pressed.connect(set_theme.bind(theme))
		theme_buttons.add_child(button)
	set_theme("MOSS_01")
	wind_label = Label.new()
	panel.add_child(wind_label)
	var wind_buttons := HBoxContainer.new()
	panel.add_child(wind_buttons)
	for setting in [["Wind off", 0.0], ["Gentle", 0.4], ["Strong", 1.0]]:
		var button := Button.new()
		button.text = setting[0]
		button.custom_minimum_size = Vector2(115, 48)
		button.pressed.connect(set_wind_strength.bind(float(setting[1])))
		wind_buttons.add_child(button)
	var pause_button := Button.new()
	pause_button.text = "Pause / resume wind"
	pause_button.custom_minimum_size = Vector2(190, 48)
	pause_button.pressed.connect(func(): wind_paused = not wind_paused)
	wind_buttons.add_child(pause_button)
	set_wind_strength(0.4)
	var back := Button.new()
	back.text = "Return to walking demo"
	back.custom_minimum_size = Vector2(260, 48)
	back.pressed.connect(func(): get_tree().change_scene_to_file("res://main.tscn"))
	panel.add_child(back)
	if OS.get_cmdline_user_args().has("--props-test"):
		check_props.call_deferred()

func check_props() -> void:
	for i in range(3):
		await get_tree().physics_frame
	if props.size() != 20:
		failures.append("Prop count")
	var hits := 0
	var decorative := 0
	for theme in ["MOSS_01", "DRY_01", "DUSK_01"]:
		set_theme(theme)
		if not theme_textures.has(theme):
			failures.append("Theme texture load " + theme)
			continue
		for body in props:
			for mesh in body.find_children("*", "MeshInstance3D", true, false):
				var active = mesh.material_override
				if active is ShaderMaterial:
					if active.get_shader_parameter("palette_texture") != theme_textures[theme]:
						failures.append("Wind theme binding " + theme)
				elif active != theme_materials[theme]:
					failures.append("Shared base theme material " + theme)
	set_theme("MOSS_01")
	if wind_materials.size() != 4:
		failures.append("Expected four vegetation wind materials")
	set_wind_strength(0.0)
	for material in wind_materials:
		if float(material.get_shader_parameter("strength")) != 0.0:
			failures.append("Wind off parameter")
		if material.get_shader_parameter("palette_texture") == null:
			failures.append("Missing wind palette")
	set_wind_strength(1.0)
	wind_paused = true
	var before := wind_phase
	_process(0.5)
	if wind_phase != before:
		failures.append("Wind pause")
	wind_paused = false
	_process(0.5)
	if is_equal_approx(wind_phase, before):
		failures.append("Wind resume")
	for material in wind_materials:
		if not is_equal_approx(float(material.get_shader_parameter("wind_phase")), wind_phase):
			failures.append("Wind phase binding")
	for body in props:
		var sample := body.position
		var descriptor = body.get_meta("collider_spec", {})
		if descriptor is Dictionary and descriptor.has("length_m"):
			sample.x += float(descriptor["length_m"]) * 0.5
		var start := sample + Vector3.UP * 3
		var end := sample - Vector3.UP
		var result := get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start, end))
		if not body.get_meta("solid"):
			if not result.is_empty() or not body.find_children("*", "CollisionShape3D", true, false).is_empty():
				failures.append("Decorative vegetation unexpectedly blocks " + str(body.name))
			else:
				decorative += 1
		elif result.is_empty() or result["collider"] != body:
			failures.append("Collision ray " + str(body.name))
		else:
			hits += 1
	var stair_checks: Array[Dictionary] = []
	for body in props:
		var descriptor = body.get_meta("collider_spec", {})
		if descriptor is Dictionary and descriptor.get("mode", "") == "SMOOTH_RAMP_PROXY":
			stair_checks.append(await test_ramp_walk(body, descriptor))
	var report := {"passed": failures.is_empty(), "failures": failures, "models": props.size(), "collision_hits": hits, "decorative_nonblocking": decorative, "wind_materials": wind_materials.size(), "theme_texture_count": theme_textures.size(), "theme_test": "3 themes bound to 20 models", "stair_walk_checks": stair_checks, "wind_control_test": "resource/parameter/pause binding only; no GPU rendering", "engine": Engine.get_version_info(), "render_test": "NOT_RUN"}
	var file := FileAccess.open("user://props_test.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	print(JSON.stringify(report))
	get_tree().quit(0 if failures.is_empty() else 1)

func test_ramp_walk(body: StaticBody3D, descriptor: Dictionary) -> Dictionary:
	var floor_body := StaticBody3D.new()
	add_child(floor_body)
	floor_body.position = body.position + Vector3(0, -0.05, 0)
	var floor_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(6, 0.1, 2)
	floor_shape.shape = box
	floor_body.add_child(floor_shape)
	var actor = preload("res://walker.gd").new()
	actor.manual_input = false
	actor.speed = 0.7
	add_child(actor)
	actor.reset_at(body.position + Vector3(-0.6, 0.05, 0))
	for i in range(30):
		await get_tree().physics_frame
	actor.scripted_direction = Vector3.RIGHT
	var length: float = descriptor["length_m"]
	var frames := int(ceil((0.6 + length * 0.8) / 0.7 * 60))
	for i in range(frames):
		await get_tree().physics_frame
	actor.scripted_direction = Vector3.ZERO
	var local_position: Vector3 = actor.position - body.position
	var passed: bool = local_position.x > length * 0.7 and local_position.y > float(descriptor["height_m"]) * 0.6 and actor.is_on_floor()
	if not passed:
		failures.append("Smooth stair ramp walk " + str(body.name))
	var report := {"asset": str(body.name), "x_m": local_position.x, "y_m": local_position.y, "on_floor": actor.is_on_floor(), "passed": passed, "collider": "smooth ramp; not individual step risers"}
	actor.queue_free()
	floor_body.queue_free()
	await get_tree().physics_frame
	return report

func attach_wind(model: Node3D, asset_id: String, phase: float) -> void:
	for child in model.find_children("*", "MeshInstance3D", true, false):
		var mesh_node := child as MeshInstance3D
		var original := mesh_node.mesh.surface_get_material(0) as StandardMaterial3D
		if original == null or original.albedo_texture == null:
			failures.append("Unsupported vegetation material " + asset_id)
			continue
		var material := ShaderMaterial.new()
		material.shader = WindShader
		material.set_shader_parameter("palette_texture", original.albedo_texture)
		material.set_shader_parameter("plant_height", mesh_node.get_aabb().size.y)
		material.set_shader_parameter("max_sway", 0.08 if "GRASS" in asset_id else 0.03)
		material.set_shader_parameter("strength", wind_strength)
		material.set_shader_parameter("instance_phase", phase * 0.73)
		mesh_node.material_override = material
		mesh_node.extra_cull_margin = 0.1
		wind_materials.append(material)

func set_wind_strength(value: float) -> void:
	wind_strength = clampf(value, 0.0, 1.0)
	for material in wind_materials:
		material.set_shader_parameter("strength", wind_strength)
	if wind_label != null:
		wind_label.text = "Wind strength: %.1f | local-space sway | decorative vegetation only" % wind_strength

func _process(delta: float) -> void:
	if not wind_paused:
		wind_phase = fmod(wind_phase + delta * 1.8, TAU)
	for material in wind_materials:
		material.set_shader_parameter("wind_phase", wind_phase)

func set_theme(theme: String) -> void:
	if not theme_textures.has(theme):
		var image := Image.load_from_file("res://palettes/" + theme + ".png")
		if image == null or image.is_empty():
			failures.append("Missing palette " + theme)
			return
		var texture := ImageTexture.create_from_image(image)
		theme_textures[theme] = texture
		var material := StandardMaterial3D.new()
		material.albedo_texture = texture
		material.roughness = 0.85
		material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		theme_materials[theme] = material
	for body in props:
		for mesh in body.find_children("*", "MeshInstance3D", true, false):
			if mesh.material_override is ShaderMaterial:
				mesh.material_override.set_shader_parameter("palette_texture", theme_textures[theme])
			else:
				mesh.material_override = theme_materials[theme]
	selected_theme = theme
	if theme_label != null:
		theme_label.text = "Palette: " + theme
