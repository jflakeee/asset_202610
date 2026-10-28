import json,struct
import numpy as np
from build import build,R

a=build();parts=a['components'];total=0
for p in parts:
    v=np.array(p['vertices']);f=np.array(p['faces']);total+=len(f)
    assert np.isfinite(v).all()
    assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
# Bottle faces share positions across two material groups. Weld and inspect all edges.
for group in [parts[:2]]+[[p] for p in parts[2:]]:
    edges={};volume=0
    for p in group:
        v=np.array(p['vertices']);f=np.array(p['faces']);keys=[tuple(np.round(x,8)) for x in v]
        volume+=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
        for tri in f:
            for i,j in zip(tri,[tri[1],tri[2],tri[0]]):
                edge=(keys[i],keys[j]);edges[edge]=edges.get(edge,0)+1
    assert all(n==1 and edges.get((b,a))==1 for (a,b),n in edges.items())
    assert volume>0
assert total==260
front=np.array(parts[-2]['vertices']);back=np.array(parts[-1]['vertices'])
assert sorted(map(tuple,np.round(front*np.array([1,1,-1]),8)))==sorted(map(tuple,np.round(back,8)))
raw=(R/'consumable_health_potion_quality.glb').read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);assert len(d['materials'])==4
assert all(m.get('alphaMode','OPAQUE')=='OPAQUE' and m['pbrMetallicRoughness']['baseColorFactor'][3]==1 for m in d['materials'])
print('PASS finite/nondegenerate, closed oriented bottle/components, symmetric symbols, GLB 260 triangles/4 opaque materials')
