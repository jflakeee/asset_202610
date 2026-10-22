"""Trace the v1.1 84-model design against the current themed export manifest.

Inventory presence is not art approval, release readiness, or a validated alias.
Run after build_themes.py. Only standard-library modules are required.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

FAMILIES = {
    '나무': ['TREE_ROUND_SMALL', 'TREE_ROUND_BROAD', 'TREE_TIERED_SLIM', 'TREE_TIERED_WIDE', 'TREE_DEAD_FORK', 'TREE_DEAD_LEAN'],
    '바위': ['ROCK_LOW_WEDGE', 'ROCK_UPRIGHT', 'ROCK_FLAT_SLAB', 'ROCK_SPLIT_MASS', 'ROCK_CLUSTER_SMALL', 'ROCK_CLUSTER_LARGE'],
    '덤불/풀': ['VEG_BUSH_ROUND', 'VEG_BUSH_LONG', 'VEG_BUSH_SPARSE', 'VEG_GRASS_LOW', 'VEG_GRASS_FAN', 'VEG_GRASS_TUFT'],
    '숲 소품': ['PROP_STUMP_ROUND', 'PROP_STUMP_SPLIT', 'PROP_LOG_STRAIGHT', 'PROP_LOG_BROKEN', 'PROP_BRANCH_FORK', 'PROP_BRANCH_PILE'],
    '목재 경계': ['WOOD_RAIL_1M', 'WOOD_RAIL_2M', 'WOOD_RAIL_4M', 'WOOD_CORNER_L90', 'WOOD_CORNER_R90', 'WOOD_END_CAP', 'WOOD_END_BROKEN', 'WOOD_POST', 'WOOD_GATE_FRAME', 'WOOD_GATE_LEAF'],
    '석재 경계': ['STONE_WALL_1M', 'STONE_WALL_2M', 'STONE_WALL_4M', 'STONE_CORNER_L90', 'STONE_CORNER_R90', 'STONE_END_CAP', 'STONE_END_RUIN', 'STONE_POST'],
}
# These are review proposals, NEVER compatibility aliases or approved fulfillment.
MAPPING_PROPOSALS = [
    ('TW_SHRUB_ROUND_A', 'TW_VEG_BUSH_ROUND_A', 'round shrub; silhouette and source-ID migration review needed'),
    ('TW_SHRUB_SPREAD_A', 'TW_VEG_BUSH_LONG_A', 'wide shrub; elongated family suitability needs review'),
    ('TW_GRASS_TUFT_A', 'TW_VEG_GRASS_TUFT_A', 'radial solid-blade tuft; variant distinction needs review'),
    ('TW_STUMP_CUT_SMALL_A', 'TW_PROP_STUMP_ROUND_A', 'cut round stump; final shape approval needed'),
    ('TW_STUMP_BROKEN_A', 'TW_PROP_STUMP_SPLIT_A', 'broken rim does not establish split-stump structure; redesign may be needed'),
    ('TW_LOG_CUT_2M_A', 'TW_PROP_LOG_STRAIGHT_A', 'straight log; final shape approval needed'),
    ('TW_LOG_BROKEN_15M_A', 'TW_PROP_LOG_BROKEN_A', '1.5 m broken log; legacy ID must not imply 15 m'),
    ('TW_GRASS_TALL_A', None, '9-blade radial tall grass; neither LOW nor FAN is demonstrated; select or redesign family'),
]
EXPANSION_IDS = {
    'TW_SIGN_ARROW_A', 'TW_SIGN_FORK_A', 'TW_CRATE_SMALL_A', 'TW_CRATE_LONG_A',
    'TW_PAVER_ROUND_A', 'TW_PAVER_LONG_A', 'TW_STEPS_LOW3_A', 'TW_STEPS_WIDE4_A',
    'TW_BENCH_SIMPLE_A', 'TW_BENCH_BACKREST_A', 'TW_TABLE_SQUARE_A', 'TW_TABLE_LONG_A',
}


def build_report(root):
    manifest_path = root / 'theme_output/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    inventory = {}
    fixtures = set()
    for entry in manifest['entries']:
        model = entry['model']
        match = re.fullmatch(r'(TW_[A-Z0-9_]+)_LOD(\d+)', model)
        if not match:
            fixtures.add(model)
            continue
        asset, lod = match.groups()
        path = root / 'theme_output' / entry['file']
        if not path.is_file():
            raise ValueError('Manifest reference missing: ' + entry['file'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry['sha256']:
            raise ValueError('Manifest hash mismatch: ' + entry['file'])
        record = inventory.setdefault(asset, {'lods': set(), 'themes': set(), 'files': []})
        record['lods'].add(int(lod)); record['themes'].add(entry['theme'])
        record['files'].append(entry['file'])
    inventory = {key: value for key, value in inventory.items() if 0 in value['lods']}
    proposals = [dict(source_id=source, proposed_design_id=target,
                      status='UNRESOLVED' if target is None else 'PROPOSED_NOT_APPROVED',
                      note=note, present=source in inventory)
                 for source, target, note in MAPPING_PROPOSALS]
    rows = []
    for category, families in FAMILIES.items():
        for family in families:
            for variant in 'AB':
                asset = f'TW_{family}_{variant}'
                candidates = [p['source_id'] for p in proposals if p['proposed_design_id'] == asset and p['present']]
                evidence = inventory.get(asset)
                rows.append(dict(design_id=asset, category=category, family=family, variant=variant,
                    implementation_status='EXACT_ID_EXPORTED' if evidence else 'MAPPING_REVIEW_REQUIRED' if candidates else 'NOT_EXPORTED',
                    candidate_source_ids=candidates, approval_status='NOT_VERIFIED',
                    lods=sorted(evidence['lods']) if evidence else [],
                    themes=sorted(evidence['themes']) if evidence else []))
    expected = {r['design_id'] for r in rows}
    assert len(rows) == len(expected) == 84
    candidate_ids = {p['source_id'] for p in proposals if p['present']}
    expansions = sorted(EXPANSION_IDS & inventory.keys())
    unmapped = sorted(inventory.keys() - expected - candidate_ids - EXPANSION_IDS)
    categories = []
    for category in FAMILIES:
        subset = [r for r in rows if r['category'] == category]
        categories.append(dict(category=category, target=len(subset),
            exact_id_exports=sum(r['implementation_status'] == 'EXACT_ID_EXPORTED' for r in subset),
            mapping_review_slots=sum(r['implementation_status'] == 'MAPPING_REVIEW_REQUIRED' for r in subset),
            not_exported=sum(r['implementation_status'] == 'NOT_EXPORTED' for r in subset)))
    return dict(schema_version='1.0.0', design_reference='original_asset_pack_design_v1.md sections 18, 24, 26 (v1.1)',
        input_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        scope='Export inventory only; no automatic art approval, alias acceptance, or release certification',
        summary=dict(designed_models=84, current_lod0_exports=len(inventory),
            exact_design_id_exports=len(expected & inventory.keys()),
            legacy_mapping_candidates=len(candidate_ids), expansion_models=len(expansions),
            other_unmapped_exports=len(unmapped), verified_art_approvals=0,
            approval_note='This scanner does not validate approval records; zero means none verified by this report.'),
        categories=categories, design_models=rows, mapping_proposals=proposals,
        expansion_ids=expansions, other_unmapped_ids=unmapped, auxiliary_fixtures=sorted(fixtures))


def markdown(report):
    s = report['summary']
    lines = ['# Trailwood 설계 대응 현황', '',
        '원설계 v1.1의 42원형 × A/B = 84종을 현재 테마 manifest와 대조한 결과다.',
        '파일 존재·해시는 검사하지만 아트 승인, 별칭 확정, 판매 준비 완료를 판정하지 않는다.', '',
        f"현재 LOD0 {s['current_lod0_exports']}종: 정확한 설계 ID {s['exact_design_id_exports']}종, 기존 이름 매핑 후보 {s['legacy_mapping_candidates']}종, 별도 확장 {s['expansion_models']}종, 기타 미매핑 {s['other_unmapped_exports']}종.",
        '**전체 제작 수를 원설계 84종의 완료 수로 사용하지 않는다.** 승인 완료 수는 별도 승인 기록으로 검증해야 한다.', '',
        '| 범주 | 설계 목표 | 정확 ID 출력 | 매핑 검토 슬롯 | 미출력 슬롯 |', '|---|---:|---:|---:|---:|']
    for c in report['categories']:
        lines.append(f"| {c['category']} | {c['target']} | {c['exact_id_exports']} | {c['mapping_review_slots']} | {c['not_exported']} |")
    lines += ['', '## 기존 이름 매핑 후보', '',
        '이 목록은 검토 제안이며 파일 이름이나 참조를 자동 변경하지 않는다. 후보가 있는 설계 슬롯도 구현 완료로 세지 않는다.', '',
        '| 기존 ID | 제안 설계 ID | 상태·검토 사유 |', '|---|---|---|']
    for p in report['mapping_proposals']:
        lines.append(f"| {p['source_id']} | {p['proposed_design_id'] or '미정'} | {p['status']}; present={p['present']}; {p['note']} |")
    lines += ['', '## 별도 확장', '', ', '.join(report['expansion_ids']) or '없음', '',
        '표지판·상자·디딤돌·계단·벤치·테이블은 원설계 84종에 더하지 않는다.', '',
        '## 84개 설계 ID', '', '| 설계 ID | 출력 상태 | 대응 후보 |', '|---|---|---|']
    for r in report['design_models']:
        lines.append(f"| {r['design_id']} | {r['implementation_status']} | {', '.join(r['candidate_source_ids']) or '—'} |")
    lines += ['', '## 아직 별도로 확인해야 할 출고 조건', '',
        '- geometry/palette/recipe 해시에 연결된 사람의 아트 승인과 변경 시 승인 무효화.',
        '- 원설계 AT01~AT16 상태를 PASS/FAIL/NOT_RUN/NOT_APPLICABLE로 구분한 실행 보고서.',
        '- 1/2/4m·코너·열린/닫힌 경로·문 통행구멍·경사에 대한 조립 검증.',
        '- 모델별 LOD 정책, 4방향 실루엣 평가, 생략 또는 기준 변경 근거.',
        '- 편집용 .blend, 조립 예제 6종, 체험 8종 허용목록, 모델별 썸네일, CSV, 이용조건.',
        '- 실제 렌더·재임포트·Android/iOS 측정. 헤드리스 성공으로 대체할 수 없다.', '',
        '재생성: `python design_traceability.py` (build_themes.py 이후).',
        '승인 검증 기능이 없는 이 보고서의 verified_art_approvals=0은 승인 기록 부재의 확정 판정이 아니다.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    report = build_report(args.root)
    (args.root / 'design_traceability.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (args.root / 'DESIGN_STATUS.md').write_text(markdown(report))
    print(json.dumps(report['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
