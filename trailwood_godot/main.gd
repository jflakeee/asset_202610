extends Node3D

const Policy = preload("res://lod_policy.gd")
const Walker = preload("res://walker.gd")
var walker: CharacterBody3D
var entries: Array[Dictionary] = []
var model_cache: Dictionary = {}
var camera: Camera3D
var status: Label
var radius: float = 15.0
var orbit: float = 0.7
var auto_orbit: bool = false
var mode: int = -1
var elapsed: float = 0.0
var transition_count: int = 0
var shape_count: int = 0
var loaded_ok: bool = true

func source_to_engine(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[2]), -float(a[1]))

func read_json(path: String) -> Dictionary:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("Invalid JSON: " + path)
		loaded_ok = false
		return {}
	return parsed

func load_model(path: String) -> Node3D:
	if model_cache.has(path):
		return model_cache[path].instantiate() as Node3D
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	var error := document.append_from_file(path, state)
	if error != OK:
		push_error("GLB load failed: " + path)
		loaded_ok = false
		return Node3D.new()
	var generated: Node3D = document.generate_scene(state) as Node3D
	if generated == null:
		loaded_ok = false
		return Node3D.new()
	var packed := PackedScene.new()
	if packed.pack(generated) != OK:
		loaded_ok = false
	else:
		model_cache[path] = packed
	return generated

func add_collision(parent: Node3D, descriptor: Dictionary) -> void:
	var node := CollisionShape3D.new()
	match descriptor["type"]:
		"box":
			var shape := BoxShape3D.new()
			var size: Array = descriptor["size_m"]
			shape.size = Vector3(size[0], size[2], size[1])
			node.shape = shape
		"cylinder":
			var shape := CylinderShape3D.new()
			shape.radius = descriptor["radius_m"]
			shape.height = descriptor["height_m"]
			node.shape = shape
		"convex_hull":
			var shape := ConvexPolygonShape3D.new()
			var points := PackedVector3Array()
			for point in descriptor["points_m"]:
				points.append(source_to_engine(point))
			shape.points = points
			node.shape = shape
		_:
			loaded_ok = false
			node.free()
			return
	if descriptor.has("center_m"):
		node.position = source_to_engine(descriptor["center_m"])
	parent.add_child(node)
	shape_count += 1

func _ready() -> void:
	var scene_data := read_json("res://data/scene.json")
	var collisions := read_json("res://data/colliders.json")
	var catalog := read_json("res://data/catalog.json")
	if not loaded_ok:
		get_tree().quit(1)
		return
	for item in scene_data["instances"]:
		var asset: String = item["asset_id"]
		var body := StaticBody3D.new()
		body.name = item["id"]
		body.position = source_to_engine(item["position_m"])
		body.rotation.y = deg_to_rad(float(item["yaw_degrees"]))
		body.collision_layer = 1
		body.collision_mask = 0
		add_child(body)
		var spec: Dictionary = catalog[asset]
		var high := load_model("res://" + str(spec["lod0"]))
		body.add_child(high)
		var low: Node3D = null
		if spec.has("lod1"):
			low = load_model("res://" + str(spec["lod1"]))
			body.add_child(low)
			low.visible = false
		for descriptor in collisions["assets"][asset]:
			add_collision(body, descriptor)
		entries.append({"body": body, "high": high, "low": low, "lod": 0,
			"height": float(spec["height_m"]), "tri0": int(spec["tri0"]),
			"tri1": int(spec.get("tri1", spec["tri0"]))})
	make_ground()
	walker = Walker.new()
	walker.name = "InspectionWalker"
	walker.position = Vector3(-5.3, 0.05, 0)
	walker.manual_input = not OS.get_cmdline_user_args().has("--self-test")
	add_child(walker)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -30, 0)
	light.shadow_enabled = true
	add_child(light)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("d4e1dc")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color.WHITE
	environment.environment.ambient_light_energy = 0.6
	add_child(environment)
	camera = Camera3D.new()
	camera.fov = 55.0
	camera.far = 150.0
	add_child(camera)
	camera.current = true
	make_ui()
	update_camera()
	if OS.get_cmdline_user_args().has("--self-test"):
		run_checks.call_deferred()

func make_ground() -> void:
	var ground := StaticBody3D.new()
	ground.name = "Ground"
	ground.collision_layer = 1
	ground.collision_mask = 0
	add_child(ground)
	add_collision(ground, {"type": "box", "size_m": [12, 9, 0.1], "center_m": [0, 0, -0.05]})
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(12, 0.1, 9)
	mesh.mesh = box
	mesh.position.y = -0.05
	var material := StandardMaterial3D.new()
	material.albedo_color = Color("9aa47a")
	mesh.material_override = material
	ground.add_child(mesh)

func make_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := VBoxContainer.new()
	panel.position = Vector2(18, 18)
	layer.add_child(panel)
	status = Label.new()
	panel.add_child(status)
	var row := HBoxContainer.new()
	panel.add_child(row)
	var labels := ["Near", "Far", "Auto LOD", "LOD0", "LOD1", "Orbit"]
	for i in range(labels.size()):
		var button := Button.new()
		button.text = labels[i]
		button.custom_minimum_size = Vector2(100, 48)
		button.pressed.connect(on_button.bind(i))
		row.add_child(button)
	var movement := HBoxContainer.new()
	panel.add_child(movement)
	var directions := [Vector3.LEFT, Vector3.RIGHT, Vector3.FORWARD, Vector3.BACK]
	var names := ["Move -X", "Move +X", "Move -Z", "Move +Z"]
	for i in range(4):
		var button := Button.new()
		button.text = names[i]
		button.custom_minimum_size = Vector2(110, 48)
		button.button_down.connect(set_walk_direction.bind(directions[i]))
		button.button_up.connect(set_walk_direction.bind(Vector3.ZERO))
		movement.add_child(button)
	var reset := Button.new()
	reset.text = "Reset walker"
	reset.custom_minimum_size = Vector2(130, 48)
	reset.pressed.connect(func(): walker.reset_at(Vector3(-5.3, 0.05, 0)))
	movement.add_child(reset)
	var gallery := Button.new()
	gallery.text = "Wood & vegetation gallery"
	gallery.custom_minimum_size = Vector2(240, 48)
	gallery.pressed.connect(func(): get_tree().change_scene_to_file("res://props_gallery.tscn"))
	panel.add_child(gallery)
	var catalog_button := Button.new()
	catalog_button.text = "Full model catalog"
	catalog_button.custom_minimum_size = Vector2(240, 48)
	catalog_button.pressed.connect(func(): get_tree().change_scene_to_file("res://catalog_viewer.tscn"))
	panel.add_child(catalog_button)
	var boundaries := Button.new()
	boundaries.text = "Boundary physics examples"
	boundaries.custom_minimum_size = Vector2(240,48)
	boundaries.pressed.connect(func(): get_tree().change_scene_to_file("res://boundary_lab.tscn"))
	panel.add_child(boundaries)

func set_walk_direction(direction: Vector3) -> void:
	walker.touch_direction = direction

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and walker != null:
		walker.touch_direction = Vector3.ZERO

func on_button(index: int) -> void:
	match index:
		0: radius = 9.0
		1: radius = 42.0
		2: mode = -1
		3: mode = 0
		4: mode = 1
		5: auto_orbit = not auto_orbit

func update_camera() -> void:
	camera.position = Vector3(cos(orbit) * radius, radius * 0.55, sin(orbit) * radius)
	camera.look_at(Vector3(0, 1, 0), Vector3.UP)

func projected_height(entry: Dictionary) -> float:
	var base: Vector3 = entry["body"].global_position
	var top: Vector3 = base + Vector3.UP * float(entry["height"])
	# Avoid unstable projection for objects intersecting the camera's near plane.
	var inv := camera.global_transform.affine_inverse()
	if -(inv * base).z <= camera.near or -(inv * top).z <= camera.near:
		return 100000.0
	return camera.unproject_position(base).distance_to(camera.unproject_position(top))

func _process(delta: float) -> void:
	if camera == null:
		return
	if auto_orbit:
		orbit += delta * 0.15
	update_camera()
	elapsed += delta
	if elapsed < 0.1:
		return
	elapsed = 0.0
	var counts := [0, 0]
	var triangles := 0
	for entry in entries:
		var selected := 0
		if entry["low"] != null:
			selected = mode if mode >= 0 else Policy.choose(entry["lod"], projected_height(entry))
		if selected != entry["lod"]:
			transition_count += 1
		entry["lod"] = selected
		entry["high"].visible = selected == 0
		if entry["low"] != null:
			entry["low"].visible = selected == 1
		counts[selected] += 1
		triangles += int(entry["tri0"] if selected == 0 else entry["tri1"])
	status.text = "Trailwood | LOD0: %d  LOD1: %d | selected asset triangles: %d\nFPS: %d | transitions: %d | shapes: %d | mode: %s" % [counts[0], counts[1], triangles, Engine.get_frames_per_second(), transition_count, shape_count, "Auto" if mode < 0 else str(mode)]

func run_checks() -> void:
	for i in range(3):
		await get_tree().physics_frame
	var failures: Array[String] = []
	var evidence: Dictionary = {}
	if not loaded_ok or entries.size() != 20:
		failures.append("Asset loading / placement count")
	if model_cache.size() != 11:
		failures.append("Expected 11 cached GLB scenes")
	for entry in entries:
		if entry["high"].find_children("*", "MeshInstance3D", true, false).is_empty():
			failures.append("Missing visible mesh in LOD0 scene")
		if entry["low"] != null and entry["low"].find_children("*", "MeshInstance3D", true, false).is_empty():
			failures.append("Missing visible mesh in LOD1 scene")
	if shape_count != 35:
		failures.append("Expected 35 collision shapes including ground")
	for case in [[0, 79.0, 1], [0, 80.0, 0], [1, 90.0, 1], [1, 100.0, 1], [1, 101.0, 0]]:
		if Policy.choose(case[0], case[1]) != case[2]:
			failures.append("LOD hysteresis")
	mode = 0
	_process(0.11)
	if count_lod1() != 0:
		failures.append("Forced LOD0")
	mode = 1
	_process(0.11)
	if count_lod1() != 11:
		failures.append("Forced LOD1")
	mode = -1
	radius = 9.0
	_process(0.11)
	var near_count := count_lod1()
	radius = 42.0
	_process(0.11)
	var far_count := count_lod1()
	evidence["near_lod1_count"] = near_count
	evidence["far_lod1_count"] = far_count
	if far_count <= near_count:
		failures.append("Camera projected automatic LOD transition")
	for entry in entries:
		if entry["high"].visible != (entry["lod"] == 0):
			failures.append("LOD0 visibility mismatch")
		if entry["low"] != null and entry["low"].visible != (entry["lod"] == 1):
			failures.append("LOD1 visibility mismatch")
	var space := get_world_3d().direct_space_state
	var floor_hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(0, 2, 0), Vector3(0, -1, 0), 1))
	if floor_hit.is_empty():
		failures.append("Ground ray")
	var post_hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-5, 0.55, -2.7), Vector3(-5, 0.55, -3.7), 1))
	if post_hit.is_empty():
		failures.append("Fence post ray")
	var path_hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-5.8, 0.55, 0), Vector3(5.8, 0.55, 0), 1))
	if not path_hit.is_empty():
		failures.append("Clear path ray")
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.6
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	query.margin = 0.001
	query.transform = Transform3D(Basis.IDENTITY, Vector3(-5.5, 0.85, 0))
	query.motion = Vector3(11, 0, 0)
	var passage := space.cast_motion(query)
	evidence["capsule_path_safe_fraction"] = passage[0]
	if passage[0] < 0.999:
		failures.append("Capsule clear path")
	query.transform = Transform3D(Basis.IDENTITY, Vector3(-5, 0.85, -1.5))
	query.motion = Vector3(0, 0, -3)
	var fence := space.cast_motion(query)
	evidence["capsule_fence_safe_fraction"] = fence[0]
	if fence[0] >= 0.999 or fence[0] <= 0.0:
		failures.append("Capsule fence collision")
	await test_walker(failures, evidence)
	var report := {"engine": Engine.get_version_info(), "failures": failures, "passed": failures.is_empty(), "instances": entries.size(), "shape_count": shape_count, "evidence": evidence, "scope": "headless GLB loading, camera LOD visibility, ray/capsule sweeps and CharacterBody3D movement; not rendered image/performance benchmark"}
	var file := FileAccess.open("user://self_test.json", FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(report, "\t"))
	print(JSON.stringify(report))
	get_tree().quit(0 if failures.is_empty() else 1)

func count_lod1() -> int:
	var result := 0
	for entry in entries:
		if entry["lod"] == 1:
			result += 1
	return result

func test_walker(failures: Array[String], evidence: Dictionary) -> void:
	walker.manual_input = false
	walker.reset_at(Vector3(-5.0, 0.1, 0))
	for i in range(45):
		await get_tree().physics_frame
	if not walker.is_on_floor():
		failures.append("Walker floor landing")
	walker.scripted_direction = Vector3.RIGHT
	for i in range(240):
		await get_tree().physics_frame
	walker.scripted_direction = Vector3.ZERO
	evidence["walker_path_end_x"] = walker.position.x
	evidence["walker_path_end_y"] = walker.position.y
	if walker.position.x < 4.8 or absf(walker.position.z) > 0.02 or absf(walker.position.y) > 0.02:
		failures.append("Walker 10m corridor traversal")
	walker.reset_at(Vector3(-5, 0.05, -1.5))
	for i in range(20):
		await get_tree().physics_frame
	walker.scripted_direction = Vector3.FORWARD
	for i in range(100):
		await get_tree().physics_frame
	walker.scripted_direction = Vector3.ZERO
	evidence["walker_fence_stop_z"] = walker.position.z
	if walker.position.z < -2.95 or walker.position.z > -2.75:
		failures.append("Walker blocked by fence")
	if not walker.is_on_floor():
		failures.append("Walker stable ground contact")
