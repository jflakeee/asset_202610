from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R.parent/'blender-source-v1');args=p.parse_args()
rows=json.loads((R/'manifest.json').read_text());out=Image.new('RGB',(1024,1088),(45,48,53));draw=ImageDraw.Draw(out)
for i,name in enumerate(('chest','ore')):
    before={'chest':568,'ore':42}[name];after=next(r['triangles'] for r in rows if r['id']==name);y=i*544
    for col,path,label in [(0,args.source/'renders'/f'{name}.png',f'{name.upper()} BASE / {before} triangles'),(1,R/'renders'/f'{name}_after.png',f'{name.upper()} SELECTIVE FINISH / {after} triangles')]:
        image=Image.open(path);out.paste(image,(col*512,y+32));draw.text((col*512+12,y+10),label,fill='white')
        for size in (64,128):image.resize((size,size),Image.Resampling.LANCZOS).save(R/'renders'/f'{name}_{"base" if col==0 else "finish"}_{size}.png')
out.save(R/'renders/comparison.png')
