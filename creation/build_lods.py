"""Deterministic per-component convex simplification of original meshes."""
from pathlib import Path
import json
import struct
from collections import Counter
import numpy as np
from scipy.spatial import ConvexHull
from build_rocks import dump,write_glb,palette_bytes
from build_trees import hull_mesh
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'lod_output'
TARGETS={'TW_ROCK_LOW_WEDGE_A':40,'TW_ROCK_UPRIGHT_A':44,'TW_TREE_ROUND_SMALL_A':180,'TW_TREE_TIERED_SLIM_A':128}
# Tiered silhouette needs a tighter geometric envelope than the other prototypes.
# Triangle targets remain preferences; the separately measured 256px IoU is the gate.
TOLERANCE_RATIOS={'TW_TREE_TIERED_SLIM_A':.01}
# Uniform spherical samples plus cardinal directions. This is not a Hausdorff bound.
i=np.arange(1024);z=1-2*(i+.5)/len(i);a=i*np.pi*(3-np.sqrt(5))
DIRS=np.vstack([np.c_[np.sqrt(1-z*z)*np.cos(a),np.sqrt(1-z*z)*np.sin(a),z],np.eye(3),-np.eye(3)])

def simplify(v,budget,tolerance):
    v=np.unique(v,axis=0);v=v[ConvexHull(v).vertices]
    original=v.copy();support=(original@DIRS.T).max(0)
    # Preserve per-component axis extrema; pivots and full bounds remain exact.
    keep=set(np.argmax(v,axis=0))|set(np.argmin(v,axis=0))
    protected=[v[j].copy() for j in sorted(keep)]
    while 2*len(v)-4>budget:
        best=None
        for j in range(len(v)):
            if any(np.array_equal(v[j],x) for x in protected):continue
            candidate=np.delete(v,j,axis=0)
            score=float(np.max(support-(candidate@DIRS.T).max(0)))
            if best is None or score<best[0]:best=(score,j)
        if best is None or best[0]>tolerance:break
        v=np.delete(v,best[1],axis=0)
    v,f=hull_mesh(v)
    error=float(np.max(np.abs(support-(v@DIRS.T).max(0))))
    return v,f,error

def main():
    reports=[]
    for asset,target in TARGETS.items():
        folder='output' if 'ROCK' in asset else 'trees_output_v2'
        original=ROOT/folder/'models'/f'{asset}_LOD0.glb';src=json.loads((ROOT/folder/'source_meshes'/f'{asset}.json').read_text())
        v0=np.array(src['vertices']);components=src.get('components',[dict(name='rock',vertex_start=0,vertex_count=len(v0),face_count=len(src['triangles']),kind='rock')])
        total=sum(c['face_count'] for c in components);vertices=[];faces=[];slots=[];details=[];off=0
        for c in components:
            source=v0[c['vertex_start']:c['vertex_start']+c['vertex_count']]
            budget=max(8,int(target*c['face_count']/total)//2*2)
            v,f,error=simplify(source,budget,float(np.ptp(v0,axis=0).max())*TOLERANCE_RATIOS.get(asset,.02))
            n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
            if c['kind']=='rock':s=np.where(n[:,2]>.45,10,np.where(n[:,0]>.25,11,np.where(n[:,1]<-.35,8,9)))
            else:
                base=4 if c['kind']=='leaf' else 0;s=np.where(n[:,2]>.4,base+2,np.where(n[:,0]<-.3,base,base+1))
            edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
            assert all(x==2 for x in edges.values()) and len(v)-len(edges)+len(f)==2
            assert np.allclose(source.min(0),v.min(0)) and np.allclose(source.max(0),v.max(0))
            assert np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()>0
            details.append(dict(name=c['name'],triangles=len(f),sampled_support_error_m=error,vertex_start=off,vertex_count=len(v),kind=c['kind']))
            vertices.append(v);faces.append(f+off);slots.extend(s.tolist());off+=len(v)
        v=np.concatenate(vertices);f=np.concatenate(faces);n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
        data=write_glb(dict(asset_id=asset,seed=0,lod=1,generator_version='0.5.0'),v,f,n,np.array(slots),palette_bytes())
        jl=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+jl]);binary=data[20+jl:]
        doc['nodes'][0]['name']=asset+'_LOD1';doc['extras']['lod']=1
        raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
        data=struct.pack('<4sII',b'glTF',2,20+len(raw)+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+binary
        path=OUT/'models'/f'{asset}_LOD1.glb';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        m=load_glb(path);assert np.isfinite(m['positions']).all() and len(m['indices'])==len(f)*3
        (OUT/'lod0').mkdir(exist_ok=True);(OUT/'lod0'/original.name).write_bytes(original.read_bytes())
        extent=float(np.ptp(v0,axis=0).max());error=max(d['sampled_support_error_m'] for d in details)
        reports.append(dict(asset_id=asset,lod0_triangles=total,lod1_triangles=len(f),target_triangles=target,reduction_percent=round(100*(1-len(f)/total),1),bounds_preserved=True,components=details,sampled_support_error_m=error,error_ratio=error/extent,target_2_percent_pass=error/extent<=.02,triangle_budget_pass=len(f)<=target,engine_import='NOT_RUN',art_approval='PENDING'))
        dump(OUT/'source_meshes'/f'{asset}_LOD1.json',dict(vertices=v.tolist(),triangles=f.tolist(),face_palette_slots=slots,components=details))
    dump(OUT/'validation.json',reports);preview(reports);print(json.dumps(reports,indent=2))

def preview(reports):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(10,14),facecolor='#eef1ed')
    for row,r in enumerate(reports):
        for col,lod in enumerate([0,1]):
            p=OUT/('lod0' if lod==0 else 'models')/f"{r['asset_id']}_LOD{lod}.glb";m=load_glb(p)
            v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);tri=v[m['indices']].reshape(-1,3,3);uv=m['uv'][m['indices'][::3]]
            color=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
            ax=fig.add_subplot(4,2,row*2+col+1,projection='3d');ax.add_collection3d(Poly3DCollection(tri,facecolors=color,edgecolors='#405040',linewidths=.15))
            center=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.55
            ax.set(xlim=(center[0]-half,center[0]+half),ylim=(center[1]-half,center[1]+half),zlim=(center[2]-half,center[2]+half),title=f"{r['asset_id'].replace('TW_','')} / LOD{lod}\n{len(tri)} triangles")
            ax.set_box_aspect((1,1,1));ax.set_proj_type('ortho');ax.view_init(20,-65);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / LOD comparison — engineering candidates',fontsize=19)
    fig.tight_layout(rect=(0,0,1,.96));fig.savefig(OUT/'preview.png',dpi=140);plt.close(fig)

if __name__=='__main__':main()
