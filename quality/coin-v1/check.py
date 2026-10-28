"""Source and exported GLB checks; no engine performance or artistic approval implied."""
import json, struct
import numpy as np
from build import build, R

a=build();parts=a['components']
for p in parts:
    v=np.array(p['vertices']);f=np.array(p['faces']);assert np.isfinite(v).all()
    assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
for front,back in [('face_front','face_back'),('seal_front','seal_back')]:
    left=np.array(next(p['vertices'] for p in parts if p['name']==front));right=np.array(next(p['vertices'] for p in parts if p['name']==back))
    assert np.allclose(left*np.array([1,1,-1]),right)
for name,sign in [('face_front',-1),('face_back',1)]:
    p=next(p for p in parts if p['name']==name);v=np.array(p['vertices']);f=np.array(p['faces'])
    assert (np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])[:,2]*sign>0).all()
# Weld the body's shared cap/edge vertices and verify each edge has two opposite uses.
vertices=[];triangles=[]
for p in parts:
    if p['name'].startswith('seal_'):continue
    start=len(vertices);vertices.extend(p['vertices']);triangles.extend((np.array(p['faces'])+start).tolist())
keys=[tuple(np.round(v,8)) for v in vertices];edges={}
for f in triangles:
    for i,j in zip(f,[f[1],f[2],f[0]]):
        edge=(keys[i],keys[j]);edges[edge]=edges.get(edge,0)+1
assert all(count==1 and edges.get((b,a))==1 for (a,b),count in edges.items())
raw=(R/'currency_coin_quality.glb').read_bytes();magic,version,total=struct.unpack_from('<4sII',raw)
assert (magic,version,total)==(b'glTF',2,len(raw))
length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length])
assert len(doc['materials'])==3
assert all(m['pbrMetallicRoughness']['metallicFactor']>=.65 for m in doc['materials'])
assert sum(doc['accessors'][p['attributes']['POSITION']]['count']//3 for p in doc['meshes'][0]['primitives'])==192
print('PASS symmetric faces/seals, outward cap normals, closed oriented body, GLB header/materials/192 triangles')
