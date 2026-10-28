extends SceneTree

func _initialize():
    call_deferred("run_checks")

func run_checks():
    var expected = {"chest":568,"ore":42,"coin":192,"rope":682,"potion":260,"wood":160}
    var rows = []
    var failed = false
    var expected_bounds = JSON.parse_string(FileAccess.get_file_as_string("res://expected_bounds.json"))
    for id in expected:
        var packed = load("res://assets/" + id + ".glb") as PackedScene
        if packed == null:
            rows.append({"id":id,"error":"load_failed"})
            failed = true
            continue
        var instance = packed.instantiate()
        root.add_child(instance)
        var triangles = 0
        var surfaces = 0
        var vertex_color_materials = 0
        var color_arrays = 0
        var material_flags = []
        var bounds = AABB()
        var has_bounds = false
        for node in instance.find_children("*", "MeshInstance3D", true, false):
            var mesh = node.mesh
            var mesh_bounds = node.global_transform * mesh.get_aabb()
            bounds = bounds.merge(mesh_bounds) if has_bounds else mesh_bounds
            has_bounds = true
            for surface in range(mesh.get_surface_count()):
                surfaces += 1
                var arrays = mesh.surface_get_arrays(surface)
                var indices = arrays[Mesh.ARRAY_INDEX]
                var vertices = arrays[Mesh.ARRAY_VERTEX]
                triangles += (indices.size() if indices != null and indices.size() > 0 else vertices.size()) / 3
                var colors = arrays[Mesh.ARRAY_COLOR]
                if colors != null and colors.size() == vertices.size():
                    color_arrays += 1
                var material = node.get_active_material(surface)
                if material is BaseMaterial3D:
                    if material.vertex_color_use_as_albedo:
                        vertex_color_materials += 1
                    material_flags.append({"name":material.resource_name,"vertex_color_use_as_albedo":material.vertex_color_use_as_albedo,"vertex_color_is_srgb":material.vertex_color_is_srgb,"metallic":material.metallic,"roughness":material.roughness})
        var row = {"id":id,"triangles":triangles,"surfaces":surfaces,"color_arrays":color_arrays,"vertex_color_materials":vertex_color_materials,"materials":material_flags,"import_ok":triangles==expected[id] and surfaces==color_arrays}
        if id == "chest":
            var players = instance.find_children("*", "AnimationPlayer", true, false)
            row["animation_ok"] = false
            if players.size() > 0:
                var player = players[0]
                row["animation_names"] = Array(player.get_animation_list())
                if player.has_animation("Chest_Open"):
                    var hinge = instance.find_child("LidHinge", true, false)
                    player.play("Chest_Open")
                    var angles = []
                    for time in [0.0,0.3,0.6]:
                        player.seek(time, true)
                        angles.append(rad_to_deg(hinge.rotation.x))
                    row["hinge_degrees"] = angles
                    row["animation_ok"] = abs(angles[0])<0.1 and abs(angles[1]-52.5)<0.1 and abs(angles[2]-105.0)<0.1
            row["import_ok"] = row["import_ok"] and row["animation_ok"]
        var target = expected_bounds[id]
        var target_min = Vector3(target["min"][0],target["min"][1],target["min"][2])
        var target_size = Vector3(target["size"][0],target["size"][1],target["size"][2])
        row["bounds_min"] = [bounds.position.x,bounds.position.y,bounds.position.z]
        row["bounds_size"] = [bounds.size.x,bounds.size.y,bounds.size.z]
        row["scale_bounds_ok"] = (bounds.position-target_min).length()<0.002 and (bounds.size-target_size).length()<0.002
        row["import_ok"] = row["import_ok"] and row["scale_bounds_ok"]
        row["color_material_ok"] = vertex_color_materials == surfaces
        failed = failed or not row["import_ok"] or not row["color_material_ok"]
        rows.append(row)
        instance.queue_free()
    var report = {"engine":Engine.get_version_info(),"headless":true,"gpu_render_verified":false,"models":rows,"passed":not failed}
    var file = FileAccess.open("res://reports/import.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(report,"  "))
    print(JSON.stringify(report))
    quit(1 if failed else 0)
