"""Original stylized iron ore. No third-party model inputs."""
from pathlib import Path
import json
import numpy as np
from core import hull, glb
R = Path(__file__).resolve().parent

def build():
    rock = hull('host_rock', [[-.31,0,-.20],[.24,0,-.23],[.33,0,.10],[.12,0,.27],[-.25,0,.22],[-.32,.19,-.06],[-.12,.33,-.16],[.17,.29,-.13],[.28,.20,.11],[.06,.34,.19],[-.20,.27,.15]], '#4C555D')
    parts = [rock]
    # Broad iron-bearing chunks bridge the rock surface, rather than tiny decorative specks.
    for name, center, size, tilt in [
        ('iron_front',[-.08,.27,-.16],[.23,.24,.15],-.20),
        ('iron_crown',[.13,.32,.015],[.18,.26,.17],.30),
        ('iron_rear',[-.10,.27,.15],[.20,.18,.16],-.35)]:
        sx,sy,sz=np.array(size)/2
        points=np.array([[-sx,-sy,-sz],[sx,-sy,-sz],[sx,-sy,sz],[-sx,-sy,sz],[-sx*.7,sy,-sz*.6],[sx*.6,sy,-sz*.8],[sx*.8,sy*.65,sz*.7],[-sx*.7,sy*.8,sz*.8]])
        c,s=np.cos(tilt),np.sin(tilt);rot=np.array([[c,-s,0],[s,c,0],[0,0,1]])
        parts.append(hull(name,points@rot.T+center,'#B5B6AE'))
    return {'asset_id':'resource_iron_ore_quality','components':parts,'coordinate_frame':'Y-up meters','front':'-Z','material_properties':{'B5B6AE':{'metallic':.65,'roughness':.55},'4C555D':{'metallic':0,'roughness':.9}},'status':'ART_REVIEW_PENDING','external_geometry_inputs':[]}

if __name__=='__main__':
    a=build()
    for p in a['components']:
        v=np.array(p['vertices']);f=np.array(p['faces'])
        assert np.isfinite(v).all()
        assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
    (R/'resource_iron_ore_quality.json').write_text(json.dumps(a,indent=2))
    (R/'resource_iron_ore_quality.glb').write_bytes(glb(a))
    print('PASS finite vertices, nondegenerate faces:',sum(len(p['faces']) for p in a['components']),'triangles')
