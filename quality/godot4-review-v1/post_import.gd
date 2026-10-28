@tool
extends EditorScenePostImport

# GLB COLOR_0 is linear. Preserve that encoding and explicitly enable its use.
func _post_import(scene):
    for node in scene.find_children("*", "MeshInstance3D", true, false):
        var mesh = node.mesh
        for surface in range(mesh.get_surface_count()):
            var arrays = mesh.surface_get_arrays(surface)
            var colors = arrays[Mesh.ARRAY_COLOR]
            var material = mesh.surface_get_material(surface)
            if colors != null and colors.size() > 0 and material is BaseMaterial3D:
                var fixed = material.duplicate()
                fixed.vertex_color_use_as_albedo = true
                fixed.vertex_color_is_srgb = false
                mesh.surface_set_material(surface, fixed)
    return scene
