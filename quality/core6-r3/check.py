"""Compare expanded triangles against art pass 2; allow only 8-bit color rounding."""
from pathlib import Path
import argparse,json,struct
import numpy as np
R=Path(__file__).resolve().parent

def load(path):
    raw=path.read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw))
    n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);binary=raw[28+n:]
    def array(i):
        a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];dtype={5126:'<f4',5123:'<u2',5121:'u1'}[a['componentType']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0)
        assert v['byteOffset']%4==0 and start+a['count']*width*np.dtype(dtype).itemsize<=len(binary)
        x=np.frombuffer(binary,dtype=dtype,count=a['count']*width,offset=start).reshape(-1,width)
        if a.get('normalized'):x=x.astype(float)/{5121:255,5123:65535}[a['componentType']]
        assert np.isfinite(x).all();return x
    return raw,d,array

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R.parent/'core6-r2');args=p.parse_args();rows=[]
    for r in json.loads((R/'manifest.json').read_text()):
        name=r['id'];old,od,oa=load(args.source/'models'/f'{name}.glb');new,nd,na=load(R/'models'/f'{name}.glb');max_error=0;vertices_before=0;vertices_after=0
        assert od['materials']==nd['materials'];assert od['nodes']==nd['nodes'];assert len(od['meshes'])==len(nd['meshes'])
        for om,nm in zip(od['meshes'],nd['meshes']):
            assert len(om['primitives'])==len(nm['primitives'])
            for op,np_ in zip(om['primitives'],nm['primitives']):
                idx=na(np_['indices']).ravel();assert idx.max()<nd['accessors'][np_['attributes']['POSITION']]['count'];assert len(idx)%3==0
                vertices_before+=len(oa(op['attributes']['POSITION']));vertices_after+=len(na(np_['attributes']['POSITION']))
                for semantic in ('POSITION','NORMAL'):
                    assert np.array_equal(oa(op['attributes'][semantic]),na(np_['attributes'][semantic])[idx]),semantic
                delta=np.abs(oa(op['attributes']['COLOR_0'])[:,:3]-na(np_['attributes']['COLOR_0'])[idx,:3]);max_error=max(max_error,float(delta.max()))
                assert delta.max()<=.5/255+1e-7
        if r['animated']:
            os=od['animations'][0]['samplers'][0];ns=nd['animations'][0]['samplers'][0]
            assert np.array_equal(oa(os['input']),na(ns['input']));assert np.array_equal(oa(os['output']),na(ns['output']))
        rows.append(dict(id=name,before_bytes=len(old),after_bytes=len(new),before_vertices=vertices_before,after_vertices=vertices_after,max_linear_color_error=max_error))
        print('PASS',name,vertices_before,'->',vertices_after,'vertices; color error',round(max_error,6))
    (R/'comparison.json').write_text(json.dumps(rows,indent=2));print('TOTAL bytes',sum(x['before_bytes'] for x in rows),'->',sum(x['after_bytes'] for x in rows))
