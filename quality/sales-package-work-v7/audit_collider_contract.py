"""Report original section23.3 differences; never approve or alter proxies."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent
root=Path(sys.argv[1]);creation=root/'creation';records=json.loads((creation/'asset_records_output/asset_records.json').read_text())['records'];cat={r['asset_id']:r for r in json.loads((root/'trailwood_godot/data/full_catalog.json').read_text())['assets']}
issues=[]
for row in records:
    aid=row['asset_id'];c=cat[aid].get('collider');parts=c.get('parts',[c]) if c else []
    if aid.startswith('TW_TREE_') and (not parts or len(parts)>2 or any(p.get('type')!='capsule' for p in parts)):
        issues.append(dict(asset_id=aid,rule='tree_capsule_max2_trunk_only',status='MISMATCH',actual_types=[p['type'] for p in parts],detail='Current descriptors do not meet original capsule contract; trunk/canopy fidelity unverified'))
    if aid.startswith('TW_ROCK_'):
        counts=[len(p.get('points_m',[])) for p in parts]
        if any(p.get('type')!='convex_hull' for p in parts) or any(n>16 for n in counts):issues.append(dict(asset_id=aid,rule='rock_convex_proxy_max16_vertices',status='MISMATCH',actual_vertex_counts=counts,detail='3cm outward error not measured; retain as engineering blocker'))
report=dict(models_checked=len(records),contract='original_asset_pack_design_v1.md section23.3',mismatch_models=len({r['asset_id'] for r in issues}),issues=issues,geometry_modified=False,sales_approved=False)
(R/'reports/collider_contract.json').write_text(json.dumps(report,indent=2));print('Collider contract differences:',report['mismatch_models'])
