extends SceneTree
func _initialize():
    call_deferred("check")
func check():
    var rows=[]
    var passed=true
    for e in JSON.parse_string(FileAccess.get_file_as_string("res://expected.json")):
        var packed=load("res://assets/"+e["id"]+"_LOD0.glb") as PackedScene
        var node=packed.instantiate()
        root.add_child(node)
        var meshes=node.find_children("*","MeshInstance3D",true,false)
        if node is MeshInstance3D:meshes.append(node)
        var tris=0
        var textures=true
        var imported_points=[]
        var bounds=AABB()
        var first=true
        for mesh_node in meshes:
            var mesh=mesh_node.mesh
            var box=mesh_node.global_transform*mesh.get_aabb()
            bounds=box if first else bounds.merge(box)
            first=false
            for i in range(mesh.get_surface_count()):
                var a=mesh.surface_get_arrays(i)
                for vertex in a[Mesh.ARRAY_VERTEX]:imported_points.append(mesh_node.global_transform*vertex)
                tris+=(a[Mesh.ARRAY_INDEX].size() if a[Mesh.ARRAY_INDEX]!=null and a[Mesh.ARRAY_INDEX].size()>0 else a[Mesh.ARRAY_VERTEX].size())/3
                var m=mesh_node.get_active_material(i)
                textures=textures and m is BaseMaterial3D and m.albedo_texture!=null
        var low=Vector3(e["min"][0],e["min"][1],e["min"][2])
        var high=Vector3(e["max"][0],e["max"][1],e["max"][2])
        var ok=tris==e["triangles"] and textures and (bounds.position-low).length()<0.002 and (bounds.end-high).length()<0.002
        var max_point_error=0.0
        for point in e["positions"]:
            var expected_point=Vector3(point[0],point[1],point[2])
            var nearest=INF
            for actual in imported_points:nearest=min(nearest,expected_point.distance_to(actual))
            max_point_error=max(max_point_error,nearest)
        ok=ok and max_point_error<0.002
        var bodies=node.find_children("*","CollisionObject3D",true,false).size()
        ok=ok and bodies==0
        rows.append({"id":e["id"],"passed":ok,"triangles":tris,"texture_present":textures,"unexpected_collision_objects":bodies,"max_source_vertex_error_m":max_point_error})
        passed=passed and ok
        node.queue_free()
    var report={"test":"AT11","engine":Engine.get_version_info(),"passed":passed,"models":rows,"headless":true,"gpu_visual":"NOT_RUN","physics_traversal":"NOT_RUN"}
    var f=FileAccess.open("res://report.json",FileAccess.WRITE)
    f.store_string(JSON.stringify(report,"  "))
    print(JSON.stringify(report))
    quit(0 if passed else 1)
