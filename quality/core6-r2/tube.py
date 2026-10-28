import numpy as np

def tube(name, points, radius, color, closed=False, sides=5, reference=(0.,1,0)):
    points=np.array(points,dtype=float);vertices=[];faces=[];count=len(points)
    for i,p in enumerate(points):
        tangent=points[(i+1)%count]-points[(i-1)%count] if closed else points[min(i+1,count-1)]-points[max(i-1,0)]
        tangent/=np.linalg.norm(tangent)
        ref=np.array(reference,dtype=float)
        if abs(tangent@ref)>.9:ref=np.array([1.,0,0])
        u=np.cross(tangent,ref);u/=np.linalg.norm(u);v=np.cross(tangent,u)
        vertices.extend([p+radius*(np.cos(t)*u+np.sin(t)*v) for t in np.arange(sides)*2*np.pi/sides])
    for i in range(count if closed else count-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides;c=((i+1)%count)*sides+(j+1)%sides;d=((i+1)%count)*sides+j
            faces.extend([[a,b,c],[a,c,d]])
    if not closed:
        for j in range(1,sides-1):faces.extend([[0,j+1,j],[(count-1)*sides,(count-1)*sides+j,(count-1)*sides+j+1]])
    vertices=np.array(vertices);f=np.array(faces)
    volume=np.einsum('ij,ij->i',vertices[f[:,0]],np.cross(vertices[f[:,1]],vertices[f[:,2]])).sum()/6
    if volume<0:faces=[x[::-1] for x in faces]
    return dict(name=name,vertices=vertices.tolist(),faces=faces,color=color,collider=False,closed_path=closed,path_samples=count,cross_section_sides=sides)
