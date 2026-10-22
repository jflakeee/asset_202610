"""Geometry-level sampling of the wind deformation. Not a GPU shader test."""
from pathlib import Path
import math
import numpy as np
from verify_glb import load_glb
from build_rocks import dump

ROOT=Path(__file__).parent
reports=[]
for path in sorted((ROOT/'vegetation_output/models').glob('*.glb')):
    m=load_glb(path);v=m['positions'].astype(float);faces=m['indices'].reshape(-1,3)
    height=float(v[:,1].max());amp=.08 if 'GRASS' in path.name else .03
    anchored=np.isclose(v[:,1],0,atol=1e-7);maximum=0.;min_area=float('inf')
    assert anchored.any()
    for phase in np.linspace(0,2*math.pi,129):
        for strength in [0.,.4,1.]:
            displaced=v.copy();h=np.clip(v[:,1]/height,0,1)
            displaced[:,0]+=amp*strength*h*h*math.sin(phase)
            displaced[:,2]+=amp*strength*h*h*.35*math.sin(2*phase+.7)
            assert np.array_equal(displaced[anchored],v[anchored])
            if strength==0:assert np.array_equal(displaced,v)
            delta=displaced-v;maximum=max(maximum,float(np.linalg.norm(delta,axis=1).max()))
            assert np.max(np.abs(delta[:,0]))<=amp+1e-9 and np.max(np.abs(delta[:,2]))<=.35*amp+1e-9
            assert np.array_equal(displaced[:,1],v[:,1])
            p=displaced[faces];area=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)/2
            min_area=min(min_area,float(area.min()));assert area.min()>1e-10
    reports.append(dict(asset_id=path.stem,phase_samples=129,strength_samples=3,anchored_split_vertices=int(anchored.sum()),max_sampled_displacement_m=maximum,min_deformed_triangle_area_m2=min_area,cull_margin_m=.1,cull_margin_covers_bound=.1>=amp*math.sqrt(1+.35**2),status='PASS'))
dump(ROOT.parent/'trailwood_godot/wind_geometry_validation.json',dict(scope='CPU sampling of actual exported vertices, not GPU rendering',assets=reports))
print(reports)
