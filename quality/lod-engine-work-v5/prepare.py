"""Prepare a disposable native Godot review project from checked canonical files."""
from pathlib import Path
import json,sys,shutil,hashlib,argparse
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('root',type=Path);parser.add_argument('lod',type=Path);parser.add_argument('--colliders',type=Path);args=parser.parse_args()
root=args.root.resolve();lod=args.lod.resolve();out=R/'godot';assets=out/'assets';assets.mkdir(exist_ok=True)
cat={a['asset_id']:a for a in json.loads((root/'trailwood_godot/data/full_catalog.json').read_text())['assets']}
overrides={}
if args.colliders:
    proxy=json.loads(args.colliders.read_text())
    assert proxy['schema_version']=='1.0' and proxy['coordinate_frame']=='SOURCE_Z_UP'
    assert proxy['source_catalog_sha256']==hashlib.sha256((root/'trailwood_godot/data/full_catalog.json').read_bytes()).hexdigest()
    overrides=proxy['overrides'];expected={aid for aid in cat if aid.startswith(('TW_TREE_','TW_ROCK_'))}
    canonical={r['asset_id'] for r in json.loads((root/'creation/asset_records_output/asset_records.json').read_text())['records']}
    assert set(overrides)==expected & canonical and len(overrides)==24
    for aid in overrides:
        assert proxy['source_model_sha256'][aid]==hashlib.sha256((root/'creation/theme_output/MOSS_01/models'/f'{aid}_LOD0.glb').read_bytes()).hexdigest()
rows=[]
for m in json.loads((lod/'reports/catalog.json').read_text())['models']:
    aid=m['asset_id'];src=root/'creation/theme_output/MOSS_01/models'/f'{aid}_LOD0.glb'
    assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
    shutil.copy2(src,assets/src.name);files=[src.name];triangles=[m['lod0_triangles']];fallback=[]
    for e in m['levels']:
        if 'file' in e:
            src=lod/e['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==e['sha256'];shutil.copy2(src,assets/src.name);files.append(src.name);triangles.append(e['triangles']);fallback.append(False)
        else:files.append(files[-1]);triangles.append(triangles[-1]);fallback.append(True)
    boundary=aid.startswith(('TW_WOOD_','TW_STONE_'))
    rows.append(dict(id=aid,files=files,triangles=triangles,omission_pending=fallback,collider=overrides.get(aid,cat[aid].get('collider')),proxy_revision='V8' if aid in overrides else 'ORIGINAL',distances=[18.,40.] if boundary else [12.,28.],grass_cull=25. if aid.startswith('TW_VEG_GRASS_') else 0.))
# These keys were obtained from official4.7.2's actual generated import files.
for path in assets.glob('*.glb'):
    settings=path.with_suffix(path.suffix+'.import')
    text=settings.read_text() if settings.exists() else '[remap]\nimporter="scene"\ntype="PackedScene"\n[params]\nmeshes/generate_lods=true\n'
    assert 'meshes/generate_lods=' in text
    import re
    text=re.sub(r'meshes/generate_lods=(true|false)', 'meshes/generate_lods=false', text)
    settings.write_text(text)
assert len(rows)==84
(out/'proxy_manifest.json').write_text(json.dumps(dict(sha256=hashlib.sha256(args.colliders.read_bytes()).hexdigest() if args.colliders else None,overridden_models=len(overrides))))
(out/'catalog.json').write_text(json.dumps(rows,indent=2))
(out/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Trailwood LOD collider review"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
print('Prepared',len(rows),'models; unique files',len(list(assets.glob('*.glb'))))
