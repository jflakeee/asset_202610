"""Original double-sided coin with a beveled edge and raised diamond seal."""
from pathlib import Path
import json
import numpy as np
from core import glb
R=Path(__file__).resolve().parent

def part(name,vertices,faces,color):
    return dict(name=name,vertices=vertices,faces=faces,color=color,collider=False)

def build():
    n=16;vertices=[]
    for radius,z in [(.166,-.035),(.18,-.021),(.18,.021),(.166,.035)]:
        vertices.extend([[radius*np.cos(t),.18+radius*np.sin(t),z] for t in np.arange(n)*2*np.pi/n])
    faces=[]
    for ring in range(3):
        for j in range(n):
            a=ring*n+j;b=ring*n+(j+1)%n;c=b+n;d=a+n
            faces.extend([[a,b,c],[a,c,d]])
    # Outward normals on each face are verified below.
    parts=[part('beveled_edge',vertices,faces,'#BA873E')]
    for sign in (-1,1):
        offset=0 if sign==-1 else 3*n
        cap=[vertices[offset+j] for j in range(n)]+[[0,.18,sign*.035]]
        capfaces=[[n,(j+1)%n,j] if sign==-1 else [n,j,(j+1)%n] for j in range(n)]
        parts.append(part('face_front' if sign==-1 else 'face_back',cap,capfaces,'#E4BE62'))
        # A thick diamond ring stays readable without tiny engraved details.
        outer=[(0,.104),(.074,0),(0,-.104),(-.074,0)]
        inner=[(0,.058),(.033,0),(0,-.058),(-.033,0)]
        v=[[x,.18+y,sign*z] for z in (.0348,.0405) for loop in (outer,inner) for x,y in loop]
        f=[]
        for j in range(4):
            k=(j+1)%4
            f.extend([[j,k,4+k],[j,4+k,4+j],[8+j,12+k,8+k],[8+j,12+j,12+k],[j,8+k,k],[j,8+j,8+k],[4+j,4+k,12+k],[4+j,12+k,12+j]])
        # Make each ring face outward using its signed volume orientation.
        vv=np.array(v);ff=np.array(f)
        volume=np.einsum('ij,ij->i',vv[ff[:,0]],np.cross(vv[ff[:,1]],vv[ff[:,2]])).sum()/6
        if volume<0:f=[face[::-1] for face in f]
        parts.append(part('seal_front' if sign==-1 else 'seal_back',v,f,'#845023'))
    return dict(asset_id='currency_coin_quality',components=parts,coordinate_frame='Y-up meters',front='-Z',status='ART_REVIEW_PENDING',external_geometry_inputs=[],material_properties={'BA873E':{'metallic':.8,'roughness':.42},'E4BE62':{'metallic':.8,'roughness':.35},'845023':{'metallic':.65,'roughness':.5}})

if __name__=='__main__':
    a=build()
    for p in a['components']:
        v=np.array(p['vertices']);f=np.array(p['faces'])
        assert np.isfinite(v).all()
        assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
    (R/'currency_coin_quality.json').write_text(json.dumps(a,indent=2))
    (R/'currency_coin_quality.glb').write_bytes(glb(a))
    print('PASS finite/nondegenerate geometry:',sum(len(p['faces']) for p in a['components']),'triangles')
