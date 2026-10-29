"""Independent convex-QP distance check against original collider solids.

For two convex polytopes, max distance to the other convex solid is attained at
one of the first polytope's vertices. This is a numerical QP check, not an exact
arithmetic proof;1e-6m allowance is retained in the acceptance budget.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import minimize
R=Path(__file__).resolve().parent

def distance(p,v,hull):
    a=hull.equations[:,:3];b=hull.equations[:,3]
    if np.max(a@p+b)<=1e-9:return 0.
    result=minimize(lambda x:.5*float((x-p)@(x-p)),v.mean(0),jac=lambda x:x-p,
        constraints=[dict(type='ineq',fun=lambda x:-(a@x+b),jac=lambda x:-a)],method='SLSQP',options=dict(ftol=1e-13,maxiter=100))
    assert result.success,result.message
    assert np.max(a@result.x+b)<1e-7
    return float(np.linalg.norm(result.x-p))

def check(root):
    old={r['asset_id']:r for r in json.loads((root/'trailwood_godot/data/full_catalog.json').read_text())['assets']};doc=json.loads((R/'overrides.json').read_text());rows=[]
    for aid,c in doc['overrides'].items():
        if not aid.startswith('TW_ROCK_'):continue
        oldc=old[aid]['collider'];oldparts=oldc.get('parts',[oldc]);newparts=c.get('parts',[c]);assert len(oldparts)==len(newparts)
        for i,(a,b) in enumerate(zip(oldparts,newparts)):
            ov=np.unique(np.array(a['points_m']),axis=0);nv=np.unique(np.array(b['points_m']),axis=0);oh=ConvexHull(ov);nh=ConvexHull(nv)
            outward=max(distance(p,ov,oh) for p in nv)
            inward=max(distance(p,nv,nh) for p in ov[oh.vertices])
            passed=len(nv)<=16 and outward+b['margin_m']+1e-6<=.03
            assert passed,(aid,i,outward)
            rows.append(dict(asset_id=aid,component=i,vertices=len(nv),outward_distance_m=outward,inward_distance_m=inward,physics_margin_setting_m=b['margin_m'],passed_outward_contract_with_1um_allowance=passed,inward_3cm_review_warning=inward>.03))
    report=dict(passed=True,models=12,components=len(rows),max_outward_distance_m=max(r['outward_distance_m'] for r in rows),max_inward_distance_m=max(r['inward_distance_m'] for r in rows),inward_warning_components=sum(r['inward_3cm_review_warning'] for r in rows),method='Independent SLSQP convex distance QPs, every hull vertex; tolerance1um',scope='Geometry distances plus configured margin budget; not a full character sweep/contact fidelity certification',rows=rows,sales_approved=False)
    (R/'reports/rock_distance_qp.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
if __name__=='__main__':check(Path(sys.argv[1]))
