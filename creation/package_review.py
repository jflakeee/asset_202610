"""Build an internal-review archive from explicit source and output allowlists."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,shutil
import numpy as np
from verify_glb import load_glb
from rebuild_all import SCRIPTS
from release_gate import audit
from release_controls import staging_errors, snapshot

ROOT=Path(__file__).resolve().parent
EXTRA=['build_catalog.py','build_boundary_examples.py','boundary_assembly.py','build_review_media.py','build_blender_sources.py','verify_lod_iou.py','design_traceability.py','release_gate.py','package_review.py','validate_khronos.cjs','rebuild_all.py']
DOCS=['PACK_START_HERE.md','REBUILD_README.md','DESIGN_STATUS.md','RELEASE_GATES.md','BLENDER_SOURCES.md','LOD_README.md','rebuild_requirements.txt','rebuild_baseline.json','rebuild_verified_report.json','source_manifest.json','design_traceability.json','release_gate_report.json','boundary_assembly_report.json']
FOLDERS=['wood_props_output','vegetation_output','camp_props_output','path_props_output','furniture_props_output','wood_modules_output','stone_modules_output','natural_catalog_output','boundary_examples_output','review_media_output','lod_iou_output','blender_sources_output']
EXTRA += ['build_closed_boundaries.py','build_slope_examples.py','gate_path_planner.py','build_boundary_runtime.py']
FOLDERS += ['closed_boundaries_output','slope_examples_output','gate_path_output']
EXTRA += ['release_controls.py']
EXTRA += ['build_asset_records.py']
EXTRA += ['build_initial_evidence.py']
FOLDERS += ['initial_evidence_output']
FOLDERS += ['asset_records_output']
DOCS += ['RELEASE_CONTROLS.md']
FOLDERS += ['release_controls_output']
ALLOWED={'.glb','.png','.json','.md','.csv','.blend'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def collect():
    entries={}
    def add(path,target):
        assert path.is_file(),f'Missing deliverable: {path}'
        assert target not in entries,f'Duplicate archive path: {target}'
        entries[target]=path
    add(ROOT/'PACK_START_HERE.md','START_HERE.md')
    add(ROOT.parent/'original_asset_pack_design_v1.md','original_asset_pack_design_v1.md')
    for name in sorted(set(SCRIPTS+EXTRA+DOCS)):add(ROOT/name,'creation/'+name)
    for folder in FOLDERS:
        directory=ROOT/folder
        assert directory.is_dir(),f'Missing output directory: {directory}'
        for path in sorted(directory.rglob('*')):
            if path.is_file():
                if path.suffix not in ALLOWED:raise ValueError(f'K001 unexpected output file: {path}')
                add(path,'creation/'+str(path.relative_to(ROOT)))
    for path in sorted((ROOT/'theme_output').rglob('*')):
        if path.is_file():
            if path.suffix not in {'.glb','.png','.json'}:raise ValueError(f'K001 unexpected themed file: {path}')
            add(path,'standalone_assets/'+str(path.relative_to(ROOT/'theme_output')))
    project=ROOT.parent/'trailwood_godot'
    for path in sorted(project.rglob('*')):
        if path.is_file() and '.godot' not in path.relative_to(project).parts:
            if path.suffix in {'.import','.uid'}:continue
            if path.suffix not in {'.gd','.gdshader','.tscn','.godot','.glb','.png','.json','.md','.log'}:
                raise ValueError(f'K001 unexpected project file: {path}')
            add(path,'trailwood_godot/'+str(path.relative_to(project)))
    return entries

def main():
    result=audit(ROOT,ROOT.parent/'original_asset_pack_design_v1.md')
    assert result['internal_review_package_permitted'],result['internal_blockers']
    assert not result['sales_release_permitted'],'Review tool does not publish sales releases'
    trial=ROOT/'release_controls_output/trial_review'
    assert not staging_errors(trial,json.loads((trial/'review_trial_manifest.json').read_text()))
    for record in json.loads((ROOT/'release_controls_output/approval_requests.json').read_text())['records']:
        assert record['decision']=='PENDING' and record['hashes']==snapshot(record['asset_id'])
    manifest=json.loads((ROOT/'theme_output/manifest.json').read_text())
    engine=json.loads((ROOT.parent/'trailwood_godot/catalog_engine_validation.json').read_text())
    assert engine['passed'] and engine['models']==manifest['unique_models']
    boundary=json.loads((ROOT.parent/'trailwood_godot/boundary_engine_validation.json').read_text())
    assert boundary['passed'] and len(boundary['cases'])==9
    assert all(c['passed'] for c in boundary['cases'])
    assert len(boundary['seam_sweeps'])==4
    assert all(c['passed'] and not c['leaks'] and c['clear_space_control'] and c['zero_mask_control'] for c in boundary['seam_sweeps'])
    assert sum(c['planned_probes'] for c in boundary['seam_sweeps'])==704
    for name,digest in boundary['tested_file_sha256'].items():
        assert sha(ROOT.parent/'trailwood_godot'/name)==digest,'Stale boundary physics result: '+name
    # Synchronize the four main-demo LODs after any validated simplification fixes.
    for p in (ROOT/'lod_output/models').glob('*.glb'):
        original=load_glb(p)
        themed=load_glb(ROOT/'theme_output/MOSS_01/models'/p.name)
        for key in ['positions','normals','uv','indices']:
            assert np.array_equal(original[key],themed[key]),'Stale LOD input: '+p.name
        shutil.copyfile(p,ROOT.parent/'trailwood_godot/assets'/p.name)
    project=ROOT.parent/'trailwood_godot'
    catalog=json.loads((project/'data/catalog.json').read_text())
    for row in catalog.values():
        for lod,key in [('lod0','tri0'),('lod1','tri1')]:
            if lod in row:
                mesh=load_glb(project/row[lod]);themed=load_glb(ROOT/'theme_output/MOSS_01/models'/Path(row[lod]).name)
                assert len(mesh['indices'])//3==row[key]
                for field in ['positions','normals','uv','indices']:
                    assert np.array_equal(mesh[field],themed[field]),'Demo/theme geometry mismatch'
    entries=collect()
    inventory=dict(version='0.23',channel='INTERNAL_REVIEW',sales_release_permitted=False,
                   unique_models=manifest['unique_models'],canonical_candidates=84,legacy_models=8,expansion_models=12,
                   standalone_glbs=manifest['glb_files'],art_approval='PENDING',files={k:dict(sha256=sha(p),bytes=p.stat().st_size) for k,p in entries.items()})
    target=ROOT.parent/'trailwood_pack_v023_20261022.zip'
    with ZipFile(target,'w',ZIP_DEFLATED) as z:
        for name,path in entries.items():z.write(path,name)
        z.writestr('review_package_manifest.json',json.dumps(inventory,ensure_ascii=False,indent=2))
    with ZipFile(target) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(entries)|{'review_package_manifest.json'}
        for name,item in inventory['files'].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==item['sha256']
    print(json.dumps(dict(file=str(target),entries=len(entries),bytes=target.stat().st_size,status='PASS',sales_release=False)))

if __name__=='__main__':main()
