"""Independent structural and engine-coordinate checks for24 collider overrides."""
from pathlib import Path
import json,sys,copy
import numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent

def errors(doc):
    found=[]
    if doc.get('coordinate_frame')!='SOURCE_Z_UP' or len(doc.get('overrides',{}))!=24:found.append('FRAME_OR_COUNT')
    for aid,collider in doc.get('overrides',{}).items():
        parts=collider.get('parts',[collider])
        if any(p.get('margin_m')!=.001 for p in parts):found.append(aid+':PHYSICS_MARGIN')
        if aid.startswith('TW_TREE_'):
            if not 1<=len(parts)<=2:found.append(aid+':CAPSULE_COUNT')
            for part in parts:
                endpoints=np.array(part.get('endpoints_m',[]));radius=part.get('radius_m',0)
                if part.get('type')!='capsule' or endpoints.shape!=(2,3) or not np.isfinite(endpoints).all() or not np.isfinite(radius) or radius<=0:found.append(aid+':CAPSULE_DATA');continue
                total=np.linalg.norm(endpoints[1]-endpoints[0])+2*radius
                if abs(part.get('height_m',-1)-total)>1e-8 or not np.allclose(part.get('center_m',[]),endpoints.mean(0),rtol=0,atol=1e-8):found.append(aid+':CAPSULE_TRANSFORM')
        elif aid.startswith('TW_ROCK_'):
            for part in parts:
                v=np.array(part.get('points_m',[]))
                if part.get('type')!='convex_hull' or not 4<=len(v)<=16 or v.shape!=(len(v),3) or not np.isfinite(v).all():found.append(aid+':HULL_DATA');continue
                if len(np.unique(v,axis=0))!=len(v) or ConvexHull(v).volume<=1e-10:found.append(aid+':HULL_DEGENERATE')
        else:found.append(aid+':UNEXPECTED_ID')
    return found
if __name__=='__main__':
    doc=json.loads((R/'overrides.json').read_text());assert not errors(doc)
    bad=copy.deepcopy(doc);bad['coordinate_frame']='Y_UP';assert errors(bad)
    aid=next(a for a in doc['overrides'] if a.startswith('TW_TREE_'));bad=copy.deepcopy(doc);parts=bad['overrides'][aid].get('parts',[bad['overrides'][aid]]);parts[0]['radius_m']=-1;assert errors(bad)
    bad=copy.deepcopy(doc);c=bad['overrides'][aid];c['parts']=[c.get('parts',[c])[0]]*3;c['type']='compound';assert errors(bad)
    aid=next(a for a in doc['overrides'] if a.startswith('TW_ROCK_'));bad=copy.deepcopy(doc);p=bad['overrides'][aid].get('parts',[bad['overrides'][aid]])[0];p['points_m']*=5;assert errors(bad)
    (R/'reports/structure.json').write_text(json.dumps(dict(passed=True,models=24,negative_controls=['wrong_frame','negative_radius','three_capsules','excess_hull_vertices'],sales_approved=False),indent=2));print('24 collider structures PASS;4 negative controls')
