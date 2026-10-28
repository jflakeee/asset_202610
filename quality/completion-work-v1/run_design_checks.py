"""Run existing design checks in a disposable repository copy. Never records art approval."""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('repository',type=Path);p.add_argument('--commit',required=True);a=p.parse_args();root=a.repository.resolve();creation=root/'creation';rows=[]
tasks=[('boundary', ['boundary_assembly.py'],0),('closed_paths',['build_closed_boundaries.py'],0),('slopes',['build_slope_examples.py'],0),('gate_reservation',['gate_path_planner.py'],0),('approval_and_allowlist_controls',['release_controls.py'],0),('canonical_84_records',['build_asset_records.py'],0),('internal_gate',['release_gate.py','--channel','review'],0),('sales_gate_rejects_incomplete',['release_gate.py','--channel','sales'],2)]
for name,args,expected in tasks:
 result=subprocess.run([sys.executable,*args],cwd=creation,capture_output=True,text=True)
 (R/'reports'/f'{name}.log').write_text(result.stdout+'\n'+result.stderr)
 rows.append(dict(check=name,exit_code=result.returncode,expected_exit_code=expected,passed=result.returncode==expected,script_sha256=hashlib.sha256((creation/args[0]).read_bytes()).hexdigest()))
 print(name,result.returncode,'expected',expected,flush=True)
outputs={'release_gate':'release_gate_report.json','canonical_records':'asset_records_output/validation.json','closed_paths':'closed_boundaries_output/validation.json','slopes':'slope_examples_output/validation.json','gate_reservation':'gate_path_output/validation.json','approval_controls':'release_controls_output/validation.json'}
for name,path in outputs.items():
 source=creation/path
 if source.is_file():(R/'reports'/f'84_{name}.json').write_bytes(source.read_bytes())
(R/'reports/design_run.json').write_text(json.dumps(dict(base_commit=a.commit,checks=rows,passed=all(r['passed'] for r in rows),scope='Fresh execution of listed checks only, not complete AT01–AT16, human art approval or device performance'),indent=2))
if not all(r['passed'] for r in rows):sys.exit(1)
