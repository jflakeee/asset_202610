"""Run from the extracted package: python verify.py. Python standard library only."""
from pathlib import Path
import hashlib,json,sys,zipfile,struct
R=Path(__file__).resolve().parent

def verify():
    manifest=json.loads((R/'manifest.json').read_text());expected={x['path'] for x in manifest['files']};errors=[]
    for item in manifest['files']:
        path=R/item['path']
        if not path.is_relative_to(R) or '..' in Path(item['path']).parts:raise ValueError('Unsafe manifest path')
        if not path.is_file():errors.append('MISSING '+item['path']);continue
        raw=path.read_bytes()
        if len(raw)!=item['bytes'] or hashlib.sha256(raw).hexdigest()!=item['sha256']:errors.append('CHANGED '+item['path'])
    actual={p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file() and p!=R/'manifest.json' and '__pycache__' not in p.parts}
    errors.extend('UNLISTED '+p for p in sorted(actual-expected))
    names=('chest','ore','coin','rope','potion','wood')
    for name in names:
        a=R/'quality/core6-r3/models'/f'{name}.glb';b=R/'quality/godot4-review-v1/assets'/f'{name}.glb'
        if a.is_file() and b.is_file() and a.read_bytes()!=b.read_bytes():errors.append('GODOT_VERSION_MISMATCH '+name)
    for folder in ('core6-r2','core6-r3'):
        path=R/'quality'/folder/'manifest.json'
        if not path.is_file():continue
        for item in json.loads(path.read_text()):
            model=path.parent/'models'/f"{item['id']}.glb"
            if not model.is_file():continue
            raw=model.read_bytes()
            if len(raw)<12 or struct.unpack_from('<4sII',raw)!=(b'glTF',2,len(raw)):errors.append('INVALID_GLB_HEADER '+str(model.relative_to(R)))
    for p in [R/'quality/core6-r3/validation/summary.json',R/'quality/godot4-review-v1/reports/clean_import.json',R/'quality/blender-source-v1/reports/reopen_checks.json',R/'quality/fbx-review-v1/reports/roundtrip.json']:
        if not p.exists():errors.append('MISSING_EVIDENCE '+str(p.relative_to(R)));continue
        data=json.loads(p.read_text())
        if 'passed' in data and not data['passed']:errors.append('FAILED_EVIDENCE '+str(p.relative_to(R)))
        if 'validator' in data and any(x['errors'] or x['warnings'] for x in data['models']):errors.append('GLTF_VALIDATION_FAILED')
    if errors:
        print('\n'.join(errors));return 1
    print('PASS',len(expected),'files; hashes, game/Godot consistency, GLB headers and saved evidence. No engine tests were rerun.');return 0
if __name__=='__main__':sys.exit(verify())
