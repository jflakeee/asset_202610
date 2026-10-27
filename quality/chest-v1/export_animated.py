import json,struct,copy,math
from pathlib import Path
import numpy as np
from build import build
from core import glb
R=Path(__file__).resolve().parent
def unpack(raw):
 n=struct.unpack_from('<I',raw,12)[0];return json.loads(raw[20:20+n]),bytearray(raw[28+n:])
a=build();pivot=np.array(a['hinge_pivot']);split=a['lid_component_start'];body=copy.deepcopy(a);body['components']=a['components'][:split];lid=copy.deepcopy(a);lid['components']=lid['components'][split:]
for p in lid['components']:p['vertices']=(np.array(p['vertices'])-pivot).tolist()
d,b=unpack(glb(body));l,lb=unpack(glb(lid));vo=len(d['bufferViews']);ao=len(d['accessors']);mo=len(d['materials']);offset=len(b)
for v in l['bufferViews']:v['byteOffset']+=offset
d['bufferViews']+=l['bufferViews']
for acc in l['accessors']:acc['bufferView']+=vo
d['accessors']+=l['accessors'];d['materials']+=l['materials']
for prim in l['meshes'][0]['primitives']:
 prim['attributes']={k:v+ao for k,v in prim['attributes'].items()};prim['material']+=mo
d['meshes']+=l['meshes'];b+=lb
d['nodes']=[{'name':'ChestRoot','children':[1,2]},{'name':'ChestBody','mesh':0},{'name':'LidHinge','mesh':1,'translation':pivot.tolist()}]
def acc(values,kind):
 arr=np.array(values,dtype='<f4');v=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':len(b),'byteLength':arr.nbytes});b.extend(arr.tobytes());i=len(d['accessors']);d['accessors'].append({'bufferView':v,'componentType':5126,'count':len(arr),'type':kind,'min':arr.min(axis=0).tolist(),'max':arr.max(axis=0).tolist()});return i
times=acc([[0],[.6]],'SCALAR');angle=math.radians(105)/2;rots=acc([[0,0,0,1],[math.sin(angle),0,0,math.cos(angle)]],'VEC4')
d['animations']=[{'name':'Chest_Open','samplers':[{'input':times,'output':rots,'interpolation':'LINEAR'}],'channels':[{'sampler':0,'target':{'node':2,'path':'rotation'}}]}]
for m in d['materials']:
 name=m['name'];p=m['pbrMetallicRoughness'];p['metallicFactor']=.8 if name in ['434E55','D5AE57'] else 0;p['roughnessFactor']=.35 if name=='D5AE57' else (.5 if name=='434E55' else .85)
d['buffers']=[{'byteLength':len(b)}];d['extras']['status']='QUALITY_REVISION_1_REVIEW_PENDING'
raw=json.dumps(d,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);b+=b'\0'*((-len(b))%4)
(R/'reward_chest_animated.glb').write_bytes(struct.pack('<4sII',b'glTF',2,28+len(raw)+len(b))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(b),b'BIN\0')+b)
# Structural geometry checks, not a substitute for engine visual review.
for part in a['components']:
 v=np.array(part['vertices']);f=np.array(part['faces']);assert np.isfinite(v).all();assert (np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10).all()
assert d['nodes'][2]['translation']==[0,.4,.28]
print('PASS finite nondegenerate geometry, hinge hierarchy, animation export',sum(len(p['faces']) for p in a['components']),'triangles')
