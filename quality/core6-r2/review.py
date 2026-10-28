from pathlib import Path
import json,copy
import numpy as np
from PIL import Image,ImageDraw
from build import build_all,R
from render_review import render

def framed(a,size=256,**options):
    a=copy.deepcopy(a);v=np.concatenate([p['vertices'] for p in a['components']]);factor=.6/max(v.max(0)-v.min(0))
    for p in a['components']:p['vertices']=(np.array(p['vertices'])*factor).tolist()
    return render(a,size,**options)

assets=build_all()
for revision in ('before','after'):
    sheet=Image.new('RGB',(768,580),'white');d=ImageDraw.Draw(sheet)
    for i,(name,a) in enumerate(assets.items()):
        if revision=='before':a=json.loads((R/'inputs'/f'{name}.json').read_text())
        x,y=i%3*256,i//3*290;sheet.paste(framed(a),(x,y+25));d.text((x+10,y+7),name.upper()+' / '+revision.upper(),fill='black')
    sheet.save(R/f'core6_{revision}.png')
for name,a in assets.items():
    for size in (64,128,256):framed(a,size).save(R/f'{name}_{size}.png')
for name in ('ore','rope'):
    sheet=Image.new('RGB',(768,580),'white');d=ImageDraw.Draw(sheet)
    for row,a in enumerate([json.loads((R/'inputs'/f'{name}.json').read_text()),assets[name]]):
        d.text((10,row*290+5),name.upper()+(' / BEFORE' if row==0 else ' / AFTER'),fill='black')
        # Fixed scale, unlike the normalized pack sheet.
        for col,opts in enumerate([{},dict(grayscale=True),dict(silhouette=True)]):sheet.paste(render(a,**opts),(col*256,row*290+25))
    sheet.save(R/f'{name}_comparison.png')
