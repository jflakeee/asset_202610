"""Inscribed <=16-vertex rock proxy candidates with convex-solid error bounds.

Directed Hausdorff error from a convex solid to a convex solid is attained at a
source vertex: distance to a convex set is convex. We therefore evaluate every
original convex-hull vertex against every candidate triangle (not sampled support
directions). Initial retained vertices belong to the original source, so that hull is
inscribed with exactly zero outward error. Optional free-point refinement stays
within0.028999m by the same exact directed distance check.
"""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from scipy.spatial import ConvexHull,cKDTree


def distances_to_solid(points, vertices):
    """Exact point-to-triangulated-convex-solid distances, to float64 precision."""
    hull=ConvexHull(vertices)
    triangles=vertices[hull.simplices]
    a,b,c=triangles[:,0],triangles[:,1],triangles[:,2]
    normals=np.cross(b-a,c-a)
    normal2=np.einsum('ij,ij->i',normals,normals)
    assert (normal2>1e-20).all()
    offsets=points[:,None,:]-a[None,:,:]
    signed=np.einsum('nfi,fi->nf',offsets,normals)/normal2[None,:]
    projection=points[:,None,:]-normals[None,:,:]*signed[:,:,None]
    inside=np.ones((len(points),len(triangles)),dtype=bool)
    for p,q in [(a,b),(b,c),(c,a)]:
        inside &= np.einsum('nfi,fi->nf',np.cross((q-p)[None,:,:],projection-p[None,:,:]),normals)>=-1e-12
    delta=points[:,None,:]-projection
    squared=np.where(inside,np.einsum('nfi,nfi->nf',delta,delta),np.inf)
    for p,q in [(a,b),(b,c),(c,a)]:
        edge=q-p
        t=np.clip(np.einsum('nfi,fi->nf',points[:,None,:]-p[None,:,:],edge)/np.einsum('fi,fi->f',edge,edge)[None,:],0.,1.)
        delta=points[:,None,:]-(p[None,:,:]+t[:,:,None]*edge[None,:,:])
        squared=np.minimum(squared,np.einsum('nfi,nfi->nf',delta,delta))
    result=np.sqrt(np.maximum(0.,squared.min(axis=1)))
    contained=np.max(points@hull.equations[:,:3].T+hull.equations[:,3],axis=1)<=1e-12
    result[contained]=0.
    return result


def reduce_component(points,budget=16):
    vertices=np.unique(np.asarray(points,dtype=np.float64),axis=0)
    vertices=vertices[ConvexHull(vertices).vertices]
    selected=list(range(len(vertices)))
    def score(indices):
        distances=distances_to_solid(vertices,vertices[indices])
        return (float(distances.max()),float(np.mean(distances*distances)))
    while len(selected)>budget:
        options=[]
        for index in selected:
            proposal=[i for i in selected if i!=index]
            if np.linalg.matrix_rank(vertices[proposal]-vertices[proposal][0])<3:continue
            options.append((score(proposal),index,proposal))
        assert options
        _,_,selected=min(options,key=lambda item:(item[0],item[1]))
    # Local exchanges improve the greedy subset while retaining source membership.
    current=score(selected)
    for _ in range(3):
        best=None
        omitted=sorted(set(range(len(vertices)))-set(selected))
        for old in selected:
            for new in omitted:
                proposal=sorted([i for i in selected if i!=old]+[new])
                candidate=score(proposal)
                if candidate[0]<current[0]-1e-10 or abs(candidate[0]-current[0])<=1e-10 and candidate[1]<current[1]-1e-12:
                    option=(candidate,old,new,proposal)
                    if best is None or option[:3]<best[:3]:best=option
        if best is None:break
        current,_,_,selected=best
    candidate=vertices[selected]
    error=distances_to_solid(vertices,candidate)
    source=ConvexHull(vertices)
    assert len(candidate)<=budget
    assert np.max(candidate@source.equations[:,:3].T+source.equations[:,3])<1e-10
    return candidate,dict(source_convex_vertices=len(vertices),proxy_vertices=len(candidate),outward_error_m=0.,inward_hausdorff_m=float(error.max()),rms_original_vertex_error_m=float(np.sqrt(np.mean(error**2))),source_volume_m3=float(source.volume),proxy_volume_m3=float(ConvexHull(candidate).volume))


def improve_component(source_points,initial,outward_limit=.028999):
    """Free-point deterministic refinement, constrained by exact outward distance."""
    v=np.unique(np.asarray(source_points,dtype=float),axis=0);v=v[ConvexHull(v).vertices]
    def score(points):
        distances=distances_to_solid(v,points)
        return float(distances.max()),float(np.mean(distances**2))
    best=np.array(initial,copy=True);bestscore=score(best);center=v.mean(0)
    for weight in [[1,1,1],[1,1,0],[0,0,1],[1,1,.4],[.4,.4,1]]:
        direction=(initial-center)*np.array(weight);direction/=np.maximum(np.linalg.norm(direction,axis=1)[:,None],1e-15)
        proposal=initial+direction*outward_limit
        assert distances_to_solid(proposal,v).max()<=outward_limit+1e-10
        candidate=score(proposal)
        if candidate<bestscore:best,bestscore=proposal,candidate
    for step in [.02,.01,.005]:
        improved=True;rounds=0
        while improved and rounds<2:
            improved=False;rounds+=1
            for i in range(len(best)):
                for axis in range(3):
                    for sign in [-1,1]:
                        proposal=best.copy();proposal[i,axis]+=sign*step
                        if distances_to_solid(proposal[i:i+1],v)[0]>outward_limit:continue
                        candidate=score(proposal)
                        if candidate[0]<bestscore[0]-1e-9 or abs(candidate[0]-bestscore[0])<1e-9 and candidate[1]<bestscore[1]-1e-10:
                            best,bestscore=proposal,candidate;improved=True
    outward=float(distances_to_solid(best,v).max())
    assert outward<=outward_limit+1e-10
    return best,dict(outward_error_m=outward,inward_hausdorff_m=bestscore[0],rms_original_vertex_error_m=bestscore[1]**.5,proxy_volume_m3=float(ConvexHull(best).volume))


def build(root:Path,optimize=False):
    root=Path(root);creation=root/'creation'
    records=json.loads((creation/'asset_records_output/asset_records.json').read_text())['records']
    records={r['asset_id']:r for r in records if r['asset_id'].startswith('TW_ROCK_')}
    assert len(records)==12
    catalog={r['asset_id']:r for r in json.loads((root/'trailwood_godot/data/full_catalog.json').read_text())['assets']}
    overrides={};rows=[]
    for aid,record in sorted(records.items()):
        source_ref=next(e for e in record['provenance']['evidence'] if e['kind']=='source_meshes')
        source_path=creation/source_ref['path'];assert hashlib.sha256(source_path.read_bytes()).hexdigest()==source_ref['sha256']
        mesh=json.loads(source_path.read_text());vertices=np.array(mesh['vertices']);components=mesh.get('components') or [dict(name='rock_mass_0',vertex_start=0,vertex_count=len(vertices))]
        original=catalog[aid]['collider'];parts=original.get('parts',[original]);assert len(parts)==len(components)
        new_parts=[];metrics=[]
        for index,(part,component) in enumerate(zip(parts,components)):
            assert part['type']=='convex_hull'
            old=np.array(part['points_m'],dtype=float)
            source_points=vertices[component['vertex_start']:component['vertex_start']+component['vertex_count']]
            distance,matched=cKDTree(old).query(source_points)
            source_descriptor_delta=float(distance.max())
            assert len(source_points)==len(old) and len(set(matched))==len(old) and source_descriptor_delta<=1e-7
            faces=np.array(mesh['triangles'])
            if mesh.get('components'):
                faces=faces[component['face_start']:component['face_start']+component['face_count']]
            actual_volume=abs(float(np.einsum('ij,ij->i',vertices[faces[:,0]],np.cross(vertices[faces[:,1]],vertices[faces[:,2]])).sum()/6))
            assert np.isclose(actual_volume,ConvexHull(source_points).volume,rtol=1e-7,atol=1e-10)
            reduced,measurement=reduce_component(source_points)
            initial_inward=measurement['inward_hausdorff_m']
            if optimize:
                reduced,updated=improve_component(source_points,reduced)
                measurement.update(updated)
            measurement['initial_inscribed_inward_error_m']=initial_inward
            new=copy.deepcopy(part);new['points_m']=reduced.tolist();new['component']=component.get('name',f'rock_mass_{index}');new_parts.append(new)
            measurement.update(source_to_descriptor_max_vertex_delta_m=source_descriptor_delta,outward_bound_vs_original_descriptor_m=measurement['outward_error_m']+source_descriptor_delta,component=new['component'],original_points=len(old),source_mesh_verified=True,source_component_convexity_verified=True,vertex_membership_verified=not optimize,construction='Bounded outward refinement' if optimize else 'Original source vertex subset',inward_3cm_pass=measurement['inward_hausdorff_m']<=.03)
            metrics.append(measurement)
        overrides[aid]=dict(type='compound',parts=new_parts)
        rows.append(dict(asset_id=aid,component_count=len(metrics),component_count_preserved=True,no_added_bridges='NOT_VERIFIED_WITH_BOUNDED_OUTWARD_VARIANT' if optimize else True,parts=metrics,max_inward_error_m=max(m['inward_hausdorff_m'] for m in metrics),outward_3cm_pass=True,vertex_limit_pass=True,review_status='ENGINEERING_CANDIDATE_ART_AND_FIDELITY_REVIEW_REQUIRED',source_sha256=source_ref['sha256']))
    report=dict(models=12,components=sum(len(r['parts']) for r in rows),vertex_limit_pass=True,outward_3cm_pass=True,max_inward_error_m=max(r['max_inward_error_m'] for r in rows),inward_over_3cm_components=sum(not m['inward_3cm_pass'] for r in rows for m in r['parts']),max_outward_error_m=max(m['outward_error_m'] for r in rows for m in r['parts']),max_outward_bound_vs_original_descriptor_m=max(m['outward_bound_vs_original_descriptor_m'] for r in rows for m in r['parts']),inward_review_target_m=.03,inward_review_pass=all(m['inward_3cm_pass'] for r in rows for m in r['parts']),distance_method='Both convex directed Hausdorff distances are maxima over all source hull vertices against every target face triangle in float64. Inscribed initial candidates have exact zero source outward error; optimized points stay within.029m of the source convex solid.',geometry_modified=False,art_approved=False,rows=rows)
    return overrides,report


def self_check():
    cube=np.array([[x,y,z] for x in [0.,1.] for y in [0.,1.] for z in [0.,1.]])
    points=np.array([[.5,.5,.5],[2.,.5,.5],[2.,2.,.5],[2.,2.,2.],[-1.,0.,0.]])
    assert np.allclose(distances_to_solid(points,cube),[0.,1.,2**.5,3**.5,1.],atol=1e-12)
    assert np.allclose(distances_to_solid(cube,cube),0.)
    reduced,metrics=reduce_component(cube)
    assert len(reduced)==8 and metrics['inward_hausdorff_m']==0.
    # Removing an extremal cube corner must produce a nonzero inner gap.
    assert np.isclose(distances_to_solid(cube,cube[:-1]).max(),1/np.sqrt(3))

if __name__=='__main__':
    import sys
    self_check();overrides,report=build(Path(sys.argv[1]));out=Path(__file__).resolve().parent/'reports';out.mkdir(exist_ok=True)
    (out/'rocks.json').write_text(json.dumps(report,indent=2));(out/'rocks_overrides.json').write_text(json.dumps(overrides,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
