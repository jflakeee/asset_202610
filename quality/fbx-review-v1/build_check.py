"""Blender FBX export and independent re-import. Not a Unity validation."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];R=Path(args[0]).resolve();SOURCE=Path(args[1]).resolve()
def stats():
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[];triangles=0
    for o in meshes:
        o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
        points.extend(o.matrix_world@v.co for v in o.data.vertices)
    materials={}
    for o in meshes:
        for m in o.data.materials:
            if not m:continue
            shader=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
            if shader:materials[m.name]=dict(base_color=list(shader.inputs['Base Color'].default_value),metallic=shader.inputs['Metallic'].default_value,roughness=shader.inputs['Roughness'].default_value)
    return dict(material_values=materials,meshes=len(meshes),triangles=triangles,min=[min(p[i] for p in points) for i in range(3)],max=[max(p[i] for p in points) for i in range(3)],materials=len({m.name for o in meshes for m in o.data.materials if m}))
rows=[]
for name in ('chest','ore','coin','rope','potion','wood'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'blend'/f'{name}.blend'));scene=bpy.context.scene;scene.frame_set(1)
    objects=list(bpy.data.collections['EditableAsset'].objects)
    for o in list(scene.objects):
        if o not in objects:bpy.data.objects.remove(o,do_unlink=True)
    before=stats();bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    scene.name='Chest_Open' if name=='chest' else name
    path=R/'models'/f'{name}.fbx'
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=name=='chest',bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_simplify_factor=0,path_mode='AUTO')
    # Clear data before re-import so source objects/actions cannot satisfy the checks.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps=30
    bpy.ops.import_scene.fbx(filepath=str(path),use_anim=True,anim_offset=0)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();after=stats()
    assert before['meshes']==after['meshes'] and before['triangles']==after['triangles']
    for key in ('min','max'):assert max(abs(a-b) for a,b in zip(before[key],after[key]))<.001
    material_error=0
    assert before['material_values'].keys()==after['material_values'].keys()
    for key,m in before['material_values'].items():
        other=after['material_values'][key]
        material_error=max(material_error,abs(m['metallic']-other['metallic']),abs(m['roughness']-other['roughness']),max(abs(a-b) for a,b in zip(m['base_color'],other['base_color'])))
    row=dict(material_parameter_max_error=material_error,id=name,before=before,after=after,bytes=path.stat().st_size,geometry_bounds_pass=True)
    if name=='chest':
        hinge=bpy.data.objects.get('LidHinge');assert hinge is not None
        bpy.context.scene.frame_set(1);initial=hinge.matrix_local.to_quaternion();angles=[]
        for frame,expected in ((1,0),(10,52.5),(19,105)):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();angle=math.degrees(initial.rotation_difference(hinge.matrix_local.to_quaternion()).angle);assert abs(angle-expected)<.02,(frame,angle);angles.append(angle)
        row['hinge_relative_degrees']=angles;row['animation_pass']=True
    rows.append(row);(R/'reports/roundtrip.json').write_text(json.dumps(dict(blender=bpy.app.version_string,models=rows,passed=len(rows)==6),indent=2));print('PASS',name,flush=True)
