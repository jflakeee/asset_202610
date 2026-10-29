"""Verify canonical media against actual exports, then write review-facing inventory."""
from pathlib import Path
import json,csv,hashlib,sys,copy
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'creation'))
from verify_glb import load_glb
media=root/'creation/review_media_output';manifest=json.loads((media/'thumbnail_manifest.json').read_text());records=json.loads((root/'creation/asset_records_output/asset_records.json').read_text())['records'];expected={r['asset_id'] for r in records}
rows=list(csv.DictReader((media/'canonical_catalog.csv').open(encoding='utf-8-sig')));thumbs={t['asset_id']:t for t in manifest['thumbnails']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert len(rows)==len(thumbs)==len(expected)==84
assert {r['asset_id'] for r in rows}==set(thumbs)==expected
assert len({r['asset_id'] for r in rows})==len(rows)
assert manifest['catalog_sha256']==sha(media/manifest['catalog_file'])
assert manifest['theme_manifest_sha256']==sha(root/'creation/theme_output/manifest.json')
checks=[];count_by_category={}
def matches(row,m):
    sockets=[n['name'] for n in m['doc']['nodes'] if n.get('name','').startswith('SOCKET_')]
    dims=np.ptp(m['positions'],axis=0)
    return int(row['triangles'])==len(m['indices'])//3 and int(row['socket_count'])==len(sockets) and row['socket_names']==';'.join(sockets) and np.allclose([float(row[k]) for k in ['width_x_m','height_y_m','depth_z_m']],dims,rtol=0,atol=1e-7)
for row in rows:
    aid=row['asset_id'];t=thumbs[aid];glb=root/'creation/theme_output'/row['glb_file'];image=media/row['thumbnail_file'];m=load_glb(glb)
    assert sha(glb)==row['glb_sha256']==t['source_glb_sha256']
    assert sha(image)==row['thumbnail_sha256']==t['sha256']
    assert row['glb_file']==t['source_glb'] and row['thumbnail_file']==t['file']
    assert matches(row,m) and Image.open(image).size==(512,512) and row['art_approval']=='PENDING'
    bad=copy.deepcopy(row);bad['triangles']=str(int(row['triangles'])+1);assert not matches(bad,m)
    bad=copy.deepcopy(row);bad['width_x_m']=str(float(row['width_x_m'])+.01);assert not matches(bad,m)
    bad=copy.deepcopy(row);bad['socket_names']+='MUTATED';assert not matches(bad,m)
    count_by_category[row['category']]=count_by_category.get(row['category'],0)+1
    checks.append(dict(id=aid,passed=True,glb_sha256=sha(glb),thumbnail_sha256=sha(image),negative_controls=['triangle_count','bounds','sockets']))
for sheet in manifest['contact_sheets']:assert sha(media/sheet['file'])==sheet['sha256']
assert len(manifest['contact_sheets'])==6
report=dict(mechanical_consistency_pass=True,models=84,thumbnails=84,contact_sheets=6,category_counts=count_by_category,checks=checks,art_approved=False,at15_complete=False,remaining='Thumbnail art approval and final sales document/license signoff')
(R/'reports/catalog_consistency.json').write_text(json.dumps(report,indent=2))
lines=['# Trailwood canonical catalog — internal review','', '84 unique LOD0 models / 42 families, A and B geometry variants. Moss, Dry and Dusk are palette themes, not extra models.','', 'Units: metres. Export coordinates: Y-up. Source collider descriptors: Z-up; Godot adapter maps (x,y,z) to (x,z,-y). Vegetation without collider descriptors remains nonblocking.','', 'All thumbnails below are 512px geometry previews from exported Moss GLBs. They are not GPU screenshots or approved sales images. The separate six-item resource pack and 20 legacy/expansion candidates are excluded.','', 'LOD review: 91 reduced candidate files; 77 pending omission decisions retain the nearest higher-detail model. Perspective initial distance thresholds natural12/28m, boundaries18/40m and grass cull25m are review defaults; orthographic uses fixed LOD0. These are, not measured mobile recommendations.','', 'Godot compatibility evidence: 4.7.2 Linux headless. GPU rendering, Android/iOS devices and final art approval remain unverified.','', '|ID|Triangles|Size X/Y/Z (m)|Sockets|Art status|','|---|---:|---|---:|---|']
for row in sorted(rows,key=lambda r:r['asset_id']):
 dims='/'.join(f"{float(row[k]):.3f}" for k in ['width_x_m','height_y_m','depth_z_m']);lines.append(f"|{row['asset_id']}|{row['triangles']}|{dims}|{row['socket_count']}|PENDING|")
lines+=['','For the exact model and image hashes use reports/catalog_consistency.json and creation/review_media_output/canonical_catalog.csv. Redistribution and sales are not approved by this inventory. Final license terms require separate signoff.','']
(R/'CATALOG.md').write_text('\n'.join(lines));print('PASS84 thumbnail/CSV/GLB checks;252 mutation controls')
