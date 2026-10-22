"""Regenerate six initial assets and bind original inputs to all themed exports."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import scipy
import build_rocks as rocks
import build_trees as trees
import build_fences as fences
from build_themes import replace, png, PALETTES

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'initial_evidence_output'
DEPS=['build_initial_evidence.py','build_rocks.py','build_trees.py','build_fences.py','build_themes.py','verify_glb.py']

def digest(data): return hashlib.sha256(data).hexdigest()

def generate():
    for module in (rocks,trees,fences):
        for recipe in module.RECIPES:
            values=module.generate(recipe)
            if module is fences:
                data,components=module.export(recipe)
                source=dict(coordinate_system='Z-up meters',components=components)
            else:
                v,f,n,s=values[:4]
                r=dict(generator_version=trees.VERSION,**recipe) if module is trees else recipe
                data=rocks.write_glb(r,v,f,n,s,rocks.palette_bytes())
                source=dict(coordinate_system='Z-up meters',vertices=v.tolist(),triangles=f.tolist(),face_palette_slots=s.tolist())
                if module is trees: source['components']=values[4]
            yield module.__name__+'.py',recipe,source,data

def verify(root=ROOT):
    try:
        report=json.loads((root/'initial_evidence_output/validation.json').read_text())
        if report['status']!='PASS' or len(report['assets'])!=6: return ['INVALID_REPORT']
        if set(report['source_sha256'])!=set(DEPS):return ['INCOMPLETE_SOURCE_BINDING']
        for name,h in report['source_sha256'].items():
            if digest((root/name).read_bytes())!=h:return ['STALE_SOURCE:'+name]
        regenerated=list(generate())
        expected={r['asset_id'] for _,r,_,_ in regenerated}
        if {r['asset_id'] for r in report['assets']}!=expected:return ['INVALID_IDS']
        for _,recipe,_,data in regenerated:
            for theme,colors in PALETTES.items():
                path=root/'theme_output'/theme/'models'/(recipe['asset_id']+'_LOD0.glb')
                if replace(data,png(colors),theme)[0]!=path.read_bytes():return ['REGENERATION_MISMATCH']
        for row in report['assets']:
            for name,h in row['evidence_sha256'].items():
                if digest((root/name).read_bytes())!=h:return ['STALE_EVIDENCE:'+name]
            for name,h in row['theme_sha256'].items():
                if digest((root/name).read_bytes())!=h:return ['STALE_EXPORT:'+name]
        return []
    except (OSError,ValueError,KeyError):return ['MISSING_OR_INVALID_EVIDENCE']

def main():
    hashes={name:digest((ROOT/name).read_bytes()) for name in DEPS}
    rows=[]
    for generator,recipe,source,data in generate():
        asset=recipe['asset_id'];themes={}
        for theme,colors in PALETTES.items():
            rebuilt=replace(data,png(colors),theme)[0]
            path=ROOT/'theme_output'/theme/'models'/f'{asset}_LOD0.glb'
            if rebuilt!=path.read_bytes():raise ValueError('Rebuild mismatch: '+str(path))
            themes[str(path.relative_to(ROOT))]=digest(rebuilt)
        evidence={}
        provenance=dict(method='Fresh procedural regeneration and byte-identical theme export comparison',
            generator=generator,source_sha256=hashes,base_glb_sha256=digest(data),
            theme_sha256=themes,external_geometry_inputs_declared=[],input_allowlist_review='PENDING',
            ai_assistance='Assistant-authored procedural code and documentation',
            human_author=None,original_creation_date=None,manual_edit_history='NOT_RECORDED',art_approval='PENDING')
        for kind,obj in [('recipes',recipe),('source_meshes',source),('provenance',provenance)]:
            path=OUT/kind/(asset+'.json');rocks.dump(path,obj);evidence[str(path.relative_to(ROOT))]=digest(path.read_bytes())
        rows.append(dict(asset_id=asset,theme_sha256=themes,evidence_sha256=evidence,status='PASS'))
    assert len(rows)==6
    rocks.dump(OUT/'validation.json',dict(status='PASS',assets=rows,source_sha256=hashes,
        comparisons=18,model_inputs_copied=0,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
        scope='Current reproducibility, not proof of historical authorship or legal approval',art_approval='PENDING'))
    assert not verify()
    print('Six initial assets: 18 themed byte comparisons PASS; approval remains PENDING')

if __name__=='__main__':main()
