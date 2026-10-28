"""Original continuous rope coil: connected tube rings, caps only at free ends."""
from pathlib import Path
import json
import numpy as np
from core import glb
R=Path(__file__).resolve().parent

def tube(name, points, radius, color, closed=False, sides=5, reference=(0.,1,0)):
    points=np.array(points,dtype=float);vertices=[];faces=[];count=len(points)
    for i,p in enumerate(points):
        tangent=points[(i+1)%count]-points[(i-1)%count] if closed else points[min(i+1,count-1)]-points[max(i-1,0)]
        tangent/=np.linalg.norm(tangent)
        ref=np.array(reference,dtype=float)
        if abs(tangent@ref)>.9:ref=np.array([1.,0,0])
        u=np.cross(tangent,ref);u/=np.linalg.norm(u);v=np.cross(tangent,u)
        vertices.extend([p+radius*(np.cos(t)*u+np.sin(t)*v) for t in np.arange(sides)*2*np.pi/sides])
    for i in range(count if closed else count-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides;c=((i+1)%count)*sides+(j+1)%sides;d=((i+1)%count)*sides+j
            faces.extend([[a,b,c],[a,c,d]])
    if not closed:
        for j in range(1,sides-1):faces.extend([[0,j+1,j],[(count-1)*sides,(count-1)*sides+j,(count-1)*sides+j+1]])
    vertices=np.array(vertices);f=np.array(faces)
    volume=np.einsum('ij,ij->i',vertices[f[:,0]],np.cross(vertices[f[:,1]],vertices[f[:,2]])).sum()/6
    if volume<0:faces=[x[::-1] for x in faces]
    return dict(name=name,vertices=vertices.tolist(),faces=faces,color=color,collider=False,closed_path=closed,path_samples=count,cross_section_sides=sides)

def build():
    t=np.linspace(0,5.5*np.pi,49)
    points=np.column_stack([.24*np.cos(t),.044+.065*t/(2*np.pi),.24*np.sin(t)])
    coil=tube('continuous_coil',points,.039,'#C99B62')
    t=np.arange(12)*2*np.pi/12
    points=np.column_stack([np.zeros(12),.13+.125*np.sin(t),-.24+.065*np.cos(t)])
    binding=tube('binding_loop',points,.020,'#795437',closed=True,reference=(1.,0,0))
    parts=[coil,binding]
    low=min(np.array(p['vertices'])[:,1].min() for p in parts)
    for p in parts:
        v=np.array(p['vertices']);v[:,1]-=low;p['vertices']=v.tolist()
    return dict(asset_id='material_rope_quality',components=parts,coordinate_frame='Y-up meters',front='-Z',status='ART_REVIEW_PENDING',external_geometry_inputs=[],material_properties={'C99B62':{'metallic':0,'roughness':.9},'795437':{'metallic':0,'roughness':.95}})

if __name__=='__main__':
    a=build();(R/'material_rope_quality.json').write_text(json.dumps(a,indent=2));(R/'material_rope_quality.glb').write_bytes(glb(a))
    print(sum(len(p['faces']) for p in a['components']),'triangles')
