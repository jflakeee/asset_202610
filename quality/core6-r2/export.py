"""glTF 2 exporter: vertex colors, shared material profiles and optional chest hinge."""
import json,struct,math
import numpy as np
PROFILES={'matte':(0,.9),'painted':(0,.6),'iron':(.65,.55),'gold':(.8,.38)}

def profile(asset,part):
    aid=asset['asset_id'];color=part['color'].upper()
    if 'coin' in aid:return 'gold'
    if 'chest' in aid:
        if color=='#D6AF4C':return 'gold'
        if color=='#42484D':return 'iron'
    if 'ore' in aid and color=='#B8B5AA':return 'iron'
    if 'potion' in aid and color in ('#A73C46','#E2D4AE'):return 'painted'
    return 'matte'

def export_glb(asset,animated=False):
    data=bytearray();views=[];accessors=[];materials=[];indices={};meshes=[]
    def accessor(values,kind,target=None):
        a=np.asarray(values,dtype='<f4');offset=len(data);data.extend(a.tobytes())
        view=dict(buffer=0,byteOffset=offset,byteLength=a.nbytes)
        if target:view['target']=target
        views.append(view);acc=dict(bufferView=len(views)-1,componentType=5126,count=len(a),type=kind)
        if kind=='SCALAR':acc.update(min=[float(a.min())],max=[float(a.max())])
        else:acc.update(min=a.min(0).tolist(),max=a.max(0).tolist())
        accessors.append(acc);return len(accessors)-1
    parts=asset['components'];pivot=np.array(asset.get('hinge_pivot',[0,0,0]))
    split=asset.get('lid_component_start',len(parts))
    groups=[(parts[:split],np.zeros(3)),(parts[split:],pivot)] if animated else [(parts,np.zeros(3))]
    for group,origin in groups:
        batches={}
        for p in group:batches.setdefault(profile(asset,p),[]).append(p)
        primitives=[]
        for key,batch in batches.items():
            triangles=[];colors=[]
            for p in batch:
                t=np.array(p['vertices'])[np.array(p['faces'])]-origin;triangles.append(t)
                rgb=np.array([int(p['color'][i:i+2],16)/255 for i in (1,3,5)])
                rgb=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
                colors.extend([rgb]*len(t)*3)
            t=np.concatenate(triangles);normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normals,axis=1)
            assert np.isfinite(t).all() and (length>1e-10).all()
            normals/=length[:,None]
            if key not in indices:
                indices[key]=len(materials);metal,rough=PROFILES[key]
                materials.append(dict(name='Trailwood_'+key,pbrMetallicRoughness=dict(baseColorFactor=[1,1,1,1],metallicFactor=metal,roughnessFactor=rough)))
            primitives.append(dict(attributes=dict(POSITION=accessor(t.reshape(-1,3),'VEC3',34962),NORMAL=accessor(np.repeat(normals,3,axis=0),'VEC3',34962),COLOR_0=accessor(colors,'VEC3',34962)),material=indices[key],mode=4))
        meshes.append(dict(primitives=primitives))
    nodes=[dict(name=asset['asset_id'],mesh=0)]
    doc=dict(asset=dict(version='2.0',generator='Trailwood art pass 2'),scene=0,scenes=[dict(nodes=[0])],nodes=nodes,meshes=meshes,materials=materials,accessors=accessors,bufferViews=views,extras=dict(status='ART_PASS_2_REVIEW_PENDING',coordinate_frame='Y-up meters',external_geometry_inputs=[]))
    if animated:
        nodes[:]=[dict(name='ChestRoot',children=[1,2]),dict(name='ChestBody',mesh=0),dict(name='LidHinge',mesh=1,translation=pivot.tolist())]
        angle=math.radians(105)/2
        times=accessor([[0],[.6]],'SCALAR');rotations=accessor([[0,0,0,1],[math.sin(angle),0,0,math.cos(angle)]],'VEC4')
        doc['animations']=[dict(name='Chest_Open',samplers=[dict(input=times,output=rotations,interpolation='LINEAR')],channels=[dict(sampler=0,target=dict(node=2,path='rotation'))])]
    doc['buffers']=[dict(byteLength=len(data))]
    raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);data+=b'\0'*((-len(data))%4)
    result=struct.pack('<4sII',b'glTF',2,28+len(raw)+len(data))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(data),b'BIN\0')+data
    return result,dict(materials=len(materials),primitives=sum(len(m['primitives']) for m in meshes),bytes=len(result),animated=animated)
