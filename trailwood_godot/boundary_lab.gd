extends Node3D

var scenes: Array = []
var stage: Node3D
var camera: Camera3D
var label: Label
var index := 0
var failures: Array[String] = []
var bodies: Array[StaticBody3D] = []

func point(v: Array) -> Vector3:
	return Vector3(v[0],v[2],-float(v[1]))

func placement(m: Array) -> Transform3D:
	return Transform3D(Basis(Vector3(m[0][0],m[1][0],m[2][0]),Vector3(m[0][1],m[1][1],m[2][1]),Vector3(m[0][2],m[1][2],m[2][2])),Vector3(m[0][3],m[1][3],m[2][3]))

func _ready() -> void:
	scenes = JSON.parse_string(FileAccess.get_file_as_string("res://data/boundary_lab.json"))["scenes"]
	camera = Camera3D.new()
	add_child(camera)
	camera.current = true
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50,-35,0)
	add_child(sun)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("d6dfd5")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color.WHITE
	env.environment.ambient_light_energy = 0.6
	add_child(env)
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := VBoxContainer.new()
	panel.position = Vector2(20,20)
	canvas.add_child(panel)
	label = Label.new()
	panel.add_child(label)
	for direction in [-1,1]:
		var button := Button.new()
		button.text = "Previous example" if direction < 0 else "Next example"
		button.custom_minimum_size = Vector2(240,48)
		button.pressed.connect(func(): index = posmod(index+direction,scenes.size()); show_scene())
		panel.add_child(button)
	var back := Button.new()
	back.text = "Return to walking demo"
	back.custom_minimum_size = Vector2(240,48)
	back.pressed.connect(func(): get_tree().change_scene_to_file("res://main.tscn"))
	panel.add_child(back)
	show_scene()
	if OS.get_cmdline_user_args().has("--boundary-test"): run_checks.call_deferred()

func show_scene() -> void:
	if stage != null:
		remove_child(stage)
		stage.free()
	stage = Node3D.new()
	add_child(stage)
	bodies.clear()
	var scene: Dictionary = scenes[index]
	label.text = str(scene["name"]) + "\nEngineering review | static gate positions"
	var bounds := AABB()
	var first := true
	for row in scene["instances"]:
		var body := StaticBody3D.new()
		stage.add_child(body)
		body.transform = placement(row["matrix"])
		bodies.append(body)
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		if doc.append_from_file("res://"+row["file"],state) != OK:
			failures.append("Load " + row["asset_id"])
			continue
		var model := doc.generate_scene(state)
		body.add_child(model)
		for mesh in model.find_children("*","MeshInstance3D",true,false):
			var box: AABB = mesh.global_transform * mesh.get_aabb()
			bounds = box if first else bounds.merge(box)
			first = false
		var desc: Dictionary = row["collider"]
		for part in desc.get("parts",[desc]):
			var node := CollisionShape3D.new()
			if part["type"] == "convex_hull":
				var shape := ConvexPolygonShape3D.new()
				var points := PackedVector3Array()
				for v in part["points_m"]: points.append(point(v))
				shape.points = points
				node.shape = shape
			elif part["type"] == "box":
				var shape := BoxShape3D.new()
				shape.size = point(part["size_m"]).abs()
				node.shape = shape
				node.position = point(part["center_m"])
			else: failures.append("Unknown collider " + str(part["type"]))
			body.add_child(node)
	var floor_body := StaticBody3D.new()
	stage.add_child(floor_body)
	var angle := deg_to_rad(float(scene["slope_degrees"]))
	floor_body.rotation.z = angle
	floor_body.position.y = -0.05/cos(angle)
	var shape := BoxShape3D.new()
	shape.size = Vector3(30,0.1,30)
	var collision := CollisionShape3D.new()
	collision.shape = shape
	floor_body.add_child(collision)
	var visual := MeshInstance3D.new()
	var floor_mesh := BoxMesh.new()
	floor_mesh.size = shape.size
	visual.mesh = floor_mesh
	floor_body.add_child(visual)
	var center := bounds.get_center()
	camera.position = center + Vector3(0.7,0.8,1).normalized()*max(bounds.size.length()*1.25,4.)
	camera.look_at(center)

func run_checks() -> void:
	var results: Array[Dictionary] = []
	var seams: Array[Dictionary] = []
	for i in range(scenes.size()):
		index = i
		show_scene()
		for tick in range(4): await get_tree().physics_frame
		var scene: Dictionary = scenes[i]
		if scene.has("seam_probes"):
			seams.append(check_seams(scene))
		var x := float(scene["test_x"])
		var height := tan(deg_to_rad(float(scene["slope_degrees"]))) * x
		var actor = preload("res://walker.gd").new()
		actor.manual_input = false
		actor.speed = 1.5
		stage.add_child(actor)
		actor.position = Vector3(x,height+0.05,-1.2)
		for tick in range(30): await get_tree().physics_frame
		actor.scripted_direction = Vector3(0,0,1)
		for tick in range(120): await get_tree().physics_frame
		actor.scripted_direction = Vector3.ZERO
		var blocked := bool(scene["expect_blocked"])
		var passed: bool = actor.position.z < -0.2 if blocked else actor.position.z > 1.2
		passed = passed and actor.is_on_floor() and abs(actor.position.x-x)<0.1
		if not passed: failures.append("Traversal " + str(scene["name"]))
		results.append({"scene":scene["name"],"expected_blocked":blocked,"passed":passed,"end_position":[actor.position.x,actor.position.y,actor.position.z],"on_floor":actor.is_on_floor(),"loaded_bodies":bodies.size()})
	var report := {"passed":failures.is_empty(),"failures":failures,"cases":results,"seam_sweeps":seams,"engine":Engine.get_version_info(),"capsule_radius_m":0.25,"capsule_height_m":1.6,"scope":"120 physics frames forward traversal per scene plus finite capsule sweeps at closed-loop socket neighborhoods and corner elbows. Gate static closed/90deg open. Slope ground supplied by lab.","corner_seam_traversal":"FINITE_CAPSULE_SWEEPS_NOT_ALL_POSSIBLE_PATHS","gpu_render":"NOT_RUN"}
	var file := FileAccess.open("user://boundary_test.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	print(JSON.stringify(report))
	get_tree().quit(0 if failures.is_empty() else 1)

func check_seams(scene: Dictionary) -> Dictionary:
	var space := get_world_3d().direct_space_state
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.6
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.collision_mask = 1
	query.margin = 0.001
	var blocked := 0
	var overlapping := 0
	var leaks: Array[Dictionary] = []
	var blocked_transform := Transform3D.IDENTITY
	var blocked_motion := Vector3.ZERO
	for probe in scene["seam_probes"]:
		var c: Array = probe["center"]
		var d: Array = probe["direction"]
		var center := Vector3(c[0],0.85,c[2])
		var direction := Vector3(d[0],0,d[2]).normalized()
		query.transform = Transform3D(Basis.IDENTITY,center-direction*1.25)
		query.motion = Vector3.ZERO
		if not space.intersect_shape(query,1).is_empty():
			overlapping += 1
			continue
		query.motion = direction*2.5
		var fractions := space.cast_motion(query)
		if fractions[0] < 0.999:
			blocked += 1
			blocked_transform = query.transform
			blocked_motion = query.motion
		else:
			leaks.append(probe)
	query.transform = Transform3D(Basis.IDENTITY,Vector3(50,0.85,50))
	query.motion = Vector3(1,0,0)
	var clear_control := space.cast_motion(query)[0] == 1.0
	query.transform = blocked_transform
	query.motion = blocked_motion
	query.collision_mask = 0
	var no_mask_control := space.cast_motion(query)[0] == 1.0
	var passed := leaks.is_empty() and blocked >= 50 and clear_control and no_mask_control
	if not passed: failures.append("Seam sweep " + str(scene["name"]))
	return {"scene":scene["name"],"passed":passed,"planned_probes":scene["seam_probes"].size(),"blocked_sweeps":blocked,"initial_overlap_skipped":overlapping,"leaks":leaks,"clear_space_control":clear_control,"zero_mask_control":no_mask_control,"scope":"Radius0.25m height1.6m sweeps; overlapping starts excluded; no claim for smaller actors or arbitrary routes"}
