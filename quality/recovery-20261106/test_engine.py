"""Exercise the unchanged restored runtime in a clean project; build a review ZIP."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def main():
 report=json.loads((HERE/'validation.json').read_text());catalog={e['asset_id']:e for e in json.loads((ROOT/'trailwood_godot/data/full_catalog.json').read_text())['assets']}
 with tempfile.TemporaryDirectory(prefix='recovered-stone-engine-') as tmp:
  project=Path(tmp);entries=[]
  shutil.copyfile(ROOT/'quality/lod-engine-work-v5/godot/lod_asset.gd',project/'lod_asset.gd');shutil.copyfile(HERE/'check_engine.gd',project/'check_engine.gd')
  (project/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Recovered stone LOD checks"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
  for c in report['candidates']:
   names=[]
   for src in [ROOT/f"standalone_assets/{c['theme']}/models/{c['asset']}_LOD0.glb",HERE/c['file']]:
    rel=f"{c['theme']}/{src.name}";dest=project/'assets'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);names.append(rel)
    dest.with_suffix('.glb.import').write_text(f'[remap]\nimporter="scene"\nimporter_version=1\ntype="PackedScene"\n[deps]\nsource_file="res://assets/{rel}"\n[params]\nmeshes/generate_lods=false\n')
   entries.append(dict(id=c['asset'],theme=c['theme'],files=[names[0],names[1],names[1]],triangles=[c['original_triangles'],c['candidate_triangles'],c['candidate_triangles']],collider=catalog[c['asset']]['collider'],distances=[18.0,40.0],grass_cull=0.0))
  (project/'manifest.json').write_text(json.dumps(entries,indent=2)+'\n');files=[p for p in project.rglob('*') if p.is_file()]
  for name,args in [('import',['--editor','--import']),('check',['--script','check_engine.gd'])]:
   run=subprocess.run(['godot','--headless','--path',str(project)]+args,capture_output=True,text=True,timeout=120);log=run.stdout+run.stderr
   assert run.returncode==0 and not any(t in log for t in ['SCRIPT ERROR','ERROR:']),(name,log[-4000:])
   if name=='check':(HERE/'engine_check.log').write_text(log)
  result=json.loads((project/'engine_report.json').read_text());assert result['entries']==48 and result['transition_samples']==336
  assert all('meshes/generate_lods=false' in p.read_text() for p in project.rglob('*.glb.import'))
  (HERE/'engine_report.json').write_text(json.dumps(result,indent=2)+'\n')
  with zipfile.ZipFile(HERE/'stone_engine_review.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in files:z.write(p,'project/'+p.relative_to(project).as_posix())
   for p in [HERE/'engine_report.json',HERE/'engine_check.log',HERE/'README.md',HERE/'test_engine.py']:z.write(p,p.name)
  with zipfile.ZipFile(HERE/'stone_engine_review.zip') as z:assert z.testzip() is None
 print(result['engine'],'48 entries / 144 logical scenes / 336 transitions passed')
if __name__=='__main__':main()
