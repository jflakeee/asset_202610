"""Rebuild every shipped GLB from code in a NEW folder and compare baseline hashes."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys

SCRIPTS=['build_rocks.py','build_trees.py','build_fences.py','build_wood_props.py',
 'build_vegetation.py','build_camp_props.py','build_path_props.py','build_furniture_props.py','build_wood_modules.py','build_stone_modules.py','build_natural_catalog.py','build_lods.py',
 'build_demo.py','build_themes.py','verify_glb.py','verify_wind_geometry.py']
STEPS=[['build_rocks.py','--out','output'],['build_trees.py','--out','trees_output_v2'],
 ['build_fences.py'],['build_wood_props.py'],['build_vegetation.py'],['build_camp_props.py'],
 ['build_path_props.py'],['build_furniture_props.py'],['build_wood_modules.py'],['build_stone_modules.py'],['build_natural_catalog.py'],['build_lods.py'],['build_demo.py'],['build_themes.py'],['verify_wind_geometry.py']]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True,help='New output directory; existing paths are refused')
    args=parser.parse_args();source=Path(__file__).resolve().parent;target=args.out.resolve()
    if target.exists():raise SystemExit('Refusing existing output directory: '+str(target))
    baseline=json.loads((source/'rebuild_baseline.json').read_text())
    for name in SCRIPTS:
        if not (source/name).is_file():raise SystemExit('Missing source: '+name)
    target.mkdir(parents=True);work=target/'creation';work.mkdir()
    # Minimal destination for optional integration output; no copied model inputs.
    (target/'trailwood_godot/data').mkdir(parents=True)
    (target/'trailwood_godot/props').mkdir()
    for name in SCRIPTS:shutil.copyfile(source/name,work/name)
    (target/'logs').mkdir()
    commands=[]
    for index,step in enumerate(STEPS):
        print(f'[{index+1}/{len(STEPS)}] {step[0]}',flush=True)
        with (target/'logs'/f'{index+1:02}_{step[0]}.log').open('w') as log:
            result=subprocess.run([sys.executable,*step],cwd=work,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands.append(dict(script=step[0],exit_code=result.returncode))
        if result.returncode:
            raise SystemExit('Build failed; inspect '+str(target/'logs'))
    actual={str(p.relative_to(work/'theme_output')):digest(p) for p in (work/'theme_output').glob('*/models/*.glb')}
    expected=baseline['theme_glb_sha256'];missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected))
    changed=[name for name in expected if name in actual and expected[name]!=actual[name]]
    import numpy,scipy,PIL,matplotlib
    report=dict(status='PASS' if not (missing or extra or changed) else 'FAIL',
        unique_models=baseline['unique_models'],glb_files=len(actual),missing=missing,extra=extra,changed=changed,
        commands=commands,model_inputs_copied=0,python=platform.python_version(),
        dependencies=dict(numpy=numpy.__version__,scipy=scipy.__version__,pillow=PIL.__version__,matplotlib=matplotlib.__version__),
        scope='Byte-identical GLBs from source; preview images and GPU behavior are not compared')
    (target/'rebuild_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if report['status']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
