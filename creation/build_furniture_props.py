"""Original static camp benches and tables; component colliders preserve open space."""
from pathlib import Path
from collections import Counter
import json,shutil
import numpy as np
from build_fences import prism
from build_rocks import dump,write_glb,palette_bytes
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'furniture_props_output'
IDS=['TW_BENCH_SIMPLE_A','TW_BENCH_BACKREST_A','TW_TABLE_SQUARE_A','TW_TABLE_LONG_A']

def box(center,size):
    x,y,z=center;w,d,h=np.array(size)/2
    v,f=prism([(x-w,z-h),(x+w,z-h),(x+w,z+h),(x-w,z+h)],d*2);v[:,1]+=y
    return v,f

def generate(asset):
    components=[]
    def add(name,mesh):components.append((name,*mesh))
    bench='BENCH' in asset
    w,d,h=(1.6,.45,.45) if bench else ((.9,.9,.75) if 'SQUARE' in asset else (1.8,.8,.75))
    thickness=.07
    for y in [-d/3,0,d/3]:
        add('seat_plank' if bench else 'top_plank',box([0,y,h-thickness/2],[w,d/3-.008,thickness]))
    for x in [-w/2+.12,w/2-.12]:
        for y in [-d/2+.07,d/2-.07]:
            add('leg',box([x,y,(h-thickness)/2],[.08,.08,h-thickness]))
        add('cross_support',box([x,0,h-.11],[.09,d-.04,.08]))
        add('lower_cross_support',box([x,0,.19],[.08,d-.08,.07]))
    add('long_stretcher',box([0,0,.19],[w-.16,.06,.07]))
    if 'BACKREST' in asset:
        for x in [-w/2+.12,w/2-.12]:
            add('back_post',box([x,d/2-.04,.72],[.08,.08,.66]))
        for z in [.73,.96]:
            add('back_plank',box([0,d/2-.095,z],[w,.055,.15]))
    vv=[];ff=[];ss=[];meta=[];off=0;faceoff=0;collision=[]
    for i,(name,v,f) in enumerate(components):
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(x==2 for x in edges.values()) and len(v)-len(edges)+len(f)==2
        p=v[f];assert np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()>0
        meta.append(dict(name=name,vertex_start=off,vertex_count=len(v),face_start=faceoff,face_count=len(f)))
        vv.append(v);ff.append(f+off);ss.extend([17 if i==0 else 18 if 'reinforcement' in name or 'plank' in name else 19]*len(f));off+=len(v);faceoff+=len(f)
        collision.append(dict(type='convex_hull',points_m=v.tolist()))
    v=np.concatenate(vv);f=np.concatenate(ff);p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(ss),meta,dict(type='compound',parts=collision)

def main():
    reports=[];entries=[]
    for asset in IDS:
        v,f,n,s,meta,collider=generate(asset);r=dict(asset_id=asset,seed=0,generator_version='0.16.0')
        p=OUT/'models'/f'{asset}_LOD0.glb';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(write_glb(r,v,f,n,s,palette_bytes()))
        m=load_glb(p);assert np.isfinite(m['positions']).all() and np.isfinite(m['normals']).all()
        assert np.allclose(np.ptp(m['positions'],axis=0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-6) and abs(m['positions'][:,1].min())<1e-6
        reports.append(dict(asset_id=asset,triangles=len(f),dimensions_xyz_m=np.ptp(v,axis=0).tolist(),closed_components=len(meta),collider_parts=len(collider['parts']),status='PASS',art_approval='PENDING'))
        dump(OUT/'source_meshes'/f'{asset}.json',dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),components=meta,coordinate_frame='Z-up meters'))
        entries.append(dict(asset_id=asset,file='props/'+p.name,triangles=len(f),collider=collider))
    dump(OUT/'validation.json',reports);dump(OUT/'catalog.json',dict(assets=entries,external_geometry_inputs=[],origin='Original dimensioned plank and leg assemblies',lod='LOD0_ONLY'))
    render()
    project=ROOT.parent/'trailwood_godot'
    if project.exists():
        for p in (OUT/'models').glob('*.glb'):shutil.copyfile(p,project/'props'/p.name)
        all_entries=[]
        for folder in ['wood_props_output','vegetation_output','camp_props_output','path_props_output','furniture_props_output']:all_entries.extend(json.loads((ROOT/folder/'catalog.json').read_text())['assets'])
        dump(project/'data/props_catalog.json',dict(assets=all_entries,coordinate_frame='Z-up meters'))
    print(reports)

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(11,9),facecolor='#f0ece2')
    for i,asset in enumerate(IDS):
        m=load_glb(OUT/'models'/f'{asset}_LOD0.glb');v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
        colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax=fig.add_subplot(2,2,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='#59452f',linewidths=.12))
        mid=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.57
        ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=asset.replace('TW_','')+f' | {len(f)} triangles')
        ax.set_box_aspect((1,1,1));ax.view_init(20,-65);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Camp benches and tables',fontsize=18);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'preview.png',dpi=145);plt.close(fig)

if __name__=='__main__':main()

