"""Create editable Blender meshes from the exact 84 canonical Moss GLBs.

Run with Blender's bpy runtime, after the full canonical themed export exists.
This preserves shipped topology, palette UVs and socket transforms. It does not
claim to recover parametric modifiers or authorize art/release approval.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

import bpy

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from design_traceability import FAMILIES


def glb_document(path):
    data = path.read_bytes()
    magic, version, size = struct.unpack_from('<4sII', data)
    if magic != b'glTF' or version != 2 or size != len(data):
        raise ValueError('Invalid GLB header: ' + path.name)
    length, kind = struct.unpack_from('<II', data, 12)
    if kind != 0x4E4F534A:
        raise ValueError('Missing JSON chunk: ' + path.name)
    return json.loads(data[20:20 + length])


def export_sources(root, output, expected_count=84):
    manifest = json.loads((root / 'theme_output/manifest.json').read_text())
    design_ids = sorted(f'TW_{family}_{variant}' for families in FAMILIES.values()
                        for family in families for variant in 'AB')
    if len(design_ids) != expected_count:
        raise ValueError('Design count mismatch')
    entries = {entry['model']: entry for entry in manifest['entries'] if entry['theme'] == 'MOSS_01'}
    selected = []
    for asset in design_ids:
        key = asset + '_LOD0'
        if key not in entries:
            raise ValueError('Canonical model missing: ' + asset)
        entry = entries[key]
        path = root / 'theme_output' / entry['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('GLB hash mismatch: ' + asset)
        doc = glb_document(path)
        sockets = [node['name'] for node in doc.get('nodes', [])
                   if node.get('name', '').startswith('SOCKET_') or node.get('name') == 'HINGE']
        selected.append((asset, path, entry, sockets))
    # No modifications to the current Blender scene until all sources validate.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene['trailwood_design_models'] = expected_count
    scene['trailwood_approval_status'] = 'PENDING'
    scene['trailwood_source_kind'] = 'Editable baked meshes from original procedural GLBs'
    parent = bpy.data.collections.new('Trailwood_Canonical_84')
    scene.collection.children.link(parent)
    records = []
    for index, (asset, path, entry, sockets) in enumerate(selected):
        before = set(bpy.data.objects)
        result = bpy.ops.import_scene.gltf(filepath=str(path))
        if result != {'FINISHED'}:
            raise RuntimeError('glTF import failed: ' + asset)
        objects = set(bpy.data.objects) - before
        meshes = [obj for obj in objects if obj.type == 'MESH']
        if not meshes:
            raise RuntimeError('No editable mesh: ' + asset)
        collection = bpy.data.collections.new(asset)
        parent.children.link(collection)
        collection['asset_id'] = asset
        collection['source_glb_sha256'] = entry['sha256']
        collection['approval_status'] = 'PENDING'
        found_sockets = []
        for obj in objects:
            original_name = obj.name
            # Previous imports have already been namespaced, so exact socket
            # names remain available for this import without .001 ambiguity.
            if original_name in sockets:
                obj['socket_role'] = original_name
                found_sockets.append(original_name)
            obj['asset_id'] = asset
            obj['source_node_name'] = original_name
            obj.name = asset + '__' + original_name
            for old in list(obj.users_collection):
                old.objects.unlink(obj)
            collection.objects.link(obj)
            if obj.type == 'MESH':
                obj.data.name = asset + '__editable_mesh'
                if not obj.data.uv_layers:
                    raise RuntimeError('Palette UV missing: ' + asset)
                if not obj.data.materials:
                    raise RuntimeError('Palette material missing: ' + asset)
        if sorted(found_sockets) != sorted(sockets):
            raise RuntimeError('Socket import mismatch: ' + asset)
        triangles = sum(len(poly.vertices) - 2 for obj in meshes for poly in obj.data.polygons)
        if triangles != entry['triangles']:
            raise RuntimeError('Triangle mismatch: ' + asset)
        # Keep source coordinates unchanged. Toggle a model collection to inspect;
        # moving models into a gallery would alter their designed source pivots.
        collection.hide_viewport = index != 0
        collection.hide_render = index != 0
        records.append(dict(asset_id=asset, editable_mesh_objects=len(meshes),
                            triangles=triangles, sockets=sorted(found_sockets),
                            source_glb_sha256=entry['sha256']))
    # Consolidate the identical embedded Moss palettes. Setting Image.filepath
    # after pack() reloads the image and can silently discard its packed bytes;
    # filepath_raw changes only the saved path, without reloading image data.
    palette_path = root / 'theme_output/palettes/MOSS_01.png'
    palette = bpy.data.images.load(str(palette_path.resolve()), check_existing=False)
    palette.name = 'Trailwood_MOSS_01'
    palette.pack()
    palette.filepath_raw = '//textures/MOSS_01.png'
    for material in bpy.data.materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    node.image = palette
    for image in list(bpy.data.images):
        if image != palette and image.users == 0:
            bpy.data.images.remove(image)
    output.mkdir(parents=True, exist_ok=True)
    blend = (output / 'Trailwood.blend').resolve()
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=False)
    # Reopen the saved file; in-memory construction alone is not sufficient.
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    reopened = {c['asset_id']: c for c in bpy.data.collections if 'asset_id' in c}
    if set(reopened) != set(design_ids):
        raise RuntimeError('Saved collection inventory mismatch')
    for record in records:
        col = reopened[record['asset_id']]
        meshes = [obj for obj in col.objects if obj.type == 'MESH']
        triangles = sum(len(p.vertices) - 2 for obj in meshes for p in obj.data.polygons)
        if triangles != record['triangles'] or any(not obj.data.uv_layers or not obj.data.materials for obj in meshes):
            raise RuntimeError('Reopened mesh/UV/material mismatch: ' + record['asset_id'])
        sockets = sorted(obj['socket_role'] for obj in col.objects if 'socket_role' in obj)
        if sockets != record['sockets']:
            raise RuntimeError('Reopened sockets mismatch: ' + record['asset_id'])
    images = [image for image in bpy.data.images if image.type == 'IMAGE' and image.size[0] > 0]
    if not images or any(not image.packed_file for image in images):
        raise RuntimeError('Saved palette images are not packed')
    palette_hash = hashlib.sha256(palette_path.read_bytes()).hexdigest()
    if any(hashlib.sha256(bytes(image.packed_file.data)).hexdigest() != palette_hash for image in images):
        raise RuntimeError('Saved packed palette differs from shipped PNG')
    report = dict(status='PASS', blender_version=bpy.app.version_string,
                  models=len(reopened), source_format='MOSS_01 LOD0 GLB',
                  editable_meshes=True, parametric_modifiers=False,
                  reopen_validation='PASS', packed_images=len(images),
                  packed_palette_sha256=palette_hash,
                  art_approval='PENDING', gpu_render_test='NOT_RUN',
                  blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),
                  assets=records)
    (output / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'assets'}))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, default=ROOT / 'blender_sources_output')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    export_sources(args.root.resolve(), args.out.resolve())


if __name__ == '__main__':
    main()
