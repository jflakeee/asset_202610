"""Original staggered stone boundary prototypes; no external geometry inputs."""
from pathlib import Path
from collections import Counter
import json, struct, hashlib
import numpy as np
from scipy.spatial.transform import Rotation
from build_camp_props import box
from build_rocks import dump, write_glb, palette_bytes
from verify_glb import load_glb

ROOT=Path(__file__).parent
OUT=ROOT/'stone_modules_output'
FAMILIES=['STONE_WALL_1M','STONE_WALL_2M','STONE_WALL_4M','STONE_CORNER_L90','STONE_CORNER_R90','STONE_END_CAP','STONE_END_RUIN','STONE_POST']
RECIPES=[dict(asset_id=f'TW_{family}_{variant}',family=family,variant=variant,seed=42000+i*2+j,generator_version='0.17.0') for i,family in enumerate(FAMILIES) for j,variant in enumerate('AB')]

def socket(name,position,outward):
    convert=lambda a: np.array(a,float)[[0,2,1]]*np.array([1,1,-1])
    p=convert(position);x=convert(outward);up=np.array([0.,1.,0.]);z=np.cross(x,up)
    return dict(name=name,translation=p.tolist(),rotation=Rotation.from_matrix(np.column_stack([x,up,z])).as_quat().tolist(),extras=dict(position_m=p.tolist(),outward_axis=x.tolist(),up_axis=up.tolist(),outward=x.tolist(),up=up.tolist(),coordinate_frame='glTF Y-up meters'))

def generate(r):
    components=[];variant=r['variant'];family=r['family'];courses=3 if variant=='A' else 4
    height=1.0;post_half=.16
    def block(name,center,size,slot=9):
        v,f=box(center,size);components.append((name,v,f,slot))
    def post(x,y,ruin=False):
        ph=.76 if ruin else 1.08
        for row in range(courses):
            width=.32 if row<courses-1 else (.34 if not ruin else .29)
            # Small alternating depth changes distinguish courses without moving sockets.
            block('post_course',[x,y,(row+.5)*ph/courses],[width,width,ph/courses],8+(row%3))
        if variant=='B':
            block('offset_crown',[x+.018,y,ph+.025],[.30,.33,.05],10)
    def wall(a,b,leg):
        a=np.array(a,float);b=np.array(b,float);length=float(np.linalg.norm(b-a));direction=(b-a)/length
        lo=post_half;hi=length-post_half
        for row in range(courses):
            unit=.42 if variant=='A' else .53
            cuts=[lo]+[float(x) for x in np.arange(lo+unit*(.5 if row%2 else 1),hi,unit) if lo+1e-6<x<hi-1e-6]+[hi]
            for j,(left,right) in enumerate(zip(cuts,cuts[1:])):
                center=a+direction*((left+right)/2)
                depth=.28 + (.018*((row+j)%2) if variant=='B' else 0)
                size=[right-left,depth,height/courses]
                v,f=box([0,0,(row+.5)*height/courses],size)
                rot=np.array([[direction[0],-direction[1],0],[direction[1],direction[0],0],[0,0,1]])
                v=v@rot.T;v[:,:2]+=center
                components.append((f'wall_{leg}_row_{row}_block_{j}',v,f,8+(row+j)%4))
    sockets=[socket('SOCKET_START',[0,0,0],[-1,0,0])]
    if 'WALL' in family:
        length=float(family.split('_')[-1][:-1]);post(0,0);wall([0,0],[length,0],0)
        sockets.append(socket('SOCKET_END',[length,0,0],[1,0,0]))
        path=[[0,0,0],[length,0,0]]
    elif 'CORNER' in family:
        side=1 if 'L90' in family else -1
        post(0,0);post(1,0);wall([0,0],[1,0],0);wall([1,0],[1,side],1)
        if side<0:
            # Right corners have a wider elbow crown, not solely a mirrored mesh.
            block('right_elbow_crown',[1,0,1.11],[.40,.34,.06],10)
        sockets.append(socket('SOCKET_END',[1,side,0],[0,side,0]));path=[[0,0,0],[1,0,0],[1,side,0]]
    else:
        ruin='RUIN' in family;post(0,0,ruin);path=[[0,0,0]]
        if 'END_CAP' in family:
            block('cap_slab',[0,0,1.12],[.38,.38,.08],10)
        if ruin:
            block('broken_crown',[.045,0,.80],[.19,.28,.08],11)
            block('fallen_fragment',[.25,.1,.09],[.22,.22,.18],8)
            if variant=='B':block('fallen_fragment_small',[-.10,.28,.06],[.14,.13,.12],9)
    vv=[];ff=[];ss=[];meta=[];colliders=[];offset=0
    for name,v,f,slot in components:
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(n==2 for n in edges.values()) and len(v)-len(edges)+len(f)==2
        p=v[f];assert np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()>0
        meta.append(dict(name=name,vertex_start=offset,vertex_count=len(v),triangle_count=len(f)))
        vv.append(v);ff.append(f+offset);ss.extend([slot]*len(f));offset+=len(v)
        colliders.append(dict(type='convex_hull',points_m=v.tolist()))
    v=np.concatenate(vv);f=np.concatenate(ff);p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(ss),meta,dict(type='compound',parts=colliders),sockets,path

def export(r):
    v,f,n,s,meta,c,sockets,path=generate(r);data=write_glb(r,v,f,n,s,palette_bytes())
    size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);binary=data[20+size:]
    start=len(doc['nodes']);doc['nodes'].extend(sockets);doc['scenes'][0]['nodes'].extend(range(start,len(doc['nodes'])))
    raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
    data=struct.pack('<4sII',b'glTF',2,20+len(raw)+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+binary
    return data,(v,f,n,s,meta,c,sockets,path)

def main():
    entries=[];reports=[]
    for r in RECIPES:
        data,parts=export(r);v,f,n,s,meta,c,sockets,path=parts
        p=OUT/'models'/f"{r['asset_id']}_LOD0.glb";p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        m=load_glb(p);assert np.isfinite(m['positions']).all() and np.isfinite(m['normals']).all()
        assert abs(m['positions'][:,1].min())<1e-6 and np.allclose(np.ptp(m['positions'],axis=0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-6)
        assert export(r)[0]==data
        for node in m['doc']['nodes'][1:]:
            assert np.allclose(Rotation.from_quat(node['rotation']).apply([1,0,0]),node['extras']['outward_axis'])
            assert np.allclose(Rotation.from_quat(node['rotation']).apply([0,1,0]),[0,1,0])
        report=dict(asset_id=r['asset_id'],triangles=len(f),closed_components=len(meta),collider_parts=len(c['parts']),status='PASS',art_approval='PENDING',socket_nodes=len(sockets),engine_import='NOT_RUN')
        reports.append(report)
        dump(OUT/'recipes'/f"{r['asset_id']}.json",r)
        dump(OUT/'source_meshes'/f"{r['asset_id']}.json",dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),components=meta,coordinate_frame='Z-up meters'))
        entries.append(dict(asset_id=r['asset_id'],family=r['family'],variant=r['variant'],file='props/'+p.name,triangles=len(f),collider=c,sockets=sockets,path_source_m=path,lod_omission_reason='Prototype LOD0; screen-size measurements and silhouette IoU pending',art_approval='PENDING'))
    # A/B must change geometry, not just the palette.
    for family in FAMILIES:
        a=generate(next(r for r in RECIPES if r['family']==family and r['variant']=='A'))
        b=generate(next(r for r in RECIPES if r['family']==family and r['variant']=='B'))
        assert a[0].shape!=b[0].shape or not np.array_equal(a[0],b[0])
    dump(OUT/'catalog.json',dict(assets=entries,external_geometry_inputs=[],coordinate_frame='source Z-up; sockets glTF Y-up',origin='Original staggered dimensioned stone blocks',lod='LOD0_ONLY'))
    dump(OUT/'validation.json',dict(status='PASS',assets=reports,deterministic_rebuild='PASS',variant_geometry='PASS',engine_import='NOT_RUN',slope_assembly='NOT_RUN',art_approval='PENDING'))
    dump(OUT/'provenance.json',dict(origin='Original Python dimensioned block geometry and own shared palette',external_geometry_inputs=[],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),ownership='Straight and corner pieces own start posts; corner owns elbow; endpoint post excluded',endpoint_protection_m=.16,limitations=['Separate closed blocks retain internal contact faces','Compound colliders are unsimplified','End ruin has an intentionally lowered crown','Slope and engine visual tests not run']))
    render();print(json.dumps(dict(models=len(entries),triangles=[r['triangles'] for r in reports],status='PASS')))

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(16,14),facecolor='#ecefe9')
    for i,r in enumerate(RECIPES):
        m=load_glb(OUT/'models'/f"{r['asset_id']}_LOD0.glb");v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
        colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax=fig.add_subplot(4,4,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='#455147',linewidths=.12))
        mid=(v.min(0)+v.max(0))/2;half=max(np.ptp(v,axis=0).max()*.56,.65)
        ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=r['asset_id'].replace('TW_STONE_','')+f' / {len(f)} tri')
        ax.set_box_aspect((1,1,1));ax.view_init(23,-65);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Original stone boundary prototypes — art approval pending',fontsize=17)
    fig.tight_layout(rect=(0,0,1,.96));fig.savefig(OUT/'preview.png',dpi=130);plt.close(fig)

if __name__=='__main__':main()
