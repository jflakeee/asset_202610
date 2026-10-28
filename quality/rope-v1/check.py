"""Geometry/export checks; not a self-intersection or engine performance test."""
import json,struct
import numpy as np
from build import build,R

a=build();total=0
for p in a['components']:
    v=np.array(p['vertices']);f=np.array(p['faces']);total+=len(f)
    assert np.isfinite(v).all()
    assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
    edges={}
    for tri in f:
        for i,j in zip(tri,[tri[1],tri[2],tri[0]]):edges[(int(i),int(j))]=edges.get((int(i),int(j)),0)+1
    assert all(n==1 and edges.get((j,i))==1 for (i,j),n in edges.items()),p['name']
    volume=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
    assert volume>0
    expected=2*(p['path_samples'] if p['closed_path'] else p['path_samples']-1)*p['cross_section_sides']
    if not p['closed_path']:expected+=2*(p['cross_section_sides']-2)
    assert len(f)==expected
assert total==606
assert abs(min(np.array(p['vertices'])[:,1].min() for p in a['components']))<1e-9
raw=(R/'material_rope_quality.glb').read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);assert len(d['materials'])==2
assert sum(d['accessors'][p['attributes']['POSITION']]['count']//3 for p in d['meshes'][0]['primitives'])==606
print('PASS finite/nondegenerate, closed oriented components, positive volumes, cap counts, floor, GLB 606 triangles/2 materials')
