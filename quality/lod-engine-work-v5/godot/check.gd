extends SceneTree
const Asset = preload("res://lod_asset.gd")
func _initialize():
    call_deferred("check")
func triangles(visual: Node3D) -> int:
    var meshes = visual.find_children("*", "MeshInstance3D", true, false)
    if visual is MeshInstance3D:
        meshes.append(visual)
    var count := 0
    for node in meshes:
        for surface in node.mesh.get_surface_count():
            var arrays = node.mesh.surface_get_arrays(surface)
            var indices = arrays[Mesh.ARRAY_INDEX]
            count += (indices.size() if indices != null and indices.size() > 0 else arrays[Mesh.ARRAY_VERTEX].size()) / 3
    return count
func ray_hits(asset) -> bool:
    if asset.body == null:
        return true
    for collision in asset.body.get_children():
        var bounds = collision.global_transform * collision.shape.get_debug_mesh().get_aabb()
        var center = bounds.get_center()
        var top = bounds.end.y
        var bottom = bounds.position.y
        var query = PhysicsRayQueryParameters3D.create(Vector3(center.x, top + 1.0, center.z), Vector3(center.x, bottom - 1.0, center.z))
        var hit = root.get_world_3d().direct_space_state.intersect_ray(query)
        if hit.is_empty() or hit.collider != asset.body:
            return false
    return true
func check():
    var results := []
    var passed := true
    for entry in JSON.parse_string(FileAccess.get_file_as_string("res://catalog.json")):
        var asset = Asset.new()
        root.add_child(asset)
        asset.setup(entry)
        await physics_frame
        await physics_frame
        var original = asset.collision_snapshot()
        var sockets = asset.sockets(asset.levels[0])
        var ok := true
        var changes := []
        for distance in [0.0, 11.99, 12.0, 29.99, 30.0, 100.0, 0.0]:
            asset.update_distance(distance)
            await physics_frame
            var level: int = asset.active_level
            var visible := 0
            for visual in asset.levels:
                visible += int(visual.visible)
            var same = original == asset.collision_snapshot()
            var socket_same = sockets == asset.sockets(asset.levels[level])
            var count = triangles(asset.levels[level])
            var hit = ray_hits(asset)
            var expected_level = 0 if distance < 12.0 else (1 if distance < 30.0 else 2)
            ok = ok and same and socket_same and visible == 1 and count == entry.triangles[level] and hit and level == expected_level
            changes.append({"distance_m":distance,"level":level,"triangles":count,"collider_unchanged":same,"sockets_unchanged":socket_same,"physics_ray_pass":hit})
        var negative_detected = null
        var disabled_rays_rejected = null
        if asset.body != null:
            for collision in asset.body.get_children():
                collision.disabled = true
            negative_detected = original != asset.collision_snapshot()
            await physics_frame
            await physics_frame
            disabled_rays_rejected = not ray_hits(asset)
            for collision in asset.body.get_children():
                collision.disabled = false
            ok = ok and negative_detected and disabled_rays_rejected
        var socket_mutation_detected = null
        if not sockets.is_empty():
            var path = sockets.keys()[0]
            var socket = asset.levels[1].get_node(path)
            var old_position = socket.position
            socket.position.x += 0.01
            socket_mutation_detected = sockets != asset.sockets(asset.levels[1])
            socket.position = old_position
            ok = ok and socket_mutation_detected
        asset.set_level(-1)
        ok = ok and asset.active_level == 0
        asset.set_level(99)
        ok = ok and asset.active_level == 2
        results.append({"id":entry.id,"passed":ok,"collision_shapes":0 if asset.body == null else asset.body.get_child_count(),"collision_mutation_detected":negative_detected,"disabled_rays_rejected":disabled_rays_rejected,"socket_mutation_detected":socket_mutation_detected,"omission_pending":entry.omission_pending,"transitions":changes})
        passed = passed and ok
        asset.free()
        await physics_frame
    var report = {"passed":passed,"engine":Engine.get_version_info(),"models":results,"headless":true,"gpu_visual":"NOT_RUN","art_approved":false,"omissions_approved":false,"at12_complete":false}
    FileAccess.open("res://report.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
    print("LOD_MODELS=",results.size()," PASS=",passed)
    quit(0 if passed else 1)
