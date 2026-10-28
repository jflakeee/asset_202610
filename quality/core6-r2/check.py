"""Run after build.py. Checks structure and array values, not official glTF conformance."""
import json,struct
import numpy as np
from build import R,build_all
manifest=json.loads((R/'manifest.json').read_text())
for record in manifest:
    a=build_all()[record['id']]
    for p in a['components']:
        v=np.array(p['vertices']);f=np.array(p['faces']);assert np.isfinite(v).all()
        assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
        if record['id'] in ('ore','rope'):
            edges={}
            for tri in f:
                for i,j in zip(tri,[tri[1],tri[2],tri[0]]):edges[(int(i),int(j))]=edges.get((int(i),int(j)),0)+1
            assert all(n==1 and edges.get((j,i))==1 for (i,j),n in edges.items())
            assert np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()>0
    raw=(R/'models'/f"{record['id']}.glb").read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
    size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
    def array(index):
        acc=doc['accessors'][index];view=doc['bufferViews'][acc['bufferView']];width={'SCALAR':1,'VEC3':3,'VEC4':4}[acc['type']]
        assert view['byteOffset']%4==0 and view['byteOffset']+view['byteLength']<=len(binary)
        result=np.frombuffer(binary,dtype='<f4',count=acc['count']*width,offset=view['byteOffset']).reshape(-1,width)
        assert np.isfinite(result).all();return result
    triangles=0
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            attrs=primitive['attributes'];pos=array(attrs['POSITION']);norm=array(attrs['NORMAL']);color=array(attrs['COLOR_0'])
            assert len(pos)==len(norm)==len(color);assert len(pos)%3==0;triangles+=len(pos)//3
            assert np.allclose(np.linalg.norm(norm,axis=1),1,atol=1e-5);assert ((color>=0)&(color<=1)).all()
    assert triangles==record['triangles'];assert len(doc['materials'])==record['materials']
    if record['animated']:
        assert doc['nodes'][2]['translation']==a['hinge_pivot']
        sampler=doc['animations'][0]['samplers'][0]
        assert np.allclose(array(sampler['input']).ravel(),[0,.6]);assert np.allclose(np.linalg.norm(array(sampler['output']),axis=1),1)
    print('PASS',record['id'])
