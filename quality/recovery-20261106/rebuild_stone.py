"""Rebuild visual contact-face candidates from the restored GitHub baseline."""
from pathlib import Path
import copy,hashlib,json,struct,sys,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'creation'))
from verify_glb import load_glb
from build_rocks import write_glb
from verify_lod_iou import VIEWS,frame,mask,iou
EPS=1e-9
def covered(lo,hi,rects):
 if not rects:return False
 cuts=[sorted(set([lo[k],hi[k]]+[float(np.clip(x,lo[k],hi[k])) for a,b in rects for x in [a[k],b[k]]])) for k in range(2)]
 for x0,x1 in zip(cuts[0],cuts[0][1:]):
  for y0,y1 in zip(cuts[1],cuts[1][1:]):
   if x1-x0<=EPS or y1-y0<=EPS:continue
   p=np.array([(x0+x1)/2,(y0+y1)/2])
   if not any(np.all(p>=a-EPS) and np.all(p<=b+EPS) for a,b in rects):return False
 return True

def reduce(src):
 v=np.asarray(src['vertices']);f=np.asarray(src['triangles']);boxes=[];cursor=0
 for c in src['components']:
  p=v[c['vertex_start']:c['vertex_start']+c['vertex_count']];lo=p.min(0);hi=p.max(0)
  assert len(p)==8 and c['triangle_count']==12 and np.all(np.isclose(p,lo,atol=EPS,rtol=0)|np.isclose(p,hi,atol=EPS,rtol=0))
  boxes.append((lo,hi,cursor));cursor+=12
 assert cursor==len(f);removed=[]
 for owner,(lo,hi,start) in enumerate(boxes):
  groups={}
  for index in range(start,start+12):
   tri=v[f[index]];n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n/=np.linalg.norm(n);axis=int(np.argmax(abs(n)));assert abs(abs(n[axis])-1)<EPS
   groups.setdefault((axis,1 if n[axis]>0 else -1),[]).append(index)
  for (axis,sign),indices in groups.items():
   assert len(indices)==2
   plane=hi[axis] if sign>0 else lo[axis];axes=[k for k in range(3) if k!=axis];rects=[]
   for other,(a,b,_) in enumerate(boxes):
    if other==owner:continue
    beyond=(a[axis]<=plane+EPS and b[axis]>plane+EPS) if sign>0 else (a[axis]<plane-EPS and b[axis]>=plane-EPS)
    if beyond and np.all(np.minimum(hi[axes],b[axes])-np.maximum(lo[axes],a[axes])>EPS):rects.append((a[axes],b[axes]))
   if covered(lo[axes],hi[axes],rects):removed.extend(indices)
 return np.array([k for k in range(len(f)) if k not in set(removed)])

def main():
 lo=np.zeros(2);hi=np.ones(2)
 assert covered(lo,hi,[(lo,np.array([.5,1])),(np.array([.5,0]),hi)])
 assert not covered(lo,hi,[(lo,np.array([.49,1])),(np.array([.51,0]),hi)])
 rows=[];inputs={}
 for p in sorted((ROOT/'creation/stone_modules_output/source_meshes').glob('*.json')):
  inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();src=json.loads(p.read_text());keep=reduce(src);quantized=copy.deepcopy(src);quantized['vertices']=np.asarray(src['vertices'],dtype=np.float32).astype(float).tolist();assert np.array_equal(keep,reduce(quantized))
  for theme in ['MOSS_01','DRY_01','DUSK_01']:
   original=ROOT/f'standalone_assets/{theme}/models/{p.stem}_LOD0.glb';inputs[str(original.relative_to(ROOT))]=hashlib.sha256(original.read_bytes()).hexdigest();base=load_glb(original);f=base['indices'].reshape(-1,3);v=base['positions'][:,[0,2,1]]*[1,-1,1]
   assert np.array_equal(v[f],np.asarray(src['vertices'],dtype=np.float32)[np.asarray(src['triangles'])])
   uv=base['uv'][f[:,0]];slots=(np.floor(uv[:,1]*4)*8+np.floor(uv[:,0]*8)).astype(int);n=base['normals'][f[:,0]][:,[0,2,1]]*[1,-1,1]
   raw=write_glb(dict(asset_id=p.stem,lod=1,seed=0,generator_version='RECOVERY_CONTACT_20261106'),v,f[keep],n[keep],slots[keep],base['png']);size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[20+size:]
   for key in ['nodes','scenes','materials']:doc[key]=copy.deepcopy(base['doc'][key])
   doc['nodes'][0]['name']=p.stem+'_CONTACT_CANDIDATE';doc['extras']['art_approval']='PENDING';j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);raw=struct.pack('<4sII',b'glTF',2,20+len(j)+len(binary))+struct.pack('<I4s',len(j),b'JSON')+j+binary
   dest=OUT/f'models/{theme}/{p.stem}_CONTACT.glb';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);m=load_glb(dest);mf=m['indices'].reshape(-1,3)
   for key in ['positions','normals','uv']:assert np.array_equal(m[key][mf],base[key][f[keep]])
   assert m['png']==base['png'] and m['doc']['nodes'][1:]==base['doc']['nodes'][1:]
   assert np.array_equal(m['positions'].min(0),base['positions'].min(0)) and np.array_equal(m['positions'].max(0),base['positions'].max(0))
   ev=m['positions'][:,[0,2,1]]*[1,-1,1];scores={}
   for name,view in VIEWS.items():
    center,scale=frame(v,ev,view);scores[name]=iou(mask(v,f,view,center,scale),mask(ev,mf,view,center,scale))
   assert min(scores.values())==1.0
   rows.append(dict(asset=p.stem,theme=theme,original_triangles=len(f),candidate_triangles=len(mf),views=scores,sha256=hashlib.sha256(raw).hexdigest(),file=str(dest.relative_to(OUT)),removed_face_ids=sorted(set(range(len(f)))-set(keep.tolist())),art_approved=False))
 assert len(rows)==48 and all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==h for k,h in inputs.items())
 report=dict(baseline_commit='7784d4a2cd279866ebb43ef252803cb9c3f67478',candidates=rows,input_sha256=inputs,source_unchanged=True,engine_tested=False,recovered_v68=False)
 (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 with zipfile.ZipFile(OUT/'stone_rebuilt_review.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and p.suffix in ['.glb','.py','.json','.md']:z.write(p,p.relative_to(OUT))
 print('48 GLBs rebuilt; all four-view IoUs 1.0; source unchanged')
if __name__=='__main__':main()
