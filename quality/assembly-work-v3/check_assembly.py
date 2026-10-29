from pathlib import Path
import json,sys,copy
import numpy as np
repo=Path(sys.argv[1]).resolve();root=repo/'creation';sys.path.insert(0,str(root))
import build_boundary_examples as examples
import build_closed_boundaries as closed
from verify_glb import load_glb
R=Path(__file__).resolve().parent;examples.ROOT=root;examples.OUT=R
scene=examples.build_scene('wood_10m_open',[(['TW_WOOD_RAIL_2M_A']*5+['TW_WOOD_POST_A'],[0,0,0])])
points=np.array(scene['logical_post_centers_y_up_m']);assert len(points)==6
assert np.allclose(points[:,0],[0,2,4,6,8,10],atol=.001)
assert all(np.linalg.norm(a-b)>.001 for i,a in enumerate(points) for b in points[:i])
assert len(scene['socket_checks'])==5 and max(c['position_error_m'] for c in scene['socket_checks'])<=.001
for inst in scene['instances']:
 matrix=np.array(inst['world_matrix_row_major']);assert np.allclose(matrix[:3,:3].T@matrix[:3,:3],np.eye(3)) and np.linalg.det(matrix[:3,:3])>0
# Sample every endpoint face vertex against the following actual mesh triangles.
def distance(p,a,b,c):
 n=np.cross(b-a,c-a);length=np.linalg.norm(n)
 if length<1e-12:return float('inf')
 n=n/length;q=p-n*np.dot(p-a,n);v0=b-a;v1=c-a;v2=q-a
 d00=v0@v0;d01=v0@v1;d11=v1@v1;d20=v2@v0;d21=v2@v1;den=d00*d11-d01*d01
 u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
 if u>=-1e-8 and v>=-1e-8 and u+v<=1+1e-8:return abs(float((p-a)@n))
 return min(np.linalg.norm(p-(x+np.clip((p-x)@(y-x)/((y-x)@(y-x)),0,1)*(y-x))) for x,y in ((a,b),(b,c),(c,a)))
world=[]
for instance in scene['instances']:
 mesh=load_glb(root/instance['file']);m=np.array(instance['world_matrix_row_major']);vertices=examples.transform_points(mesh['positions'],m);world.append((vertices,mesh['indices'].reshape(-1,3)))
contact=[]
for (left,_),(right,faces) in zip(world,world[1:]):
 end=left[left[:,0]>=left[:,0].max()-1e-6];triangles=right[faces]
 gaps=[min(distance(p,*tri) for tri in triangles) for p in end];maximum=max(gaps)
 assert maximum<=.001,maximum
 contact.append(dict(endpoint_vertices=len(end),max_sampled_surface_distance_m=float(maximum)))
loops=[]
for material in ('WOOD','STONE'):
 straight='RAIL' if material=='WOOD' else 'WALL'
 for turn in ('L','R'):
  assets=[]
  for length in (2,4,2,4):assets.extend([f'TW_{material}_{straight}_{length}M_A',f'TW_{material}_CORNER_{turn}90_A'])
  item=closed.validate(examples.build_scene(f'{material.lower()}_closed_{turn.lower()}',[(assets,[0,0,0])]))
  assert item['terminal_posts']==0 and item['logical_duplicate_posts']==0
  loops.append(dict(id=item['example_id'],joints=len(item['closure_checks']),max_error_m=max(c['position_error_m'] for c in item['closure_checks']),terminal_posts=0))
# An extra owner at an existing position must fail uniqueness.
bad=np.vstack([points,points[0]]);assert any(np.linalg.norm(a-b)<.001 for i,a in enumerate(bad) for b in bad[:i])
report=dict(AT02=dict(passed=True,span_m=10,modules=5,terminal_posts=1,duplicate_posts=0,contacts=contact),AT05=dict(passed=True,scope='Real exported mesh/socket assembly and post ownership; not character physics',open_terminal_posts=1,closed_examples=loops,extra_owner_control='REJECTED'),engine_physics='NOT_RUN',gpu_visual='NOT_RUN')
(R/'reports/assembly.json').write_text(json.dumps(report,indent=2));print('PASS AT02/AT05 geometric assembly and endpoint-contact sampling')
