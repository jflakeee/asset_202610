"""Fail-closed content/approval checks and an INTERNAL REVIEW trial subset.

Local reviewer records bind content; they do not authenticate a human identity.
This module never publishes or turns a pending record into an approval.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime
import argparse,hashlib,json,shutil,tempfile
import numpy as np
from verify_glb import load_glb
from build_rocks import dump

ROOT=Path(__file__).parent
OUT=ROOT/'release_controls_output'
TRIAL_IDS=['TW_TREE_ROUND_SMALL_A','TW_TREE_TIERED_SLIM_A','TW_ROCK_LOW_WEDGE_A','TW_ROCK_UPRIGHT_A','TW_VEG_GRASS_LOW_A','TW_WOOD_RAIL_2M_A','TW_WOOD_POST_A','TW_STONE_WALL_1M_A']

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':')).encode()

def geometry_hash(mesh):
    positions=np.rint(mesh['positions']*1_000_000).astype(np.int64)
    uv=mesh['uv'];slots=np.floor(uv[:,1]*4).astype(int)*8+np.floor(uv[:,0]*8).astype(int)
    triangles=[]
    for face in mesh['indices'].reshape(-1,3):
        values=[tuple(int(x) for x in positions[i])+(int(slots[i]),) for i in face]
        # Rotate, never reflect winding. Sort faces without depending on export vertex order.
        triangles.append(min(tuple(values[k:]+values[:k]) for k in range(3)))
    return sha(canonical(sorted(triangles)))

def snapshot(asset):
    path=ROOT/'theme_output/MOSS_01/models'/f'{asset}_LOD0.glb';m=load_glb(path)
    # Conservatively bind every shipped generator plus available recipe inputs.
    recipes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(ROOT.glob(f'*/recipes/{asset}.json'))}
    sources=json.loads((ROOT/'source_manifest.json').read_text())['source_sha256']
    return dict(geometry_sha256=geometry_hash(m),palette_sha256=sha(m['png']),
        recipe_sha256=sha(canonical(dict(recipes=recipes,generator_sources=sources))),
        export_sha256=sha(path.read_bytes()))

def approval_errors(asset,current,record):
    if not isinstance(record,dict) or record.get('asset_id')!=asset or record.get('decision')!='APPROVED':return ['P001']
    if not record.get('reviewer') or not record.get('preview_profile'):return ['P001']
    try:
        date=datetime.fromisoformat(record['reviewed_at'])
        if date.tzinfo is None:return ['P001']
    except (KeyError,ValueError,TypeError):return ['P001']
    if record.get('hashes')!=current:return ['P002']
    return []

def staging_errors(stage,manifest):
    errors=[];files=manifest.get('files',{})
    expected={f'models/{asset}_LOD0.glb' for asset in TRIAL_IDS}|{'README.md'}
    if set(files)!=expected or manifest.get('asset_ids')!=TRIAL_IDS or manifest.get('theme')!='MOSS_01' or manifest.get('channel')!='INTERNAL_REVIEW' or manifest.get('public_distribution_permitted') is not False:errors.append('K002')
    for name,record in files.items():
        rel=PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name:errors.append('K001');continue
        path=stage/name
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent!=stage.parent):errors.append('K001');continue
        if not path.is_file() or path.stat().st_size!=record.get('bytes') or sha(path.read_bytes())!=record.get('sha256'):errors.append('K002')
    actual={str(p.relative_to(stage)) for p in stage.rglob('*') if p.is_file() or p.is_symlink()}
    if actual!=set(files)|{'review_trial_manifest.json'}:errors.append('K001')
    return sorted(set(errors))

def make_trial():
    stage=OUT/'trial_review'
    # Refuse contaminated existing staging rather than silently absorbing or deleting it.
    if stage.exists():
        old=stage/'review_trial_manifest.json'
        if not old.is_file() or staging_errors(stage,json.loads(old.read_text())):raise ValueError('K001/K002: existing trial staging is dirty')
    (stage/'models').mkdir(parents=True,exist_ok=True)
    for asset in TRIAL_IDS:shutil.copyfile(ROOT/'theme_output/MOSS_01/models'/f'{asset}_LOD0.glb',stage/'models'/f'{asset}_LOD0.glb')
    (stage/'README.md').write_text('# Trailwood trial subset — INTERNAL REVIEW ONLY\n\nExact eight design IDs, Moss LOD0 only. Not approved for public distribution.\nFinal license, art decisions and release-wide checks remain pending.\n')
    files={str(p.relative_to(stage)):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='review_trial_manifest.json'}
    manifest=dict(channel='INTERNAL_REVIEW',asset_ids=TRIAL_IDS,theme='MOSS_01',files=files,public_distribution_permitted=False)
    dump(stage/'review_trial_manifest.json',manifest)
    assert not staging_errors(stage,manifest)
    return stage,manifest

def self_test(stage,manifest,current):
    checks=[]
    asset=TRIAL_IDS[0]
    # Synthetic reviewer data is in memory only and never attached to real release records.
    synthetic=dict(asset_id=asset,decision='APPROVED',reviewer='TEST_FIXTURE_ONLY',reviewed_at='2000-01-01T00:00:00+00:00',preview_profile='TEST',hashes=current)
    assert approval_errors(asset,current,synthetic)==[];checks.append('synthetic matching approval accepted')
    assert approval_errors(asset,current,None)==['P001'];checks.append('missing approval blocked P001')
    for field in current:
        changed=dict(current);changed[field]='0'*64
        assert approval_errors(asset,changed,synthetic)==['P002']
    checks.append('geometry/palette/recipe/export mutation blocked P002')
    with tempfile.TemporaryDirectory(prefix='trial-negative-') as tmp:
        target=Path(tmp)/'stage';shutil.copytree(stage,target)
        extra=target/'third_party.bin';extra.write_bytes(b'TEST_ONLY')
        assert 'K001' in staging_errors(target,manifest);extra.unlink();checks.append('unlisted file blocked K001')
        file=target/next(n for n in manifest['files'] if n.endswith('.glb'));original=file.read_bytes();file.write_bytes(original+b'CHANGED')
        assert 'K002' in staging_errors(target,manifest);file.write_bytes(original);checks.append('asset mutation blocked K002')
        file.unlink();assert 'K002' in staging_errors(target,manifest);file.write_bytes(original);checks.append('missing model blocked K002')
        file.unlink();file.symlink_to(stage/next(n for n in manifest['files'] if n.endswith('.glb')))
        assert 'K001' in staging_errors(target,manifest);file.unlink();file.write_bytes(original);checks.append('symlink blocked K001')
        bad=json.loads(json.dumps(manifest));bad['files']['../escape.bin']=dict(bytes=0,sha256=sha(b''));assert 'K001' in staging_errors(target,bad);checks.append('parent path blocked K001')
    mesh=load_glb(stage/'models'/f'{asset}_LOD0.glb');reordered=dict(mesh);reordered['indices']=mesh['indices'].reshape(-1,3)[::-1].reshape(-1)
    assert geometry_hash(mesh)==geometry_hash(reordered);checks.append('normalized geometry independent of triangle order')
    altered=dict(mesh);altered['positions']=mesh['positions'].copy();altered['positions'][0,0]+=.01
    assert geometry_hash(mesh)!=geometry_hash(altered);checks.append('actual geometry mutation changes normalized hash')
    return checks

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-approvals',type=Path,help='Read externally reviewed records; never edits them or publishes')
    args=parser.parse_args()
    if args.check_approvals:
        records=json.loads(args.check_approvals.read_text()).get('records',[])
        ids=[r.get('asset_id') for r in records]
        errors={asset:approval_errors(asset,snapshot(asset),next((r for r in records if r.get('asset_id')==asset),None)) for asset in TRIAL_IDS}
        invalid=len(ids)!=len(set(ids)) or set(ids)!=set(TRIAL_IDS)
        report=dict(status='FAIL' if invalid or any(errors.values()) else 'PASS_CONTENT_BINDING_ONLY',errors=errors,invalid_id_set=invalid,
            public_distribution_permitted=False,reviewer_identity_verified=False)
        dump(OUT/'approval_check.json',report);print(json.dumps(report))
        raise SystemExit(2 if report['status']=='FAIL' else 0)
    stage,manifest=make_trial();targets={asset:snapshot(asset) for asset in TRIAL_IDS}
    pending=[dict(asset_id=asset,decision='PENDING',reviewer=None,reviewed_at=None,preview_profile='MOSS_01_512_NEUTRAL',hashes=hashes,issues=[]) for asset,hashes in targets.items()]
    dump(OUT/'approval_requests.json',dict(status='PENDING_HUMAN_REVIEW',records=pending))
    tests=self_test(stage,manifest,targets[TRIAL_IDS[0]])
    blocked={r['asset_id']:approval_errors(r['asset_id'],targets[r['asset_id']],r) for r in pending}
    assert all(codes==['P001'] for codes in blocked.values())
    dump(OUT/'validation.json',dict(status='PASS',trial_model_count=8,trial_theme='MOSS_01',tests=tests,
        pending_approval_blockers=blocked,public_distribution_permitted=False,
        scope='Local content-binding and allowlist validation; does not authenticate reviewer identity or satisfy all sales gates'))
    print('Exact trial8 review subset; mutation/allowlist controls PASS; real approvals remain pending')

if __name__=='__main__':main()
