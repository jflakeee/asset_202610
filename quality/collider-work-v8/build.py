"""Build24 hash-bound engineering collider overrides, leaving source catalog intact."""
from pathlib import Path
import json,hashlib,sys
from rock_proxies import build as rocks
from tree_proxies import build as trees
from verify import errors
R=Path(__file__).resolve().parent

def main(root):
    root=Path(root).resolve();out={};reports={}
    for name,builder in [('rocks',rocks),('trees',trees)]:
        overrides,report=builder(root,optimize=False) if name=='rocks' else builder(root);assert len(overrides)==12
        out.update(overrides);reports[name]=report
        (R/f'reports/{name}.json').write_text(json.dumps(report,indent=2))
    assert len(out)==24
    for c in out.values():
        for p in c.get('parts',[c]):p['margin_m']=.001
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    doc=dict(schema_version='1.0',coordinate_frame='SOURCE_Z_UP',source_catalog_sha256=sha(root/'trailwood_godot/data/full_catalog.json'),source_model_sha256={aid:sha(root/'creation/theme_output/MOSS_01/models'/f'{aid}_LOD0.glb') for aid in sorted(out)},overrides=out,art_approved=False,collision_fidelity_approved=False,sales_approved=False)
    assert not errors(doc),errors(doc)
    (R/'overrides.json').write_text(json.dumps(doc,indent=2));print('24 hash-bound override candidates written')
if __name__=='__main__':main(sys.argv[1])
