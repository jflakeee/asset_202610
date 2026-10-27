from pathlib import Path
import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from core import box,beam,hull,glb
R=Path(__file__).resolve().parent
brown='#795437';light='#C99B62';gold='#D6AF4C';dark='#42484D'
def ring(name,y,r,c,n=10):
 return [[r*math.cos(t),y,r*math.sin(t)] for t in np.arange(n)*2*math.pi/n]
def make():
 items=[]
 def add(i,label,parts):items.append({'asset_id':i,'label':label,'components':parts})
 add('resource_wood','통나무',[beam('bark',[-.5,.19,0],[.5,.19,0],.19,brown,9),beam('end_a',[-.505,.19,0],[-.51,.19,0],.16,light,9),beam('end_b',[.505,.19,0],[.51,.19,0],.16,light,9),beam('branch',[.1,.28,0],[.25,.5,.08],.06,brown)])
 pts=[[-.3,0,-.22],[.3,0,-.2],[.27,0,.25],[-.22,0,.23],[-.18,.32,-.1],[.1,.4,.04],[.2,.22,.17]]
 add('resource_iron_ore','철광석',[hull('rock',pts,'#68716D'),hull('iron',[[-.17,.26,-.14],[-.08,.4,-.06],[.04,.31,-.14],[-.03,.26,-.24]],'#B8B5AA')])
 rope=[]
 for layer in range(3):
  for j in range(20):
   a=j*math.tau/20;b=(j+1)*math.tau/20
   rope.append(beam('rope', [.25*math.cos(a),.045+layer*.065,.25*math.sin(a)],[.25*math.cos(b),.045+layer*.065,.25*math.sin(b)],.04,light,5,False))
 rope.append(beam('tie',[-.12,.23,-.03],[.12,.23,.03],.045,brown,6,False))
 add('material_rope','밧줄',rope)
 add('consumable_health_potion','회복약',[hull('bottle',ring('',0,.1,'')+ring('',.08,.16,'')+ring('',.3,.13,'')+ring('',.38,.06,''),'#A73C46'),beam('neck',[0,.36,0],[0,.45,0],.065,'#D5C9A7',10),beam('cork',[0,.44,0],[0,.5,0],.057,brown,8),box('label',[0,.2,-.145],[.12,.12,.012],'#E9DEBF')])
 add('currency_coin','동전',[beam('coin',[0,.18,-.025],[0,.18,.025],.18,gold,12),beam('face',[0,.18,-.026],[0,.18,-.031],.135,'#E8CB73',12),box('mark',[0,.18,-.038],[.04,.14,.014],brown)])
 chest=[box('body',[0,.18,0],[.64,.36,.44],brown),hull('lid',[[-.32,.36,-.22],[.32,.36,-.22],[-.32,.36,.22],[.32,.36,.22],[-.32,.5,0],[.32,.5,0]],light)]
 for x in [-.22,.22]:chest.append(box('band',[x,.19,-.227],[.055,.34,.022],dark))
 chest.append(box('lock',[0,.3,-.25],[.09,.12,.035],gold))
 add('reward_chest','보물상자',chest)
 return items

def render(a,path):
 fig=plt.figure(figsize=(2.56,2.56),dpi=100);ax=fig.add_axes([0,0,1,1],projection='3d')
 allv=np.concatenate([p['vertices'] for p in a['components']]);lo=allv.min(0);hi=allv.max(0);mid=(lo+hi)/2;radius=max(hi-lo)*.62
 for p in a['components']:
  v=np.array(p['vertices'])[:,[0,2,1]];ax.add_collection3d(Poly3DCollection(v[np.array(p['faces'])],facecolor=p['color'],edgecolor='none',linewidth=0))
 for setlim,m in zip([ax.set_xlim,ax.set_ylim,ax.set_zlim],mid[[0,2,1]]):setlim(m-radius,m+radius)
 ax.set_box_aspect((1,1,1));ax.view_init(24,-60);ax.set_proj_type('ortho');ax.axis('off');fig.patch.set_alpha(0);ax.patch.set_alpha(0);fig.savefig(path,transparent=True,dpi=100);plt.close(fig)

if __name__=='__main__':
 for d in ['models','icons/64','icons/128','icons/256','sources']:(R/d).mkdir(parents=True,exist_ok=True)
 records=[];checks=[]
 for a in make():
  aid=a['asset_id'];(R/'models'/f'{aid}.glb').write_bytes(glb(a));(R/'sources'/f'{aid}.json').write_text(json.dumps(a,indent=2))
  render(a,R/'icons/256'/f'{aid}.png')
  for size in [64,128]:Image.open(R/'icons/256'/f'{aid}.png').resize((size,size),Image.Resampling.LANCZOS).save(R/'icons'/str(size)/f'{aid}.png')
  t=sum(len(p['faces']) for p in a['components']);finite=all(np.isfinite(np.array(p['vertices'])).all() for p in a['components'])
  records.append({'id':aid.replace('_','.',1),'label':a['label'],'model':f'models/{aid}.glb','icon':f'icons/128/{aid}.png','triangles':t,'pickup_effect':None})
  checks.append({'id':aid,'finite':bool(finite),'triangles':t,'materials':len(set(p['color'] for p in a['components']))})
 (R/'items.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(R/'validation.json').write_text(json.dumps(checks,indent=2));print(checks)
