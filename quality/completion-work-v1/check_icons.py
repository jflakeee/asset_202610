from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent;records=[]
for name in ('chest','ore','coin','rope','potion','wood'):
 for size in (64,128,256):
  p=R/'icons'/str(size)/f'{name}.png';im=Image.open(p);assert im.mode=='RGBA' and im.size==(size,size)
  alpha=im.getchannel('A');assert alpha.getextrema()==(0,255);box=alpha.getbbox();margin=min(box[0],box[1],size-box[2],size-box[3]);assert margin>=2
  assert all(alpha.getpixel(x)==0 for x in ((0,0),(size-1,0),(0,size-1),(size-1,size-1)))
  records.append(dict(id=name,size=size,margin_px=margin,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
metadata=json.loads((R/'icons/atlas.json').read_text());atlas=Image.open(R/'icons/atlas.png');assert atlas.mode=='RGBA' and atlas.size==(1024,512)
rects=[]
for entry in metadata['entries']:
 x,y,w,h=entry['rect'];assert x>=4 and y>=4 and x+w<=1020 and y+h<=508
 assert all(x+w<=a or a+c<=x or y+h<=b or b+d<=y for a,b,c,d in rects);rects.append((x,y,w,h))
 expected=Image.open(R/'icons'/f"{entry['id']}_master.png").convert('RGBa').resize((248,248),Image.Resampling.LANCZOS).convert('RGBA')
 assert atlas.crop((x,y,x+w,y+h)).tobytes()==expected.tobytes()
(R/'reports/icons.json').write_text(json.dumps(dict(passed=True,pngs=records,atlas_regions=len(rects),alpha='straight',method='Premultiplied-alpha downsampling followed by straight-alpha PNG encoding'),indent=2));print('PASS 18 PNGs and exact 6 atlas regions')
