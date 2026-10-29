extends Node3D
# Review candidates only. Missing reductions retain the nearest higher-detail model.
var levels: Array[Node3D] = []
var active_level := -1
var body: StaticBody3D
var distances := [12.0, 28.0]
var grass_cull := 0.0
func setup(entry: Dictionary):
    distances = entry.distances
    grass_cull = entry.grass_cull
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
            elif part.type == "capsule":
                var first = part.endpoints_m[0]
                var second = part.endpoints_m[1]
                var a = Vector3(first[0], first[2], -first[1])
                var b = Vector3(second[0], second[2], -second[1])
                var shape := CapsuleShape3D.new()
                shape.radius = part.radius_m
                shape.height = a.distance_to(b) + 2.0 * part.radius_m
                collision.shape = shape
                collision.position = (a + b) / 2.0
                if a.distance_to(b) > 0.000001:
                    collision.quaternion = Quaternion(Vector3.UP, (b - a).normalized())
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
            if part.has("margin_m"):
                collision.shape.margin = part.margin_m
            body.add_child(collision)
    set_level(0)
func set_level(level: int):
    active_level = clampi(level, 0, 2)
    for i in levels.size():
        levels[i].visible = i == active_level
func update_distance(distance_m: float):
    set_level(0 if distance_m < distances[0] else (1 if distance_m < distances[1] else 2))
    if grass_cull > 0.0 and distance_m >= grass_cull:
        for visual in levels: visual.visible = false
func collision_snapshot() -> Array:
    var result := []
    if body == null:
        return result
    result.append([body.get_instance_id(), body.global_transform, body.collision_layer, body.collision_mask])
    for child in body.get_children():
        result.append([child.get_instance_id(), child.shape.get_instance_id(), child.disabled, child.global_transform, child.shape.margin, shape_data(child.shape)])
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
    if shape is CapsuleShape3D:
        return [shape.radius, shape.height]
    if shape is CylinderShape3D:
        return [shape.radius, shape.height]
    return null

func configure_for_camera(orthographic: bool):
    # Orthographic size does not shrink with camera distance: fixed LOD0.
    for i in levels.size():
        levels[i].visible = not orthographic or i == 0
        var meshes = levels[i].find_children("*", "MeshInstance3D", true, false)
        if levels[i] is MeshInstance3D: meshes.append(levels[i])
        for mesh in meshes:
            mesh.visibility_range_begin = 0.0 if orthographic or i == 0 else distances[i-1]
            var end = 0.0 if i == 2 else distances[i]
            if grass_cull > 0.0: end = grass_cull if end == 0.0 else minf(end, grass_cull)
            mesh.visibility_range_end = 0.0 if orthographic else end
            # A grass level beginning beyond cull distance must remain hidden.
            if not orthographic and grass_cull > 0.0 and mesh.visibility_range_begin >= grass_cull:
                levels[i].visible = false
                mesh.visibility_range_begin = 0.0
            mesh.visibility_range_begin_margin = 0.0
            mesh.visibility_range_end_margin = 0.0
            mesh.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
