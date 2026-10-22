extends Node3D

var entries: Array = []
var index: int = 0
var subject: Node3D
var camera: Camera3D
var heading: Label
var detail: Label
var theme: String = "MOSS_01"
var failures: Array[String] = []
var loaded_count: int = 0
var collision_parts: int = 0

func point(v: Array) -> Vector3:
	return Vector3(float(v[0]), float(v[2]), -float(v[1]))

func _ready() -> void:
	entries = JSON.parse_string(FileAccess.get_file_as_string("res://data/full_catalog.json"))["assets"]
	camera = Camera3D.new()
	add_child(camera)
	camera.current = true
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, -35, 0)
	add_child(sun)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("d8ded4")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color.WHITE
	environment.environment.ambient_light_energy = 0.65
	add_child(environment)
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := VBoxContainer.new()
	panel.position = Vector2(20,20)
	layer.add_child(panel)
	heading = Label.new()
	panel.add_child(heading)
	detail = Label.new()
	panel.add_child(detail)
	var buttons := HBoxContainer.new()
	panel.add_child(buttons)
	for direction in [-1,1]:
		var button := Button.new()
		button.text = "Previous" if direction == -1 else "Next"
		button.custom_minimum_size = Vector2(130,48)
		button.pressed.connect(func(): index = posmod(index + direction, entries.size()); show_asset())
		buttons.add_child(button)
	for name in ["MOSS_01","DRY_01","DUSK_01"]:
		var button := Button.new()
		button.text = name.trim_suffix("_01")
		button.custom_minimum_size = Vector2(110,48)
		button.pressed.connect(func(): theme = name; show_asset())
		buttons.add_child(button)
	var back := Button.new()
	back.text = "Return to walking demo"
	back.custom_minimum_size = Vector2(260,48)
	back.pressed.connect(func(): get_tree().change_scene_to_file("res://main.tscn"))
	panel.add_child(back)
	show_asset()
	if OS.get_cmdline_user_args().has("--catalog-test"):
		check_catalog.call_deferred()

func show_asset() -> void:
	if subject != null:
		remove_child(subject)
		subject.free()
	subject = StaticBody3D.new()
	add_child(subject)
	var row: Dictionary = entries[index]
	heading.text = "%d / %d  %s" % [index+1,entries.size(),row["asset_id"]]
	detail.text = "%d triangles | %s | Art review pending" % [row["triangles"],theme]
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file("res://" + str(row["file"]),state) != OK:
		failures.append("Load " + row["asset_id"])
		return
	var model := doc.generate_scene(state)
	subject.add_child(model)
	var material := StandardMaterial3D.new()
	var palette := Image.load_from_file("res://palettes/" + theme + ".png")
	if palette != null:
		material.albedo_texture = ImageTexture.create_from_image(palette)
	material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	material.roughness = 0.85
	var meshes := model.find_children("*","MeshInstance3D",true,false)
	if meshes.is_empty(): failures.append("No mesh " + row["asset_id"])
	for mesh in meshes: mesh.material_override = material
	if material.albedo_texture == null: failures.append("Missing palette " + theme)
	if row["collider"] != null:
		var descriptor: Dictionary = row["collider"]
		for part in descriptor.get("parts",[descriptor]):
			var node := CollisionShape3D.new()
			match part["type"]:
				"convex_hull":
					var shape := ConvexPolygonShape3D.new()
					var points := PackedVector3Array()
					for v in part["points_m"]: points.append(point(v))
					shape.points = points
					node.shape = shape
				"box":
					var shape := BoxShape3D.new()
					shape.size = point(part["size_m"]).abs()
					node.position = point(part["center_m"])
					node.shape = shape
				"cylinder":
					var shape := CylinderShape3D.new()
					shape.radius = float(part["radius_m"])
					shape.height = float(part["height_m"])
					node.position = point(part["center_m"])
					node.shape = shape
				_:
					failures.append("Unknown collider " + str(part["type"]))
			if node.shape != null:
				subject.add_child(node)
				collision_parts += 1
			else: node.free()
	var a: Array = row["bounds_min"]
	var b: Array = row["bounds_max"]
	var lo := Vector3(a[0],a[1],a[2])
	var hi := Vector3(b[0],b[1],b[2])
	var center := (lo+hi)*0.5
	var distance: float = max((hi-lo).length()*1.5, 1.4)
	camera.position = center + Vector3(0.8,0.55,1.0).normalized()*distance
	camera.look_at(center)
	loaded_count += 1

func check_catalog() -> void:
	loaded_count = 0
	collision_parts = 0
	for i in range(entries.size()):
		index = i
		for name in ["MOSS_01","DRY_01","DUSK_01"]:
			theme = name
			show_asset()
		await get_tree().physics_frame
	var report := {"passed":failures.is_empty(),"failures":failures,"models":entries.size(),"theme_loads":loaded_count,"collision_shapes_created_across_themes":collision_parts,"engine":Engine.get_version_info(),"scope":"GLB import, mesh presence, palette binding, collider construction; no contact or GPU test","render_test":"NOT_RUN"}
	var file := FileAccess.open("user://catalog_test.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	print(JSON.stringify(report))
	get_tree().quit(0 if failures.is_empty() else 1)
