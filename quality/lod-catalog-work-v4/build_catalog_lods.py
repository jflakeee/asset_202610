"""Measured LOD candidates for all canonical models; never grants omission/art approval."""
from pathlib import Path
import sys,json,copy,struct,hashlib
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
root=Path(sys.argv[1]).resolve()/'creation';sys.path.insert(0,str(root))
from build_lods import simplify
from build_rocks import write_glb
from verify_glb import load_glb
from verify_lod_iou import VIEWS,frame,mask,iou
R=Path(__file__).resolve().parent
records=json.loads((root/'asset_records_output/asset_records.json').read_text())['records'];rows=[]
for record in records:
    asset=record['asset_id'];p0=root/'theme_output/MOSS_01/models'/f'{asset}_LOD0.glb';base=load_glb(p0);oldv=base['positions'][:,[0,2,1]]*np.array([1,-1,1]);oldf=base['indices'].reshape(-1,3)
    refs=[root/e['path'] for e in record['provenance']['evidence'] if e['kind']=='source_meshes']
    if not refs:refs=list(root.glob(f'*/source_meshes/{asset}.json'))
    src=json.loads(refs[0].read_text());components=src.get('components') or [dict(name='whole',vertex_start=0,vertex_count=len(src['vertices']),face_count=len(src['triangles']))];parts=[];face_cursor=0
    for c in components:
        if 'vertices' in c:v=np.array(c['vertices']);f=np.array(c['triangles'])
        else:
            start=c['vertex_start'];v=np.array(src['vertices'][start:start+c['vertex_count']]);count=c.get('face_count',c.get('triangle_count'));startface=c.get('face_start',face_cursor);f=np.array(src['triangles'][startface:startface+count])-start;face_cursor=startface+count
        parts.append((v,f))
    slot_uv=base['uv'][oldf[:,0]];oldslots=(np.floor(slot_uv[:,1]*4).astype(int)*8+np.floor(slot_uv[:,0]*8).astype(int));tree=cKDTree(oldv[oldf].mean(1));entry=dict(asset_id=asset,lod0_triangles=len(oldf),source_sha256=hashlib.sha256(p0.read_bytes()).hexdigest(),approval='PENDING',levels=[])
    for lod,ratio,tolerance,threshold in [(1,.5,.01,.95),(2,.2,.02,.88)]:
        # Tighter per-asset support limits after recorded first-attempt silhouette failures.
        tolerance={('TW_PROP_BRANCH_FORK_A',1):.005,('TW_PROP_LOG_STRAIGHT_A',2):.01}.get((asset,lod),tolerance)
        vv=[];ff=[];offset=0
        for v,f in parts:
            volume=abs(float(np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6));hull=ConvexHull(v)
            if abs(hull.volume-volume)>max(1e-8,hull.volume*1e-5):nv,nf=v,f
            else:nv,nf,_=simplify(v,max(8,int(len(f)*ratio)),float(np.ptp(oldv,axis=0).max())*tolerance)
            vv.append(nv);ff.append(nf+offset);offset+=len(nv)
        v=np.concatenate(vv);f=np.concatenate(ff)
        if len(f)>=len(oldf):
            entry['levels'].append(dict(lod=lod,support_tolerance_ratio=tolerance,status='OMISSION_REVIEW_REQUIRED',reason='No triangle reduction under bounds/support constraints',triangles=len(f),exception_approved=False));continue
        n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);length=np.linalg.norm(n,axis=1);assert (length>1e-10).all();n/=length[:,None]
        slots=oldslots[tree.query(v[f].mean(1))[1]];data=write_glb(dict(asset_id=asset,seed=0,lod=lod,generator_version='LOD_CATALOG_CANDIDATE_1'),v,f,n,slots,base['png'])
        size=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+size]);binary=data[20+size:];doc['nodes']=copy.deepcopy(base['doc']['nodes']);doc['scenes']=copy.deepcopy(base['doc']['scenes']);doc['materials']=copy.deepcopy(base['doc']['materials']);doc['nodes'][0]['name']=f'{asset}_LOD{lod}';doc['extras']['art_approval']='PENDING'
        raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);data=struct.pack('<4sII',b'glTF',2,20+len(raw)+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+binary
        path=R/'models'/f'{asset}_LOD{lod}.glb';path.write_bytes(data);loaded=load_glb(path);ev=loaded['positions'][:,[0,2,1]]*np.array([1,-1,1]);ef=loaded['indices'].reshape(-1,3)
        views={}
        for name,view in VIEWS.items():
            center,scale=frame(oldv,ev,view);views[name]=iou(mask(oldv,oldf,view,center,scale),mask(ev,ef,view,center,scale))
        sockets=lambda d:[x for x in d['nodes'] if x.get('name','').startswith(('SOCKET_','HINGE'))]
        assert sockets(base['doc'])==sockets(loaded['doc'])
        entry['levels'].append(dict(lod=lod,support_tolerance_ratio=tolerance,status='SILHOUETTE_PASS_REVIEW_REQUIRED' if min(views.values())>=threshold else 'SILHOUETTE_FAIL',triangles=len(f),views=views,threshold=threshold,sockets_preserved=True,collider_policy='Reuse unchanged LOD0 collider; engine binding unverified',file=path.relative_to(R).as_posix(),sha256=hashlib.sha256(data).hexdigest(),exception_approved=False))
    rows.append(entry);(R/'reports/catalog.json').write_text(json.dumps(dict(models=rows,complete_candidates=len(rows)==84,sales_approved=False),indent=2));print(len(rows),asset,[e['status'] for e in entry['levels']],flush=True)

expected={e['file'] for m in rows for e in m['levels'] if 'file' in e}
for path in (R/'models').glob('*.glb'):
    if path.relative_to(R).as_posix() not in expected:path.unlink()
