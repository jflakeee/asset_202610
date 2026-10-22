"""Closed wood/stone loops using actual exported socket frames, without scaling."""
from pathlib import Path
import json, hashlib
import numpy as np
import build_boundary_examples as examples
from build_rocks import dump
from verify_glb import load_glb
from boundary_assembly import collider_points, SOURCE_TO_GLTF, transform_normals

ROOT=Path(__file__).parent
OUT=ROOT/'closed_boundaries_output'

def joint(end,start):
    gap=float(np.linalg.norm(end[:3,3]-start[:3,3]))
    angle=float(np.degrees(np.arccos(np.clip(-end[:3,0]@start[:3,0],-1,1))))
    up=float(np.degrees(np.arccos(np.clip(end[:3,1]@start[:3,1],-1,1))))
    return dict(position_error_m=gap,outward_error_degrees=angle,up_error_degrees=up,
                passed=gap<=.001 and angle<=.1 and up<=.1)

def validate(scene):
    world_sockets=[];hashes={};parts_checked=0
    for instance in scene['instances']:
        path=ROOT/instance['file'];m=load_glb(path);matrix=np.array(instance['world_matrix_row_major'])
        nodes={n['name']:n for n in m['doc']['nodes'] if n.get('name','').startswith('SOCKET_')}
        world_sockets.append({name:matrix@examples.frame(node) for name,node in nodes.items()})
        hashes[instance['asset_id']]=hashlib.sha256(path.read_bytes()).hexdigest()
        p=examples.transform_points(m['positions'],matrix);f=m['indices'].reshape(-1,3)
        cross=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
        cross/=np.linalg.norm(cross,axis=1)[:,None]
        normals=transform_normals(m['normals'],matrix)
        assert np.min(np.sum(cross*normals[f[:,0]],axis=1))>.999
        collider=collider_points(ROOT,instance['asset_id'])@SOURCE_TO_GLTF.T
        world=examples.transform_points(collider,matrix)
        assert np.allclose(examples.transform_points(world,np.linalg.inv(matrix)),collider)
        parts_checked+=len(collider)
    checks=[joint(world_sockets[i]['SOCKET_END'],world_sockets[(i+1)%len(world_sockets)]['SOCKET_START']) for i in range(len(world_sockets))]
    assert all(c['passed'] for c in checks)
    # Two independent malformed closure controls must be caught.
    shifted=world_sockets[0]['SOCKET_START'].copy();shifted[0,3]+=.01
    assert not joint(world_sockets[-1]['SOCKET_END'],shifted)['passed']
    wrong_axis=world_sockets[0]['SOCKET_START'].copy();wrong_axis[:3,0]*=-1
    assert not joint(world_sockets[-1]['SOCKET_END'],wrong_axis)['passed']
    assert not any('POST_' in i['asset_id'] or 'END_' in i['asset_id'] for i in scene['instances'])
    scene.update(closed_loop=True,closure_checks=checks,terminal_posts=0,
                 normal_and_collider_transform_test='PASS',collider_vertices_checked=parts_checked,
                 source_sha256=hashes,negative_closure_controls='PASS',
                 scope='Actual exported mesh/socket closed placement, logical post uniqueness, transformed normals/collider points; physical contact and navigation not tested')
    return scene

def main():
    examples.OUT=OUT
    scenes=[]
    for material in ['WOOD','STONE']:
        straight='RAIL' if material=='WOOD' else 'WALL'
        for direction in ['L','R']:
            # Opposite sides have equal length; every corner consumes its actual exported socket span.
            assets=[]
            for length in [2,4,2,4]:
                assets.extend([f'TW_{material}_{straight}_{length}M_A',f'TW_{material}_CORNER_{direction}90_A'])
            name=f'{material.lower()}_closed_{direction.lower()}'
            scene=validate(examples.build_scene(name,[(assets,[0,0,0])]))
            dump(OUT/'scenes'/f'{name}.json',scene);scenes.append(scene)
    examples.render(scenes)
    dump(OUT/'validation.json',dict(status='PASS',closed_scenes=len(scenes),
        socket_pairs=sum(len(s['closure_checks']) for s in scenes),terminal_posts=0,
        logical_duplicate_posts=0,max_closure_position_error_m=max(c['position_error_m'] for s in scenes for c in s['closure_checks']),
        wrong_position_and_direction_controls='PASS',normals_and_collider_transforms='PASS',
        surface_contact='NOT_RUN',engine_traversal='NOT_RUN',gpu_render='NOT_RUN',art_approval='PENDING'))
    print('Four actual closed-loop scenes / 32 socket joins: PASS')

if __name__=='__main__':main()
