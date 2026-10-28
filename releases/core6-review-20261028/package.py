"""Assemble already-reviewed files into a self-contained internal review archive."""
from pathlib import Path
import hashlib,json,shutil,zipfile,argparse
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,default=Path.cwd());W=p.parse_args().source_root.resolve();ROOT=R/'Trailwood_Review_20261028'
MAPPING={'quality_r2':'core6-r2','quality_r3':'core6-r3','blender_review':'blender-source-v1','fbx_review':'fbx-review-v1','godot_review':'godot4-review-v1'}
ROOT.mkdir(exist_ok=True)
for source,target in MAPPING.items():
    dest=ROOT/'quality'/target
    if dest.exists():shutil.rmtree(dest)
    origin=W/'quality'/target
    if not origin.exists():origin=W/source
    shutil.copytree(origin,dest,ignore=shutil.ignore_patterns('__pycache__','.godot','*.blend1','node_modules','.DS_Store'))
for f in ('README.md','verify.py','QUALITY_STATUS.md'):
    shutil.copy(R/f,ROOT/f)
# Canonical imports must be byte-identical to the compact game GLBs.
for name in ('chest','ore','coin','rope','potion','wood'):
    assert (ROOT/'quality/core6-r3/models'/f'{name}.glb').read_bytes()==(ROOT/'quality/godot4-review-v1/assets'/f'{name}.glb').read_bytes()
rows=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p!=ROOT/'manifest.json':
        rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
manifest=dict(name='Trailwood Core Six Internal Review',date='2026-10-28',status='NOT_APPROVED_FOR_SALE',files=rows)
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
archive=R/'trailwood_core6_review_20261028.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob('*')):
        if p.is_file():z.write(p,Path(ROOT.name)/p.relative_to(ROOT))
(R/'archive.json').write_text(json.dumps(dict(filename=archive.name,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(rows)+1,status=manifest['status']),indent=2))
print((R/'archive.json').read_text())
