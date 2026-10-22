"""256px orthographic silhouette IoU for the four shipped LOD0/LOD1 pairs.

Rasterizes actual exported triangles. Shared union bounding frame per pair/view,
8px padding, no independent mesh normalization, no backface culling. This is
silhouette agreement, not a distance metric or GPU shading test. LOD2 is absent.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw
from verify_glb import load_glb
from build_rocks import dump

ROOT=Path(__file__).parent;OUT=ROOT/'lod_iou_output'
IDS=['TW_ROCK_LOW_WEDGE_A','TW_ROCK_UPRIGHT_A','TW_TREE_ROUND_SMALL_A','TW_TREE_TIERED_SLIM_A']
VIEWS={'front':np.array([[1,0,0],[0,0,1.]]),'side':np.array([[0,1,0],[0,0,1.]]),
 'diagonal45':np.array([[1/math.sqrt(2),-1/math.sqrt(2),0],[0,0,1.]]),'top':np.array([[1,0,0],[0,1,0.]])}

def mesh(path):
    m=load_glb(path)
    return m['positions'][:,[0,2,1]]*np.array([1,-1,1]),m['indices'].reshape(-1,3)

def frame(v0,v1,view):
    p=np.concatenate([v0,v1])@view.T;lo=p.min(0);hi=p.max(0)
    return (lo+hi)/2,239/float((hi-lo).max())

def mask(v,f,view,center,scale):
    p=(v@view.T-center)*scale+127.5;p[:,1]=255-p[:,1]
    im=Image.new('1',(256,256),0);draw=ImageDraw.Draw(im)
    for face in f:
        # Degenerate projected triangles (edge on) have zero silhouette area.
        t=p[face];area=abs(float(np.cross(t[1]-t[0],t[2]-t[0])))
        if area>1e-9:draw.polygon([tuple(np.rint(x).astype(int)) for x in t],fill=1)
    return np.asarray(im,dtype=bool)

def iou(a,b):
    union=np.logical_or(a,b).sum()
    if not union:raise ValueError('Empty projected union')
    return float(np.logical_and(a,b).sum()/union)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-pass',action='store_true',help='Exit nonzero if any supplied LOD1 silhouette fails; absent LOD2 remains NOT_RUN')
    args=parser.parse_args()
    rows=[];panels=[]
    for asset in IDS:
        folder='output' if 'ROCK' in asset else 'trees_output_v2'
        p0=ROOT/folder/'models'/f'{asset}_LOD0.glb';p1=ROOT/'lod_output/models'/f'{asset}_LOD1.glb'
        v0,f0=mesh(p0);v1,f1=mesh(p1);views=[]
        for name,view in VIEWS.items():
            center,scale=frame(v0,v1,view);a=mask(v0,f0,view,center,scale);b=mask(v1,f1,view,center,scale);score=iou(a,b)
            assert iou(a,a)==1.0
            views.append(dict(view=name,iou=score,status='PASS' if score>=.95 else 'FAIL',lod0_pixels=int(a.sum()),lod1_pixels=int(b.sum())))
            rgb=np.full((256,256,3),245,dtype=np.uint8);rgb[a&b]=[70,77,69];rgb[a&~b]=[207,81,72];rgb[b&~a]=[70,155,123]
            panel=Image.new('RGB',(256,288),'white');panel.paste(Image.fromarray(rgb),(0,32));draw=ImageDraw.Draw(panel);draw.text((5,3),asset.replace('TW_',''),fill='black');draw.text((5,17),f'{name}: {score:.4f}',fill='black');panels.append(panel)
        view=VIEWS['front'];center,scale=frame(v0,v1,view);reference=mask(v0,f0,view,center,scale)
        shifted=v0+np.array([np.ptp(v0[:,0])*.3,0,0]);mutant=iou(reference,mask(shifted,f0,view,center,scale))
        assert mutant<.95,'Translation regression not detected'
        rows.append(dict(asset_id=asset,lod1_status='PASS' if all(v['status']=='PASS' for v in views) else 'FAIL',lod2_status='NOT_RUN',lod2_reason='LOD2 not supplied',views=views,translation_negative_control_iou=mutant,
            source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [p0,p1]}))
    report=dict(status='PASS' if all(r['lod1_status']=='PASS' for r in rows) else 'FAIL',criterion='Each of four 256px orthographic view IoUs >= 0.95 for LOD1',
        method='Exported GLB triangles; source Z-up; front +X/up +Z, side +Y/up +Z, 45-degree XY diagonal/up +Z, top X/Y; per-pair union bounds shared by both meshes; uniform scale; approximately8px padding; nearest integer triangle rasterization; no antialiasing or culling',
        resolution=256,views=list(VIEWS),lod1_minimum=.95,lod2_minimum=.88,lod2_status='NOT_RUN',identical_mask_control='PASS',translation_negative_controls='PASS',art_approval='PENDING',assets=rows)
    dump(OUT/'report.json',report)
    sheet=Image.new('RGB',(1024,288*len(IDS)),'white')
    for i,panel in enumerate(panels):sheet.paste(panel,((i%4)*256,(i//4)*288))
    sheet.save(OUT/'silhouette_comparison.png')
    (OUT/'README.md').write_text('# LOD silhouette verification\n\n'+report['method']+'\n\nDark gray = shared silhouette; red = LOD0 only; green = LOD1 only.\nThe actual threshold result is in report.json. FAIL is retained and is not converted into an exception automatically. LOD2 has not been supplied. This test does not establish GPU quality, collider invariance, or human art approval.\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],assets=[dict(asset_id=r['asset_id'],status=r['lod1_status'],min_iou=min(v['iou'] for v in r['views'])) for r in rows]),indent=2))
    if args.require_pass and report['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
