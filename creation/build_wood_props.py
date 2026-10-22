"""Original ring-profile wood props; no external geometry input."""
from pathlib import Path
from collections import Counter
import math
import shutil
import numpy as np
from build_rocks import dump,write_glb,palette_bytes,rand
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'wood_props_output'
RECIPES=[
 dict(asset_id='TW_STUMP_CUT_SMALL_A',seed=41001,radius=.32,height=.48,sides=12,kind='stump',broken=False),
 dict(asset_id='TW_STUMP_BROKEN_A',seed=41002,radius=.44,height=.82,sides=12,kind='stump',broken=True),
 dict(asset_id='TW_LOG_CUT_2M_A',seed=42001,radius=.24,height=2.0,sides=12,kind='log',broken=False),
 dict(asset_id='TW_LOG_BROKEN_15M_A',seed=42002,radius=.3,height=1.5,sides=12,kind='log',broken=True),
]

def generate(r):
    n=r['sides'];v=[];f=[];s=[]
    # Three side rings with identical angular phase; top may have a jagged end.
    for ring,t in enumerate([0,.3,1]):
        for k in range(n):
            angle=2*math.pi*k/n
            radial=1+.08*(rand(r,'bark',k)-.5)
            taper=(1.18 if ring==0 else 1.0 if ring==1 else .88) if r['kind']=='stump' else 1-.08*t
            z=r['height']*t
            if ring==2 and r['broken']:z-=r['height']*.18*rand(r,'break',k)
            v.append([r['radius']*taper*radial*math.cos(angle),r['radius']*taper*radial*math.sin(angle),z])
    for ring in range(2):
        for k in range(n):
            j=(k+1)%n;a=ring*n+k;b=ring*n+j;c=(ring+1)*n+k;d=(ring+1)*n+j
            f.extend([[a,b,d],[a,d,c]]);s.extend([16+k%3]*2)
    # Bottom cap and two inset end-grain rings, joined watertight to outer ring.
    for k in range(1,n-1):f.append([0,k+1,k]);s.append(16)
    for scale in [.73,.42]:
        for k in range(n):
            p=np.array(v[2*n+k]);p[:2]*=scale
            p[2]=r['height']*(.94 if r['broken'] else 1)
            v.append(p.tolist())
    for ring in [2,3]:
        for k in range(n):
            j=(k+1)%n;a=ring*n+k;b=ring*n+j;c=(ring+1)*n+k;d=(ring+1)*n+j
            f.extend([[a,b,d],[a,d,c]]);s.extend([19 if ring==2 else 18]*2)
    center=len(v);v.append([0,0,r['height']*(.94 if r['broken'] else 1)])
    for k in range(n):f.append([4*n+k,4*n+(k+1)%n,center]);s.append(19)
    v=np.array(v);f=np.array(f)
    # Normalize intended axial height; retain the asymmetric broken rim.
    v[:,2]*=r['height']/v[:,2].max()
    if r['kind']=='log':
        v=v[:,[2,1,0]]*np.array([1,1,-1]);v[:,0]-=r['height']/2;v[:,2]-=v[:,2].min()
    p=v[f];normals=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
    return v,f,normals,np.array(s)

def main():
    reports=[];catalog=[]
    for r in RECIPES:
        v,f,n,s=generate(r);edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(c==2 for c in edges.values()) and len(v)-len(edges)+len(f)==2
        p=v[f];volume=np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()/6
        assert volume>0 and np.isfinite(n).all() and np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1).min()>1e-8
        path=OUT/'models'/f"{r['asset_id']}_LOD0.glb";path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(write_glb(dict(r,generator_version='0.9.0'),v,f,n,s,palette_bytes()))
        m=load_glb(path);assert abs(m['positions'][:,1].min())<1e-6
        assert np.allclose(m['positions'].max(0)-m['positions'].min(0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-6)
        assert np.allclose(np.linalg.norm(m['normals'],axis=1),1,atol=1e-6)
        dump(OUT/'source_meshes'/f"{r['asset_id']}.json",dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),coordinate_frame='Z-up meters'))
        dump(OUT/'recipes'/f"{r['asset_id']}.json",r)
        # Conservative, engine-ready single convex proxy, including broken recesses.
        from scipy.spatial import ConvexHull
        hull=ConvexHull(v);points=v[hull.vertices]
        catalog.append(dict(asset_id=r['asset_id'],file='props/'+path.name,triangles=len(f),collider=dict(type='convex_hull',points_m=points.tolist())))
        reports.append(dict(asset_id=r['asset_id'],triangles=len(f),dimensions_xyz_m=np.ptp(v,axis=0).tolist(),closed_manifold=True,volume_m3=float(volume),status='PASS',art_approval='PENDING'))
    dump(OUT/'validation.json',reports);dump(OUT/'catalog.json',dict(assets=catalog,coordinate_frame='Z-up meters',lod='LOD0_ONLY',origin='Original ring profiles and own palette',external_geometry_inputs=[]))
    render();project=ROOT.parent/'trailwood_godot'
    if project.exists():
        (project/'props').mkdir(exist_ok=True)
        for p in (OUT/'models').glob('*.glb'):shutil.copyfile(p,project/'props'/p.name)
        # Regenerate vegetation afterward to restore the combined gallery catalog.
        shutil.copyfile(OUT/'catalog.json',project/'data/props_catalog.json')
    print(reports)

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(12,9),facecolor='#f2eee3')
    for index,r in enumerate(RECIPES):
        m=load_glb(OUT/'models'/f"{r['asset_id']}_LOD0.glb");v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
        colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax=fig.add_subplot(2,2,index+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='#4c402e',linewidths=.15))
        center=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.58
        ax.set(xlim=(center[0]-half,center[0]+half),ylim=(center[1]-half,center[1]+half),zlim=(center[2]-half,center[2]+half),title=r['asset_id'].replace('TW_','')+' | 118 triangles')
        ax.set_box_aspect((1,1,1));ax.view_init(30,-45);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Original stump and fallen-log prototypes',fontsize=18)
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)

if __name__=='__main__':main()
