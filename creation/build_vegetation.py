"""Original solid low-poly shrubs and grass; no texture cards or external meshes."""
from pathlib import Path
from collections import Counter
import math
import json
import shutil
import numpy as np
from scipy.spatial import ConvexHull
from build_rocks import dump,write_glb,palette_bytes,rand
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'vegetation_output'
RECIPES=[
 dict(asset_id='TW_SHRUB_ROUND_A',seed=51001,kind='shrub',size=[.95,.85,.65],count=3),
 dict(asset_id='TW_SHRUB_SPREAD_A',seed=51002,kind='shrub',size=[1.4,.95,.5],count=5),
 dict(asset_id='TW_GRASS_TUFT_A',seed=52001,kind='grass',size=[.55,.5,.42],count=7),
 dict(asset_id='TW_GRASS_TALL_A',seed=52002,kind='grass',size=[.65,.5,.85],count=9),
]

def hull(points):
    v=np.array(points,float);h=ConvexHull(v);faces=[]
    for face,eq in zip(h.simplices,h.equations):
        face=face.copy()
        if np.dot(np.cross(v[face[1]]-v[face[0]],v[face[2]]-v[face[0]]),eq[:3])<0:face[[1,2]]=face[[2,1]]
        faces.append(face.tolist())
    return v,np.array(faces)

def generate(r):
    components=[]
    for i in range(r['count']):
        angle=i*2*math.pi/r['count'];dx=.22*math.cos(angle);dy=.2*math.sin(angle)
        if r['kind']=='shrub':
            points=[];radius=.35*(.85+.3*rand(r,'size',i));center=np.array([dx,dy,.25+.12*rand(r,'height',i)])
            for level,z in enumerate([-.75,0,.75]):
                rr=math.sqrt(1-z*z)
                for k in range(7):
                    a=2*math.pi*(k+.15*(level%2))/7
                    points.append(center+radius*np.array([rr*math.cos(a),rr*math.sin(a),z]))
            points.extend([center+[0,0,radius],center-[0,0,radius]])
        else:
            # Closed blade with a triangular ridge and a tapered tip.
            height=.45+.4*rand(r,'height',i);width=.045+.02*rand(r,'width',i)
            radial=np.array([math.cos(angle),math.sin(angle),0]);side=np.array([-math.sin(angle),math.cos(angle),0])
            base=np.array([dx*.35,dy*.35,0]);middle=base+radial*.11+[0,0,height*.55];tip=base+radial*.23+[0,0,height]
            points=[base-side*width,base+side*width,base+radial*.018,
                    middle-side*width*.65,middle+side*width*.65,middle+radial*.025,tip]
        components.append(hull(points))
    allv=np.concatenate([v for v,f in components]);lo=allv.min(0);hi=allv.max(0)
    vertices=[];faces=[];slots=[];metadata=[];off=0;faceoff=0
    for i,(v,f) in enumerate(components):
        v=(v-lo)/(hi-lo)*r['size'];v[:,:2]-=np.array(r['size'][:2])/2
        p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
        base=4 if r['kind']=='shrub' else 12
        s=np.where(n[:,2]>.4,base+2,np.where(n[:,0]<-.25,base,base+1))
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        used=len(set(f.ravel().tolist()))
        assert all(x==2 for x in edges.values()) and used-len(edges)+len(f)==2
        assert np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()>0
        metadata.append(dict(name=f"{r['kind']}_{i}",vertex_start=off,vertex_count=len(v),face_start=faceoff,face_count=len(f)))
        vertices.append(v);faces.append(f+off);slots.extend(s.tolist());off+=len(v);faceoff+=len(f)
    v=np.concatenate(vertices);f=np.concatenate(faces);p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(slots),metadata

def main():
    reports=[];catalog=[]
    for r in RECIPES:
        v,f,n,s,c=generate(r);path=OUT/'models'/f"{r['asset_id']}_LOD0.glb";path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(write_glb(dict(r,generator_version='0.10.0'),v,f,n,s,palette_bytes()))
        m=load_glb(path);assert np.allclose(np.ptp(m['positions'],axis=0),np.array(r['size'])[[0,2,1]],atol=1e-6)
        assert abs(m['positions'][:,1].min())<1e-6 and np.isfinite(m['normals']).all()
        assert np.allclose(np.linalg.norm(m['normals'],axis=1),1,atol=1e-5)
        dump(OUT/'source_meshes'/f"{r['asset_id']}.json",dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),components=c,coordinate_frame='Z-up meters'))
        dump(OUT/'recipes'/f"{r['asset_id']}.json",r)
        reports.append(dict(asset_id=r['asset_id'],triangles=len(f),dimensions_xyz_m=r['size'],closed_components=len(c),status='PASS',collider='NONE_DECORATIVE',wind_animation='NOT_IMPLEMENTED',art_approval='PENDING'))
        catalog.append(dict(asset_id=r['asset_id'],file='props/'+path.name,triangles=len(f),collider=None))
    dump(OUT/'validation.json',reports);dump(OUT/'catalog.json',dict(assets=catalog,origin='Original convex shrubs and solid blades',external_geometry_inputs=[],lod='LOD0_ONLY'))
    render()
    project=ROOT.parent/'trailwood_godot'
    if project.exists():
        for p in (OUT/'models').glob('*.glb'):shutil.copyfile(p,project/'props'/p.name)
        wood=json.loads((ROOT/'wood_props_output/catalog.json').read_text())
        dump(project/'data/props_catalog.json',dict(assets=wood['assets']+catalog,coordinate_frame='Z-up meters'))
    print(reports)

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(11,9),facecolor='#eef1e8')
    for i,r in enumerate(RECIPES):
        m=load_glb(OUT/'models'/f"{r['asset_id']}_LOD0.glb");v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
        color=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax=fig.add_subplot(2,2,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=color,edgecolors='#3b5132',linewidths=.18))
        mid=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.58
        ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=f"{r['asset_id'].replace('TW_','')} | {len(f)} triangles")
        ax.set_box_aspect((1,1,1));ax.view_init(25,-55);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Shrubs and solid grass prototypes',fontsize=18);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)

if __name__=='__main__':main()
