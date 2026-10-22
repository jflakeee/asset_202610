"""Independent reader/structural and mesh checks for the exported prototype GLBs.
Not a substitute for Khronos validation or target-engine testing.
"""
import hashlib
import io
import json
from collections import Counter
import struct
import numpy as np
from PIL import Image


def load_glb(path):
    data=path.read_bytes()
    magic,version,length=struct.unpack_from('<4sII',data)
    assert magic==b'glTF' and version==2 and length==len(data)
    jlen,jtype=struct.unpack_from('<I4s',data,12)
    assert jtype==b'JSON' and jlen%4==0
    doc=json.loads(data[20:20+jlen])
    blen,btype=struct.unpack_from('<I4s',data,20+jlen)
    assert btype==b'BIN\0' and blen%4==0
    blob=data[28+jlen:]
    assert len(blob)==blen and doc['buffers'][0]['byteLength']<=blen
    for view in doc['bufferViews']:
        assert view.get('byteOffset',0)%4==0
        assert view.get('byteOffset',0)+view['byteLength']<=doc['buffers'][0]['byteLength']
    def access(i):
        a=doc['accessors'][i]; view=doc['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5123:'<u2'}[a['componentType']]
        width={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']]
        offset=view.get('byteOffset',0)+a.get('byteOffset',0)
        assert a.get('byteOffset',0)+a['count']*width*np.dtype(dtype).itemsize<=view['byteLength']
        return np.frombuffer(blob,dtype=dtype,count=a['count']*width,offset=offset).reshape(-1,width)
    prim=doc['meshes'][0]['primitives'][0]
    p=access(prim['attributes']['POSITION']); n=access(prim['attributes']['NORMAL']); uv=access(prim['attributes']['TEXCOORD_0']); ix=access(prim['indices']).ravel().astype(int)
    image=doc['images'][0]; view=doc['bufferViews'][image['bufferView']]
    assert image['mimeType']=='image/png' and 'uri' not in image
    png=blob[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
    im=Image.open(io.BytesIO(png)); im.load()
    return dict(doc=doc,positions=p,normals=n,uv=uv,indices=ix,image=im,png=png)


def verify_all(out,recipes):
    results=[]
    for r in recipes:
        path=out/'models'/f"{r['asset_id']}_LOD0.glb"
        try:
            m=load_glb(path); p=m['positions']; ix=m['indices']; n=m['normals']; uv=m['uv']
            assert np.isfinite(p).all() and np.isfinite(n).all() and np.isfinite(uv).all()
            assert len(ix)%3==0 and ix.min()>=0 and ix.max()<len(p)
            tri=p[ix].reshape(-1,3,3)
            cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); area=np.linalg.norm(cross,axis=1)/2
            assert area.min()>1e-10 and len(tri)<=800
            assert np.allclose(np.linalg.norm(n,axis=1),1,atol=1e-5)
            assert np.all(np.sum(cross*n[ix.reshape(-1,3)[:,0]],axis=1)>0)
            assert np.allclose(p.max(0)-p.min(0),np.array(r['size_m'])[[0,2,1]],atol=1e-6)
            assert abs(float(p[:,1].min()))<1e-6
            assert np.allclose((p.min(0)+p.max(0))[[0,2]],0,atol=1e-6)
            assert uv.min()>=0 and uv.max()<=1 and m['image'].size==(256,256)
            expected_slots={8,9,10,11}
            assert set((np.floor(uv[:,1]*4)*8+np.floor(uv[:,0]*8)).astype(int)).issubset(expected_slots)
            # Weld split normal/UV vertices for topology checks.
            unique,inverse=np.unique(p,axis=0,return_inverse=True); wf=inverse[ix].reshape(-1,3)
            edges=Counter(tuple(sorted((int(a),int(b)))) for f in wf for a,b in zip(f,np.roll(f,-1)))
            assert all(v==2 for v in edges.values())
            assert len(unique)-len(edges)+len(wf)==2
            volume=float(np.sum(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])))/6)
            assert volume>0
            doc=m['doc']; mat=doc['materials'][0]
            assert len(doc['materials'])==1 and len(doc['images'])==1 and mat.get('doubleSided',False)==False
            assert mat['pbrMetallicRoughness']['baseColorTexture']['index']==0
            assert not any('uri' in x for x in doc['buffers']+doc['images'])
            assert m['png']==(out/'textures'/'MOSS_01.png').read_bytes()
            results.append(dict(asset_id=r['asset_id'],status='PASS',triangles=len(tri),welded_vertices=len(unique),volume_m3=volume,min_area_m2=float(area.min()),checks=['GLB binary bounds','finite positions/normals/UV','unit normals and outward winding','target metric dimensions','ground pivot','closed 2-manifold edges','Euler characteristic 2','embedded PNG and UV slots','one opaque single-sided material']))
        except Exception as e:
            results.append(dict(asset_id=r['asset_id'],status='FAIL',error=repr(e)))
    return dict(status='PASS' if all(r['status']=='PASS' for r in results) else 'FAIL',assets=results,engine_import='NOT_RUN',mobile_benchmark='NOT_RUN',art_approval='PENDING',lod_and_collider='NOT_IMPLEMENTED')
