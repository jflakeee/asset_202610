"""Orthographic mesh review with per-pixel depth; not a marketing render."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from build import build_all
R=Path(__file__).resolve().parent

def render(asset, size=256, direction=(1,.7,-1), grayscale=False, silhouette=False):
    n=size*2
    forward=np.array(direction,dtype=float);forward/=np.linalg.norm(forward)
    right=np.cross([0,1,0],forward);right/=np.linalg.norm(right)
    up=np.cross(forward,right)
    basis=np.array([right,up,forward])
    allv=np.concatenate([p['vertices'] for p in asset['components']]);center=(allv.max(0)+allv.min(0))/2
    scale=n*.78/.72 # Same world-size framing for both revisions.
    depth=np.full((n,n),-np.inf);pixels=np.full((n,n,3),238,dtype=np.uint8)
    light=np.array([-.4,.8,-.6]);light/=np.linalg.norm(light)
    for part in asset['components']:
        v=np.array(part['vertices']);color=np.array([int(part['color'][i:i+2],16) for i in (1,3,5)])
        for face in part['faces']:
            world=v[face];normal=np.cross(world[1]-world[0],world[2]-world[0]);normal/=np.linalg.norm(normal)
            if normal@forward<=0:continue
            t=(world-center)@basis.T;t[:,:2]*=scale;t[:,0]+=n/2;t[:,1]=n/2-t[:,1]
            x0,y0=np.maximum(np.floor(t[:,:2].min(0)).astype(int),0);x1,y1=np.minimum(np.ceil(t[:,:2].max(0)).astype(int),n-1)
            if x1<x0 or y1<y0:continue
            x,y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            a,b,c=t;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-10:continue
            w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
            w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;w2=1-w0-w1
            z=w0*a[2]+w1*b[2]+w2*c[2];section=depth[y0:y1+1,x0:x1+1]
            mask=(w0>=0)&(w1>=0)&(w2>=0)&(z>section)
            shade=np.clip(color*(.48+.52*max(0,normal@light)),0,255)
            if grayscale:shade[:]=shade@np.array([.2126,.7152,.0722])
            if silhouette:shade[:]=35
            pixels[y0:y1+1,x0:x1+1][mask]=shade.astype(np.uint8);section[mask]=z[mask]
    return Image.fromarray(pixels).resize((size,size),Image.Resampling.LANCZOS)

