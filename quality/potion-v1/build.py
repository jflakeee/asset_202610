"""Opaque mobile-friendly potion with readable fill band and droplet seal."""
from pathlib import Path
import json
import numpy as np
from core import hull,glb
R=Path(__file__).resolve().parent

def build():
    n=12;profiles=[(0,.09),(.035,.135),(.09,.16),(.255,.15),(.32,.10),(.35,.065),(.405,.065)]
    vertices=[[r*np.cos(t),y,r*np.sin(t)] for y,r in profiles for t in np.arange(n)*2*np.pi/n+np.pi/12]
    groups={}
    for i in range(len(profiles)-1):
        color='#A73C46' if i<3 else '#E2D4AE'
        faces=groups.setdefault(color,[])
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;c=b+n;d=a+n
            faces.extend([[a,c,b],[a,d,c]])
    # Bottom and top caps use existing ring vertices (no interior ring caps).
    for j in range(1,n-1):
        groups.setdefault('#A73C46',[]).append([0,j,j+1])
        start=(len(profiles)-1)*n;groups.setdefault('#E2D4AE',[]).append([start,start+j+1,start+j])
    parts=[dict(name='bottle_'+color[1:],vertices=vertices,faces=faces,color=color,collider=False) for color,faces in groups.items()]
    for name,y0,y1,r,color in [('neck_binding',.365,.40,.073,'#795437'),('cork',.397,.465,.057,'#B88952')]:
        pts=[[r*np.cos(t),y,r*np.sin(t)] for y in (y0,y1) for t in np.arange(8)*np.pi/4]
        parts.append(hull(name,pts,color,False))
    # Raised droplet silhouette on both broad faces, no medical/trademark symbol.
    outline=[(0,.065),(.045,-.012),(.03,-.048),(0,-.059),(-.03,-.048),(-.045,-.012)]
    for sign in (-1,1):
        pts=[[x,.18+y,sign*z] for z in (.149,.158) for x,y in outline]
        parts.append(hull('droplet_front' if sign<0 else 'droplet_back',pts,'#E2D4AE',False))
    return dict(asset_id='consumable_health_potion_quality',components=parts,coordinate_frame='Y-up meters',front='-Z',status='ART_REVIEW_PENDING',external_geometry_inputs=[],material_properties={'A73C46':{'metallic':0,'roughness':.5},'E2D4AE':{'metallic':0,'roughness':.65},'795437':{'metallic':0,'roughness':.9},'B88952':{'metallic':0,'roughness':.95}})

if __name__=='__main__':
    a=build();(R/'consumable_health_potion_quality.json').write_text(json.dumps(a,indent=2));(R/'consumable_health_potion_quality.glb').write_bytes(glb(a));print(sum(len(p['faces']) for p in a['components']),'triangles')
