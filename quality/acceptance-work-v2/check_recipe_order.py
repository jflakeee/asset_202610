from pathlib import Path
import sys,json,hashlib,tempfile
repo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(repo/'creation'))
import build_initial_evidence as evidence

def collect():
    rows={}
    for generator,recipe,source,glb in evidence.generate():
        key=recipe['asset_id'];assert key not in rows
        rows[key]={'glb_sha256':hashlib.sha256(glb).hexdigest(),'source_sha256':hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
    return rows
before=collect();assert len(before)==6
modules=(evidence.rocks,evidence.trees,evidence.fences);original=[m.RECIPES for m in modules]
try:
    for m in modules:m.RECIPES=list(reversed(m.RECIPES))
    after=collect()
finally:
    for m,recipes in zip(modules,original):m.RECIPES=recipes
assert before==after
errors=evidence.verify(repo/'creation');assert not errors,errors
report={'AT01':{'passed':True,'unique_recipes':6,'generation_success':True,'provenance_file_hashes_verified':True,'human_provenance_approval':False},'AT08':{'passed':True,'scope':'Six P0 recipes; reversed per-generator recipe order','results':before}}
R=Path(__file__).resolve().parent;(R/'reports/recipe_order.json').write_text(json.dumps(report,indent=2));print('PASS AT01 technical P0 evidence and AT08 recipe order invariance: six models')
