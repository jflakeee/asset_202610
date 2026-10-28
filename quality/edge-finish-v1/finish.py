"""Blender finishing study. Inputs: previous editable sources; outputs keep base meshes editable."""
import bpy,sys,json,copy
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];R=Path(args[0]).resolve();SOURCE=Path(args[1]).resolve()
records=[]
for name in ('chest','ore'):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'blend'/f'{name}.blend'))
    bpy.context.scene.frame_set(1)
    asset=json.loads((SOURCE/'inputs'/f'{name}.json').read_text());result=copy.deepcopy(asset)
    objects=sorted([o for o in bpy.data.collections['EditableAsset'].objects if o.type=='MESH'],key=lambda o:int(o.name.split('_')[0]))
    assert len(objects)==len(asset['components'])
    changes=[]
    for obj,part in zip(objects,asset['components']):
        component=part['name'];width=0
        if name=='ore':width=.008 if component=='host_rock' else .0035
        elif component in ('side_wall','rim','lid_plank','lid_edge'):width=.006
        elif component in ('corner_guard','lock_plate'):width=.0015
        modifier=obj.modifiers.get('Optional_edge_finish')
        if width:
            if modifier is None:modifier=obj.modifiers.new('Edge_finish','BEVEL')
            modifier.name='Edge_finish';modifier.width=width;modifier.segments=1;modifier.limit_method='ANGLE';modifier.angle_limit=.6;modifier.use_clamp_overlap=True;modifier.show_viewport=True;modifier.show_render=True
            changes.append(dict(component=component,width_m=width))
    bpy.context.view_layer.update();depsgraph=bpy.context.evaluated_depsgraph_get()
    for obj,part in zip(objects,result['components']):
        evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
        vertices=[]
        for vertex in mesh.vertices:
            p=obj.matrix_world@vertex.co;vertices.append([float(p.x),float(p.z),float(-p.y)])
        part['vertices']=vertices;part['faces']=[list(t.vertices) for t in mesh.loop_triangles]
        evaluated.to_mesh_clear()
    result['revision']='EDGE_FINISH_REVIEW_PENDING'
    (R/'sources'/f'{name}.json').write_text(json.dumps(result,indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'blend'/f'{name}.blend'),compress=True)
    bpy.context.scene.render.filepath=str(R/'renders'/f'{name}_after.png');bpy.ops.render.render(write_still=True)
    if name=='chest':
        bpy.context.scene.frame_set(19);bpy.context.scene.render.filepath=str(R/'renders'/'chest_open_after.png');bpy.ops.render.render(write_still=True)
    records.append(dict(id=name,base_triangles=sum(len(p['faces']) for p in asset['components']),finished_triangles=sum(len(p['faces']) for p in result['components']),modified_components=changes))
(R/'reports'/'finish.json').write_text(json.dumps(dict(blender=bpy.app.version_string,models=records),indent=2))
print('FINISH_STUDY_COMPLETE',records,flush=True)
