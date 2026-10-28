from pathlib import Path
import json,hashlib,sys
import numpy as np
first,second,repo=map(lambda p:Path(p).resolve(),sys.argv[1:4]);sys.path.insert(0,str(repo/'creation'));from verify_glb import load_glb;from release_controls import geometry_hash
for p in (first,second):assert json.loads((p/'rebuild_report.json').read_text())['status']=='PASS'
for path in (first/'creation').glob('*.py'):assert path.read_bytes()==(second/'creation'/path.name).read_bytes()
def hashes(root):return {p.relative_to(root/'creation/theme_output').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'creation/theme_output').glob('*/models/*.glb')}
a,b=hashes(first),hashes(second);assert a==b and len(a)==327
records=json.loads((repo/'creation/asset_records_output/asset_records.json').read_text())['records'];rows=[]
for record in records:
 id=record['asset_id'];name='creation/theme_output/MOSS_01/models/'+id+'_LOD0.glb';x,y=load_glb(first/name),load_glb(second/name);hx,hy=geometry_hash(x),geometry_hash(y);assert hx==hy
 assert np.array_equal(x['positions'].min(0),y['positions'].min(0)) and np.array_equal(x['positions'].max(0),y['positions'].max(0))
 rows.append(dict(id=id,normalized_geometry_sha256=hx,triangles=len(x['indices'])//3))
R=Path(__file__).resolve().parent;(R/'reports/rebuild_repeat.json').write_text(json.dumps(dict(test='AT07',passed=True,fresh_builds=2,byte_identical_glbs=327,canonical_normalized_geometry_and_bounds=84,models=rows),indent=2));print('PASS AT07: 2 fresh builds, 327 byte-identical GLBs, 84 normalized geometry hashes and bounds')
