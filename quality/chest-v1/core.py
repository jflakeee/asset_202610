"""Original Y-up meter geometry and self-contained glTF 2 exporter."""
import json, struct, math
import numpy as np
from scipy.spatial import ConvexHull

def hull(name, points, color, collider=True):
    v=np.asarray(points,dtype=float); h=ConvexHull(v); faces=[]
    for face,eq in zip(h.simplices,h.equations):
        a,b,c=v[face]
        if np.dot(np.cross(b-a,c-a),eq[:3])<0:face=face[[0,2,1]]
        faces.append(face.tolist())
    used=sorted(set(sum(faces,[]))); mapping={old:i for i,old in enumerate(used)}
    return dict(name=name,vertices=v[used].tolist(),faces=[[mapping[x] for x in f] for f in faces],color=color,collider=collider)

def box(name, center, size, color, collider=True):
    c=np.asarray(center);s=np.asarray(size)/2
    return hull(name,[c+s*np.array([x,y,z]) for x in (-1,1) for y in (-1,1) for z in (-1,1)],color,collider)

def beam(name,a,b,radius,color,segments=6,collider=True):
    a=np.array(a,dtype=float);b=np.array(b,dtype=float);axis=b-a;axis/=np.linalg.norm(axis)
    ref=np.array([1.,0,0]) if abs(axis[0])<.8 else np.array([0.,0,1])
    u=np.cross(axis,ref);u/=np.linalg.norm(u);v=np.cross(axis,u)
    points=[p+radius*(math.cos(t)*u+math.sin(t)*v) for p in (a,b) for t in np.arange(segments)*2*math.pi/segments]
    return hull(name,points,color,collider)

def glb(asset):
    data=bytearray();views=[];accessors=[];primitives=[];materials=[];colors={}
    def accessor(values,kind):
        arr=np.asarray(values,dtype='<f4');offset=len(data);raw=arr.tobytes();data.extend(raw)
        views.append(dict(buffer=0,byteOffset=offset,byteLength=len(raw),target=34962))
        accessors.append(dict(bufferView=len(views)-1,componentType=5126,count=len(arr),type=kind,min=arr.min(0).tolist(),max=arr.max(0).tolist()))
        return len(accessors)-1
    batches={}
    for part in asset['components']:
        batches.setdefault(part['color'].lstrip('#').upper(),[]).append(part)
    for color,parts in batches.items():
        triangles=[]
        for part in parts:
            triangles.append(np.array(part['vertices'])[np.array(part['faces'])])
        t=np.concatenate(triangles)
        n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
        if color not in colors:
            colors[color]=len(materials);rgb=[int(color[i:i+2],16)/255 for i in (0,2,4)]
            # sRGB artist swatches converted into glTF linear factors.
            rgb=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb]
            materials.append(dict(name=color,pbrMetallicRoughness=dict(baseColorFactor=rgb+[1],metallicFactor=0,roughnessFactor=1)))
        primitives.append(dict(attributes=dict(POSITION=accessor(t.reshape(-1,3),'VEC3'),NORMAL=accessor(np.repeat(n,3,axis=0),'VEC3')),material=colors[color],mode=4))
    doc=dict(asset=dict(version='2.0',generator='Trailwood quality iteration 2'),scene=0,scenes=[dict(nodes=[0])],nodes=[dict(name=asset['asset_id'],mesh=0)],meshes=[dict(primitives=primitives)],materials=materials,buffers=[dict(byteLength=len(data))],bufferViews=views,accessors=accessors,extras=dict(coordinate_frame='Y-up meters',status='PROTOTYPE_ART_REVIEW_PENDING',external_geometry_inputs=[]))
    raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);data+=b'\0'*((-len(data))%4)
    return struct.pack('<4sII',b'glTF',2,28+len(raw)+len(data))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(data),b'BIN\0')+data
