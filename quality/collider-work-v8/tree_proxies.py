"""Trunk-only swept-sphere proxies; endpoints are sphere centers, source Z-up.

Capsules deliberately contain every trunk triangle. The rounded base consequently
extends below the flat model base; this is measured, never silently clamped.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from scipy.spatial import ConvexHull


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _segment_distance(points, a, b):
    axis=b-a
    t=np.clip((points-a)@axis/float(axis@axis),0.0,1.0)
    return np.linalg.norm(points-(a+t[:,None]*axis),axis=1)


def _sphere_directions():
    # Only a visualization diagnostic; the guarantee below uses convexity, not samples.
    i=np.arange(2048);z=1-2*(i+.5)/len(i);angle=i*np.pi*(3-np.sqrt(5))
    return np.vstack([np.c_[np.sqrt(1-z*z)*np.cos(angle),np.sqrt(1-z*z)*np.sin(angle),z],np.eye(3),-np.eye(3)])


def _capsule(vertices, centers, first, last):
    points=vertices[first*8:(last+1)*8]
    a,b=centers[first].copy(),centers[last].copy()
    distance=_segment_distance(points,a,b)
    radius=float(distance.max()+1e-6)
    length=float(np.linalg.norm(b-a))
    assert length>0 and radius>0
    return dict(type='capsule',endpoints_m=[a.tolist(),b.tolist()],center_m=((a+b)/2).tolist(),
                radius_m=radius,height_m=length+2*radius,
                axis='ENDPOINTS',role='trunk_proxy',component='trunk',
                source_ring_range=[first,last]),points


def build(root: Path):
    root=Path(root).resolve();creation=root/'creation'
    records=json.loads((creation/'asset_records_output/asset_records.json').read_text())['records']
    targets=sorted(r['asset_id'] for r in records if r['asset_id'].startswith('TW_TREE_'))
    assert len(targets)==12
    overrides={};rows=[];directions=_sphere_directions()
    for aid in targets:
        # Prefer the original P0 source over a later evidence duplicate; both are checked input records.
        sources=[p for p in creation.glob(f'*/source_meshes/{aid}.json') if p.parent.parent.name!='initial_evidence_output']
        assert len(sources)==1,(aid,sources)
        path=sources[0];doc=json.loads(path.read_text())
        components=[c for c in doc['components'] if c['name']=='trunk'];assert len(components)==1
        component=components[0];start=component['vertex_start'];count=component['vertex_count']
        vertices=np.asarray(doc['vertices'],float)[start:start+count]
        assert count%8==0 and count//8>=3
        rings=vertices.reshape(-1,8,3);centers=rings.mean(axis=1)
        assert np.all(np.diff(centers[:,2])>0)
        # Ring boundaries come from the actual preserved8-sided trunk component, never foliage.
        candidates=[]
        for split in range(1,len(rings)-1):
            lower,lv=_capsule(vertices,centers,0,split)
            upper,uv=_capsule(vertices,centers,split,len(rings)-1)
            parts=[lower,upper]
            volume=sum(math.pi*p['radius_m']**2*(p['height_m']-2*p['radius_m'])+4/3*math.pi*p['radius_m']**3 for p in parts)
            candidates.append((volume,split,parts,[lv,uv]))
        _,split,parts,pieces=min(candidates,key=lambda x:(x[0],x[1]))
        max_excess=0.0;part_rows=[]
        # Partition actual source triangles at the shared ring; each triangle belongs to one convex capsule.
        faces=np.asarray(doc['triangles'],int)[component['face_start']:component['face_start']+component['face_count']]-start
        assert faces.min()>=0 and faces.max()<count
        assert np.all(np.ptp(faces//8,axis=1)<=1), 'Changed trunk ring topology; fit requires review'
        face_covered=np.zeros(len(faces),dtype=bool)
        for part,points in zip(parts,pieces):
            a,b=np.array(part['endpoints_m']);r=part['radius_m']
            first,last=part['source_ring_range']
            excess=float(np.maximum(_segment_distance(points,a,b)-r,0).max())
            max_excess=max(max_excess,excess)
            ids=(faces>=first*8)&(faces<(last+1)*8)
            face_covered|=ids.all(axis=1)
            # Convexity proves an exact directed surface bound of0: a capsule containing all
            # triangle vertices contains the entire triangle, not merely the sampled vertices.
            hull=ConvexHull(points)
            assert np.max(hull.equations[:,:3]@a+hull.equations[:,3])<1e-8
            assert np.max(hull.equations[:,:3]@b+hull.equations[:,3])<1e-8
            # Because the axis endpoints lie inside the component hull, every capsule point
            # is at most r from that hull. This is a conservative Euclidean upper bound.
            capsule_samples=np.vstack([a+r*directions,b+r*directions])
            violations=capsule_samples@hull.equations[:,:3].T+hull.equations[:,3]
            sampled_plane_lower_bound=float(np.maximum(violations.max(axis=1),0).max())
            part_rows.append(dict(rings=[first,last],radius_m=r,height_m=part['height_m'],
                                  axis_length_m=part['height_m']-2*r,
                                  source_vertices=len(points),trunk_surface_to_capsule_upper_bound_m=excess,
                                  capsule_to_piece_convex_hull_upper_bound_m=r,
                                  sampled_outward_plane_violation_lower_bound_m=sampled_plane_lower_bound,
                                  bound_note='Sampled plane violation is a lower bound, not a Hausdorff guarantee; radius is the conservative directed upper bound'))
        assert face_covered.all() and max_excess<=1e-12
        low=min(min(p['endpoints_m'][0][2],p['endpoints_m'][1][2])-p['radius_m'] for p in parts)
        high=max(max(p['endpoints_m'][0][2],p['endpoints_m'][1][2])+p['radius_m'] for p in parts)
        base=float(vertices[:,2].min());top=float(vertices[:,2].max())
        overrides[aid]=dict(type='compound',parts=parts)
        rows.append(dict(asset_id=aid,source_file=path.relative_to(creation).as_posix(),source_sha256=_sha(path),
                         coordinate_frame='source Z-up metres; endpoints are sphere centers',
                         capsule_count=2,split_ring=split,trunk_rings=len(rings),
                         source_trunk_vertices=count,source_trunk_triangles=len(faces),all_trunk_triangles_contained=True,
                         exact_directed_trunk_surface_excess_m=0.0,
                         ground_extension_below_trunk_base_m=max(0.0,base-low),
                         top_extension_above_trunk_m=max(0.0,high-top),
                         excluded_components=[c['name'] for c in doc['components'] if c['name']!='trunk'],
                         canopy_or_branch_geometry_used=False,
                         approximation_review_required=True,parts=part_rows))
    report=dict(models=12,passed_trunk_capsule_contract=True,coordinate_frame='source Z-up metres',
                constraints='At most2 capsules; totalheight>=2radius; trunk component only; no source mesh changes',
                containment_proof='Each trunk triangle has all3 vertices inside one convex capsule; therefore the complete triangle is contained',
                limitation='Flat trunk bases cannot be fully contained by rounded capsule caps with zero ground extension. Proxies intentionally extend below ground; extension and conservative outward bounds require review.',
                geometry_modified=False,art_approved=False,physics_engine_test='PARENT_INTEGRATION_PENDING',models_detail=rows)
    return overrides,report


if __name__=='__main__':
    import sys
    overrides,report=build(Path(sys.argv[1]))
    out=Path(__file__).resolve().parent/'reports';out.mkdir(exist_ok=True)
    (out/'trees.json').write_text(json.dumps(report,indent=2))
    (out/'trees_overrides.json').write_text(json.dumps(overrides,indent=2))
    print(json.dumps(dict(models=report['models'],passed=report['passed_trunk_capsule_contract'],
                          max_ground_extension_m=max(r['ground_extension_below_trunk_base_m'] for r in report['models_detail']),
                          max_capsule_radius_m=max(p['radius_m'] for r in report['models_detail'] for p in r['parts']))))
