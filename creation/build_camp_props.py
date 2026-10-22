"""Original unlettered trail signs and closed wooden crates."""
from pathlib import Path
from collections import Counter
import json,shutil
import numpy as np
from build_fences import prism
from build_rocks import dump,write_glb,palette_bytes
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'camp_props_output'
IDS=['TW_SIGN_ARROW_A','TW_SIGN_FORK_A','TW_CRATE_SMALL_A','TW_CRATE_LONG_A']

def box(center,size):
    x,y,z=center;w,d,h=np.array(size)/2
    v,f=prism([(x-w,z-h),(x+w,z-h),(x+w,z+h),(x-w,z+h)],d*2);v[:,1]+=y
    return v,f

def generate(asset):
    components=[]
    def add(name,mesh):components.append((name,*mesh))
    if 'SIGN' in asset:
        add('post',box([0,0,.72],[.12,.14,1.44]))
        profile=[(-.48,1.02),(.27,1.02),(.52,1.17),(.27,1.32),(-.48,1.32)]
        v,f=prism(profile,.07);v[:,1]-=.105;add('arrow_right',(v,f))
        if 'FORK' in asset:
            v,f=prism(profile,.07);v[:,0]*=-1;v[:,2]-=.4;v[:,1]-=.105;f=f[:,[0,2,1]];add('arrow_left',(v,f))
    else:
        w,d,h=(.65,.65,.65) if 'SMALL' in asset else (1.2,.65,.55)
        add('closed_body',box([0,0,h/2],[w,d,h]))
        for side in [-1,1]:
            for x in [-w/2+.055,w/2-.055]:add('vertical_reinforcement',box([x,side*(d/2+.025),h/2],[.08,.05,h]))
            for z in [.045,h-.045]:add('horizontal_reinforcement',box([0,side*(d/2+.025),z],[w,.05,.08]))
        if 'LONG' in asset:
            for x in [-.24,.24]:
                add('top_cross_plank',box([x,0,h+.025],[.09,d,.05]))
                add('front_center_plank',box([x,-d/2-.03,h/2],[.06,.06,h]))
    vv=[];ff=[];ss=[];meta=[];off=0;faceoff=0;collision=[]
    for i,(name,v,f) in enumerate(components):
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(x==2 for x in edges.values()) and len(v)-len(edges)+len(f)==2
        p=v[f];assert np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()>0
        meta.append(dict(name=name,vertex_start=off,vertex_count=len(v),face_start=faceoff,face_count=len(f)))
        vv.append(v);ff.append(f+off);ss.extend([17 if i==0 else 18 if 'reinforcement' in name or 'plank' in name else 19]*len(f));off+=len(v);faceoff+=len(f)
        if 'SIGN' in asset:collision.append(dict(type='convex_hull',points_m=v.tolist()))
    v=np.concatenate(vv);f=np.concatenate(ff);p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    if 'CRATE' in asset:
        lo=v.min(0);hi=v.max(0);points,_=box((lo+hi)/2,hi-lo);collision=[dict(type='convex_hull',points_m=points.tolist())]
    return v,f,n,np.array(ss),meta,dict(type='compound',parts=collision)

def main():
    reports=[];entries=[]
    for asset in IDS:
        v,f,n,s,meta,collider=generate(asset);r=dict(asset_id=asset,seed=0,generator_version='0.13.0')
        p=OUT/'models'/f'{asset}_LOD0.glb';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(write_glb(r,v,f,n,s,palette_bytes()))
        m=load_glb(p);assert np.isfinite(m['positions']).all() and np.isfinite(m['normals']).all()
        assert np.allclose(np.ptp(m['positions'],axis=0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-6) and abs(m['positions'][:,1].min())<1e-6
        reports.append(dict(asset_id=asset,triangles=len(f),dimensions_xyz_m=np.ptp(v,axis=0).tolist(),closed_components=len(meta),collider_parts=len(collider['parts']),status='PASS',art_approval='PENDING'))
        dump(OUT/'source_meshes'/f'{asset}.json',dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),components=meta,coordinate_frame='Z-up meters'))
        entries.append(dict(asset_id=asset,file='props/'+p.name,triangles=len(f),collider=collider))
    dump(OUT/'validation.json',reports);dump(OUT/'catalog.json',dict(assets=entries,external_geometry_inputs=[],origin='Original box and arrow profiles',lod='LOD0_ONLY'))
    render()
    project=ROOT.parent/'trailwood_godot'
    if project.exists():
        for p in (OUT/'models').glob('*.glb'):shutil.copyfile(p,project/'props'/p.name)
        all_entries=[]
        for folder in ['wood_props_output','vegetation_output','camp_props_output']:all_entries.extend(json.loads((ROOT/folder/'catalog.json').read_text())['assets'])
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
    fig.suptitle('TRAILWOOD / Trail signs and camp crates',fontsize=18);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'preview.png',dpi=145);plt.close(fig)

if __name__=='__main__':main()
