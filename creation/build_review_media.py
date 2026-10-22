"""Create neutral review thumbnails and a machine CSV from exported canonical GLBs.

This is a geometry review rendering, not an engine screenshot or art approval.
The default requires all 84 design IDs. --allow-incomplete is for development only.
"""
from pathlib import Path
import argparse, csv, hashlib, json, math
import numpy as np
from PIL import Image, ImageDraw
from design_traceability import FAMILIES, EXPANSION_IDS, MAPPING_PROPOSALS
from verify_glb import load_glb
from build_rocks import dump

ROOT=Path(__file__).parent
OUT=ROOT/'review_media_output'
CATEGORY_SLUGS=['trees','rocks','vegetation','forest_props','wood_boundaries','stone_boundaries']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def thumbnail(path,dest,label):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    m=load_glb(path);v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3)
    assert np.isfinite(v).all() and len(f)>0
    uv=m['uv'][f[:,0]];im=np.array(m['image'].convert('RGB'));h,w=im.shape[:2]
    colors=im[np.clip((uv[:,1]*h).astype(int),0,h-1),np.clip((uv[:,0]*w).astype(int),0,w-1)]/255
    fig=plt.figure(figsize=(4,4),dpi=128,facecolor='#eceeea')
    ax=fig.add_axes([0,.10,1,.90],projection='3d',facecolor='#eceeea')
    ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='#4c5149',linewidths=.12))
    mid=(v.min(0)+v.max(0))/2;half=max(np.ptp(v,axis=0).max()*.58,.05)
    ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half))
    ax.set_box_aspect((1,1,1));ax.set_proj_type('ortho');ax.view_init(23,-65);ax.set_axis_off()
    fig.text(.5,.055,label,ha='center',va='center',fontsize=7.3,color='#30362e')
    fig.text(.5,.022,f'{len(f)} triangles | geometry preview',ha='center',va='center',fontsize=6.5,color='#5a6058')
    dest.parent.mkdir(parents=True,exist_ok=True);fig.savefig(dest,dpi=128,facecolor=fig.get_facecolor());plt.close(fig)
    assert Image.open(dest).size==(512,512)
    return m

def contact(paths,title,dest):
    cols=4;cell=256;rows=math.ceil(len(paths)/cols);canvas=Image.new('RGB',(cols*cell,rows*cell+48),'#eceeea')
    draw=ImageDraw.Draw(canvas);draw.text((15,15),title,fill='#30362e')
    for i,p in enumerate(paths):
        with Image.open(p) as im:canvas.paste(im.convert('RGB').resize((cell,cell),Image.Resampling.LANCZOS),((i%cols)*cell,48+(i//cols)*cell))
    dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--allow-incomplete',action='store_true');args=parser.parse_args()
    manifest_path=ROOT/'theme_output/manifest.json';manifest=json.loads(manifest_path.read_text())
    canonical={f'TW_{family}_{v}':(category,family,v) for category,families in FAMILIES.items() for family in families for v in 'AB'}
    assert len(canonical)==84
    entries={e['model'][:-5]:e for e in manifest['entries'] if e['theme']=='MOSS_01' and e['model'].endswith('_LOD0')}
    missing=sorted(canonical.keys()-entries.keys())
    if missing and not args.allow_incomplete:raise SystemExit('Missing canonical models: '+', '.join(missing))
    collider_catalog={}
    base_descriptors=ROOT/'demo_output/colliders.json'
    if base_descriptors.exists():
        for asset,parts in json.loads(base_descriptors.read_text())['assets'].items():
            collider_catalog[asset]=dict(asset_id=asset,collider=dict(type='compound',parts=parts))
    for p in sorted(ROOT.glob('*_output/catalog.json')):
        data=json.loads(p.read_text())
        for item in data.get('assets',[]):
            if 'asset_id' in item:collider_catalog[item['asset_id']]=item
    rows=[];thumbs=[]
    for asset,(category,family,variant) in canonical.items():
        if asset not in entries:continue
        e=entries[asset];src=ROOT/'theme_output'/e['file'];assert sha(src)==e['sha256']
        dest=OUT/'thumbnails'/f'{asset}.png';m=thumbnail(src,dest,asset)
        sockets=[node for node in m['doc']['nodes'] if node.get('name','').startswith('SOCKET_')]
        info=collider_catalog.get(asset);collider=info.get('collider') if info else None
        part_count=len(collider.get('parts',[collider])) if collider else 0
        bounds=np.ptp(m['positions'],axis=0)
        row=dict(asset_id=asset,category=category,family=family,variant=variant,theme='MOSS_01',triangles=len(m['indices'])//3,
                 width_x_m=float(bounds[0]),height_y_m=float(bounds[1]),depth_z_m=float(bounds[2]),
                 socket_count=len(sockets),socket_names=';'.join(s['name'] for s in sockets),
                 collider_status='DESCRIPTOR_PRESENT' if collider else 'NO_COLLISION' if info and 'collider' in info else 'NOT_FOUND_IN_CATALOG',
                 collider_parts=part_count,glb_file=e['file'],glb_sha256=e['sha256'],thumbnail_file=str(dest.relative_to(OUT)),thumbnail_sha256=sha(dest),art_approval='PENDING')
        rows.append(row);thumbs.append(dict(asset_id=asset,file=row['thumbnail_file'],sha256=row['thumbnail_sha256'],source_glb=e['file'],source_glb_sha256=e['sha256']))
    OUT.mkdir(exist_ok=True)
    with (OUT/'canonical_catalog.csv').open('w',newline='',encoding='utf-8-sig') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]) if rows else ['asset_id']);writer.writeheader();writer.writerows(rows)
    sheets=[]
    for (category,families),slug in zip(FAMILIES.items(),CATEGORY_SLUGS):
        paths=[OUT/r['thumbnail_file'] for r in rows if r['category']==category]
        if paths:
            dest=OUT/'contact_sheets'/f'{slug}.png';contact(paths,f'TRAILWOOD / {slug} / {len(paths)} canonical models / ART PENDING',dest)
            sheets.append(dict(file=str(dest.relative_to(OUT)),sha256=sha(dest),model_count=len(paths)))
    legacy_ids={p[0] for p in MAPPING_PROPOSALS};extras=[]
    for asset in sorted(entries.keys()-canonical.keys()):
        extras.append(dict(asset_id=asset,classification='LEGACY_REVIEW_CANDIDATE' if asset in legacy_ids else 'EXPANSION' if asset in EXPANSION_IDS else 'OTHER',file=entries[asset]['file'],included_in_84=False))
    dump(OUT/'separate_inventory.json',dict(assets=extras,note='Legacy and expansion assets are not included in the 84 canonical thumbnail count.'))
    dump(OUT/'thumbnail_manifest.json',dict(status='PASS' if len(rows)==84 else 'INCOMPLETE',expected_canonical_models=84,thumbnail_count=len(rows),missing_ids=missing,
        theme_manifest_sha256=sha(manifest_path),thumbnails=thumbs,contact_sheets=sheets,catalog_file='canonical_catalog.csv',catalog_sha256=sha(OUT/'canonical_catalog.csv'),
        renderer='matplotlib Poly3DCollection, orthographic 23deg/-65deg, 512x512, bounds fit, shared neutral background',
        scope='Actual exported GLB geometry and embedded palette; no GPU engine lighting, wind, import, performance or art approval',art_approval='PENDING'))
    print(json.dumps(dict(status='PASS' if len(rows)==84 else 'INCOMPLETE',canonical_thumbnails=len(rows),contact_sheets=len(sheets),separate_assets=len(extras))))

if __name__=='__main__':main()
