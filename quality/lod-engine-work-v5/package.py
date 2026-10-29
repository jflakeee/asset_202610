from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parent
p=R/'godot/report.json';report=json.loads(p.read_text());assert report['passed'] and len(report['models'])==84
for row in report['models']:
 assert row['passed'] and len(row['transitions'])==7
 if row['collision_shapes']:assert row['collision_mutation_detected'] and row['disabled_rays_rejected']
 if row['socket_mutation_detected'] is not None:assert row['socket_mutation_detected']
(R/'reports/engine.json').write_text(json.dumps(report,indent=2))
summary=dict(models=84,transitions=sum(len(r['transitions']) for r in report['models']),collision_shapes=sum(r['collision_shapes'] for r in report['models']),collidable_models=sum(r['collision_shapes']>0 for r in report['models']),nonblocking_models=sum(r['collision_shapes']==0 for r in report['models']),socket_mutation_controls=sum(r['socket_mutation_detected'] is not None for r in report['models']),all_passed=True,engine=report['engine'],gpu_visual='NOT_RUN',art_approved=False,omissions_approved=False,at12_complete=False)
(R/'reports/summary.json').write_text(json.dumps(summary,indent=2))
files=[R/'README.md',R/'prepare.py',R/'package.py',*sorted((R/'reports').glob('*.json')),*sorted((R/'godot').glob('*.gd')),R/'godot/project.godot',R/'godot/catalog.json',*sorted((R/'godot/assets').glob('*.glb'))]
files=[f for f in files if f.name!='archive.json'];manifest={f.relative_to(R).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
archive=R/'trailwood_lod_engine_review_20261029.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,'trailwood_lod_engine_review/'+f.relative_to(R).as_posix())
 z.writestr('trailwood_lod_engine_review/SHA256SUMS.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive) as z:
 for path,sha in manifest.items():assert hashlib.sha256(z.read('trailwood_lod_engine_review/'+path)).hexdigest()==sha
(R/'reports/archive.json').write_text(json.dumps(dict(file=archive.name,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),verified_files=len(manifest),sales_approved=False),indent=2))
print(json.dumps(summary));print('Archive',archive.stat().st_size)
