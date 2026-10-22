"""Assemble original Trailwood meshes and export reviewable collision descriptors."""
from pathlib import Path
import json
import shutil
import hashlib
import numpy as np
from scipy.spatial import ConvexHull
from build_rocks import dump,write_glb,palette_bytes
from verify_glb import load_glb

ROOT=Path(__file__).parent
OUT=ROOT/'demo_output'

def collect():
    sources={}
    for folder in ['output','trees_output_v2','fences_output']:
        for p in (ROOT/folder/'models').glob('*.glb'):sources[p.stem.removesuffix('_LOD0')]=p
    sources['TW_TERMINAL_POST']=ROOT/'fences_output/fixtures/TW_TERMINAL_POST.glb'
    assert len(sources)==7
    return sources

def placements():
    items=[]
    def add(asset,x,y,yaw=0):items.append(dict(id=f'instance_{len(items):02}',asset_id=asset,position_m=[x,y,0],yaw_degrees=yaw))
    for x in [-5,-3,-1,1,3]:add('TW_WOOD_RAIL_2M_A',x,3.2)
    add('TW_TERMINAL_POST',5,3.2)
    for x in [-5,-4]:add('TW_WOOD_RAIL_1M_A',x,-3.2)
    add('TW_TERMINAL_POST',-3,-3.2)
    for x,y,yaw in [(-4,1.5,20),(-1.6,1.7,75),(3.8,1.7,130)]:add('TW_TREE_ROUND_SMALL_A',x,y,yaw)
    for x,y,yaw in [(-3.2,-1.8,35),(1.3,1.9,110),(3.5,-1.8,190)]:add('TW_TREE_TIERED_SLIM_A',x,y,yaw)
    for x,y,yaw in [(-4.5,-1.5,0),(-.7,-1.7,35),(4.8,-1.5,80)]:add('TW_ROCK_LOW_WEDGE_A',x,y,yaw)
    for x,y,yaw in [(-2.5,1.2,40),(2.3,-1.8,120)]:add('TW_ROCK_UPRIGHT_A',x,y,yaw)
    return items

def read_source(path):
    m=load_glb(path);v=m['positions'][:,[0,2,1]]*np.array([1,-1,1])
    f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
    slots=(np.floor(uv[:,1]*4)*8+np.floor(uv[:,0]*8)).astype(int)
    assert m['png']==palette_bytes()
    return v,f,slots

def colliders(asset,v):
    if 'ROCK' in asset:
        # These original rock meshes are convex, so one convex hull is exact.
        pts=np.unique(v,axis=0);h=ConvexHull(pts)
        return [dict(type='convex_hull',points_m=pts[h.vertices].tolist(),role='solid_rock')]
    if 'TREE' in asset:
        height=1.65 if 'ROUND' in asset else 2.4
        # Conservative trunk proxy; foliage and branches intentionally non-solid.
        return [dict(type='cylinder',radius_m=.22,height_m=height,center_m=[0,0,height/2],axis='Z',role='trunk_proxy')]
    boxes=[dict(type='box',size_m=[.14,.14,1.1],center_m=[0,0,.55],role='post')]
    if 'RAIL' in asset:
        length=1 if '_1M_' in asset else 2
        for z in [.4,.8]:boxes.append(dict(type='box',size_m=[length-.14,.08,.12],center_m=[length/2,0,z],role='rail'))
    return boxes

def main():
    sources=collect();items=placements();OUT.mkdir(exist_ok=True)
    asset_data={a:read_source(p) for a,p in sources.items()}
    collision={a:colliders(a,data[0]) for a,data in asset_data.items()}
    vv=[];ff=[];ss=[];offset=0;stats=[]
    for item in items:
        v,f,s=asset_data[item['asset_id']];angle=np.deg2rad(item['yaw_degrees']);c=np.cos(angle);q=np.sin(angle)
        rotation=np.array([[c,-q,0],[q,c,0],[0,0,1]])
        world=v@rotation.T+item['position_m'];vv.append(world);ff.append(f+offset);ss.append(s);offset+=len(v)
        stats.append(dict(instance_id=item['id'],triangles=len(f),bounds_min_m=world.min(0).tolist(),bounds_max_m=world.max(0).tolist()))
    v=np.concatenate(vv);f=np.concatenate(ff);s=np.concatenate(ss)
    n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
    assert len(f)*3<65536
    r=dict(asset_id='TW_DEMO_CLEARING',seed=0,generator_version='0.4.0')
    (OUT/'models').mkdir(exist_ok=True);path=OUT/'models/TW_DEMO_CLEARING.glb'
    path.write_bytes(write_glb(r,v,f,n,s,palette_bytes()))
    m=load_glb(path)
    assert len(m['indices'])==len(f)*3 and np.isfinite(m['positions']).all()
    assert np.allclose(m['positions'].min(0),np.min(v[:,[0,2,1]]*np.array([1,1,-1]),axis=0),atol=1e-6)
    # Clear walking strip y in [-0.7, 0.7], checked against collider bounds (not canopies).
    clearance=[]
    for item in items:
        angle=np.deg2rad(item['yaw_degrees']);c=np.cos(angle);q=np.sin(angle)
        rot=np.array([[c,-q,0],[q,c,0],[0,0,1]])
        for shape in collision[item['asset_id']]:
            if shape['type']=='convex_hull':points=np.array(shape['points_m']);lo=(points@rot.T+item['position_m']).min(0);hi=(points@rot.T+item['position_m']).max(0)
            else:
                center=np.array(shape['center_m'])@rot.T+item['position_m']
                half=np.array(shape['size_m'])/2 if shape['type']=='box' else np.array([shape['radius_m'],shape['radius_m'],shape['height_m']/2])
                extent=np.abs(rot)@half;lo=center-extent;hi=center+extent
            assert hi[1]<=-.7 or lo[1]>=.7, (item['id'],lo,hi)
            clearance.append(dict(instance_id=item['id'],role=shape['role'],y_min=float(lo[1]),y_max=float(hi[1])))
    assets=[]
    for a,p in sorted(sources.items()):
        dest=OUT/'assets'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest)
        assets.append(dict(asset_id=a,file='assets/'+p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),triangles=len(asset_data[a][1])))
    dump(OUT/'scene.json',dict(coordinate_frame='Z-up meters; yaw about +Z',glb_mapping='(x,z,-y)',instances=items,assets=assets,ground=dict(size_m=[12,9],height_m=0,visual_in_glb=False),clear_path=dict(y_range_m=[-.7,.7],width_m=1.4)))
    dump(OUT/'colliders.json',dict(schema_version='0.1',coordinate_frame='asset-local Z-up meters',status='DESCRIPTORS_ONLY_ENGINE_UNTESTED',assets=collision))
    dump(OUT/'validation.json',dict(status='PASS',instances=len(items),unique_assets=6,terminal_fixture_count=2,total_triangles=len(f),palette_count=1,ground_in_glb=False,geometry_roundtrip='PASS',clearance='PASS_AABB_CONSERVATIVE',clearance_checks=clearance,engine_import='NOT_RUN',physics_simulation='NOT_RUN',render_performance='NOT_MEASURED',instance_stats=stats))
    preview(m)
    print(json.dumps(dict(instances=len(items),triangles=len(f),clearance='PASS')))

def preview(m):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib.patches import Rectangle
    v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);tri=v[m['indices']].reshape(-1,3,3)
    uv=m['uv'][m['indices'][::3]];colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
    fig=plt.figure(figsize=(13,8),facecolor='#eeeee5');ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
    ax.add_collection3d(Poly3DCollection([[[-6,-4.5,-.02],[6,-4.5,-.02],[6,4.5,-.02],[-6,4.5,-.02]]],facecolors='#b3b68f',zorder=0))
    ax.add_collection3d(Poly3DCollection([[[-6,-.7,0],[6,-.7,0],[6,.7,0],[-6,.7,0]]],facecolors='#d4c4a1',zorder=1))
    ax.add_collection3d(Poly3DCollection(tri,facecolors=colors,edgecolors='#333d30',linewidths=.08,zorder=2))
    ax.set(xlim=(-6,6),ylim=(-4.5,4.5),zlim=(0,4));ax.set_box_aspect((12,9,4));ax.view_init(35,-60);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Integrated clearing prototype',fontsize=20)
    fig.text(.5,.06,'20 placements | 6 original models + terminal fixture | 1.4 m clear walking strip\nGround and path are preview guides; physics and engine performance not tested.',ha='center',fontsize=11)
    fig.savefig(OUT/'preview.png',dpi=160,bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
