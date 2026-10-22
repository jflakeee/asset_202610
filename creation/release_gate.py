"""Audit prototype integrity separately from the original v1 sales contract.

This is an evidence audit, never an art-approval generator. Exit 0 permits only
the requested channel; --channel sales fails closed while any gate is open.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
THEMES = ('MOSS_01', 'DRY_01', 'DUSK_01')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def audit(root, design):
    checks = []

    def add(key, status, detail, blocks_internal=False):
        checks.append(dict(id=key, status=status, detail=detail,
                           blocks_internal=blocks_internal, blocks_sales=status != 'PASS'))

    text = design.read_text() if design.is_file() else ''
    section = text.split('## 18. 42개 원형 카탈로그', 1)[-1].split('## 19.', 1)[0] if text else ''
    families = []
    for line in section.splitlines():
        if line.startswith('|'):
            families.extend(re.findall(r'`([A-Z][A-Z0-9_]+)`', line))
    canonical = {f'TW_{family}_{variant}' for family in families for variant in ('A', 'B')}
    add('design_contract', 'PASS' if len(set(families)) == 42 and len(canonical) == 84 else 'FAIL',
        dict(design_file=design.name, sha256=sha(design) if design.is_file() else None,
             family_count=len(set(families)), canonical_lod0_count=len(canonical)), True)

    theme_root = root / 'theme_output'
    manifest_path = theme_root / 'manifest.json'
    manifest = read(manifest_path) if manifest_path.is_file() else {}
    entries = manifest.get('entries', [])
    files = {str(p.relative_to(theme_root)): p for p in theme_root.glob('*/models/*.glb')}
    listed = [e['file'] for e in entries]
    wrong_hash = [e['file'] for e in entries if e['file'] in files and sha(files[e['file']]) != e.get('sha256')]
    missing = sorted(set(listed) - set(files))
    unlisted = sorted(set(files) - set(listed))
    duplicates = sorted({n for n in listed if listed.count(n) > 1})
    count_ok = manifest.get('glb_files') == len(files)
    add('glb_manifest_integrity', 'PASS' if entries and count_ok and not (wrong_hash or missing or unlisted or duplicates) else 'FAIL',
        dict(actual_files=len(files), declared_files=manifest.get('glb_files'),
             wrong_hash=wrong_hash, missing=missing, unlisted=unlisted, duplicate_paths=duplicates), True)
    ids_by_theme = {theme: {Path(n).stem[:-5] for n in files if n.startswith(theme + '/') and n.endswith('_LOD0.glb')} for theme in THEMES}
    ids = ids_by_theme['MOSS_01']
    add('theme_model_sets', 'PASS' if ids and all(ids_by_theme[t] == ids for t in THEMES) else 'FAIL',
        {theme: len(ids_by_theme[theme]) for theme in THEMES}, True)
    add('canonical_84_candidates', 'PASS' if canonical and canonical <= ids else 'MISSING',
        dict(required=84, exact_id_candidates=len(ids & canonical),
             missing=sorted(canonical - ids), noncanonical_candidates=sorted(ids - canonical),
             note='Exact IDs only; legacy aliases need an explicit reviewed mapping. Candidate existence is not human approval.'))

    validator_errors = []
    for theme in THEMES:
        path = theme_root / theme / 'khronos_summary.json'
        if not path.is_file():
            validator_errors.append(theme + ': no summary')
            continue
        rows = read(path).get('results', [])
        expected = {Path(n).name for n in files if n.startswith(theme + '/')}
        if {r['file'] for r in rows} != expected or len(rows) != len(expected):
            validator_errors.append(theme + ': coverage mismatch')
        validator_errors.extend(theme + '/' + r['file'] for r in rows if r['errors'] or r['warnings'])
    add('khronos_recorded_results', 'PASS' if not validator_errors else 'FAIL',
        dict(issues=validator_errors, freshness='Recorded report coverage checked; rerun validator after edits. Reports are not cryptographically tied to GLBs.'), True)

    baseline_path = root / 'rebuild_baseline.json'
    baseline = read(baseline_path).get('theme_glb_sha256', {}) if baseline_path.is_file() else {}
    changed = [name for name, path in files.items() if baseline.get(name) != sha(path)]
    report_path = root / 'rebuild_verified_report.json'
    rebuilt = read(report_path) if report_path.is_file() else {}
    rebuilt_ok = rebuilt.get('status') == 'PASS' and rebuilt.get('glb_files') == len(files)
    add('recorded_rebuild', 'PASS' if baseline and set(baseline) == set(files) and not changed and rebuilt_ok else 'FAIL',
        dict(changed_or_untracked=changed, baseline_files=len(baseline), recorded_status=rebuilt.get('status'),
             note='Checks current output hashes against baseline plus recorded rebuild; does not execute the rebuild.'), True)

    # Approval verifier exists; no actual verified human approval is supplied.
    # Presence of a file, a generator flag, or test success must not approve art.
    add('human_art_approval', 'NOT_VERIFIED',
        'No verified human decisions bound to geometry/palette/recipe hashes. Never infer approval from generated candidates or PASS tests.')
    add('provenance_complete', 'NOT_VERIFIED',
        'Some original generators carry provenance; per-canonical-model author/tool/date/reference-purpose/AI-stage completeness and approved input allowlist are not verified.')
    from build_asset_records import validate as validate_records
    records_path = root / 'asset_records_output/asset_records.json'
    record_errors = validate_records(read(records_path), root) if records_path.is_file() else ['MISSING_RECORDS']
    add('canonical_evidence_inventory', 'FAIL' if record_errors else 'PASS',
        dict(errors=record_errors, scope='84 fresh per-model file/LOD/evidence records; not provenance or human approval.'), True)
    iou_path = root / 'lod_iou_output/report.json'
    iou = read(iou_path) if iou_path.is_file() else {}
    iou_assets = iou.get('assets', [])
    iou_ok = len(iou_assets) == 4 and all(len(a.get('views', [])) == 4 and all(v['iou'] >= .95 for v in a['views']) for a in iou_assets)
    for asset in iou_assets:
        for name, digest in asset.get('source_sha256', {}).items():
            if not (root / name).is_file() or sha(root / name) != digest: iou_ok = False
    add('existing_four_lod1_silhouette_iou', 'PASS' if iou_ok else 'FAIL',
        dict(models=len(iou_assets), threshold=.95, scope='Four existing LOD1 pairs only; full catalog coverage and LOD2 remain open.'))
    add('lod_coverage', 'NOT_VERIFIED',
        'Every canonical model needs LOD policy and documented omission/exception, with preserved sockets/collider. Existence of a few LOD1 files is insufficient.')
    add('gpu_visual_review', 'NOT_RUN',
        'Headless import/resource tests and matplotlib geometry previews do not establish GPU material, shadows, wind, mipmap, or LOD transition quality.')
    add('mobile_performance', 'NOT_RUN',
        'No verified Android/iOS device measurements for 100/500/1000 objects, warmup 60s, measurement 120s, p50/p95 CPU/GPU, draw calls, memory and load time. Do not claim mobile optimization complete.')
    add('platform_and_terms_review', 'NOT_VERIFIED',
        'Final license/support scope, product name, accurate AI-use disclosure, and current publication-platform requirements require review. This audit is not legal advice or permission to publish.')

    # Audit intended release staging only, never treat internal code archives as sales ZIPs.
    staging = root / 'release_staging'
    required = ['README.md', 'LICENSE.txt', 'CHANGELOG.md', 'manifest.csv',
                'release_manifest.json', 'source/Trailwood.blend',
                'docs/import-guide.md', 'docs/specifications.md']
    absent = [name for name in required if not (staging / name).is_file()]
    add('sales_required_files', 'MISSING' if absent else 'NOT_VERIFIED',
        dict(staging='release_staging', missing=absent,
             note='File presence does not establish valid Blender source, final license, or approved manifest. Internal generator sources are permitted only in review packages by the original design.'))
    add('sales_allowlist_packaging', 'NOT_VERIFIED',
        'Requires fresh staging built only from release_manifest paths, hashes/sizes, no unlisted files, research, credentials, cache, or internal generator/recipe code.')
    add('examples_catalog_thumbnails', 'NOT_VERIFIED',
        'Requires six named assembly examples, validation scene, neutral catalog scene, 84 approved-model PNG thumbnails, genuine engine images, and new-buyer import/reimport checks.')
    add('free_trial_subset', 'NOT_VERIFIED',
        'Requires the exact eight canonical IDs in design section 18, Moss only, own license and allowlist. No extra paid-only files.')

    blend_path = root / 'blender_sources_output/validation.json'
    blend = read(blend_path) if blend_path.is_file() else {}
    source_file = root / 'blender_sources_output/Trailwood.blend'
    blend_ok = blend.get('status') == 'PASS' and blend.get('models') == 84 and source_file.is_file() and sha(source_file) == blend.get('blend_sha256')
    for asset in blend.get('assets', []):
        glb = theme_root / 'MOSS_01/models' / (asset['asset_id'] + '_LOD0.glb')
        if not glb.is_file() or sha(glb) != asset.get('source_glb_sha256'): blend_ok = False
    add('editable_blender_review_source', 'PASS' if blend_ok else 'FAIL',
        dict(models=blend.get('models'), version=blend.get('blender_version'), reopen=blend.get('reopen_validation'), scope='Editable baked meshes, UV/materials and sockets; not parametric modifiers or art approval.'))

    internal_blockers = [c['id'] for c in checks if c['blocks_internal'] and c['status'] != 'PASS']
    sales_blockers = [c['id'] for c in checks if c['blocks_sales']]
    return dict(audit_version='1.0', internal_review_package_permitted=not internal_blockers,
                sales_release_permitted=not sales_blockers, internal_blockers=internal_blockers,
                sales_blockers=sales_blockers, checks=checks,
                approval_policy='No automatic approvals; no publication performed.',
                scope='Local recorded-evidence audit. PASS for internal review is not sales readiness.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--design', type=Path, default=ROOT.parent / 'original_asset_pack_design_v1.md')
    parser.add_argument('--channel', choices=['review', 'sales'], default='review')
    parser.add_argument('--out', type=Path, default=ROOT / 'release_gate_report.json')
    args = parser.parse_args()
    result = audit(args.root.resolve(), args.design.resolve())
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'checks'}, ensure_ascii=False, indent=2))
    permitted = result['internal_review_package_permitted' if args.channel == 'review' else 'sales_release_permitted']
    raise SystemExit(0 if permitted else 2)


if __name__ == '__main__':
    main()
