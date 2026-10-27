from pathlib import Path
import json,sys
import numpy as np

from core import box,beam,glb
from build_items import render
R=Path(__file__).resolve().parent
wood='#795437';trim='#A77A48';metal='#434E55';gold='#D5AE57';inside='#4F3828'
def build(opened=False):
 body=[box('floor',[0,.035,0],[.68,.07,.48],inside)]
 for z in [-.215,.215]:
  for i in range(4): body.append(box('wall_plank',[(-1.5+i)*.165,.205,z],[.162,.27,.05],wood))
 for x in [-.315,.315]:body.append(box('side_wall',[x,.205,0],[.05,.27,.38],wood))
 for z in [-.242,.242]:body.append(box('rim',[0,.34,z],[.7,.045,.035],trim))
 for x in [-.342,.342]:body.append(box('rim',[x,.34,0],[.035,.045,.48],trim))
 for x in [-.24,.24]:
  for z in [-.247,.247]:body.append(box('body_band',[x,.195,z],[.045,.31,.018],metal))
  body.append(box('bottom_band',[x,.014,0],[.045,.018,.50],metal))
 for x in [-.344,.344]:
  for z in [-.205,.205]:body.append(box('corner_guard',[x,.09,z],[.025,.12,.065],metal))
 body.append(box('lock_plate',[0,.29,-.266],[.105,.12,.025],gold))
 body.append(box('keyhole',[0,.29,-.281],[.018,.045,.008],inside))
 for x in [-.22,.22]:body.append(beam('hinge_pin',[x-.045,.4,.28],[x+.045,.4,.28],.018,metal,8))
 lid=[]
 for i in range(5):lid.append(box('lid_plank',[(-2+i)*.138,.388,0],[.135,.06,.50],trim))
 for x in [-.24,.24]:lid.append(box('lid_band',[x,.428,0],[.045,.02,.51],metal))
 for z in [-.252,.252]:lid.append(box('lid_edge',[0,.393,z],[.70,.075,.025],wood))
 for x in [-.24,.24]:
  for z in [-.19,.19]:lid.append(beam('rivet',[x,.438,z],[x,.447,z],.012,gold,6))
 for p in lid:
  p['vertices']=(np.array(p['vertices'])+np.array([0,.015,0])).tolist()
 if opened:
  a=np.deg2rad(105);rot=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]]);pivot=np.array([0,.4,.28])
  for p in lid:p['vertices']=((np.array(p['vertices'])-pivot)@rot.T+pivot).tolist()
 return {'asset_id':'reward_chest_quality_open' if opened else 'reward_chest_quality','components':body+lid,'lid_component_start':len(body),'hinge_pivot':[0,.4,.28]}
if __name__=='__main__':
 for opened in [False,True]:
  a=build(opened);name=a['asset_id'];(R/(name+'.json')).write_text(json.dumps(a,indent=2));(R/(name+'.glb')).write_bytes(glb(a));render(a,R/(name+'.png'))
  print(name,sum(len(p['faces']) for p in a['components']))
