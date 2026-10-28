import bpy,sys,json,math
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+1]).resolve();rows=[]
for name in ('chest','ore'):
    bpy.ops.wm.open_mainfile(filepath=str(R/'blend'/f'{name}.blend'))
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();triangles=0;enabled=0
    for obj in bpy.data.collections['EditableAsset'].objects:
        if obj.type!='MESH':continue
        enabled+=sum(m.show_viewport and m.show_render for m in obj.modifiers if m.type=='BEVEL')
        evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();triangles+=len(mesh.loop_triangles);evaluated.to_mesh_clear()
    target=json.loads((R/'sources'/f'{name}.json').read_text());assert triangles==sum(len(p['faces']) for p in target['components'])
    row=dict(id=name,evaluated_triangles=triangles,enabled_bevels=enabled,reopen_ok=True)
    if name=='chest':
        hinge=bpy.data.objects['LidHinge'];angles=[]
        for frame,angle in [(1,0),(10,52.5),(19,105)]:
            bpy.context.scene.frame_set(frame);actual=math.degrees(hinge.rotation_euler.x);assert abs(actual-angle)<1e-4;angles.append(actual)
        row['hinge_degrees']=angles
    rows.append(row)
(R/'reports/reopen.json').write_text(json.dumps(dict(blender=bpy.app.version_string,models=rows,passed=True),indent=2));print(rows)
