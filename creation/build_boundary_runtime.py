"""Export review boundary placements/colliders for the Godot physics laboratory."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
from build_rocks import dump
from verify_glb import load_glb

ROOT=Path(__file__).parent;PROJECT=ROOT.parent/'trailwood_godot'

def main():
    assets={r['asset_id']:r for r in json.loads((PROJECT/'data/full_catalog.json').read_text())['assets']}
    scenes=[]
    for path in sorted((ROOT/'closed_boundaries_output/scenes').glob('*.json')):
        source=json.loads(path.read_text());rows=[];seams=[]
        for row in source['instances']:
            model=assets[row['asset_id']]
            rows.append(dict(asset_id=row['asset_id'],file=model['file'],collider=model['collider'],matrix=row['world_matrix_row_major']))
            matrix=np.array(row['world_matrix_row_major'])
            glb=load_glb(PROJECT/model['file'])
            start=next(n for n in glb['doc']['nodes'] if n.get('name')=='SOCKET_START')
            center=matrix[:3,:3]@np.array(start['translation'])+matrix[:3,3]
            tangent=matrix[:3,:3]@(-np.array(start['extras']['outward'],float))
            normal=np.cross(tangent,[0,1,0])
            for offset in [-.2,0,.2]:
                sample=center+tangent*offset
                for angle in [-45,0,45]:
                    a=np.radians(angle);direction=normal*np.cos(a)+tangent*np.sin(a)
                    for sign in [-1,1]:
                        seams.append(dict(kind='socket_neighborhood',asset_id=row['asset_id'],center=sample.tolist(),direction=(direction*sign).tolist(),offset_m=offset,angle_degrees=angle))
            if 'CORNER' in row['asset_id']:
                elbow=matrix[:3,:3]@np.array([.5 if 'WOOD' in row['asset_id'] else 1,0,0])+matrix[:3,3]
                for degrees in range(0,360,45):
                    a=np.radians(degrees)
                    seams.append(dict(kind='corner_elbow',asset_id=row['asset_id'],center=elbow.tolist(),direction=[float(np.cos(a)),0,float(np.sin(a))],angle_degrees=degrees))
        scenes.append(dict(name=source['example_id'],instances=rows,slope_degrees=0,test_x=1,expect_blocked=True,seam_probes=seams))
    pieces=json.loads((ROOT/'gate_path_output/exact_7_6m.json').read_text())['pieces']
    frame=load_glb(PROJECT/assets['TW_WOOD_GATE_FRAME_A']['file'])
    hinge=next(n['translation'] for n in frame['doc']['nodes'] if n.get('name')=='SOCKET_HINGE')
    for opened in [False,True]:
        rows=[]
        for piece in pieces:
            model=assets[piece['asset_id']];matrix=np.eye(4);matrix[0,3]=piece['start_m']
            rows.append(dict(asset_id=piece['asset_id'],file=model['file'],collider=model['collider'],matrix=matrix.tolist()))
        model=assets['TW_WOOD_GATE_LEAF_A'];matrix=np.eye(4);matrix[:3,3]=np.array(hinge)+[2,0,0]
        if opened:matrix[:3,:3]=[[0,0,1],[0,1,0],[-1,0,0]]
        rows.append(dict(asset_id='TW_WOOD_GATE_LEAF_A',file=model['file'],collider=model['collider'],matrix=matrix.tolist()))
        scenes.append(dict(name='gate_open_90' if opened else 'gate_closed',instances=rows,slope_degrees=0,test_x=2.65,expect_blocked=not opened))
    (PROJECT/'boundary_models').mkdir(exist_ok=True)
    report=json.loads((ROOT/'slope_examples_output/validation.json').read_text())
    for row in report['examples']:
        asset=row['asset_id'];path=ROOT/'slope_examples_output/models'/f'{asset}_LOD0.glb'
        shutil.copyfile(path,PROJECT/'boundary_models'/path.name)
        collider=json.loads((ROOT/'slope_examples_output/colliders'/f'{asset}.json').read_text())
        scenes.append(dict(name=asset.lower(),instances=[dict(asset_id=asset,file='boundary_models/'+path.name,collider=collider,matrix=np.eye(4).tolist())],slope_degrees=row['degrees'],test_x=1,expect_blocked=True))
    for scene in scenes:
        for row in scene['instances']:
            row['glb_sha256']=hashlib.sha256((PROJECT/row['file']).read_bytes()).hexdigest()
    dump(PROJECT/'data/boundary_lab.json',dict(scenes=scenes,coordinate_frame='Y-up rigid matrix; collider Z-up',scope='Engineering examples, not art approval'))
    print(f'{len(scenes)} boundary physics laboratory scenes exported')

if __name__=='__main__':main()
