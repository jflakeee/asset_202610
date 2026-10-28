"""Original tapered log with planar angled cuts and broad end-grain rings."""
from pathlib import Path
import json
import numpy as np
from core import beam,glb
R=Path(__file__).resolve().parent

def build():
    n=10;angles=np.arange(n)*2*np.pi/n;irregular=np.array([1,.94,1.04,.97,1.02,.93,1.03,.96,1.01,.95])
    vertices=[]
    for x,r in [(-.48,.17),(0,.195),(.47,.155)]:
        for j,t in enumerate(angles):
            y=.195+r*irregular[j]*np.cos(t);z=r*irregular[j]*np.sin(t)
            vertices.append([x+(.12*(y-.195)-.08*z if x<0 else -.10*(y-.195)+.12*z if x>0 else 0),y,z])
    groups={}
    for k in range(2):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;c=b+n;d=a+n
            groups.setdefault('#795437' if j%3 else '#63432F',[]).extend([[a,b,c],[a,c,d]])
    # Build each cut in its own plane so rings cannot float off an angled end.
    for sign,start in [(-1,0),(1,2*n)]:
        edge=np.array(vertices[start:start+n]);center=edge.mean(0);rings=[edge]
        for factor in (.72,.59):rings.append(center+(edge-center)*factor)
        base=len(vertices);vertices.extend(np.concatenate(rings).tolist());center_id=len(vertices);vertices.append(center.tolist())
        for k in range(2):
            for j in range(n):
                a=base+k*n+j;b=base+k*n+(j+1)%n;c=b+n;d=a+n
                faces=[[a,b,c],[a,c,d]]
                if sign<0:faces=[f[::-1] for f in faces]
                groups.setdefault('#C99B62' if k==0 else '#906238',[]).extend(faces)
        for j in range(n):
            f=[center_id,base+2*n+j,base+2*n+(j+1)%n]
            if sign<0:f=f[::-1]
            groups.setdefault('#C99B62',[]).append(f)
    parts=[dict(name='log_'+color[1:],vertices=vertices,faces=faces,color=color,collider=False) for color,faces in groups.items()]
    parts.append(beam('branch_stub',[.06,.30,.015],[.20,.47,.07],.055,'#795437',6,False))
    low=min(np.array(p['vertices'])[:,1].min() for p in parts)
    for p in parts:
        v=np.array(p['vertices']);v[:,1]-=low;p['vertices']=v.tolist()
    return dict(asset_id='resource_wood_quality',components=parts,coordinate_frame='Y-up meters',front='-Z',status='ART_REVIEW_PENDING',external_geometry_inputs=[],material_properties={c:{'metallic':0,'roughness':.9} for c in ('795437','63432F','C99B62','906238')})

if __name__=='__main__':
    a=build();(R/'resource_wood_quality.json').write_text(json.dumps(a,indent=2));(R/'resource_wood_quality.glb').write_bytes(glb(a));print(sum(len(p['faces']) for p in a['components']),'triangles')
