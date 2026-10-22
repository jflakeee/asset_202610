"""Example-only sloped rails regenerated from profiles; posts remain vertical."""
from pathlib import Path
import math,struct,json
from collections import Counter
import numpy as np
from build_fences import prism
from build_camp_props import box
from build_rocks import write_glb,palette_bytes,dump
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'slope_examples_output'

def generate(degrees,length=2.):
    if not math.isfinite(degrees) or abs(degrees)>15:raise ValueError('MANUAL_SLOPE_OVER_15_DEG')
    if not math.isfinite(length) or length<=.14:raise ValueError('INVALID_LENGTH')
    slope=math.tan(math.radians(degrees));rise=length*slope
    components=[]
    # Terminal post included in this self-contained example, not a sale module.
    for x in [0.,length]:components.append(('vertical_post',*box([x,0,slope*x+.55],[.14,.14,1.1])))
    for z in [.4,.8]:
        a=.07;b=length-.07
        profile=[(a,z+slope*a-.06),(b,z+slope*b-.06),(b,z+slope*b+.06),(a,z+slope*a+.06)]
        components.append(('sloped_rail',*prism(profile,.08)))
    vv=[];ff=[];slots=[];off=0;parts=[]
    for name,v,f in components:
        edges=Counter(tuple(sorted((int(a),int(b)))) for tri in f for a,b in zip(tri,np.roll(tri,-1)))
        assert all(count==2 for count in edges.values()) and len(v)-len(edges)+len(f)==2
        assert np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()>0
        if name=='vertical_post':assert np.allclose(np.ptp(v,axis=0),[.14,.14,1.1])
        vv.append(v);ff.append(f+off);off+=len(v);slots.extend([17 if name=='vertical_post' else 18]*len(f))
        parts.append(dict(type='convex_hull',points_m=v.tolist(),role=name))
    v=np.concatenate(vv);f=np.concatenate(ff);n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None]
    assert np.isfinite(n).all()
    return v,f,n,np.array(slots),parts,rise

def main():
    reports=[]
    for degrees in [0,15,-15]:
        v,f,n,slots,parts,rise=generate(degrees)
        asset='TW_EXAMPLE_SLOPE_'+str(degrees).replace('-','MINUS')
        data=write_glb(dict(asset_id=asset,seed=0,generator_version='0.18'),v,f,n,slots,palette_bytes())
        size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);binary=data[20+size:]
        nodes=[dict(name='SOCKET_START',translation=[0,0,0],extras=dict(outward=[-1,0,0],up=[0,1,0])),dict(name='SOCKET_END',translation=[2,rise,0],extras=dict(outward=[1,0,0],up=[0,1,0]))]
        doc['nodes'].extend(nodes);doc['scenes'][0]['nodes'].extend([1,2])
        raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
        result=struct.pack('<4sII',b'glTF',2,20+len(raw)+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+binary
        path=OUT/'models'/f'{asset}_LOD0.glb';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(result)
        loaded=load_glb(path);assert np.allclose(np.ptp(loaded['positions'],axis=0),np.ptp(v,axis=0)[[0,2,1]],atol=1e-6)
        dump(OUT/'colliders'/f'{asset}.json',dict(type='compound',parts=parts,coordinate_frame='source Z-up meters'))
        dump(OUT/'source_meshes'/f'{asset}.json',dict(vertices=v.tolist(),triangles=f.tolist(),slots=slots.tolist()))
        reports.append(dict(asset_id=asset,degrees=degrees,rise_m=rise,triangles=len(f),vertical_posts=2,terminal_included=True,status='PASS'))
    rejected=[]
    for slope in [16,-16,float('nan')]:
        try:generate(slope)
        except ValueError:rejected.append(str(slope))
        else:raise AssertionError('Out-of-range slope accepted')
    dump(OUT/'validation.json',dict(status='PASS',examples=reports,rejected_inputs=rejected,
        canonical_count_contribution=0,terrain='linear height h(x)=x*tan(angle); post feet use centerline terrain samples',
        surface_contact='NOT_RUN',engine_physics='NOT_RUN',art_approval='PENDING'))
    print('Slope examples 0/+15/-15 generated; vertical posts; reject +/-16: PASS')

if __name__=='__main__':main()
