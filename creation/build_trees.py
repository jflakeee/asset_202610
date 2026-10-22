"""Original procedural tree prototypes; uses the existing self-contained GLB writer."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.spatial import ConvexHull
from build_rocks import rand, palette_bytes, write_glb, dump
from verify_glb import load_glb

VERSION='0.2.0'
RECIPES=[
    dict(asset_id='TW_TREE_ROUND_SMALL_A',family_id='TREE_ROUND_SMALL',seed=11001,
         height_m=2.8,trunk_height_m=1.85,trunk_radius_m=.14,trunk_sides=8,trunk_rings=5,
         bend_deg=7,branch_count=3,canopy_lobes=3,canopy_width_m=1.8,canopy_height_m=1.65),
    dict(asset_id='TW_TREE_TIERED_SLIM_A',family_id='TREE_TIERED_SLIM',seed=11003,
         height_m=3.8,trunk_height_m=3.55,trunk_radius_m=.12,trunk_sides=8,trunk_rings=6,
         bend_deg=3,branch_count=0,tier_count=3,tier_sides=9,canopy_width_m=1.7,tier_overlap_ratio=.18),
]


def hull_mesh(points):
    v=np.asarray(points,dtype=float); h=ConvexHull(v); faces=[]
    for t,eq in zip(h.simplices,h.equations):
        t=t.copy()
        if np.dot(np.cross(v[t[1]]-v[t[0]],v[t[2]]-v[t[0]]),eq[:3])<0:t[[1,2]]=t[[2,1]]
        faces.append(t)
    used=sorted(set(np.array(faces).ravel())); mapping={old:i for i,old in enumerate(used)}
    f=[[mapping[x] for x in t] for t in faces]
    f=[x[x.index(min(x)):]+x[:x.index(min(x))] for x in f]
    return v[used],np.array(sorted(f),dtype=np.uint32)


def tube(centers,radii,sides):
    centers=np.asarray(centers,float); vertices=[]
    for i,c in enumerate(centers):
        tangent=centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]
        tangent/=np.linalg.norm(tangent)
        ref=np.array([0.,1,0]); u=np.cross(ref,tangent);u/=np.linalg.norm(u);w=np.cross(tangent,u)
        for k in range(sides):
            angle=2*math.pi*k/sides
            vertices.append(c+radii[i]*(u*math.cos(angle)+w*math.sin(angle)))
    faces=[]
    for i in range(len(centers)-1):
        for k in range(sides):
            a=i*sides+k;b=i*sides+(k+1)%sides;c=(i+1)*sides+k;d=(i+1)*sides+(k+1)%sides
            faces.extend([[a,b,d],[a,d,c]])
    # Cap by a fan, reversed on bottom; all faces are closed and oriented.
    for k in range(1,sides-1):
        faces.append([0,k+1,k]);off=(len(centers)-1)*sides
        faces.append([off,off+k,off+k+1])
    return np.array(vertices),np.array(faces,dtype=np.uint32)


def generate(r):
    if r['family_id'] not in ['TREE_ROUND_SMALL','TREE_TIERED_SLIM']:raise ValueError('unknown family')
    for key in ['height_m','trunk_height_m','trunk_radius_m','canopy_width_m']:
        if not math.isfinite(r[key]) or r[key]<=0:raise ValueError(key)
    if not 4<=r['trunk_sides']<=16 or not 2<=r['trunk_rings']<=12:raise ValueError('rings/sides')
    if not 0<=r['bend_deg']<=15:raise ValueError('bend')
    if r['family_id']=='TREE_ROUND_SMALL' and (r['branch_count']!=3 or r['canopy_lobes']!=3):raise ValueError('prototype supports three branches/lobes')
    if r['family_id']=='TREE_TIERED_SLIM' and (r['tier_count']!=3 or not 6<=r['tier_sides']<=12 or not 0<=r['tier_overlap_ratio']<=.3):raise ValueError('tier parameters')
    components=[]
    def add(name,mesh,kind):components.append(dict(name=name,v=mesh[0],f=mesh[1],kind=kind))
    # bend_deg is a maximum. Constrain slim-tree bend to keep the tip inside foliage.
    bend_factor=.3 if r['family_id']=='TREE_TIERED_SLIM' else 1.0
    def center(t):return np.array([bend_factor*math.tan(math.radians(r['bend_deg']))*r['trunk_height_m']*t*t,0,r['trunk_height_m']*t])
    ts=np.linspace(0,1,r['trunk_rings'])
    trunk=tube([center(t) for t in ts],[r['trunk_radius_m']*(1-.7*t) for t in ts],r['trunk_sides'])
    # Ground slice is horizontal; source frame tilt must not put vertices below ground.
    trunk[0][:r['trunk_sides'],2]=0
    add('trunk',trunk,'wood')
    if r['family_id']=='TREE_ROUND_SMALL':
        canopy=[]
        for lobe,(cx,cy,cz,sx,sy,sz) in enumerate([(-.43,-.12,1.9,.63,.60,.72),(.43,.02,2.02,.66,.58,.68),(.05,.1,2.43,.61,.57,.61)]):
            points=[]
            for j in range(1,5):
                phi=math.pi*j/5
                for k in range(9):
                    theta=2*math.pi*(k+.15*(j%2))/9
                    jitter=1+.08*(rand(r,'canopy',lobe*100+j*9+k)-.5)
                    points.append([cx+sx*math.sin(phi)*math.cos(theta)*jitter,cy+sy*math.sin(phi)*math.sin(theta)*jitter,cz+sz*math.cos(phi)*jitter])
            points.extend([[cx,cy,cz+sz],[cx,cy,cz-sz]])
            canopy.append(hull_mesh(points))
        # Normalize canopy only, keeping the trunk metric dimensions intact.
        allv=np.concatenate([m[0] for m in canopy]);lo=allv.min(0);hi=allv.max(0)
        scale=np.array([r['canopy_width_m']/(hi[0]-lo[0]),r['canopy_width_m']*.85/(hi[1]-lo[1]),r['canopy_height_m']/(hi[2]-lo[2])])
        for i,(v,f) in enumerate(canopy):
            v=(v-(lo+hi)/2)*scale
            v[:,2]+=r['height_m']-r['canopy_height_m']/2
            add(f'canopy_{i}',(v,f),'leaf')
            # Endpoints inside each convex lobe: convex average of its vertices.
            end=v.mean(0);start=center(.53+i*.09)
            add(f'branch_{i}',tube([start,end],[.065,.032],6),'wood')
    else:
        overlap=r['tier_overlap_ratio']; ratio=[1,.72,.45]
        bottom=.65;available=r['height_m']-bottom
        # Equal vertical layer heights, with the specified fractional overlap.
        h=available/(3-2*overlap)
        for j in range(3):
            z=bottom+j*h*(1-overlap);radius=r['canopy_width_m']*.5*ratio[j]
            points=[]
            for level,rr,zz in [(0,.88,z),(1,1,z+h*.16),(2,.64,z+h*.55)]:
                for k in range(r['tier_sides']):
                    angle=2*math.pi*k/r['tier_sides']
                    jitter=1+.06*(rand(r,'tier',j*100+level*12+k)-.5)
                    points.append([radius*rr*math.cos(angle)*jitter,radius*rr*math.sin(angle)*jitter,zz])
            points.append([radius*.08,0,z+h])
            add(f'tier_{j}',hull_mesh(points),'leaf')
        leaves=[c for c in components if c['kind']=='leaf'];allv=np.concatenate([c['v'] for c in leaves]);lo=allv.min(0);hi=allv.max(0)
        xycenter=(lo+hi)[:2]/2
        for c in leaves:c['v'][:,:2]=(c['v'][:,:2]-xycenter)*r['canopy_width_m']/(hi[0]-lo[0])
    verts=[];faces=[];slots=[];metadata=[];offset=0;faceoff=0
    for c in components:
        v,f=c['v'],c['f'];p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
        base=4 if c['kind']=='leaf' else 0
        ss=np.where(n[:,2]>.4,base+2,np.where(n[:,0]<-.3,base,base+1))
        verts.append(v);faces.append(f+offset);slots.extend(ss)
        metadata.append(dict(name=c['name'],vertex_start=offset,vertex_count=len(v),face_start=faceoff,face_count=len(f),kind=c['kind']))
        offset+=len(v);faceoff+=len(f)
    v=np.concatenate(verts);f=np.concatenate(faces);p=v[f];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    return v,f,n,np.array(slots),metadata


def validate(path,recipe,components):
    from collections import Counter
    m=load_glb(path);p=m['positions'];f=m['indices'].reshape(-1,3);tri=p[f]
    cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(cross,axis=1)/2
    assert np.isfinite(p).all() and np.isfinite(m['normals']).all()
    assert areas.min()>1e-10 and len(f)<=1200
    assert np.allclose(np.linalg.norm(m['normals'],axis=1),1,atol=1e-5)
    assert np.all(np.sum(cross*m['normals'][f[:,0]],axis=1)>0)
    assert abs(float(p[:,1].min()))<1e-6 and abs(float(p[:,1].max())-recipe['height_m'])<1e-5
    assert abs(float(np.ptp(p[:,0]))-recipe['canopy_width_m'])<1e-5
    assert m['image'].size==(256,256) and len(m['doc']['materials'])==1
    assert np.all((m['uv']>=0)&(m['uv']<=1))
    assert set((np.floor(m['uv'][:,1]*4)*8+np.floor(m['uv'][:,0]*8)).astype(int))<={0,1,2,4,5,6}
    volumes=[]
    for c in components:
        pts=tri[c['face_start']:c['face_start']+c['face_count']]
        u,inv=np.unique(pts.reshape(-1,3),axis=0,return_inverse=True);wf=inv.reshape(-1,3)
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in wf for a,b in zip(face,np.roll(face,-1)))
        assert all(x==2 for x in edges.values()) and len(u)-len(edges)+len(wf)==2
        volume=float(np.sum(np.einsum('ij,ij->i',pts[:,0],np.cross(pts[:,1],pts[:,2])))/6)
        assert volume>0;volumes.append(dict(component=c['name'],volume_m3=volume))
    return dict(asset_id=recipe['asset_id'],status='PASS',triangles=len(f),components=len(components),height_m=float(p[:,1].max()),width_m=float(np.ptp(p[:,0])),min_triangle_area_m2=float(areas.min()),component_volumes=volumes,engine_import='NOT_RUN',art_approval='PENDING',notes='Closed components may overlap intentionally; not a single welded watertight object.')


def render(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(14,9),facecolor='#eef1ed');light=np.array([-.4,-.5,.8]);light/=np.linalg.norm(light)
    for row,r in enumerate(RECIPES):
        m=load_glb(out/'models'/f"{r['asset_id']}_LOD0.glb");p=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);tri=p[f]
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
        uv=m['uv'][f[:,0]];im=np.array(m['image'])/255;colors=im[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]
        colors=np.clip(colors*(.64+.36*np.maximum(normals@light,0))[:,None],0,1)
        for col,(elev,azim,label) in enumerate([(20,-65,'Three-quarter'),(90,-90,'Top'),(15,-65,'Wireframe')]):
            ax=fig.add_subplot(2,3,row*3+col+1,projection='3d');ax.set_facecolor('#eef1ed')
            ax.add_collection3d(Poly3DCollection(tri,facecolors=colors,edgecolors='#304536' if col==2 else 'none',linewidths=.25))
            center=(p.min(0)+p.max(0))/2;half=max(np.ptp(p,axis=0))*.53
            ax.set_xlim(center[0]-half,center[0]+half);ax.set_ylim(center[1]-half,center[1]+half);ax.set_zlim(center[2]-half,center[2]+half)
            ax.set_box_aspect([1,1,1]);ax.set_proj_type('ortho');ax.view_init(elev,azim);ax.set_axis_off()
            name='ROUND CANOPY' if row==0 else 'TIERED CANOPY'
            ax.set_title(f"{name} / {label}\n{len(f)} triangles | {r['height_m']} m tall",fontsize=11,color='#263b30')
    fig.suptitle('TRAILWOOD / P0 TREE PROTOTYPES',fontsize=22,weight='bold',color='#20382c',y=.97)
    fig.text(.5,.025,'Actual exported GLB geometry + embedded palette / technical preview / engine testing pending',ha='center',fontsize=10,color='#526454')
    fig.subplots_adjust(top=.85,bottom=.07,hspace=.14,wspace=.02);fig.savefig(out/'preview.png',dpi=140);plt.close(fig)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=Path('trees_output'));args=ap.parse_args();out=args.out
    if out.exists():raise SystemExit('Output exists: choose a new folder.')
    (out/'models').mkdir(parents=True);(out/'textures').mkdir();png=palette_bytes();(out/'textures'/'MOSS_01.png').write_bytes(png)
    reports=[];manifest=[]
    for r in RECIPES:
        v,f,n,s,c=generate(r);data=write_glb(dict(generator_version=VERSION,**r),v,f,n,s,png);path=out/'models'/f"{r['asset_id']}_LOD0.glb";path.write_bytes(data)
        reports.append(validate(path,r,c));dump(out/'recipes'/f"{r['asset_id']}.json",r)
        dump(out/'source_meshes'/f"{r['asset_id']}.json",dict(coordinate_system='Z_UP',vertices=v.tolist(),triangles=f.tolist(),face_palette_slots=s.tolist(),components=c))
        dump(out/'provenance'/f"{r['asset_id']}.json",dict(method='Original ring tubes and seeded convex foliage',third_party_asset_inputs=[],ai_assistance='Assistant-authored code; no generated image/model inputs',source_hashes={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ['build_trees.py','build_rocks.py','verify_glb.py']},art_approval='PENDING'))
        manifest.append(dict(asset_id=r['asset_id'],triangles=len(f),file=path.relative_to(out).as_posix(),sha256=hashlib.sha256(data).hexdigest(),state='REVIEW_READY',lod='LOD0_ONLY',collider='NOT_IMPLEMENTED'))
    dump(out/'manifest.json',manifest);dump(out/'validation.json',reports)
    dump(out/'toolchain.lock.json',dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,tree_generator=VERSION,glb_writer='0.1.0',blender='NOT_AVAILABLE',godot='NOT_AVAILABLE'))
    render(out);print(json.dumps(reports,indent=2))


if __name__=='__main__':main()
