"""Reproducible evidence inventory, never an authorship or art approval."""
from pathlib import Path
import copy
import hashlib
import json
from design_traceability import FAMILIES
from verify_glb import load_glb

ROOT = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def build(root=ROOT):
    canonical = sorted(f'TW_{f}_{v}' for fs in FAMILIES.values() for f in fs for v in ('A','B'))
    catalog_path = root.parent/'trailwood_godot/data/full_catalog.json'
    catalog = {a['asset_id']: a for a in json.loads(catalog_path.read_text())['assets']}
    manifest = json.loads((root/'theme_output/manifest.json').read_text())
    iou_path = root/'lod_iou_output/report.json'
    iou = {a['asset_id']: a for a in json.loads(iou_path.read_text())['assets']}
    source = json.loads((root/'source_manifest.json').read_text())['source_sha256']
    for name,digest in source.items():
        if sha(root/name) != digest: raise ValueError('Stale source manifest: '+name)
    records=[]
    for asset in canonical:
        exports=[]
        for entry in manifest['entries']:
            if not entry['model'].startswith(asset+'_LOD'): continue
            path=root/'theme_output'/entry['file']
            if sha(path)!=entry['sha256']: raise ValueError('Stale export: '+entry['file'])
            mesh=load_glb(path)
            exports.append(dict(path=str(path.relative_to(root)),sha256=sha(path),theme=entry['theme'],
                lod=int(entry['model'].rsplit('_LOD',1)[1]),triangles=len(mesh['indices'])//3,
                vertices=len(mesh['positions']),bounds_min=mesh['positions'].min(axis=0).tolist(),
                material_count=len(mesh['doc'].get('materials',[])),image_count=len(mesh['doc'].get('images',[])),
                bounds_max=mesh['positions'].max(axis=0).tolist(),coordinate_system='glTF Y-up',
                embedded_palette_sha256=hashlib.sha256(mesh['png']).hexdigest()))
        if {e['theme'] for e in exports if e['lod']==0}!={'MOSS_01','DRY_01','DUSK_01'}:
            raise ValueError('Incomplete theme coverage: '+asset)
        refs=[]
        # Reference only the packaged evidence directories; old scratch outputs are not evidence.
        for folder in ('natural_catalog_output','wood_modules_output','stone_modules_output','initial_evidence_output'):
            for kind in ('recipes','provenance','source_meshes'):
                for p in sorted((root/folder/kind).glob(asset+'.json')):
                    refs.append(dict(path=str(p.relative_to(root)),sha256=sha(p),kind=kind))
        a=catalog[asset]
        for folder in ('wood_modules_output','stone_modules_output'):
            if any(ref['path'].startswith(folder+'/') for ref in refs):
                p=root/folder/'provenance.json'
                if p.is_file(): refs.append(dict(path=str(p.relative_to(root)),sha256=sha(p),kind='shared_provenance'))
        lods=sorted({e['lod'] for e in exports})
        measured=iou.get(asset)
        if measured:
            for name,digest in measured.get('source_sha256',{}).items():
                if sha(root/name)!=digest: raise ValueError('Stale LOD measurement: '+name)
        policy=[]
        for level,threshold in ((1,.95),(2,.88)):
            present=level in lods
            policy.append(dict(lod=level,files_present=present,
                state='MEASURED_PENDING_REVIEW' if present and level==1 and measured else 'IMPLEMENT_OR_REVIEW_EXCEPTION',
                required_iou=threshold,exception_approved=False,
                next_action='Review silhouette and in-engine transition' if present else 'Implement reduction or document and review omission; no automatic triangle-count exemption'))
        records.append(dict(asset_id=asset,family=asset[3:-2],variant=asset[-1],exports=exports,
            collision=dict(coordinate_system='source Z-up',declared=a.get('collider_declared'),descriptor=a.get('collider')),
            sockets=a.get('sockets'),lod_policy=policy,lod1_recorded_measurement=measured,
            provenance=dict(method='Procedural mesh generation; evidence references below',
                ai_stage='Assistant-authored generation code and documentation',
                human_author=None,creation_date=None,manual_edit_history='NOT_RECORDED',
                reference_purpose_review='PENDING',input_allowlist_review='PENDING',license_review='PENDING',
                evidence=refs,evidence_status='REFERENCED_NOT_APPROVED' if refs else 'PER_MODEL_EVIDENCE_MISSING',
                source_set='source_manifest.json; whole pipeline scope, not a per-model dependency proof'),
            approval=dict(decision='PENDING',reviewer=None,reviewed_at=None)))
    return dict(schema_version='1.0',channel='INTERNAL_REVIEW',sales_release_permitted=False,
        inputs=dict(source_manifest=sha(root/'source_manifest.json'),theme_manifest=sha(root/'theme_output/manifest.json'),
                    full_catalog=sha(catalog_path),lod_measurements=sha(iou_path)),records=records)

def validate(document,root=ROOT):
    try:
        from build_initial_evidence import verify
        errors=verify(root)
        if errors:return errors
        expected=build(root)
        return [] if document==expected else ['RECORD_CONTENT_OR_INPUT_MISMATCH']
    except (OSError,ValueError,KeyError,TypeError) as e:
        return ['EVIDENCE_INVALID: '+str(e)]

def main():
    doc=build(); rows=doc['records']; assert len(rows)==84
    tests={}
    for label,change in (
        ('missing_asset',lambda d:d['records'].pop()),
        ('duplicate_asset',lambda d:d['records'].append(d['records'][0])),
        ('changed_hash',lambda d:d['records'][0]['exports'][0].update(sha256='0'*64)),
        ('invented_approval',lambda d:d['records'][0]['approval'].update(decision='APPROVED')),
        ('invented_lod_exception',lambda d:d['records'][0]['lod_policy'][0].update(exception_approved=True))):
        bad=copy.deepcopy(doc);change(bad);tests[label]=bool(validate(bad))
    assert all(tests.values()) and not validate(doc)
    out=ROOT/'asset_records_output';out.mkdir(exist_ok=True)
    (out/'asset_records.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    summary=dict(status='PASS',canonical_records=len(rows),lod1_present=sum(any(e['lod']==1 for e in r['exports']) for r in rows),
        lod2_present=sum(any(e['lod']==2 for e in r['exports']) for r in rows),
        per_model_evidence_missing=[r['asset_id'] for r in rows if not r['provenance']['evidence']],
        approval='ALL_PENDING',negative_controls=tests,sales_release_permitted=False)
    (out/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    lines=['# 84종 제작 근거 및 LOD 작업표','',
        '실제 파일과 제작 근거를 연결한 내부 검토 기록입니다. 작성자·제작일·수작업 이력은 확인되지 않아 승인하지 않았습니다.',
        'LOD1은 4종에만 있으며 LOD2는 없습니다. 누락 항목은 구현 또는 사유를 기록한 예외 검토가 필요합니다.',
        '기존 IoU는 기록된 측정값이며 GPU 전환 품질 검사를 대신하지 않습니다. 제작 근거가 연결되어도 권리·입력 허용목록 검토는 대기입니다.','',
        '| 모델 | LOD0 삼각형 | LOD1 | 제작 근거 파일 | 승인 |','|---|---:|---|---:|---|']
    for r in rows:
        e=next(e for e in r['exports'] if e['lod']==0 and e['theme']=='MOSS_01')
        lines.append(f"| {r['asset_id']} | {e['triangles']} | {'측정됨·검토 대기' if r['lod_policy'][0]['files_present'] else '구현/예외 검토'} | {len(r['provenance']['evidence'])} | 대기 |")
    (out/'REVIEW_QUEUE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary))

if __name__=='__main__':main()
