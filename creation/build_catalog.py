"""Build a complete, explicit review catalog; never infer art approval."""
from pathlib import Path
import json, shutil
import numpy as np
from build_rocks import dump
from verify_glb import load_glb

ROOT=Path(__file__).parent
FOLDERS=['wood_props_output','vegetation_output','camp_props_output','path_props_output','furniture_props_output','wood_modules_output','stone_modules_output','natural_catalog_output']

def main():
    project=ROOT.parent/'trailwood_godot'
    (project/'catalog_models').mkdir(parents=True,exist_ok=True)
    descriptors={}
    for folder in FOLDERS:
        path=ROOT/folder/'catalog.json'
        if path.exists():
            for row in json.loads(path.read_text())['assets']:
                descriptors[row['asset_id']]=row.get('collider')
    for key,parts in json.loads((ROOT/'demo_output/colliders.json').read_text())['assets'].items():
        descriptors[key]=dict(type='compound',parts=parts)
    rows=[]
    for path in sorted((ROOT/'theme_output/MOSS_01/models').glob('*_LOD0.glb')):
        asset=path.stem.removesuffix('_LOD0');m=load_glb(path)
        shutil.copyfile(path,project/'catalog_models'/path.name)
        lo=m['positions'].min(0);hi=m['positions'].max(0)
        rows.append(dict(asset_id=asset,file='catalog_models/'+path.name,triangles=len(m['indices'])//3,
            bounds_min=lo.tolist(),bounds_max=hi.tolist(),collider=descriptors.get(asset),
            collider_declared=asset in descriptors,sockets=[n for n in m['doc']['nodes'] if n.get('name','').startswith('SOCKET_')],
            art_approval='PENDING'))
    assert rows and len({r['asset_id'] for r in rows})==len(rows)
    assert all(r['collider_declared'] for r in rows),'Missing collider declaration (null is allowed for decorations)'
    dump(project/'data/full_catalog.json',dict(assets=rows,coordinate_frame='GLB bounds Y-up; collider descriptors source Z-up',purpose='INTERNAL_REVIEW'))
    print(f'Catalog: {len(rows)} models, all collider policies explicit')

if __name__=='__main__':main()
