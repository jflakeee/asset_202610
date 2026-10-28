"""Reopen all .blend files and verify editable mesh and animation data."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]).resolve();rows=[]
for path in sorted((R/'blend').glob('*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(path));a=json.loads((R/'inputs'/f'{path.stem}.json').read_text());objects=list(bpy.data.collections['EditableAsset'].objects)
    meshes=[o for o in objects if o.type=='MESH'];expected=sum(len(p['faces']) for p in a['components']);triangles=0;valid=True
    for obj in meshes:
        assert all(abs(s-1)<1e-7 for s in obj.scale)
        assert len(obj.data.materials)==1 and obj.data.materials[0].use_nodes
        assert not any(m.show_viewport or m.show_render for m in obj.modifiers if m.type=='BEVEL')
        for v in obj.data.vertices:assert all(math.isfinite(x) for x in v.co)
        obj.data.calc_loop_triangles();triangles+=len(obj.data.loop_triangles)
    assert triangles==expected;assert len(meshes)==len(a['components'])
    row=dict(id=path.stem,mesh_objects=len(meshes),triangles=triangles,reopen_ok=True,base_mesh_ok=True)
    if path.stem=='chest':
        hinge=bpy.data.objects['LidHinge'];assert hinge.animation_data.action.name=='Chest_Open';angles=[]
        for frame,expected_angle in [(1,0),(10,52.5),(19,105)]:
            bpy.context.scene.frame_set(frame);angle=math.degrees(hinge.rotation_euler.x);assert abs(angle-expected_angle)<1e-4;angles.append(angle)
        row['hinge_degrees']=angles;row['animation_ok']=True
    rows.append(row)
(R/'reports'/'reopen_checks.json').write_text(json.dumps(dict(blender=bpy.app.version_string,models=rows,passed=True),indent=2));print('ALL_BLEND_REOPEN_CHECKS_PASS',rows,flush=True)
