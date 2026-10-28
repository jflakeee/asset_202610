from pathlib import Path
import json
import numpy as np
R=Path(__file__).resolve().parent
for name in ('chest','ore'):
    asset=json.loads((R/'sources'/f'{name}.json').read_text())
    for part in asset['components']:
        vertices=np.array(part['vertices']);faces=np.array(part['faces'])
        assert np.isfinite(vertices).all()
        assert (np.linalg.norm(np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]]),axis=1)>1e-10).all()
        edges={}
        for tri in faces:
            for i,j in zip(tri,[tri[1],tri[2],tri[0]]):edges[(int(i),int(j))]=edges.get((int(i),int(j)),0)+1
        assert all(count==1 and edges.get((j,i))==1 for (i,j),count in edges.items()),part['name']
    print('PASS finite/nondegenerate, oriented closed components',name)
