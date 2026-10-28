"""Convex original mesh helper."""
import numpy as np
from scipy.spatial import ConvexHull

def hull(name, points, color, collider=True):
    v=np.asarray(points,dtype=float); h=ConvexHull(v); faces=[]
    for face,eq in zip(h.simplices,h.equations):
        a,b,c=v[face]
        if np.dot(np.cross(b-a,c-a),eq[:3])<0:face=face[[0,2,1]]
        faces.append(face.tolist())
    used=sorted(set(sum(faces,[]))); mapping={old:i for i,old in enumerate(used)}
    return dict(name=name,vertices=v[used].tolist(),faces=[[mapping[x] for x in f] for f in faces],color=color,collider=collider)
