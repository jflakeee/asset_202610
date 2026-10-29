"""Run inside Blender; sanitize only path metadata in a new editable copy."""
import bpy,sys,json,hashlib
from pathlib import Path
src,dest,report=map(Path,sys.argv[sys.argv.index('--')+1:])
source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
assert source_sha==json.loads((src.parent/'validation.json').read_text())['blend_sha256']
bpy.ops.wm.open_mainfile(filepath=str(src))
def geometry():
    d={o.name:dict(matrix=[list(row) for row in o.matrix_world],vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],uv=[[list(v.uv) for v in layer.data] for layer in o.data.uv_layers]) for o in bpy.data.objects if o.type=='MESH'}
    return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
before=geometry()
packed_before={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
images=[]
for image in bpy.data.images:
    if image.source in {'GENERATED','VIEWER'}:continue
    if not image.packed_file:image.pack()
    assert image.packed_file
    image.filepath='//../textures/moss.png'
    for packed in image.packed_files:packed.filepath='//../textures/moss.png'
    images.append(image.name)
assert len(images)==1
assert not bpy.data.libraries and not bpy.data.texts
for scene in bpy.data.scenes:scene.render.filepath='//renders/'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True,check_existing=False,relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(dest))
after=geometry()
mesh_count=sum(o.type=='MESH' for o in bpy.data.objects)
assert before==after and mesh_count==84
assert packed_before=={i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
for image in bpy.data.images:
    if image.source not in {'GENERATED','VIEWER'}:
        assert image.packed_file and image.filepath=='//../textures/moss.png'
        assert all(p.filepath=='//../textures/moss.png' for p in image.packed_files)
Path(report).write_text(json.dumps(dict(passed=True,source_sha256=source_sha,mesh_objects=mesh_count,packed_images=images,no_linked_libraries=True,no_text_blocks=True,relative_image_paths=True,relative_packed_file_paths=True,geometry_uv_transforms_unchanged=True,geometry_sha256=after,packed_image_hashes=packed_before,blender_version=bpy.app.version_string,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))
