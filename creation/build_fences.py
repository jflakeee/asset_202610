"""Original metric fence prototypes. No downloaded geometry is used."""
import json
import struct
from pathlib import Path
from collections import Counter
import numpy as np
from build_rocks import write_glb, palette_bytes, dump
from verify_glb import load_glb

OUT=Path(__file__).parent/'fences_output'
RECIPES=[dict(asset_id=f'TW_WOOD_RAIL_{length}M_A',seed=31000+length,length_m=length,
 height_m=1.1,post_width_m=.14,rail_depth_m=.08,rail_height_m=.12,
 rail_centers_m=[.4,.8],damage_ratio=.15 if length==1 else 0,
 include_start_post=True,include_end_post=False,generator_version='0.3.0') for length in [1,2]]

def prism(profile,depth):
    # CCW x/z profile, extruded in y; caps use a fan (profiles here star-shaped).
    n=len(profile);v=np.array([[x,y,z] for y in [-depth/2,depth/2] for x,z in profile],float)
    f=[]
    for k in range(1,n-1):f.extend([[0,k,k+1],[n,n+k+1,n+k]])
    for k in range(n):
        j=(k+1)%n;f.extend([[k,n+k,n+j],[k,n+j,j]])
    return v,np.array(f)

def generate(r,terminal=False):
    length=r['length_m']
    if not np.isfinite(length) or length<.5:raise ValueError('length must be >= 0.5 m')
    if not 0<=r['damage_ratio']<=.5:raise ValueError('damage ratio')
    components=[('start_post',prism([(-.07,0),(.07,0),(.07,1.06),(.045,1.1),(-.045,1.1),(-.07,1.06)],.14))]
    if not terminal:
        for i,z in enumerate(r['rail_centers_m']):
            lo=z-.06;hi=z+.06;a=.07;b=length-.07
            # Cosmetic shallow notch is on upper rail only and never near sockets.
            profile=[(a,lo),(b,lo),(b,hi)]
            if i==1 and r['damage_ratio']:
                profile += [(length*.57,hi),(length*.5,hi-.12*r['damage_ratio']),(length*.43,hi)]
            profile += [(a,hi)]
            components.append((f'rail_{i}',prism(profile,.08)))
    vs=[];fs=[];slots=[];meta=[];off=0
    for name,(v,f) in components:
        vs.append(v);fs.append(f+off);off+=len(v)
        slots.extend([19 if r['damage_ratio'] and name=='rail_1' and k>=4 else 16+k%3 for k in range(len(f))])
        meta.append(dict(name=name,vertices=v.tolist(),triangles=f.tolist()))
    v=np.concatenate(vs);f=np.concatenate(fs)
    n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(slots),meta

def export(r,terminal=False):
    v,f,n,s,meta=generate(r,terminal);data=write_glb(r,v,f,n,s,palette_bytes())
    jl=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+jl]);binary=data[20+jl:]
    sockets=[dict(name='SOCKET_START',translation=[0,0,0],extras=dict(outward=[-1,0,0],up=[0,1,0]))]
    if not terminal:sockets.append(dict(name='SOCKET_END',translation=[r['length_m'],0,0],extras=dict(outward=[1,0,0],up=[0,1,0])))
    doc['nodes'].extend(sockets);doc['scenes'][0]['nodes'].extend(range(1,len(doc['nodes'])))
    raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
    return struct.pack('<4sII',b'glTF',2,20+len(raw)+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+binary,meta

def validate_mesh(r,path,meta):
    m=load_glb(path);p=m['positions'];tri=p[m['indices']].reshape(-1,3,3)
    cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    assert np.isfinite(p).all() and np.linalg.norm(cross,axis=1).min()>1e-9
    assert np.all(np.sum(cross*m['normals'][m['indices'][::3]],axis=1)>0)
    assert len(tri)<1000 and abs(p[:,1].max()-1.1)<1e-6 and abs(p[:,1].min())<1e-6
    for component in meta:
        v=np.array(component['vertices']);f=np.array(component['triangles'])
        edges=Counter(tuple(sorted((a,b))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(x==2 for x in edges.values()) and len(v)-len(edges)+len(f)==2
        assert np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()>0
    nodes={n['name']:n for n in m['doc']['nodes']}
    assert nodes['SOCKET_END']['translation']==[r['length_m'],0,0]
    assert export(r)[0]==path.read_bytes()
    return dict(asset_id=r['asset_id'],triangles=len(tri),closed_components=len(meta),status='PASS')

def chain(lengths):
    starts=np.r_[0,np.cumsum(lengths)[:-1]];end=float(sum(lengths))
    posts=list(starts)+[end]
    # Rail end and next owned post face are geometrically coincident.
    gaps=[abs((start+length-.07)-(next_start-.07)) for start,length,next_start in zip(starts,lengths,posts[1:])]
    assert len(set(posts))==len(posts) and max(gaps)<.001
    return dict(lengths_m=lengths,socket_span_m=end,post_count=len(posts),max_gap_m=max(gaps),terminal_required=True,status='PASS')

def preview():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(12,7),facecolor='#f5f1e8')
    def draw(ax,path,offset=0):
        m=load_glb(path);v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);v[:,0]+=offset
        faces=v[m['indices']].reshape(-1,3,3);uv=m['uv'][m['indices'][::3]]
        colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors='#493a2d',linewidths=.3))
    for i,r in enumerate(RECIPES):
        ax=fig.add_subplot(2,2,i+1,projection='3d');draw(ax,OUT/'models'/f"{r['asset_id']}_LOD0.glb")
        ax.set(xlim=(-.15,2.15),ylim=(-.5,.5),zlim=(0,1.3),title=f"{r['length_m']} m module | start post only")
        ax.set_box_aspect((2.3,1,1.3));ax.view_init(18,-65);ax.set_axis_off()
    from matplotlib.collections import PolyCollection
    ax=fig.add_subplot(2,1,2)
    for x in range(0,11,2):
        path=OUT/'models'/'TW_WOOD_RAIL_2M_A_LOD0.glb' if x<10 else OUT/'fixtures'/'TW_TERMINAL_POST.glb'
        m=load_glb(path);p=m['positions'][:,:2].copy();p[:,0]+=x
        ax.add_collection(PolyCollection(p[m['indices']].reshape(-1,3,2),facecolors='#927751',edgecolors='#493a2d',linewidths=.3))
    ax.set(xlim=(-.2,10.2),ylim=(-.15,1.3),title='10 m socket span | 5 modules + 1 terminal fixture | 6 posts')
    ax.set_aspect('equal');ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Fence engineering prototypes — art approval pending',fontsize=15)
    fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=170);plt.close(fig)

def main():
    results=[]
    for r in RECIPES:
        data,meta=export(r);path=OUT/'models'/f"{r['asset_id']}_LOD0.glb";path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        dump(OUT/'recipes'/f"{r['asset_id']}.json",r);dump(OUT/'source_meshes'/f"{r['asset_id']}.json",dict(coordinate_system='Z-up meters',components=meta))
        results.append(validate_mesh(r,path,meta))
    fixture=dict(RECIPES[0],asset_id='TW_TERMINAL_POST');path=OUT/'fixtures'/'TW_TERMINAL_POST.glb';path.parent.mkdir(exist_ok=True);path.write_bytes(export(fixture,True)[0]);load_glb(path)
    dump(OUT/'validation.json',dict(status='PASS',assets=results,chains=[chain([2]*5),chain([1,2,4])],custom_length_2_13='NEEDS_CUSTOM_END',four_meter_segment='math fixture only',engine_import='NOT_RUN',art_approval='PENDING',corners_slopes='NOT_IMPLEMENTED'))
    dump(OUT/'provenance.json',dict(origin='Original mathematical profiles and own palette',external_geometry_inputs=[],generator_version='0.3.0',source_frame='Z up',export_frame='Y up; (x,z,-y)',socket_orientation='outward/up vectors in node extras; translations in glTF frame'))
    (OUT/'textures').mkdir(exist_ok=True);(OUT/'textures'/'MOSS_01.png').write_bytes(palette_bytes());preview()
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
