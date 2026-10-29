"""Explicit canonical allowlists for full/trial INTERNAL REVIEW customer-layout ZIPs.

Sales mode intentionally fails while this build's release gates remain unresolved.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,csv,io,shutil,stat,zipfile,re
R=Path(__file__).resolve().parent
THEMES={'MOSS_01':'moss','DRY_01':'dry','DUSK_01':'dusk'}
TRIAL=['TW_TREE_ROUND_SMALL_A','TW_TREE_TIERED_SLIM_A','TW_ROCK_LOW_WEDGE_A','TW_ROCK_UPRIGHT_A','TW_VEG_GRASS_LOW_A','TW_WOOD_RAIL_2M_A','TW_WOOD_POST_A','TW_STONE_WALL_1M_A']
BLOCKERS=['Human art decisions missing','77 LOD omission decisions pending','Reduced models currently reviewed in Moss only','Final sales/trial license terms not signed off','GPU screenshots and device benchmark not run','Source/provenance signoff missing','Collider fidelity against original design requires review']
def sha(data):return hashlib.sha256(data).hexdigest()
def safe(name):
    p=PurePosixPath(name)
    return bool(name) and not p.is_absolute() and p.as_posix()==name and '..' not in p.parts and '\\' not in name and ':' not in name

def plan(root,subset):
    creation=root/'creation';records=json.loads((creation/'asset_records_output/asset_records.json').read_text())['records'];ids=sorted(TRIAL if subset=='trial' else [r['asset_id'] for r in records]);assert len(ids)==(8 if subset=='trial' else 84)
    section=(root/'original_asset_pack_design_v1.md').read_text().split('## 18. 42개 원형 카탈로그',1)[1].split('## 19.',1)[0]
    families=[]
    for line in section.splitlines():
        if line.startswith('|'):families.extend(re.findall(r'`([A-Z][A-Z0-9_]+)`',line))
    canonical={f'TW_{family}_{variant}' for family in families for variant in 'AB'}
    assert len(set(families))==42 and len(canonical)==84
    assert len(records)==84 and {r['asset_id'] for r in records}==canonical
    assert all(r['asset_id']==f"TW_{r['family']}_{r['variant']}" and r['variant'] in 'AB' for r in records)
    files={};exports=[];models=[]
    def add(name,data):
        assert safe(name) and name.casefold() not in {n.casefold() for n in files}
        files[name]=data
    def source(name,path,expected=None):
        assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
        data=path.read_bytes()
        if expected:assert sha(data)==expected
        add(name,data)
    media=creation/'review_media_output';tm=json.loads((media/'thumbnail_manifest.json').read_text());thumbs={t['asset_id']:t for t in tm['thumbnails']}
    fullcat={a['asset_id']:a for a in json.loads((root/'trailwood_godot/data/full_catalog.json').read_text())['assets']}
    for record in records:
        aid=record['asset_id']
        if aid not in ids:continue
        for e in record['exports']:
            if e['lod']!=0 or e['theme'] not in THEMES or subset=='trial' and e['theme']!='MOSS_01':continue
            dest=f"models/glb/lod0/{THEMES[e['theme']]}/{aid}_LOD0.glb";source(dest,creation/e['path'],e['sha256']);exports.append(dict(asset_id=aid,theme=THEMES[e['theme']],lod=0,file=dest,triangles=e['triangles'],sha256=e['sha256']))
        t=thumbs[aid];source(f'previews/thumbnails/{aid}.png',media/t['file'],t['sha256']);models.append(dict(asset_id=aid,family=record['family'],variant=record['variant'],collider=fullcat[aid].get('collider'),lod_status='LOD0_ONLY_IN_THIS_LAYOUT_PREVIEW',art_approval='PENDING'))
    assert len(exports)==len(ids)*(1 if subset=='trial' else 3)
    if subset=='full':
        audit=json.loads((R/'reports/blend_audit.json').read_text());assert audit['passed']
        source('source/Trailwood.blend',R/'sanitized/Trailwood.blend',audit['sha256'])
        for sheet in tm['contact_sheets']:source('previews/contact_sheets/'+Path(sheet['file']).name,media/sheet['file'],sheet['sha256'])
        example_root=creation/'boundary_examples_output';examples=json.loads((example_root/'catalog.json').read_text())['examples'];assert len(examples)==6
        for e in examples:
            # Scenes are static assembly descriptions, not a generator or an executable editor.
            doc=json.loads((example_root/e['scene']).read_text())
            for instance in doc['instances']:
                assert instance['asset_id'] in ids
                instance['file']=f"models/glb/lod0/moss/{instance['asset_id']}_LOD0.glb"
                assert instance['file'] in files
            add('examples/'+e['scene'],json.dumps(doc,indent=2).encode());source('examples/'+e['preview'],example_root/e['preview'])
    # External palettes are extracted from the same embedded data used by the verified exports.
    import sys
    sys.path.insert(0,str(creation));from verify_glb import load_glb
    for theme in (['MOSS_01'] if subset=='trial' else THEMES):
        mesh=load_glb(creation/'theme_output'/theme/'models'/f'{ids[0]}_LOD0.glb');add(f'textures/{THEMES[theme]}.png',mesh['png'])
    payload=dict(schema_version='1.0',channel='INTERNAL_REVIEW',subset=subset,unique_model_count=len(ids),asset_ids=ids,themes=['moss'] if subset=='trial' else list(THEMES.values()),models=models,exports=exports,sales_approved=False,blockers=BLOCKERS)
    add('asset_manifest.json',json.dumps(payload,indent=2).encode())
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=['asset_id','theme','lod','file','triangles','sha256']);w.writeheader();w.writerows(exports);add('manifest.csv',stream.getvalue().encode('utf-8-sig'))
    add('README.md',f'''# Trailwood {subset} - INTERNAL REVIEW

{len(ids)} unique LOD0 models; {len(payload['themes'])} palette theme(s); {len(exports)} GLB files.
This is a customer-layout preview, not a sales release or public free trial.
All models and thumbnails have pending art approval.

Start with docs/import-guide.md. See asset_manifest.json for exact IDs and contents.
This layout deliberately contains LOD0 only; the91 reduced Moss candidates and77 omission reviews remain separate engineering work. It does not claim the complete planned LOD deliverable.

Full layout includes84 thumbnails,6 contact sheets,6 static assembly descriptions/previews and an editable Blender source. Trial contains exactly8 Moss models and8 thumbnails, without the full Blender source or full examples.

LICENSE.txt is a pending-terms notice, not a grant of customer distribution rights.
'''.encode())
    add('LICENSE.txt',b'''PENDING TERMS - INTERNAL REVIEW ONLY
This archive is not an approved commercial product or public free trial.
Final customer license terms have not been approved. No CC0 or exclusive-rights claim is made.
The intended business terms are recorded in docs/terms-proposal.md for review.
Do not treat this notice as the final customer license.
''')
    add('docs/terms-proposal.md',b'''# Business terms proposal - not final contract language

Proposed use: commercial and noncommercial games, videos and images; modification inside the buyer's project.
Proposed restriction: resale or redistribution of original or modified models as downloadable asset packs or libraries.
Proposed team access: one purchasing organization and its project contributors; contractor access ends with the work.
Ownership is not exclusive. Trial terms must be separately stated; free pricing does not imply CC0.
Initial support scope: missing download files and import problems in the stated tested engine version. No response time, lifetime support or unlimited updates are promised.
Final platform terms, customer license, pricing and support commitments require signoff before release.
''')
    add('docs/import-guide.md',b'''# Import guide

1. Unzip to a new directory. Check the file hashes in release_manifest.json before use.
2. Import models/glb/lod0/moss/<asset_id>_LOD0.glb into the engine at scale1.0. Coordinates are Y-up; units are metres. Each file embeds its palette.
3. The full layout also has dry and dusk folders. They recolor the same geometry, not additional model designs.
4. Godot4.7.2 Linux headless import is engineering evidence. Native Unity/URP support, GPU appearance and Android/iOS performance are not established.
5. In Godot's Advanced Import Settings disable Generate LODs before reimporting manually authored LODs. Automatic import collision must remain off if descriptors are used to construct collision.
6. Collision descriptors in asset_manifest.json are source Z-up: map(x,y,z) to(x,z,-y) exactly once. Grass/bush entries with null descriptors are nonblocking. Descriptors are separate data, not portable glTF physics.
7. The full Blender source is an editable imported mesh/UV/material/socket document, not a parametric generator. Its Moss image is packed; image paths are relative.
8. Static example JSONs describe assembly and are not ready-to-play scenes. No dynamic gate controller is included.

For material sharing, first confirm embedded materials render correctly, then replace matching materials with one shared palette material in your engine. Nearest sampling and disabled repeat avoid palette-slot bleed. A material per model does not imply one draw call for the scene.
''')
    add('docs/specifications.md',f'''# Specifications and measured limits

- Unique models: {len(ids)}; GLB exports: {len(exports)}; thumbnails: {len(ids)}.
- Metre units, Y-up GLB geometry, source Z-up collider descriptors.
- A/B variants have separate geometry. Palette themes do not increase the unique model count.
- This layout contains LOD0 only. No unsupported LOD-completeness or mobile-performance claim is made.
- Tested engineering environment: Godot4.7.2 Linux headless. GPU screenshots, physical Android/iOS, art approval and final terms are pending.
- Orthographic top-down examples should keep LOD0. Perspective initial distances: natural12/28m, boundary18/40m; grass cull25m. These are design starting values, not device recommendations.
- Gates in examples are static positions. Damaged fence collision can use a simplified intact proxy and needs review.
- Customer layout excludes generators, recipes, third-party research, credentials, caches and absolute machine paths.
'''.encode())
    add('CHANGELOG.md',b'# Internal layout preview 2026-10-29\n\nFirst explicit full/trial allowlists; JSON-derived CSV; verified editable-source paths; no sales approval.\n')
    return payload,files

def expected_manifest(files):
    payload=json.loads(files['asset_manifest.json'])
    return dict(channel='INTERNAL_REVIEW',subset=payload['subset'],asset_ids=payload['asset_ids'],unique_model_count=len(payload['asset_ids']),sales_approved=False,files={n:dict(bytes=len(d),sha256=sha(d)) for n,d in files.items()})

def staging_errors(stage,files):
    errors=[]
    if stage.is_symlink():return ['K001']
    actual={p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file() or p.is_symlink()}
    if actual!=set(files)|{'release_manifest.json'}:errors.append('K001')
    for name,data in files.items():
        if not safe(name):errors.append('K001');continue
        p=stage/name
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents if parent!=stage.parent):errors.append('K001');continue
        if not p.is_file() or p.read_bytes()!=data:errors.append('K002')
    manifest_path=stage/'release_manifest.json'
    if not manifest_path.is_file() or manifest_path.is_symlink():errors.append('K002')
    else:
        try:
            m=json.loads(manifest_path.read_text())
            if m!=expected_manifest(files):errors.append('K002')
        except (ValueError,UnicodeError):errors.append('K002')
    return sorted(set(errors))

def archive_errors(path,files):
    errors=[]
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(files)|{'release_manifest.json'}:errors.append('K001')
        for info in z.infolist():
            if not safe(info.filename) or stat.S_ISLNK(info.external_attr>>16):errors.append('K001');continue
            if info.filename in files and z.read(info)!=files[info.filename]:errors.append('K002')
        if 'release_manifest.json' in names:
            try:
                m=json.loads(z.read('release_manifest.json'))
                if m!=expected_manifest(files):errors.append('K002')
            except (ValueError,UnicodeError):errors.append('K002')
        else:errors.append('K002')
    return sorted(set(errors))

def build(root,out,subset):
    payload,files=plan(root,subset)
    if out.exists():raise ValueError('Output must be new, refusing to merge contaminated staging')
    out.mkdir(parents=True)
    for name,data in files.items():p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    manifest=expected_manifest(files)
    (out/'release_manifest.json').write_text(json.dumps(manifest,indent=2));assert not staging_errors(out,files)
    archive=out.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name in sorted(set(files)|{'release_manifest.json'}):
            info=zipfile.ZipInfo(name,date_time=(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,(out/name).read_bytes())
    assert not archive_errors(archive,files)
    return payload,files,archive

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--subset',choices=['full','trial'],default='full');p.add_argument('--channel',choices=['internal-review','sales'],default='internal-review');a=p.parse_args()
    if a.channel=='sales':
        print(json.dumps(dict(sales_approved=False,blockers=BLOCKERS),indent=2));raise SystemExit(2)
    payload,files,archive=build(a.root.resolve(),a.out,a.subset)
    print(json.dumps(dict(subset=a.subset,unique_models=len(payload['asset_ids']),files=len(files)+1,archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),sales_approved=False)))
if __name__=='__main__':main()
