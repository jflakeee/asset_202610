"""Actual mesh + collider wire overlays for engineering review, not GPU screenshots."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image,ImageDraw
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parent;root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'creation'))
from verify_glb import load_glb

def wire(ax,part):
    if part['type']=='convex_hull':
        v=np.array(part['points_m']);f=ConvexHull(v).simplices
        edges={tuple(sorted((int(a),int(b)))) for tri in f for a,b in zip(tri,np.roll(tri,-1))}
        for a,b in edges:ax.plot(*v[[a,b]].T,color='#16b8a6',linewidth=.6)
        return v
    a,b=np.array(part['endpoints_m']);r=part['radius_m'];axis=b-a;length=np.linalg.norm(axis);axis=axis/length
    u=np.cross(axis,[1,0,0] if abs(axis[0])<.8 else [0,1,0]);u/=np.linalg.norm(u);v=np.cross(axis,u)
    curves=[]
    for z in np.linspace(0,length,5):
        theta=np.linspace(0,2*np.pi,33);curves.append(a+z*axis+r*(np.cos(theta)[:,None]*u+np.sin(theta)[:,None]*v))
    for theta in np.linspace(0,2*np.pi,9)[:-1]:
        radial=np.cos(theta)*u+np.sin(theta)*v
        phi=np.linspace(-np.pi/2,0,10);curves.append(a+r*(np.sin(phi)[:,None]*axis+np.cos(phi)[:,None]*radial))
        curves.append(np.array([a+r*radial,b+r*radial]))
        phi=np.linspace(0,np.pi/2,10);curves.append(b+r*(np.sin(phi)[:,None]*axis+np.cos(phi)[:,None]*radial))
    for curve in curves:ax.plot(*curve.T,color='#16b8a6',linewidth=.55)
    return np.concatenate(curves)

for category in ['TREE','ROCK']:
    paths=[]
    for aid,c in sorted(json.loads((R/'overrides.json').read_text())['overrides'].items()):
        if not aid.startswith('TW_'+category+'_'):continue
        m=load_glb(root/'creation/theme_output/MOSS_01/models'/f'{aid}_LOD0.glb');v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3)
        uv=m['uv'][f[:,0]];palette=np.array(m['image'].convert('RGB'));h,w=palette.shape[:2];colors=palette[np.clip((uv[:,1]*h).astype(int),0,h-1),np.clip((uv[:,0]*w).astype(int),0,w-1)]/255
        fig=plt.figure(figsize=(4,4),dpi=96,facecolor='#f1f3ef');ax=fig.add_axes([0,.12,1,.88],projection='3d');ax.set_facecolor('#f1f3ef');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='none',alpha=.32));allv=[v]
        for p in c.get('parts',[c]):allv.append(wire(ax,p))
        points=np.concatenate(allv);mid=(points.max(0)+points.min(0))/2;half=np.ptp(points,axis=0).max()*.58
        ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half));ax.set_box_aspect((1,1,1));ax.set_axis_off();ax.set_proj_type('ortho');ax.view_init(20,-65)
        fig.text(.5,.065,aid,ha='center',fontsize=7);fig.text(.5,.025,'TEAL = COLLIDER / REVIEW ONLY',ha='center',fontsize=7,color='#12655c')
        path=R/'previews'/f'{aid}.png';path.parent.mkdir(exist_ok=True);fig.savefig(path,dpi=96);plt.close(fig);paths.append(path)
    sheet=Image.new('RGB',(1024,48+3*256),'#f1f3ef');draw=ImageDraw.Draw(sheet);draw.text((15,15),category+' collider candidates / actual mesh overlays / NOT ART APPROVAL',fill='#204b43')
    for i,p in enumerate(paths):
        with Image.open(p) as im:sheet.paste(im.resize((256,256),Image.Resampling.LANCZOS),(i%4*256,48+i//4*256))
    sheet.save(R/'previews'/f'{category.lower()}_sheet.png')
print('24 actual mesh/proxy overlays +2 sheets')
