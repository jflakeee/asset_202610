"""Restore generated prerequisites ONLY into a disposable checkout, using a verified clean rebuild."""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('disposable_checkout',type=Path);p.add_argument('rebuild',type=Path);a=p.parse_args();root=a.disposable_checkout.resolve();rebuild=a.rebuild.resolve()
report=json.loads((rebuild/'rebuild_report.json').read_text());assert report['status']=='PASS' and report['model_inputs_copied']==0
expected=json.loads((root/'creation/rebuild_baseline.json').read_text())['theme_glb_sha256']
actual={p.relative_to(rebuild/'creation/theme_output').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (rebuild/'creation/theme_output').glob('*/models/*.glb')};assert actual==expected
for file in (rebuild/'creation').glob('*.py'):assert file.read_bytes()==(root/'creation'/file.name).read_bytes()
for folder in (rebuild/'creation').iterdir():
 if folder.is_dir() and folder.name!='__pycache__':shutil.copytree(folder,root/'creation'/folder.name,dirs_exist_ok=True)
shutil.copytree(rebuild/'trailwood_godot',root/'trailwood_godot',dirs_exist_ok=True)
shutil.copy(rebuild/'rebuild_report.json',root/'creation/rebuild_verified_report.json')
print('PASS prerequisite restoration after exact GLB baseline and generator-source comparison')
