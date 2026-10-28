from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;names=('chest','ore','coin','rope','potion','wood');records=[]
atlas=Image.new('RGBA',(1024,512),(0,0,0,0));preview=Image.new('RGB',(768,512),(230,230,230))
for i,name in enumerate(names):
    master=Image.open(R/'icons'/f'{name}_master.png').convert('RGBA')
    assert master.getchannel('A').getextrema()==(0,255)
    for size in (64,128,256):
        image=master.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
        path=R/'icons'/str(size)/f'{name}.png';image.save(path)
        box=image.getchannel('A').getbbox();assert box and min(box[0],box[1],size-box[2],size-box[3])>=2
    tile=master.convert('RGBa').resize((248,248),Image.Resampling.LANCZOS).convert('RGBA');x=i%4*256+4;y=i//4*256+4;atlas.paste(tile,(x,y))
    preview.paste(Image.alpha_composite(Image.new('RGBA',(256,256),(235,235,235,255)),Image.open(R/'icons/256'/f'{name}.png')).convert('RGB'),(i%3*256,i//3*256))
    records.append(dict(id=name,rect=[x,y,248,248],pivot=[.5,.5],icon_sizes=[64,128,256],source='blender-source-v1',alpha='straight',padding=4))
atlas.save(R/'icons/atlas.png');preview.save(R/'icons/preview_light.png')
(R/'icons/atlas.json').write_text(json.dumps(dict(width=1024,height=512,premultiplied=False,entries=records),indent=2))
print('PASS 18 transparent PNGs; 6 atlas regions; alpha extrema and minimum 2px margin')
