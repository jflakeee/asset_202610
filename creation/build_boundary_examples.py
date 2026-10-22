"""Six review scenes assembled from exported socket frames, never scaled to fit."""
from pathlib import Path
import json
import numpy as np
from build_rocks import dump
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'boundary_examples_output'
FOLDERS=['fences_output','wood_modules_output','stone_modules_output']

def frame(node):
    extras=node['extras'];x=np.array(extras['outward'],float);y=np.array(extras['up'],float)
    assert abs(np.dot(x,y))<1e-8 and np.allclose([np.linalg.norm(x),np.linalg.norm(y)],1)
    matrix=np.eye(4);matrix[:3,:3]=np.column_stack([x,y,np.cross(x,y)]);matrix[:3,3]=node['translation']
    return matrix

def transform_points(points,matrix):return np.asarray(points)@matrix[:3,:3].T+matrix[:3,3]

def build_scene(name,chains,gate=False):
    instances=[];checks=[];posts=[]
    def add(asset,matrix):
        candidates=[ROOT/folder/'models'/f'{asset}_LOD0.glb' for folder in FOLDERS]
        path=next(p for p in candidates if p.exists());model=load_glb(path)
        nodes={n['name']:n for n in model['doc']['nodes'] if n.get('name','').startswith('SOCKET_')}
        vertices=transform_points(model['positions'],matrix)
        assert np.allclose(matrix[:3,:3].T@matrix[:3,:3],np.eye(3)) and np.isclose(np.linalg.det(matrix[:3,:3]),1)
        instance=dict(asset_id=asset,file=str(path.relative_to(ROOT)),world_matrix_row_major=matrix.tolist(),bounds_y_up_m=[vertices.min(0).tolist(),vertices.max(0).tolist()])
        instances.append(instance)
        # Explicit logical post ownership, independent of decorative collar/course count.
        owners=[] if 'GATE_LEAF' in asset else [[0,0,0]]
        if 'CORNER' in asset:owners.append([.5 if 'WOOD' in asset else 1.,0,0])
        if 'GATE_FRAME' in asset:owners.append([1.3,0,0])
        posts.extend(transform_points(owners,matrix).tolist() if owners else [])
        return model,nodes,matrix
    def join(previous,next_asset,kind='connection'):
        _,previous_nodes,previous_matrix=previous
        end_name='SOCKET_HINGE' if kind=='hinge' else 'SOCKET_END'
        start_name='SOCKET_HINGE' if kind=='hinge' else 'SOCKET_START'
        candidates=[ROOT/f/'models'/f'{next_asset}_LOD0.glb' for f in FOLDERS]
        next_model=load_glb(next(p for p in candidates if p.exists()))
        next_nodes={n['name']:n for n in next_model['doc']['nodes'] if n.get('name','').startswith('SOCKET_')}
        flip=np.eye(4) if kind=='hinge' else np.diag([-1.,1.,-1.,1.])
        world_end=previous_matrix@frame(previous_nodes[end_name])
        matrix=world_end@flip@np.linalg.inv(frame(next_nodes[start_name]))
        result=add(next_asset,matrix);world_start=matrix@frame(next_nodes[start_name])
        error=float(np.linalg.norm(world_end[:3,3]-world_start[:3,3]))
        expected=world_end[:3,0]*(1 if kind=='hinge' else -1)
        angle=float(np.degrees(np.arccos(np.clip(np.dot(expected,world_start[:3,0]),-1,1))))
        assert error<=.001 and angle<=.1
        checks.append(dict(from_asset=previous[0]['doc']['nodes'][0]['name'],to_asset=next_asset,kind=kind,position_error_m=error,outward_error_degrees=angle,status='PASS'))
        return result
    for assets,origin in chains:
        matrix=np.eye(4);matrix[:3,3]=origin;previous=add(assets[0],matrix)
        for asset in assets[1:]:previous=join(previous,asset)
    if gate:
        # Frame is the first and only chain member; leaf remains a separate instance/body.
        root=instances[0];model=load_glb(ROOT/root['file']);nodes={n['name']:n for n in model['doc']['nodes'] if n.get('name','').startswith('SOCKET_')}
        join((model,nodes,np.array(root['world_matrix_row_major'])),'TW_WOOD_GATE_LEAF_A','hinge')
    for i,p in enumerate(posts):
        for q in posts[:i]:assert np.linalg.norm(np.array(p)-q)>.001
    scene=dict(example_id=name,coordinate_frame='glTF Y-up meters',matrix_layout='row-major 4x4; column vectors',instances=instances,socket_checks=checks,logical_post_centers_y_up_m=posts,logical_duplicate_posts=0,status='PASS',scope='Rigid socket placement and logical post ownership; not physical character or GPU validation',gate_state='closed static leaf, separate frame/leaf instances' if gate else None)
    dump(OUT/'scenes'/f'{name}.json',scene)
    return scene

def main():
    scenes=[
        build_scene('wood_7m',[(['TW_WOOD_RAIL_1M_A','TW_WOOD_RAIL_2M_A','TW_WOOD_RAIL_4M_A','TW_WOOD_POST_A'],[0,0,0])]),
        build_scene('stone_7m',[(['TW_STONE_WALL_1M_A','TW_STONE_WALL_2M_A','TW_STONE_WALL_4M_A','TW_STONE_POST_A'],[0,0,0])]),
        build_scene('wood_left_turn',[(['TW_WOOD_RAIL_2M_B','TW_WOOD_CORNER_L90_B','TW_WOOD_RAIL_2M_A','TW_WOOD_END_CAP_A'],[0,0,0])]),
        build_scene('stone_right_turn',[(['TW_STONE_WALL_2M_B','TW_STONE_CORNER_R90_A','TW_STONE_WALL_2M_A','TW_STONE_END_CAP_A'],[0,0,0])]),
        build_scene('wood_gate',[(['TW_WOOD_GATE_FRAME_A'],[0,0,0])],gate=True),
        build_scene('boundary_comparison',[(['TW_WOOD_RAIL_2M_A','TW_WOOD_POST_A'],[0,0,0]),(['TW_STONE_WALL_2M_A','TW_STONE_POST_A'],[0,0,2.0])])]
    # These are placements from actual exported nodes, not mathematical 4m stand-ins.
    for scene in scenes[:2]:assert np.allclose(scene['instances'][-1]['world_matrix_row_major'][0][3],7)
    render(scenes)
    dump(OUT/'validation.json',dict(status='PASS',examples=6,socket_pairs=sum(len(s['socket_checks']) for s in scenes),max_socket_position_error_m=max(c['position_error_m'] for s in scenes for c in s['socket_checks']),no_scaling=True,logical_duplicate_posts=0,geometry_contact_test='NOT_RUN',character_collision_test='NOT_RUN',closed_loop_test='NOT_RUN',slope_test='NOT_RUN',gpu_render='NOT_RUN',art_approval='PENDING'))
    dump(OUT/'catalog.json',dict(examples=[dict(example_id=s['example_id'],scene='scenes/'+s['example_id']+'.json',preview='previews/'+s['example_id']+'.png',instances=len(s['instances'])) for s in scenes],scope='Internal engineering review examples; not approved sales scenes'))
    print('Six boundary scenes, 15 socket joins, no rigid scaling: PASS')

def render(scenes):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    (OUT/'previews').mkdir(parents=True,exist_ok=True)
    for scene in scenes:
        fig=plt.figure(figsize=(10,6),facecolor='#f0ece2');ax=fig.add_subplot(111,projection='3d');all_vertices=[]
        for instance in scene['instances']:
            model=load_glb(ROOT/instance['file']);points=transform_points(model['positions'],np.array(instance['world_matrix_row_major']))
            v=points[:,[0,2,1]]*np.array([1,-1,1]);faces=model['indices'].reshape(-1,3);uv=model['uv'][faces[:,0]]
            colors=np.array(model['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
            ax.add_collection3d(Poly3DCollection(v[faces],facecolors=colors,edgecolors='#59452f',linewidths=.18));all_vertices.append(v)
        v=np.concatenate(all_vertices);mid=(v.min(0)+v.max(0))/2;span=np.maximum(np.ptp(v,axis=0),.6);margin=.2
        ax.set(xlim=(mid[0]-span[0]/2-margin,mid[0]+span[0]/2+margin),ylim=(mid[1]-span[1]/2-margin,mid[1]+span[1]/2+margin),zlim=(0,v[:,2].max()+margin),title=scene['example_id']+' / actual exported meshes')
        ax.set_box_aspect(span);ax.view_init(25,-65);ax.set_axis_off();fig.tight_layout();fig.savefig(OUT/'previews'/f"{scene['example_id']}.png",dpi=140);plt.close(fig)

if __name__=='__main__':main()
