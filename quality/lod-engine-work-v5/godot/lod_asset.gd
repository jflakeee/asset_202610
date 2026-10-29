extends Node3D
# Review candidates only. Missing reductions retain the nearest higher-detail model.
var levels: Array[Node3D] = []
var active_level := -1
var body: StaticBody3D
func setup(entry: Dictionary):
    for file in entry.files:
        var visual = load("res://assets/" + file).instantiate() as Node3D
        add_child(visual)
        levels.append(visual)
    if entry.collider != null:
        body = StaticBody3D.new()
        add_child(body)
        var desc: Dictionary = entry.collider
        var parts = desc.parts if desc.type == "compound" else [desc]
        for part in parts:
            var collision := CollisionShape3D.new()
            if part.type == "convex_hull":
                var points := PackedVector3Array()
                for p in part.points_m:
                    points.append(Vector3(p[0], p[2], -p[1]))
                var shape := ConvexPolygonShape3D.new()
                shape.points = points
                collision.shape = shape
            elif part.type == "box":
                var shape := BoxShape3D.new()
                var size = part.size_m
                shape.size = Vector3(size[0], size[2], size[1])
                collision.shape = shape
            elif part.type == "cylinder":
                assert(part.axis == "Z")
                var shape := CylinderShape3D.new()
                shape.radius = part.radius_m
                shape.height = part.height_m
                collision.shape = shape
            else:
                push_error("Unsupported collider " + str(part.type))
                assert(false)
            if part.has("center_m"):
                var p = part.center_m
                collision.position = Vector3(p[0], p[2], -p[1])
            body.add_child(collision)
    set_level(0)
func set_level(level: int):
    active_level = clampi(level, 0, 2)
    for i in levels.size():
        levels[i].visible = i == active_level
func update_distance(distance_m: float):
    set_level(0 if distance_m < 12.0 else (1 if distance_m < 30.0 else 2))
func collision_snapshot() -> Array:
    var result := []
    if body == null:
        return result
    result.append([body.get_instance_id(), body.global_transform, body.collision_layer, body.collision_mask])
    for child in body.get_children():
        result.append([child.get_instance_id(), child.shape.get_instance_id(), child.disabled, child.global_transform, shape_data(child.shape)])
    return result
func sockets(visual: Node3D) -> Dictionary:
    var result := {}
    for node in visual.find_children("*", "Node3D", true, false):
        if node.name.begins_with("SOCKET_") or node.name.begins_with("HINGE"):
            result[str(visual.get_path_to(node))] = node.global_transform
    return result

func shape_data(shape: Shape3D):
    if shape is ConvexPolygonShape3D:
        return shape.points
    if shape is BoxShape3D:
        return shape.size
    if shape is CylinderShape3D:
        return [shape.radius, shape.height]
    return null
