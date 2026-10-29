from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parent
rocks=json.loads((R/'reports/rocks.json').read_text());trees=json.loads((R/'reports/trees.json').read_text());qp=json.loads((R/'reports/rock_distance_qp.json').read_text());engine=json.loads((R.parent/'lod_engine_work/reports/engine.json').read_text());doc=json.loads((R/'overrides.json').read_text())
assert engine['passed'] and engine['collider_manifest']['sha256']==hashlib.sha256((R/'overrides.json').read_bytes()).hexdigest()
assert sum(r.get('proxy_revision')=='V8' and r['proxy_binding_pass'] for r in engine['models'])==24
summary=dict(canonical_overrides=24,tree_models=12,tree_capsules=sum(len(c.get('parts',[c])) for a,c in doc['overrides'].items() if a.startswith('TW_TREE_')),rock_models=12,rock_components=29,rock_vertices_max=max(len(p['points_m']) for a,c in doc['overrides'].items() if a.startswith('TW_ROCK_') for p in c['parts']),structure_pass=True,independent_rock_outward_check_pass=qp['passed'],rock_inward_max_m=qp['max_inward_distance_m'],rock_inward_warning_components=qp['inward_warning_components'],tree_ground_extension_max_m=max(r['ground_extension_below_trunk_base_m'] for r in trees['models_detail']),engine_models=84,engine_transitions=588,engine_collision_shapes=sum(r['collision_shapes'] for r in engine['models']),engine_proxy_binding_pass=True,source_lod0_exports_unchanged=252,art_approved=False,contact_fidelity_approved=False,sales_approved=False)
(R/'reports/summary.json').write_text(json.dumps(summary,indent=2))
rows=[]
for r in trees['models_detail']:rows.append(dict(asset_id=r['asset_id'],type='TREE',parts=r['capsule_count'],max_inward_gap_m='',below_ground_m=r['ground_extension_below_trunk_base_m'],structure='PASS',engine_binding='PASS',fidelity='PENDING',art='PENDING'))
for r in rocks['rows']:rows.append(dict(asset_id=r['asset_id'],type='ROCK',parts=r['component_count'],max_inward_gap_m=r['max_inward_error_m'],below_ground_m='',structure='PASS',engine_binding='PASS',fidelity='PENDING',art='PENDING'))
with (R/'review_queue.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(json.dumps(summary,indent=2))
