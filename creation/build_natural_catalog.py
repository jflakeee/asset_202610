"""Original canonical natural catalog candidates; no external model inputs.

Keeps the four original P0 tree/rock GLBs untouched. Every new A/B variant
changes structure or major proportions. Art approval remains human-owned.
"""
from pathlib import Path
from collections import Counter
import hashlib
import math
import json
import numpy as np
from build_rocks import dump, write_glb, palette_bytes, rand
from build_trees import hull_mesh, tube
from verify_glb import load_glb

ROOT=Path(__file__).parent
OUT=ROOT/'natural_catalog_output'
FAMILIES=['TREE_ROUND_SMALL','TREE_ROUND_BROAD','TREE_TIERED_SLIM','TREE_TIERED_WIDE','TREE_DEAD_FORK','TREE_DEAD_LEAN',
 'ROCK_LOW_WEDGE','ROCK_UPRIGHT','ROCK_FLAT_SLAB','ROCK_SPLIT_MASS','ROCK_CLUSTER_SMALL','ROCK_CLUSTER_LARGE',
 'VEG_BUSH_ROUND','VEG_BUSH_LONG','VEG_BUSH_SPARSE','VEG_GRASS_LOW','VEG_GRASS_FAN','VEG_GRASS_TUFT',
 'PROP_STUMP_ROUND','PROP_STUMP_SPLIT','PROP_LOG_STRAIGHT','PROP_LOG_BROKEN','PROP_BRANCH_FORK','PROP_BRANCH_PILE']
PRESERVED={'TW_TREE_ROUND_SMALL_A','TW_TREE_TIERED_SLIM_A','TW_ROCK_LOW_WEDGE_A','TW_ROCK_UPRIGHT_A'}
RECIPES=[dict(asset_id='TW_'+family+'_'+variant,family_id=family,variant=variant,seed=70000+i*2+j,
 generator_version='0.17.0',coordinate_frame='Z-up meters') for i,family in enumerate(FAMILIES) for j,variant in enumerate(['A','B']) if 'TW_'+family+'_'+variant not in PRESERVED]

def ellipsoid(center,radii,sides=8,rings=3,phase=0):
    pts=[]
    for j in range(1,rings+1):
        phi=math.pi*j/(rings+1)
        for k in range(sides):
            a=2*math.pi*(k+.17*(j%2))/sides+phase
            pts.append(np.array(center)+np.array(radii)*[math.sin(phi)*math.cos(a),math.sin(phi)*math.sin(a),math.cos(phi)])
    pts += [np.array(center)+[0,0,radii[2]],np.array(center)-[0,0,radii[2]]]
    return hull_mesh(pts)

def twig(centers,radii,sides=7):
    # tube's local frame requires a tangent not parallel to global Y.
    return tube(np.asarray(centers,float),radii,sides)

def generate(r):
    family=r['family_id'];b=int(r['variant']=='B');parts=[]
    def add(name,mesh,base,solid=True):parts.append(dict(name=name,v=mesh[0].copy(),f=mesh[1].copy(),base=base,solid=solid))
    if family.startswith('TREE_'):
        dead='DEAD' in family;wide='BROAD' in family or 'WIDE' in family
        h=(3.2 if wide else 2.8)+.25*b if 'ROUND' in family else (3.5 if wide else 3.8)+.3*b
        if dead:h=2.9+.35*b
        radius=(.18 if wide else .13)+.018*b
        lean=.85 if 'LEAN' in family else .18+.12*b
        centers=[[0,0,0],[lean*.15,-.035*b,h*.32],[lean*.55,.09*b,h*.66],[lean,.12*b,h*.92]]
        trunk=twig(centers,[radius*1.2,radius,radius*.69,radius*.33],8)
        trunk[0][:8,2]=0
        add('trunk',trunk,0)
        if 'ROUND' in family:
            count=(4 if wide else 3)+b
            for i in range(count):
                a=2*math.pi*i/count+.4*b;rr=.72 if wide else .48
                c=np.array([rr*math.cos(a),rr*.8*math.sin(a),h-.55-.22*(i%2)])
                add('canopy_lobe_'+str(i),ellipsoid(c,[.78 if wide else .61,.69 if wide else .57,.72+.08*b],8+b,3,phase=.2*i),4,False)
                add('branch_'+str(i),twig([[lean*.25,0,h*.43],c],[radius*.43,.03],6),0)
            add('canopy_top',ellipsoid([lean*.3,0,h-.25],[.65 if wide else .5,.61 if wide else .46,.5],8,3),4,False)
        elif 'TIERED' in family:
            count=3+b;bottom=.65;layer=(h-bottom)/(count-.2*(count-1));width=1.3 if wide else .85
            for i in range(count):
                z=bottom+i*layer*.8;rad=width*(1-.19*i);pts=[]
                for lev,rr,zz in [(0,.86,z),(1,1,z+.16*layer),(2,.53,z+.65*layer)]:
                    for k in range(8+b):
                        a=2*math.pi*k/(8+b)+i*.11
                        pts.append([rad*rr*math.cos(a)+lean*.3,rad*rr*math.sin(a),zz])
                pts.append([lean*.5,0,z+layer]);add('tier_'+str(i),hull_mesh(pts),4,False)
        else:
            count=(3 if 'FORK' in family else 2)+b
            for i in range(count):
                a=.3+i*2.3;z=h*(.42+.12*i);start=np.array([lean*(z/h)**1.5,0,z]);reach=.62+.19*(i%2)
                middle=start+[reach*.64*math.cos(a),reach*.64*math.sin(a),.32]
                end=start+[reach*math.cos(a),reach*math.sin(a),.72-.1*(i%2)]
                add('dead_branch_'+str(i),twig([start,middle,end],[radius*.55,.065,.025],6+b),0)
    elif family.startswith('ROCK_'):
        if 'CLUSTER' in family:count=(3 if 'SMALL' in family else 5)+b
        elif 'SPLIT' in family:count=2+b
        else:count=1
        for i in range(count):
            if 'UPRIGHT' in family:size=np.array([.95,.57,1.75])
            elif 'FLAT' in family:size=np.array([1.45+.2*b,.92-.1*b,.24+.07*b])
            elif 'WEDGE' in family:size=np.array([1.4,.82,.56])
            elif 'SPLIT' in family:size=np.array([.65,.83,1.1])
            else:size=np.array([.63,.58,.61])*(1+.18*(i%3))*(1.3 if 'LARGE' in family else 1)
            size*=np.array([1+.12*b,1-.08*b,1+.06*b])
            if 'SPLIT' in family:center=np.array([(i-(count-1)/2)*.63,0,0])
            else:center=np.array([.38*math.cos(i*2.4),.34*math.sin(i*2.4),0]) if count>1 else np.zeros(3)
            pts=[];sides=7+b
            for j,(z,rad) in enumerate([(0,.83),(.28,1),(.73,.79),(1,.45)]):
                for k in range(sides):
                    a=2*math.pi*k/sides+.12*j
                    jitter=1+.14*(rand(r,'facet',i*100+j*sides+k)-.5)
                    pt=np.array([math.cos(a)*rad*.5*jitter+.13*z*(1 if b else -1),math.sin(a)*rad*.5*jitter,z])
                    if j==3:pt[2]-=.16*(.5+.5*math.cos(a))
                    pts.append(center+size*pt)
            add('rock_mass_'+str(i),hull_mesh(pts),8)
    elif family.startswith('VEG_BUSH'):
        count=(3 if 'ROUND' in family else 4 if 'LONG' in family else 2)+b
        for i in range(count):
            if 'LONG' in family:c=[(i-(count-1)/2)*.33,.07*((i%2)*2-1),.3]
            elif 'SPARSE' in family:c=[(i-(count-1)/2)*.46,.14*(i%2),.29+.1*(i%2)]
            else:
                a=2*math.pi*i/count;c=[.22*math.cos(a),.22*math.sin(a),.34+.05*(i%2)]
            radii=[.33,.28,.3] if 'SPARSE' in family else [.38+.03*b,.34,.35]
            add('bush_lobe_'+str(i),ellipsoid(c,radii,7+b,2),4,False)
    elif family.startswith('VEG_GRASS'):
        count=5+2*b
        for i in range(count):
            fan='FAN' in family;low='LOW' in family
            a=(math.pi*i/(count-1)) if fan else 2*math.pi*i/count+.2*b
            h=(.22 if low else .65 if fan else .42)*( .8+.35*rand(r,'height',i))
            radial=np.array([math.cos(a),math.sin(a),0]);side=np.array([-math.sin(a),math.cos(a),0])
            base=np.array([(i-(count-1)/2)*.045,0,0]) if fan else radial*.055
            width=.035 if low else .045;mid=base+radial*.09+[0,0,h*.55];tip=base+radial*(.14+.04*b)+[0,0,h]
            pts=[base-side*width,base+side*width,base+radial*.018,mid-side*width*.6,mid+side*width*.6,mid+radial*.025,tip]
            add('solid_blade_'+str(i),hull_mesh(pts),12,False)
    elif family.startswith('PROP_STUMP'):
        split='SPLIT' in family;radius=.34+.09*b;h=.5+.16*b;sides=9+b
        if not split:
            mesh=twig([[0,0,0],[.025*b,0,h*.32],[.06*b,0,h]],[radius*1.18,radius,radius*.84],sides)
            mesh[0][:sides,2]=0;add('stump',mesh,0)
            for i in range(3+b):
                a=i*2*math.pi/(3+b);end=[radius*1.4*math.cos(a),radius*1.4*math.sin(a),.06]
                add('root_flare_'+str(i),twig([[0,0,.19],end],[.11,.035],6),0)
        else:
            # Two individually closed separated pieces form a visible split;
            # each split half has a large angled top rather than a concave fan cap.
            sectors=3 if b else 2
            for sector in range(sectors):
                pts=[];angle=sector*2*math.pi/sectors
                for z,scale in [(0,1.15),(h*.5,1),(h, .84)]:
                    pts.append([.035*math.cos(angle),.035*math.sin(angle),z])
                    for k in range(7):
                        a=angle-math.pi/sectors+.04+k*(2*math.pi/sectors-.08)/6
                        top_notch=(.16 if b and sector==1 else .09) if k in [2,3] and z==h else 0
                        pts.append([radius*scale*math.cos(a),radius*scale*math.sin(a),z-top_notch])
                add('split_sector_'+str(sector),hull_mesh(pts),0)
    elif family.startswith('PROP_LOG'):
        broken='BROKEN' in family;length=(1.65 if broken else 2.2)+.35*b;radius=.2+.04*b
        centers=[[-length/2,0,radius],[-length*.1,.05*b,radius],[length/2,.09*b,radius]]
        mesh=twig(centers,[radius,radius*.93,radius*.82],10+b)
        if broken:
            # Nonplanar closed cap produced by convex hull per splinter.
            mesh=twig(centers[:-1]+[[length/2-.18,.09*b,radius]],[radius,radius*.93,radius*.82],10+b)
            for i in range(3+b):
                a=i*2*math.pi/(3+b);c=np.array([length/2-.2,.09*b,radius])+[0,math.cos(a)*radius*.55,math.sin(a)*radius*.55]
                add('broken_splinter_'+str(i),twig([c,c+[.19+.08*(i%2),0,.015]],[.065,.012],5),0)
        add('log_body',mesh,0)
        for i in range(1+b):
            x=-.4+i*.65;add('branch_stub_'+str(i),twig([[x,0,radius],[x+.06,(-1 if i%2 else 1)*.28,radius+.22]],[.075,.035],6),0)
    elif family.startswith('PROP_BRANCH'):
        pile='PILE' in family
        count=(3+b) if pile else 1
        for i in range(count):
            angle=(i*.71 if pile else .13*b);length=1.2+.19*b-.09*i
            direction=np.array([math.cos(angle),math.sin(angle),0]);start=-direction*length*.5+[0,0,.075+i*.08]
            end=direction*length*.5+[0,0,.1+i*.08]
            add('branch_'+str(i),twig([start,(start+end)/2+[0,.04,.04],end],[.065,.05,.018],6+b),0)
            fork=(start+end)/2;tip=fork+[-.13,.42 if not pile else .26,.08]
            add('fork_'+str(i),twig([fork,tip],[.045,.012],5),0)
            if not pile and b:add('second_fork',twig([fork+direction*.23,fork+[.38,-.31,.16]],[.035,.01],5),0)
    else:raise ValueError(family)
    # Place ground-contact center at origin without changing relative parts.
    allv=np.concatenate([p['v'] for p in parts]);shift=np.array([(allv[:,0].min()+allv[:,0].max())/2,(allv[:,1].min()+allv[:,1].max())/2,allv[:,2].min()])
    vv=[];ff=[];ss=[];meta=[];coll=[];off=0;foff=0
    for p in parts:
        v=p['v']-shift;f=p['f'];tris=v[f];cross=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);areas=np.linalg.norm(cross,axis=1)
        assert areas.min()>1e-9,p['name'];norm=cross/areas[:,None]
        edges=Counter(tuple(sorted((int(a),int(b)))) for face in f for a,b in zip(face,np.roll(face,-1)))
        assert all(x==2 for x in edges.values()) and len(v)-len(edges)+len(f)==2,p['name']
        assert np.einsum('ij,ij->i',tris[:,0],np.cross(tris[:,1],tris[:,2])).sum()>0,p['name']
        slots=np.where(norm[:,2]>.4,p['base']+2,np.where(norm[:,0]<-.25,p['base'],p['base']+1))
        # Visible end grain on axial tube caps, retaining palette UV convention.
        if p['base']==0:
            cap=(np.abs(norm[:,0])>.96) if family.startswith('PROP_LOG') else (norm[:,2]>.96)
            slots=np.where(cap,3,slots)
        vv.append(v);ff.append(f+off);ss.extend(slots.tolist());meta.append(dict(name=p['name'],vertex_start=off,vertex_count=len(v),face_start=foff,face_count=len(f)))
        if p['solid']:
            cv,_=hull_mesh(v);coll.append(dict(type='convex_hull',points_m=cv.tolist()))
        off+=len(v);foff+=len(f)
    v=np.concatenate(vv);f=np.concatenate(ff);t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    collider=dict(type='compound',parts=coll) if coll else None
    return v,f,n,np.array(ss),meta,collider

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    for prefix in ['TREE','ROCK','VEG','PROP']:
        recipes=[r for r in RECIPES if r['family_id'].startswith(prefix)]
        fig=plt.figure(figsize=(15,3.6*math.ceil(len(recipes)/4)),facecolor='#efeee7')
        for i,r in enumerate(recipes):
            m=load_glb(OUT/'models'/f"{r['asset_id']}_LOD0.glb");v=m['positions'][:,[0,2,1]]*[1,-1,1];f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
            color=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
            ax=fig.add_subplot(math.ceil(len(recipes)/4),4,i+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=color,edgecolors='#58604c',linewidths=.12))
            mid=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.56
            ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=r['asset_id'].replace('TW_','')+'\n'+str(len(f))+' tris')
            ax.set_box_aspect((1,1,1));ax.view_init(23,-60);ax.set_axis_off()
        fig.suptitle('TRAILWOOD / '+prefix+' canonical candidates - art approval pending',fontsize=17)
        fig.tight_layout(rect=(0,0,1,.96));fig.savefig(OUT/(prefix.lower()+'_preview.png'),dpi=140);plt.close(fig)

def main():
    reports=[];catalog=[];hashes={};png=palette_bytes()
    for r in RECIPES:
        v,f,n,s,meta,collider=generate(r);p=OUT/'models'/f"{r['asset_id']}_LOD0.glb";p.parent.mkdir(parents=True,exist_ok=True)
        data=write_glb(r,v,f,n,s,png);p.write_bytes(data);m=load_glb(p)
        assert np.isfinite(m['positions']).all() and np.isfinite(m['normals']).all()
        assert np.allclose(np.linalg.norm(m['normals'],axis=1),1,atol=1e-5)
        assert abs(m['positions'][:,1].min())<1e-6
        assert np.allclose(np.ptp(m['positions'],axis=0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-5)
        assert len(f)<1200
        again=generate(r);assert write_glb(r,*again[:4],png)==data
        h=hashlib.sha256(v.tobytes()+f.tobytes()).hexdigest();assert h not in hashes.values();hashes[r['asset_id']]=h
        dump(OUT/'recipes'/f"{r['asset_id']}.json",r)
        dump(OUT/'source_meshes'/f"{r['asset_id']}.json",dict(vertices=v.tolist(),triangles=f.tolist(),slots=s.tolist(),components=meta,coordinate_frame='Z-up meters'))
        dump(OUT/'provenance'/f"{r['asset_id']}.json",dict(origin='Original parametric tubes, hulls and own palette',external_geometry_inputs=[],source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['build_natural_catalog.py','build_trees.py','build_rocks.py']},art_approval='PENDING'))
        catalog.append(dict(asset_id=r['asset_id'],family_id=r['family_id'],variant=r['variant'],file='props/'+p.name,triangles=len(f),collider=collider,wind_supported=False,lod='LOD0_ONLY',lod_omission_reason='Candidate stage; screen-size and silhouette requirements not evaluated',art_approval='PENDING'))
        reports.append(dict(asset_id=r['asset_id'],status='PASS',triangles=len(f),closed_components=len(meta),dimensions_xyz_m=np.ptp(v,axis=0).tolist(),geometry_sha256=h,engine_import='NOT_RUN',art_approval='PENDING'))
    assert len(catalog)==44
    # Order independence is intrinsic: recipes use keyed random streams, no global RNG.
    for r in reversed(RECIPES):
        v,f,*_=generate(r);assert hashlib.sha256(v.tobytes()+f.tobytes()).hexdigest()==hashes[r['asset_id']]
    dump(OUT/'catalog.json',dict(assets=catalog,coordinate_frame='Z-up meters',external_geometry_inputs=[],preserved_original_ids=sorted(PRESERVED)))
    dump(OUT/'validation.json',dict(status='PASS',new_models=len(reports),assets=reports,deterministic_repeat='PASS',reversed_recipe_order='PASS',duplicate_geometry='NONE',gpu_render='NOT_RUN',art_approval='PENDING'))
    render();print(json.dumps(dict(new_models=len(catalog),triangles_total=sum(x['triangles'] for x in catalog),status='PASS',art_approval='PENDING')))

if __name__=='__main__':main()
