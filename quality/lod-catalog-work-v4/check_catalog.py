from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;doc=json.loads((R/'reports/catalog.json').read_text());assert len(doc['models'])==84 and len({m['asset_id'] for m in doc['models']})==84
files=[];omissions=0
for model in doc['models']:
 assert {e['lod'] for e in model['levels']}=={1,2} and model['approval']=='PENDING'
 for level in model['levels']:
  assert level['exception_approved'] is False
  if level['status']=='OMISSION_REVIEW_REQUIRED':assert 'file' not in level;omissions+=1;continue
  assert level['status']=='SILHOUETTE_PASS_REVIEW_REQUIRED'
  assert len(level['views'])==4 and min(level['views'].values())>=level['threshold']
  assert level['triangles']<model['lod0_triangles'] and level['sockets_preserved']
  path=R/level['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==level['sha256'];files.append(path.name)
assert set(files)=={p.name for p in (R/'models').glob('*.glb')} and len(files)==len(set(files))
validation=json.loads((R/'reports/validator.json').read_text());assert {r['file'] for r in validation['results']}==set(files)
for row in validation['results']:
 assert row['errors']==row['warnings']==0
 assert hashlib.sha256((R/'models'/row['file']).read_bytes()).hexdigest()==row['sha256']
summary=dict(canonical_models=84,lod_decisions=168,silhouette_pass_candidates=len(files),omission_reviews_required=omissions,all_exported_models_validated=True,at12_complete=False,reason='Omission approvals, engine LOD switching/collider binding, GPU visual and art review remain open')
(R/'reports/summary.json').write_text(json.dumps(summary,indent=2));print(summary)
