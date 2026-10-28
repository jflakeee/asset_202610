from pathlib import Path
import sys,json,hashlib
import numpy as np
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'creation'));from verify_glb import load_glb
records=json.loads((root/'creation/asset_records_output/asset_records.json').read_text())['records'];results=[]
for record in records:
    asset=record['asset_id'];meshes=[load_glb(root/'creation/theme_output'/theme/'models'/f'{asset}_LOD0.glb') for theme in ('MOSS_01','DRY_01','DUSK_01')]
    for mesh in meshes[1:]:
        for key in ('positions','indices','uv'):assert np.array_equal(meshes[0][key],mesh[key]),(asset,key)
        assert meshes[0]['doc']['nodes']==mesh['doc']['nodes'],asset
    results.append(dict(asset_id=asset,passed=True))
out=Path(__file__).resolve().parent/'reports/theme_invariance.json';out.write_text(json.dumps(dict(test='AT10',passed=True,models=len(results),checks='Identical positions/indices/UV/node sockets across three palettes',results=results),indent=2));print('PASS AT10',len(results),'canonical models / 3 themes')
