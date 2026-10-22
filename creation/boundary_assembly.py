"""Reusable millimetre path planning and measured GLB socket assembly.

Plans do not deform models, generate slopes, or establish physical corner closure.
All assembly transforms in the returned scene data operate in glTF Y-up metres.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from verify_glb import load_glb

ROOT = Path(__file__).resolve().parent
SOURCE_TO_GLTF = np.array([[1.,0,0],[0,0,1],[0,-1,0]])


def split_length(length_m, modules_mm=(1000,2000,4000)):
    """DP minimizes uncovered length, then module count; never scales a module."""
    if not math.isfinite(length_m) or length_m <= 0:
        raise ValueError('ZERO_OR_INVALID_LENGTH')
    if not modules_mm or any(type(n) is not int or n <= 0 for n in modules_mm):
        raise ValueError('INVALID_MODULE_LENGTHS')
    target_mm = int(math.floor(length_m * 1000 + 0.5))
    if target_mm > 1_000_000:
        raise ValueError('PATH_OVER_1KM_SPLIT_REQUIRED')
    best = {0: ()}
    for position in range(target_mm + 1):
        if position not in best:
            continue
        for module in sorted(set(modules_mm), reverse=True):
            end = position + module
            if end <= target_mm:
                candidate = best[position] + (module,)
                if end not in best or len(candidate) < len(best[end]):
                    best[end] = candidate
    occupied = max(best)
    residual_mm = length_m * 1000 - occupied
    status = 'EXACT_WITHIN_1MM' if abs(residual_mm) <= 1 + 1e-9 else ('NEEDS_CUSTOM_END' if residual_mm <= 250 + 1e-9 else 'UNSUPPORTED_LENGTH')
    return dict(status=status, input_length_m=length_m, quantized_length_mm=target_mm,
                modules_mm=list(best[occupied]), occupied_mm=occupied,
                residual_mm=residual_mm, scale_applied=False)


def clean_polyline(points):
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError('INVALID_POINTS')
    result = []
    for point in points:
        if not result or np.linalg.norm(point-result[-1]) >= .001:
            result.append(point)
    if len(result) < 2:
        raise ValueError('ZERO_LENGTH_PATH')
    return np.array(result)


def plan_polyline(points):
    """Source Z-up points; 15deg acceptance is policy only, not slope geometry."""
    clean = clean_polyline(points)
    delta = np.diff(clean, axis=0)
    segments = []
    for vector in delta:
        horizontal = float(np.linalg.norm(vector[:2]))
        slope = math.degrees(math.atan2(abs(vector[2]), horizontal))
        segments.append(dict(horizontal_length_m=horizontal, slope_degrees=slope,
            slope_policy='WITHIN_15_DEG_POLICY' if slope <= 15+1e-9 else 'MANUAL_SLOPE_OVER_15_DEG',
            split=split_length(horizontal) if horizontal > 0 else None,
            physical_slope_generation='NOT_IMPLEMENTED'))
    turns = []
    for left,right in zip(delta,delta[1:]):
        denom=np.linalg.norm(left[:2])*np.linalg.norm(right[:2])
        degrees=math.degrees(math.acos(float(np.clip(np.dot(left[:2],right[:2])/denom,-1,1)))) if denom else None
        policy='STRAIGHT' if degrees is not None and degrees<.1 else ('CORNER_90_REQUIRES_FITTING' if degrees is not None and abs(degrees-90)<=.1 else 'MANUAL_UNSUPPORTED_TURN')
        turns.append(dict(turn_degrees=degrees,policy=policy))
    closed=bool(np.linalg.norm(clean[-1]-clean[0])<=.001)
    return dict(points_m=clean.tolist(), merged_points=len(points)-len(clean),segments=segments,turns=turns,
                closed_endpoint=closed, physical_closed_assembly='NOT_IMPLEMENTED',
                note='Polyline endpoint coincidence does not prove outgoing socket direction or physical corner fit.')


def post_ownership(module_count, closed=False):
    if type(module_count) is not int or module_count<1:
        raise ValueError('INVALID_MODULE_COUNT')
    # Topological vertices only; corner spans and real socket frames are separate.
    return dict(start_post_owners=list(range(module_count)),terminal_posts=0 if closed else 1,
                unique_post_count=module_count if closed else module_count+1,
                scope='TOPOLOGY_ONLY_NOT_PHYSICAL_CORNER_CLOSURE')


def socket_frame(node):
    out=np.array(node['extras']['outward'],float);up=np.array(node['extras']['up'],float)
    if not np.isclose(np.linalg.norm(out),1) or not np.isclose(np.linalg.norm(up),1) or abs(out@up)>1e-6:
        raise ValueError('NON_ORTHONORMAL_SOCKET')
    frame=np.eye(4);frame[:3,:3]=np.column_stack((out,np.cross(up,out),up));frame[:3,3]=node.get('translation',[0,0,0])
    if not np.isclose(np.linalg.det(frame[:3,:3]),1):raise ValueError('REFLECTED_SOCKET')
    return frame


def transform_points(points,matrix):
    return np.asarray(points)@matrix[:3,:3].T+matrix[:3,3]


def transform_normals(normals,matrix):
    result=np.asarray(normals)@np.linalg.inv(matrix[:3,:3])
    return result/np.linalg.norm(result,axis=1)[:,None]


def discover(root,asset_id):
    paths=sorted(root.glob(f'*_output/models/{asset_id}_LOD0.glb'))
    if not paths:raise FileNotFoundError(asset_id)
    # Ignore themed copies; detect ambiguous differently-generated originals.
    hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if len(hashes)!=1:raise ValueError('AMBIGUOUS_SOURCE '+asset_id)
    return paths[0]


def collider_points(root,asset):
    for catalog in sorted(root.glob('*_output/catalog.json')):
        for item in json.loads(catalog.read_text()).get('assets',[]):
            if item['asset_id']==asset and item.get('collider'):
                desc=item['collider'];parts=desc.get('parts',[desc])
                return np.concatenate([np.asarray(p['points_m'],float) for p in parts])
    # Legacy 1m/2m A engineering descriptors exist only in the original demo.
    path=root/'demo_output/colliders.json'
    parts=json.loads(path.read_text()).get('assets',{}).get(asset,[]) if path.is_file() else []
    points=[]
    for p in parts:
        if p['type']!='box':raise ValueError('UNSUPPORTED_COLLIDER')
        signs=np.array([[x,y,z] for x in [-1,1] for y in [-1,1] for z in [-1,1]])
        points.extend(signs*np.array(p['size_m'])/2+np.array(p['center_m']))
    if not points:raise ValueError('MISSING_COLLIDER '+asset)
    return np.array(points)


def assemble_straight(root, lengths=(1,2,4), yaw_degrees=0):
    angle=math.radians(yaw_degrees);c=math.cos(angle);s=math.sin(angle)
    placement=np.eye(4);placement[:3,:3]=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    flip=np.diag([-1.,-1,1,1]);previous=None;instances=[];joints=[]
    for length in lengths:
        asset=f'TW_WOOD_RAIL_{length}M_A';path=discover(root,asset);mesh=load_glb(path)
        nodes={n.get('name'):n for n in mesh['doc']['nodes']}
        start=socket_frame(nodes['SOCKET_START']);end=socket_frame(nodes['SOCKET_END'])
        if previous is not None:placement=previous@flip@np.linalg.inv(start)
        world_start=placement@start;world_end=placement@end
        if previous is not None:
            gap=float(np.linalg.norm(previous[:3,3]-world_start[:3,3]))
            angle_error=math.degrees(math.acos(float(np.clip(-previous[:3,0]@world_start[:3,0],-1,1))))
            assert gap<=.001 and angle_error<=.1
            joints.append(dict(gap_m=gap,outward_opposition_error_degrees=angle_error))
        vertices=transform_points(mesh['positions'],placement)
        normals=transform_normals(mesh['normals'],placement)
        triangles=vertices[mesh['indices']].reshape(-1,3,3)
        geometric=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);geometric/=np.linalg.norm(geometric,axis=1)[:,None]
        normal_dot=np.sum(geometric*normals[mesh['indices'][::3]],axis=1)
        assert float(normal_dot.min())>.999
        local_collider=collider_points(root,asset)
        world_collider=transform_points(local_collider@SOURCE_TO_GLTF.T,placement)
        restored=transform_points(world_collider,np.linalg.inv(placement))@SOURCE_TO_GLTF
        assert np.allclose(restored,local_collider,atol=1e-8)
        assert abs(np.linalg.det(placement[:3,:3])-1)<1e-8
        instances.append(dict(asset_id=asset,source=str(path.relative_to(root)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            transform_y_up=placement.tolist(),socket_start=world_start[:3,3].tolist(),socket_end=world_end[:3,3].tolist(),
            minimum_transformed_normal_dot=float(normal_dot.min()),collider_points_checked=len(world_collider),
            collider_transform='SAME_RIGID_TRANSFORM_AS_MESH',bounds_min=vertices.min(0).tolist(),bounds_max=vertices.max(0).tolist()))
        previous=world_end
    span=float(np.linalg.norm(np.array(instances[-1]['socket_end'])-instances[0]['socket_start']))
    assert abs(span-sum(lengths))<1e-6
    return dict(status='PASS',yaw_degrees=yaw_degrees,span_m=span,instances=instances,joints=joints,
                scope='Actual GLB sockets/triangles/normals and collision descriptor transforms; no engine physics or render test.')


def run_checks(root):
    results={}
    results['7m']=split_length(7);assert sorted(results['7m']['modules_mm'])==[1000,2000,4000]
    results['2.13m']=split_length(2.13);assert results['2.13m']['status']=='NEEDS_CUSTOM_END'
    results['2.251m']=split_length(2.251);assert results['2.251m']['status']=='UNSUPPORTED_LENGTH'
    results['2.001m']=split_length(2.001);assert results['2.001m']['status']=='EXACT_WITHIN_1MM'
    try:split_length(0)
    except ValueError:results['zero_length']='REJECTED_AS_REQUIRED'
    else:raise AssertionError('Zero accepted')
    merged=plan_polyline([[0,0,0],[.0005,0,0],[2,0,0]]);assert merged['merged_points']==1;results['sub1mm_merge']=merged
    for slope in [15,16]:
        plan=plan_polyline([[0,0,0],[2,0,2*math.tan(math.radians(slope))]])
        assert plan['segments'][0]['slope_policy']==('WITHIN_15_DEG_POLICY' if slope==15 else 'MANUAL_SLOPE_OVER_15_DEG')
        results[f'{slope}deg_slope_policy']=plan
    turn=plan_polyline([[0,0,0],[2,0,0],[3,1,0]]);assert turn['turns'][0]['policy']=='MANUAL_UNSUPPORTED_TURN';results['45deg_turn']=turn
    results['closed_ownership']=post_ownership(4,True);assert results['closed_ownership']['unique_post_count']==4
    results['open_ownership']=post_ownership(4,False);assert results['open_ownership']['unique_post_count']==5
    for yaw in [0,90]:
        try:results[f'actual_1_2_4m_yaw_{yaw}']=assemble_straight(root,yaw_degrees=yaw)
        except FileNotFoundError as error:results[f'actual_1_2_4m_yaw_{yaw}']=dict(status='NOT_RUN',missing_asset=str(error))
    return dict(status='PASS_EXECUTED_CHECKS',tests=results,
                not_implemented=['physical corner fitting and closed-loop socket closure','slope geometry generation','gate reservation/path clipping','engine collision traversal'],
                automatic_art_approval=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path,default=ROOT/'boundary_assembly_report.json');args=parser.parse_args()
    report=run_checks(args.root.resolve());args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],actual_mesh_checks={k:v['status'] for k,v in report['tests'].items() if k.startswith('actual_')},not_implemented=report['not_implemented']),indent=2))


if __name__=='__main__':main()
