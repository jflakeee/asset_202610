"""Run with Blender --background --python build_blends.py -- /path/to/this/folder."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(sys.argv[sys.argv.index('--')+1]).resolve()

# Source uses Y-up meters; Blender uses Z-up. Proper rotation, not reflection.
def coordinate(p):return (p[0],-p[2],p[1])
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4

def material(asset,part,cache):
    color=part['color'].upper();aid=asset['asset_id'];profile='matte'
    if 'coin' in aid or ('chest' in aid and color=='#D6AF4C'):profile='gold'
    elif ('chest' in aid and color=='#42484D') or ('ore' in aid and color=='#B8B5AA'):profile='iron'
    elif 'potion' in aid and color in ('#A73C46','#E2D4AE'):profile='painted'
    key=(color,profile)
    if key in cache:return cache[key]
    rgb=[linear(int(color[i:i+2],16)/255) for i in (1,3,5)]
    m=bpy.data.materials.new(f'{profile}_{color[1:]}');m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1)
    metal,rough={'matte':(0,.9),'painted':(0,.6),'iron':(.65,.55),'gold':(.8,.38)}[profile]
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;cache[key]=m;return m

def light(name,location,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj);obj.location=location
    obj.rotation_euler=(Vector((0,0,.15))-obj.location).to_track_quat('-Z','Y').to_euler()

def build(name,asset):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.render.threads_mode='FIXED';scene.render.threads=8
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.world=bpy.data.worlds.new('NeutralWorld');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.17,.19,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    scene.render.fps=30;scene.frame_start=1;scene.frame_end=19
    source=bpy.data.collections.new('EditableAsset');scene.collection.children.link(source)
    root=bpy.data.objects.new('Trailwood_'+name,None);source.objects.link(root);root['source_id']=asset['asset_id'];root['status']='EDITABLE_REVIEW_PENDING';root['source_coordinates']='Y-up meters converted to Blender Z-up'
    cache={};hinge=None;split=asset.get('lid_component_start',10**9)
    if name=='chest':
        hinge=bpy.data.objects.new('LidHinge',None);source.objects.link(hinge);hinge.parent=root;hinge.location=coordinate(asset['hinge_pivot']);hinge.rotation_mode='XYZ'
        for frame,degrees in [(1,0),(19,105)]:hinge.rotation_euler.x=math.radians(degrees);hinge.keyframe_insert(data_path='rotation_euler',index=0,frame=frame)
        hinge.animation_data.action.name='Chest_Open'
        # Blender 4.5 layered actions expose channel bags rather than legacy action.fcurves.
        for layer in hinge.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
    all_points=[];triangle_count=0
    for index,part in enumerate(asset['components']):
        used=sorted({i for face in part['faces'] for i in face});mapping={old:new for new,old in enumerate(used)}
        vertices=[coordinate(part['vertices'][i]) for i in used];all_points.extend(vertices)
        parent=hinge if hinge is not None and index>=split else root
        if parent==hinge:vertices=[tuple(Vector(v)-hinge.location) for v in vertices]
        faces=[[mapping[i] for i in f] for f in part['faces']];triangle_count+=len(faces)
        mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata(vertices,[],faces);mesh.update()
        obj=bpy.data.objects.new(f'{index:02d}_{part["name"]}',mesh);source.objects.link(obj);obj.parent=parent
        obj.data.materials.append(material(asset,part,cache));obj['source_component']=part['name']
        # Optional, disabled finishing study; base geometry remains the game mesh.
        if name in ('chest','ore'):
            mod=obj.modifiers.new('Optional_edge_finish','BEVEL');mod.width=.0015;mod.segments=1;mod.limit_method='ANGLE';mod.show_viewport=False;mod.show_render=False
    scene.frame_set(1)
    mins=Vector(tuple(min(p[i] for p in all_points) for i in range(3)));maxs=Vector(tuple(max(p[i] for p in all_points) for i in range(3)));center=(mins+maxs)/2;extent=max(maxs-mins)
    camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);scene.collection.objects.link(cam)
    cam.location=center+Vector((1,1,.7)).normalized()*extent*3;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=extent*1.55;scene.camera=cam
    light('Key',(1,2,3),90,3);light('Fill',(-2,1,1.5),50,3);light('Rim',(0,-2,2),60,2)
    bpy.context.view_layer.objects.active=root;root.select_set(True)
    scene['source_triangles']=triangle_count;scene['review_renderer']='Cycles CPU; not mobile GPU benchmark'
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'blend'/f'{name}.blend'),compress=True)
    scene.render.filepath=str(R/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
    if name=='chest':
        scene.frame_set(19);scene.render.filepath=str(R/'renders'/'chest_open.png');bpy.ops.render.render(write_still=True);scene.frame_set(1)
    return dict(id=name,triangles=triangle_count,objects=len(source.objects),materials=len(cache),blend_bytes=(R/'blend'/f'{name}.blend').stat().st_size,optional_bevel_enabled=False)

rows=[]
for path in sorted((R/'inputs').glob('*.json')):
    rows.append(build(path.stem,json.loads(path.read_text())))
    (R/'reports'/'build.json').write_text(json.dumps(dict(blender=bpy.app.version_string,models=rows),indent=2))
print('EDITABLE_SOURCE_BUILD_COMPLETE',rows,flush=True)
