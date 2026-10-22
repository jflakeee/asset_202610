extends CharacterBody3D

var manual_input: bool = true
var scripted_direction := Vector3.ZERO
var touch_direction := Vector3.ZERO
var speed: float = 2.5

func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	floor_snap_length = 0.15
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.25
	capsule.height = 1.6
	var shape := CollisionShape3D.new()
	shape.shape = capsule
	shape.position.y = 0.8
	add_child(shape)
	var visual := MeshInstance3D.new()
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.25
	mesh.height = 1.6
	visual.mesh = mesh
	visual.position.y = 0.8
	var material := StandardMaterial3D.new()
	material.albedo_color = Color("dd914d")
	visual.material_override = material
	add_child(visual)

func _physics_process(delta: float) -> void:
	var direction := scripted_direction
	if manual_input:
		var axes := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
		direction = Vector3(axes.x, 0, axes.y) + touch_direction
	if direction.length_squared() > 1.0:
		direction = direction.normalized()
	velocity.x = direction.x * speed
	velocity.z = direction.z * speed
	if not is_on_floor():
		velocity.y -= 9.8 * delta
	else:
		velocity.y = 0.0
	move_and_slide()

func reset_at(point: Vector3) -> void:
	position = point
	velocity = Vector3.ZERO
	scripted_direction = Vector3.ZERO
	touch_direction = Vector3.ZERO
