"""Original paving stones and visual stairs with optional smooth ramp colliders."""
from pathlib import Path
from collections import Counter
import json,shutil,math
import numpy as np
from build_camp_props import box
from build_vegetation import hull
from build_rocks import dump,write_glb,palette_bytes
from verify_glb import load_glb
ROOT=Path(__file__).parent;OUT=ROOT/'path_props_output'
RECIPES=[dict(asset_id='TW_PAVER_ROUND_A',kind='paver',size=[.7,.6,.1],sides=9),dict(asset_id='TW_PAVER_LONG_A',kind='paver',size=[1.05,.55,.12],sides=8),dict(asset_id='TW_STEPS_LOW3_A',kind='stairs',count=3,tread=.4,rise=.12,width=1.2),dict(asset_id='TW_STEPS_WIDE4_A',kind='stairs',count=4,tread=.45,rise=.15,width=1.5)]

def generate(r):
    components=[]
    if r['kind']=='paver':
        points=[];n=r['sides']
        for z,scale in [(0,.93),(.75,1),(1,.88)]:
            for k in range(n):
                a=2*math.pi*k/n;radius=1+.06*math.sin(k*2.7)
                points.append([scale*radius*math.cos(a),scale*radius*math.sin(a),z])
        v,f=hull(points);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo)*r['size'];v[:,:2]-=np.array(r['size'][:2])/2;components.append((v,f))
        collider=dict(type='convex_hull',points_m=v.tolist())
    else:
        length=r['count']*r['tread'];height=r['count']*r['rise'];w=r['width']/2
        for i in range(r['count']):components.append(box([(i+.5)*r['tread'],0,(i+1)*r['rise']/2],[r['tread'],r['width'],(i+1)*r['rise']]))
        points=[[0,y,0] for y in [-w,w]]+[[length,y,z] for y in [-w,w] for z in [0,height]]
        collider=dict(type='convex_hull',points_m=points,mode='SMOOTH_RAMP_PROXY',length_m=length,height_m=height)
    vv=[];ff=[];ss=[];meta=[];off=0
    for i,(v,f) in enumerate(components):
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(x==2 for x in edges.values())
        p=v[f];assert np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()>0
        n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
        slots=np.where(n[:,2]>.5,10,np.where(n[:,0]<-.3,8,9))
        vv.append(v);ff.append(f+off);ss.extend(slots.tolist());meta.append(dict(vertex_start=off,vertex_count=len(v),triangles=len(f)));off+=len(v)
    v=np.concatenate(vv);f=np.concatenate(ff);p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(ss),meta,collider

def main():
    entries=[];reports=[]
    for r in RECIPES:
        v,f,n,s,meta,c=generate(r);p=OUT/'models'/f"{r['asset_id']}_LOD0.glb";p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(write_glb(dict(r,seed=0,generator_version='0.14.0'),v,f,n,s,palette_bytes()))
        m=load_glb(p);assert np.isfinite(m['positions']).all() and np.isfinite(m['normals']).all() and abs(m['positions'][:,1].min())<1e-6
        reports.append(dict(asset_id=r['asset_id'],triangles=len(f),dimensions_xyz_m=np.ptp(v,axis=0).tolist(),status='PASS',collider_mode=c.get('mode','CONVEX'),art_approval='PENDING'))
        dump(OUT/'recipes'/f"{r['asset_id']}.json",r);dump(OUT/'source_meshes'/f"{r['asset_id']}.json",dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),components=meta,coordinate_frame='Z-up meters'))
        entries.append(dict(asset_id=r['asset_id'],file='props/'+p.name,triangles=len(f),collider=c))
    dump(OUT/'catalog.json',dict(assets=entries,origin='Original beveled radial stones and box steps',external_geometry_inputs=[],lod='LOD0_ONLY'));dump(OUT/'validation.json',reports)
    render()
    project=ROOT.parent/'trailwood_godot'
    if project.exists():
        for p in (OUT/'models').glob('*.glb'):shutil.copyfile(p,project/'props'/p.name)
        entries=[]
        for folder in ['wood_props_output','vegetation_output','camp_props_output','path_props_output']:entries.extend(json.loads((ROOT/folder/'catalog.json').read_text())['assets'])
        dump(project/'data/props_catalog.json',dict(assets=entries,coordinate_frame='Z-up meters'))
    print(reports)

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(11,9),facecolor='#ecefe9')
    for i,r in enumerate(RECIPES):
        m=load_glb(OUT/'models'/f"{r['asset_id']}_LOD0.glb");v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
        colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax=fig.add_subplot(2,2,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='#455147',linewidths=.18))
        mid=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.56
        ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=r['asset_id'].replace('TW_','')+f' | {len(f)} triangles')
        ax.set_box_aspect((1,1,1));ax.view_init(28,-125);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Paving stones and low stairs',fontsize=18);fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'preview.png',dpi=145);plt.close(fig)

if __name__=='__main__':main()
