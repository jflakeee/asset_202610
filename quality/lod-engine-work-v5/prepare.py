"""Prepare a disposable native Godot review project from checked canonical files."""
from pathlib import Path
import json,sys,shutil,hashlib
R=Path(__file__).resolve().parent
root=Path(sys.argv[1]).resolve();lod=Path(sys.argv[2]).resolve();out=R/'godot';assets=out/'assets';assets.mkdir(exist_ok=True)
cat={a['asset_id']:a for a in json.loads((root/'trailwood_godot/data/full_catalog.json').read_text())['assets']}
rows=[]
for m in json.loads((lod/'reports/catalog.json').read_text())['models']:
    aid=m['asset_id'];src=root/'creation/theme_output/MOSS_01/models'/f'{aid}_LOD0.glb'
    assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
    shutil.copy2(src,assets/src.name);files=[src.name];triangles=[m['lod0_triangles']];fallback=[]
    for e in m['levels']:
        if 'file' in e:
            src=lod/e['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==e['sha256'];shutil.copy2(src,assets/src.name);files.append(src.name);triangles.append(e['triangles']);fallback.append(False)
        else:files.append(files[-1]);triangles.append(triangles[-1]);fallback.append(True)
    rows.append(dict(id=aid,files=files,triangles=triangles,omission_pending=fallback,collider=cat[aid].get('collider')))
assert len(rows)==84
(out/'catalog.json').write_text(json.dumps(rows,indent=2))
(out/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Trailwood LOD collider review"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
print('Prepared',len(rows),'models; unique files',len(list(assets.glob('*.glb'))))
