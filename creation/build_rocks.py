"""Original procedural rock prototype. No third-party asset inputs.

Run: python build_rocks.py --out output
Dependencies: numpy, scipy, Pillow, matplotlib.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import struct

import numpy as np
import scipy
from scipy.spatial import ConvexHull
from PIL import Image
import PIL

VERSION = "0.1.0"
COLORS = [
    "3B3028", "66503B", "8C7251", "C8A875", "253D31", "456044", "6F8752", "A3AE6D",
    "424A4B", "69716B", "929A87", "8E816C", "394A2D", "657C3C", "90A24F", "A59B6C",
    "493A2D", "796045", "A18762", "C0A17B", "51483A", "292D2C", "565E59", "C4C5AD",
    "8C6A4E", "B7966B", "574539", "8A8D72", "51483A", "292D2C", "565E59", "C4C5AD",
]
RECIPES = [
    dict(asset_id="TW_ROCK_LOW_WEDGE_A", family_id="ROCK_LOW_WEDGE", seed=21001,
         size_m=[1.3, .9, .65], radial_segments=9, height_rings=4,
         radial_jitter_ratio=.12, lean_deg=11, base_inset_ratio=.08),
    dict(asset_id="TW_ROCK_UPRIGHT_A", family_id="ROCK_UPRIGHT", seed=21002,
         size_m=[.8, .65, 1.55], radial_segments=8, height_rings=5,
         radial_jitter_ratio=.10, lean_deg=6, base_inset_ratio=.06),
]


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rand(recipe, channel, index):
    key = f"1.0.0|{recipe['asset_id']}|{recipe['seed']}|{channel}|{index}"
    return (int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") >> 11) / 2**53


def validate_recipe(r):
    if r['family_id'] not in ('ROCK_LOW_WEDGE', 'ROCK_UPRIGHT'):
        raise ValueError('Unsupported rock family')
    if len(r['size_m']) != 3 or not all(math.isfinite(x) and x > 0 for x in r['size_m']):
        raise ValueError('size_m must contain three finite positive dimensions')
    if not (isinstance(r['seed'], int) and 0 <= r['seed'] <= 4294967295):
        raise ValueError('seed out of range')
    if not (6 <= r['radial_segments'] <= 24 and 3 <= r['height_rings'] <= 8):
        raise ValueError('ring parameters out of range')
    if not (0 <= r['radial_jitter_ratio'] <= .2 and 0 <= r['base_inset_ratio'] < .3):
        raise ValueError('jitter/inset out of range')


def generate(r):
    validate_recipe(r)
    n, k = r['radial_segments'], r['height_rings']
    points = []
    for j in range(k):
        t = j / (k - 1)
        # Broad lower body and offset crown; convex hull makes closed original facets.
        profile = np.interp(t, [0, .35, .7, 1], [1-r['base_inset_ratio'], 1, .85, .43])
        for i in range(n):
            idx = j*n+i
            theta = 2*math.pi*(i + .1*(rand(r, 'angle', idx)-.5))/n
            radius = profile * (1+r['radial_jitter_ratio']*(2*rand(r, 'radius', idx)-1))
            x = .5*radius*math.cos(theta) + math.tan(math.radians(r['lean_deg']))*t*.3
            y = .5*radius*math.sin(theta)
            z = t
            if j == k-1:
                z -= .12*(.5+.5*math.cos(theta))
            points.append([x, y, z])
    vertices = np.array(points, dtype=np.float64)
    lo, hi = vertices.min(0), vertices.max(0)
    vertices = (vertices-lo)/(hi-lo)*np.array(r['size_m'])
    vertices[:, :2] -= np.array(r['size_m'][:2])*.5
    hull = ConvexHull(vertices)
    faces = []
    for tri, eq in zip(hull.simplices, hull.equations):
        tri = tri.copy()
        a, b, c = vertices[tri]
        if np.dot(np.cross(b-a, c-a), eq[:3]) < 0:
            tri[[1,2]] = tri[[2,1]]
        faces.append(tri)
    # Compact and deterministically order vertices and triangles.
    used = sorted(set(np.array(faces).ravel().tolist()))
    mapping = {old:new for new,old in enumerate(used)}
    v = vertices[used]
    faces = [[mapping[x] for x in tri] for tri in faces]
    faces = [f[f.index(min(f)):] + f[:f.index(min(f))] for f in faces]
    f = np.array(sorted(faces), dtype=np.uint32)
    p = v[f]
    normals = np.cross(p[:,1]-p[:,0], p[:,2]-p[:,0])
    normals /= np.linalg.norm(normals, axis=1)[:,None]
    # Assign stable broad plane colors, independent of triangle ordering.
    slots = []
    for normal, tri in zip(normals, p):
        if normal[2] > .45: slot = 10
        elif normal[0] > .25: slot = 11
        elif normal[1] < -.35: slot = 8
        else: slot = 9
        slots.append(slot)
    return v, f, normals, np.array(slots)


def palette_bytes():
    im = Image.new('RGB', (256,256))
    for i, color in enumerate(COLORS):
        im.paste(tuple(bytes.fromhex(color)), ((i%8)*32, (i//8)*64, (i%8+1)*32, (i//8+1)*64))
    bio = io.BytesIO()
    im.save(bio, format='PNG')
    return bio.getvalue()


def write_glb(r, v, f, normals, slots, png):
    # Blender-style Z-up -> glTF Y-up, rotation determinant +1.
    rotation = np.array([[1,0,0],[0,0,1],[0,-1,0]])
    positions = (v[f].reshape(-1,3) @ rotation.T).astype('<f4')
    ns = (np.repeat(normals,3,axis=0) @ rotation.T).astype('<f4')
    uv = np.repeat(np.array([[(i%8+.5)/8, (i//8+.5)/4] for i in slots]),3,axis=0).astype('<f4')
    idx = np.arange(len(positions), dtype='<u2')
    blob = bytearray()
    views = []
    def add(data, target=None):
        while len(blob)%4: blob.append(0)
        view = dict(buffer=0, byteOffset=len(blob), byteLength=len(data))
        if target is not None: view['target'] = target
        views.append(view)
        blob.extend(data)
        return len(views)-1
    pview=add(positions.tobytes(),34962)
    nview=add(ns.tobytes(),34962)
    uview=add(uv.tobytes(),34962)
    iview=add(idx.tobytes(),34963)
    imageview=add(png)
    doc = {
        'asset':{'version':'2.0','generator':f'Trailwood original procedural prototype {VERSION}'},
        'scene':0, 'scenes':[{'nodes':[0]}],
        'nodes':[{'name':r['asset_id']+'_LOD0','mesh':0}],
        'meshes':[{'name':r['asset_id']+'_LOD0','primitives':[{
            'attributes':{'POSITION':0,'NORMAL':1,'TEXCOORD_0':2},'indices':3,'material':0,'mode':4}]}],
        'accessors':[
            dict(bufferView=pview,componentType=5126,count=len(positions),type='VEC3',min=positions.min(0).tolist(),max=positions.max(0).tolist()),
            dict(bufferView=nview,componentType=5126,count=len(ns),type='VEC3'),
            dict(bufferView=uview,componentType=5126,count=len(uv),type='VEC2'),
            dict(bufferView=iview,componentType=5123,count=len(idx),type='SCALAR')],
        'bufferViews':views,'buffers':[{'byteLength':len(blob)}],
        'images':[{'bufferView':imageview,'mimeType':'image/png','name':'MOSS_01'}],
        'samplers':[{'magFilter':9728,'minFilter':9728,'wrapS':33071,'wrapT':33071}],
        'textures':[{'sampler':0,'source':0}],
        'materials':[{'name':'TW_PALETTE_BASE_V1','doubleSided':False,
            'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],
                'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.85}}],
        'extras':{'prototype':True,'approval_status':'review_ready','unit':'meter','recipe':r},
    }
    js=json.dumps(doc,separators=(',',':')).encode()
    js+=b' '*((-len(js))%4)
    blob+=b'\0'*((-len(blob))%4)
    return struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(blob))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(blob),b'BIN\0')+blob


def preview(out, recipes):
    # Re-read exported GLB, including its embedded PNG and UVs. No source-mesh proxy.
    from verify_glb import load_glb
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(15,9), facecolor='#eef1ed')
    light=np.array([-.4,-.5,.8]); light/=np.linalg.norm(light)
    for row,r in enumerate(recipes):
        mesh=load_glb(out/'models'/f"{r['asset_id']}_LOD0.glb")
        pos=mesh['positions'][:,[0,2,1]]*np.array([1,-1,1])
        faces=pos[mesh['indices'].reshape(-1,3)]
        normals=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]); normals/=np.linalg.norm(normals,axis=1)[:,None]
        texture=np.array(mesh['image'])/255.
        uv=mesh['uv'][mesh['indices'].reshape(-1,3)[:,0]]
        colors=texture[np.minimum((uv[:,1]*256).astype(int),255),np.minimum((uv[:,0]*256).astype(int),255)]
        colors=np.clip(colors*(.55+.45*np.maximum(normals@light,0))[:,None],0,1)
        for col,(elev,azim,label) in enumerate([(28,-55,'Three-quarter'),(90,-90,'Top'),(15,-75,'Wireframe')]):
            ax=fig.add_subplot(2,3,row*3+col+1,projection='3d',computed_zorder=False)
            ax.set_facecolor('#eef1ed')
            ax.add_collection3d(Poly3DCollection(faces,facecolors=colors,edgecolors='#394640' if col==2 else 'none',linewidths=.5))
            lo=pos.min(0); hi=pos.max(0); center=(lo+hi)/2; half=max(hi-lo)*.6
            ax.set_xlim(center[0]-half,center[0]+half); ax.set_ylim(center[1]-half,center[1]+half)
            ax.set_zlim(center[2]-half,center[2]+half); ax.set_box_aspect([1,1,1]); ax.set_proj_type('ortho')
            ax.view_init(elev=elev,azim=azim); ax.set_axis_off()
            name='LOW WEDGE' if row==0 else 'UPRIGHT'
            ax.set_title(f"{name}  /  {label}\n{len(faces)} triangles | {r['size_m'][0]} x {r['size_m'][1]} x {r['size_m'][2]} m", fontsize=11,color='#263b30')
    fig.suptitle('TRAILWOOD / P0 ROCK PROTOTYPES',fontsize=23,color='#20382c',weight='bold',y=.97)
    fig.text(.5,.025,'Actual exported geometry + embedded palette / technical preview / not an engine render',ha='center',fontsize=11,color='#526454')
    fig.subplots_adjust(top=.85,bottom=.07,hspace=.12,wspace=.02)
    fig.savefig(out/'preview.png',dpi=140,facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=Path('output')); args=ap.parse_args()
    out=args.out
    if out.exists(): raise SystemExit('Output already exists; select a new directory to preserve earlier builds.')
    (out/'models').mkdir(parents=True)
    (out/'textures').mkdir()
    png=palette_bytes(); (out/'textures'/'MOSS_01.png').write_bytes(png)
    manifests=[]
    for r in RECIPES:
        v,f,n,s=generate(r)
        data=write_glb(r,v,f,n,s,png)
        path=out/'models'/f"{r['asset_id']}_LOD0.glb"; path.write_bytes(data)
        dump(out/'recipes'/f"{r['asset_id']}.json",dict(schema_version='1.0.0',generator_version=VERSION,**r))
        dump(out/'source_meshes'/f"{r['asset_id']}.json",dict(coordinate_system='Z_UP',vertices=v.tolist(),triangles=f.tolist(),face_palette_slots=s.tolist()))
        manifests.append(dict(asset_id=r['asset_id'],triangles=len(f),unique_positions=len(v),exported_vertices=3*len(f),dimensions_m=r['size_m'],file=path.relative_to(out).as_posix(),sha256=hashlib.sha256(data).hexdigest(),approval_status='REVIEW_READY',lod_policy='LOD0_ONLY_PENDING_REVIEW'))
        dump(out/'provenance'/f"{r['asset_id']}.json",dict(method='Original hash-seeded ring points and convex hull',third_party_asset_inputs=[],generator_source='build_rocks.py',generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),ai_assistance='Assistant-authored procedural source code; no image/model generation service used',art_approval='PENDING',seed=r['seed']))
    dump(out/'manifest.json',manifests)
    dump(out/'toolchain.lock.json',dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,pillow=PIL.__version__,generator=VERSION,blender='NOT_AVAILABLE',godot='NOT_AVAILABLE'))
    from verify_glb import verify_all
    result=verify_all(out,RECIPES)
    dump(out/'validation.json',result)
    if result['status']!='PASS': raise SystemExit('Validation failed')
    preview(out,RECIPES)
    print(json.dumps(dict(out=str(out.resolve()),assets=manifests,validation=result['status']),indent=2))


if __name__=='__main__': main()
