import json,struct
import numpy as np
from build import build,R

a=build();total=0
for group in [a['components'][:-1],a['components'][-1:]]:
    edges={};volume=0
    for p in group:
        v=np.array(p['vertices']);f=np.array(p['faces']);total+=len(f)
        assert np.isfinite(v).all()
        assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
        volume+=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
        keys=[tuple(np.round(x,8)) for x in v]
        for tri in f:
            for i,j in zip(tri,[tri[1],tri[2],tri[0]]):
                edge=(keys[i],keys[j]);edges[edge]=edges.get(edge,0)+1
    assert all(n==1 and edges.get((b,a))==1 for (a,b),n in edges.items())
    assert volume>0
assert total==160
assert abs(min(np.array(p['vertices'])[:,1].min() for p in a['components']))<1e-9
raw=(R/'resource_wood_quality.glb').read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);assert len(d['materials'])==4
assert sum(d['accessors'][p['attributes']['POSITION']]['count']//3 for p in d['meshes'][0]['primitives'])==160
print('PASS finite/nondegenerate, welded closed log/branch, oriented edges, positive volume, floor, GLB 160 triangles/4 materials')
