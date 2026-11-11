extends SceneTree
const Asset = preload("res://lod_asset.gd")
func _initialize(): call_deferred("run")
func run():
    var rows: Array = []
    var switches := 0
    for entry in JSON.parse_string(FileAccess.get_file_as_string("res://manifest.json")):
        var item = Asset.new()
        root.add_child(item)
        item.setup(entry)
        var snapshot = item.collision_snapshot()
        var expected := [0,0,1,1,2,2,0]
        var path := [0.0,17.99,18.0,39.99,40.0,100.0,0.0]
        for step in range(path.size()):
            item.update_distance(path[step])
            assert(item.active_level == expected[step])
            for i in range(3): assert(item.levels[i].visible == (i == expected[step]))
            assert(item.collision_snapshot() == snapshot)
            switches += 1
        for level in range(3):
            var meshes = item.levels[level].find_children("*","MeshInstance3D",true,false)
            if item.levels[level] is MeshInstance3D: meshes.append(item.levels[level])
            assert(not meshes.is_empty())
            var triangles := 0
            for mesh in meshes:
                for surface in range(mesh.mesh.get_surface_count()):
                    var arrays = mesh.mesh.surface_get_arrays(surface)
                    triangles += arrays[Mesh.ARRAY_INDEX].size()/3
                    for point in arrays[Mesh.ARRAY_VERTEX]: assert(point.is_finite())
                    var mat = mesh.get_active_material(surface)
                    assert(mat is BaseMaterial3D and mat.albedo_texture != null)
                    assert(RenderingServer.mesh_get_surface(mesh.mesh.get_rid(),surface).get("lods",[]).is_empty())
            assert(triangles == entry.triangles[level])
        item.configure_for_camera(true)
        assert(item.levels[0].visible and not item.levels[1].visible and not item.levels[2].visible)
        assert(item.collision_snapshot() == snapshot)
        rows.append({"asset":entry.id,"theme":entry.theme,"passed":true})
        item.free()
    var result := {"engine":Engine.get_version_info().string,"entries":rows.size(),"logical_scenes":rows.size()*3,"transition_samples":switches,"passed":true,"checks":rows,"graphics_rendered":false,"contact_physics_tested":false,"art_approved":false}
    var file := FileAccess.open("res://engine_report.json",FileAccess.WRITE)
    file.store_string(JSON.stringify(result,"  ")+"\n")
    file.close()
    print("RECOVERY_ENGINE_PASS entries=",rows.size()," transitions=",switches)
    quit()
