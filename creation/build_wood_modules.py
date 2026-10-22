"""Original missing canonical wood boundary candidates, independent deterministic build."""
from pathlib import Path
from collections import Counter
import json, struct, hashlib
import numpy as np
from build_camp_props import box
from build_fences import prism
from build_rocks import dump, write_glb, palette_bytes
from verify_glb import load_glb

ROOT=Path(__file__).parent
OUT=ROOT/'wood_modules_output'
FAMILIES=['RAIL_1M','RAIL_2M','RAIL_4M','CORNER_L90','CORNER_R90','END_CAP','END_BROKEN','POST','GATE_FRAME','GATE_LEAF']
IDS=['TW_WOOD_'+family+'_'+variant for family in FAMILIES for variant in 'AB' if not (family in ['RAIL_1M','RAIL_2M'] and variant=='A')]

def gltf_point(p):return [float(p[0]),float(p[2]),-float(p[1])]

def generate(asset):
    family=asset[len('TW_WOOD_'):-2];variant=asset[-1];components=[];sockets=[]
    def add(name,vf,slot=17):
        v,f=vf;components.append((name,np.asarray(v),np.asarray(f),slot))
    def cube(name,c,s,slot=17):add(name,box(c,s),slot)
    def post(x,y,height=1.1,broken=False):
        top=[(.07,height-.10),(.035,height-.15),(.0,height),(-.025,height-.12),(-.07,height-.06)] if broken else [(.07,height-.04),(.045,height),(-.045,height),(-.07,height-.04)]
        profile=[(-.07,0),(.07,0)]+top
        v,f=prism(profile,.14);v+=np.array([x,y,0]);add('post', (v,f),17)
        if variant=='B' and family!='GATE_FRAME':cube('post_collar',[x,y,height-.19],[.18,.18,.065],18)
    def beam(name,a,b,z):
        a=np.array(a,float);b=np.array(b,float);delta=b-a;length=np.linalg.norm(delta);u=delta/length
        v,f=box([length/2,0,z],[length,.08,.12]);rot=np.array([[u[0],-u[1],0],[u[1],u[0],0],[0,0,1]])
        v=v@rot.T+np.array([a[0],a[1],0]);add(name,(v,f),18)
    def socket(name,p,out):sockets.append(dict(name=name,position_m=gltf_point(p),outward_axis=gltf_point(out),up_axis=[0,1,0]))
    socket('SOCKET_START',[0,0,0],[-1,0,0])
    aperture=None;notes=[]
    if family.startswith('RAIL_'):
        length=float(family.split('_')[1][:-1]);post(0,0)
        for z in [.4,.8]:beam('rail',[.07,0],[length-.07,0],z)
        if variant=='B':
            # A structural diagonal on the rear face changes silhouette, never socket positions.
            a=np.array([.13,.065,.34]);b=np.array([length-.13,.065,.86]);d=b-a;L=np.linalg.norm(d);u=d/L
            v,f=box([L/2,0,0],[L,.055,.065]);theta=np.arctan2(d[2],d[0]);rot=np.array([[np.cos(theta),0,-np.sin(theta)],[0,1,0],[np.sin(theta),0,np.cos(theta)]])
            add('diagonal_brace',(v@rot.T+a,f),16)
        socket('SOCKET_END',[length,0,0],[1,0,0])
    elif family.startswith('CORNER_'):
        sign=1 if family=='CORNER_L90' else -1
        post(0,0);post(.5,0)
        for z in [.4,.8]:
            beam('incoming_rail',[.07,0],[.43,0],z)
            beam('outgoing_rail',[.5,sign*.07],[.5,sign*.43],z)
        if family=='CORNER_R90':
            cube('right_corner_vertical_tie',[.25,0,.6],[.065,.12,.53],16)
        if variant=='B':
            cube('outgoing_vertical_tie',[.5,sign*.25,.6],[.12,.065,.53],16)
        socket('SOCKET_END',[.5,sign*.5,0],[0,sign,0])
        notes.append('Owns start and internal turn posts; outgoing end post belongs to next module.')
    elif family in ['END_CAP','END_BROKEN','POST']:
        post(0,0,broken=family=='END_BROKEN')
        if family=='END_CAP':cube('terminal_cap',[0,0,1.13],[.20,.20,.06],18)
        if family=='END_BROKEN':
            # Broken top is aesthetic; lower supporting section is intact.
            cube('exposed_end_band',[0,0,.90],[.145,.145,.04],19)
        notes.append('Terminal only: one connection socket, no outgoing span.')
    elif family=='GATE_FRAME':
        # The right jamb is internal. Exit at 1.6 still does not own an end post.
        post(0,0,2.2);post(1.3,0,2.2)
        cube('lintel',[.65,0,2.12],[1.44,.16,.16],18)
        for z in [.4,.8]:beam('exit_rail',[1.37,0],[1.53,0],z)
        if variant=='B':cube('lintel_crown',[.65,0,2.235],[1.0,.12,.07],18)
        socket('SOCKET_END',[1.6,0,0],[1,0,0])
        socket('SOCKET_HINGE',[.07,0,0],[1,0,0])
        aperture=dict(x_min=.07,x_max=1.23,z_min=0,z_max=2.04,width_m=1.16,height_m=2.04)
        notes.append('Internal right jamb at x=1.3; reserved module span 1.6m. No collider across aperture.')
    else:
        sockets=[];socket('SOCKET_HINGE',[0,0,0],[1,0,0])
        width=1.12;count=5 if variant=='A' else 7
        for i in range(count):
            h=1.65 if variant=='A' else 1.53+.18*(1-abs((i+.5)/count*2-1))
            cube('gate_plank',[(i+.5)*width/count,0,.12+h/2],[width/count-.015,.07,h],17 if i%2 else 18)
        for z in [.4,1.45]:cube('gate_crossbar',[width/2,.065,z],[width,.06,.10],16)
        for z in [.4,1.45]:cube('hinge_block',[.025,-.065,z],[.05,.06,.08],16)
        notes.append('Hinge origin at x=y=z=0, leaf bottom clearance 0.12m; mount at frame SOCKET_HINGE. Static separate body, no animation.')
    vs=[];fs=[];slots=[];meta=[];colliders=[];offset=0
    for name,v,f,slot in components:
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(n==2 for n in edges.values()) and len(v)-len(edges)+len(f)==2
        p=v[f];assert np.einsum('ij,ij->i',p[:,0],np.cross(p[:,1],p[:,2])).sum()>1e-10
        vs.append(v);fs.append(f+offset);slots.extend([slot]*len(f));offset+=len(v)
        meta.append(dict(name=name,vertices=v.tolist(),triangles=f.tolist()))
        colliders.append(dict(type='convex_hull',points_m=v.tolist(),component=name))
    v=np.concatenate(vs);f=np.concatenate(fs);n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(slots),meta,sockets,dict(type='compound',parts=colliders),aperture,notes

def with_sockets(data,sockets):
    size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);binary=data[20+size:]
    for s in sockets:
        doc['nodes'].append(dict(name=s['name'],translation=s['position_m'],extras=dict(outward=s['outward_axis'],up=s['up_axis'])))
        doc['scenes'][0]['nodes'].append(len(doc['nodes'])-1)
    raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*(-len(raw)%4)
    return struct.pack('<4sII',b'glTF',2,20+len(raw)+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+binary

def main():
    entries=[];reports=[]
    for asset in IDS:
        v,f,n,s,meta,sockets,collider,aperture,notes=generate(asset)
        recipe=dict(asset_id=asset,seed=0,generator_version='0.17.0',family_id=asset[3:-2],variant=asset[-1])
        data=with_sockets(write_glb(recipe,v,f,n,s,palette_bytes()),sockets)
        path=OUT/'models'/f'{asset}_LOD0.glb';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        m=load_glb(path);tri=m['positions'][m['indices']].reshape(-1,3,3);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        assert np.isfinite(m['positions']).all() and np.linalg.norm(cross,axis=1).min()>1e-9
        assert np.all(np.sum(cross*m['normals'][m['indices'][::3]],axis=1)>0)
        assert np.allclose(np.ptp(m['positions'],axis=0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-6)
        assert abs(m['positions'][:,1].min()-(.12 if 'GATE_LEAF' in asset else 0))<1e-6
        nodes={x['name']:x for x in m['doc']['nodes']}
        assert all(nodes[x['name']]['translation']==x['position_m'] for x in sockets)
        assert data==with_sockets(write_glb(recipe,v,f,n,s,palette_bytes()),sockets)
        if aperture:
            # Every component excludes a box representing the required aperture.
            for c in collider['parts']:
                p=np.array(c['points_m']);lo=p.min(0);hi=p.max(0)
                assert hi[0]<=.0700001 or lo[0]>=1.2299999 or lo[2]>=2.0399999
        dump(OUT/'source_meshes'/f'{asset}.json',dict(coordinate_frame='Z-up meters',components=meta))
        dump(OUT/'recipes'/f'{asset}.json',recipe)
        entries.append(dict(asset_id=asset,file='props/'+path.name,triangles=len(f),collider=collider,sockets=sockets,socket_coordinate_frame='Y-up meters',aperture=aperture,notes=notes,lod_omission_reason='LOD0 engineering candidate; simplification and four-view IoU review pending',art_approval='PENDING'))
        reports.append(dict(asset_id=asset,triangles=len(f),closed_components=len(meta),status='PASS',sha256=hashlib.sha256(data).hexdigest(),aperture_check='PASS' if aperture else 'NOT_APPLICABLE',engine_test='NOT_RUN',art_approval='PENDING'))
    dump(OUT/'catalog.json',dict(assets=entries,coordinate_frame='Z-up meters for colliders; Y-up for sockets',external_geometry_inputs=[]))
    dump(OUT/'validation.json',dict(status='PASS',assets=reports,models=len(entries),existing_1m_2m_A='Not rewritten',art_approval='PENDING'))
    dump(OUT/'provenance.json',dict(origin='Original dimensioned wood profiles and component assemblies',external_geometry_inputs=[],generator='build_wood_modules.py',generator_version='0.17.0'))
    render();print(json.dumps(dict(models=len(entries),status='PASS',triangles=sum(e['triangles'] for e in entries))))

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(15,18),facecolor='#f0ece2')
    for i,asset in enumerate(IDS):
        m=load_glb(OUT/'models'/f'{asset}_LOD0.glb');v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
        colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
        ax=fig.add_subplot(6,3,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='#59452f',linewidths=.12))
        mid=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.57
        ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=asset.replace('TW_WOOD_','')+f' | {len(f)} tris')
        ax.set_box_aspect((1,1,1));ax.view_init(20,-65);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Wood module candidates - actual GLB geometry',fontsize=18);fig.tight_layout(rect=(0,0,1,.97));fig.savefig(OUT/'preview.png',dpi=140);plt.close(fig)

if __name__=='__main__':main()
