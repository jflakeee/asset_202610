"""Second art pass; input sources are our own first-pass meshes."""
from pathlib import Path
import copy,json
import numpy as np
from core import hull
from tube import tube
from export import export_glb
R=Path(__file__).resolve().parent

# One warm palette shared by wood, bindings, medicine and reward assets.
PALETTE={'#A77A48':'#C99B62','#D5AE57':'#D6AF4C','#E4BE62':'#D6AF4C','#BA873E':'#A77A48','#B88952':'#C99B62','#E2D4AE':'#E2D4AE','#B5B6AE':'#B8B5AA','#4C555D':'#42484D','#434E55':'#42484D'}

def build_all():
    assets={name:json.loads((R/'inputs'/f'{name}.json').read_text()) for name in ('chest','ore','coin','rope','potion','wood')}
    ore=assets['ore'];rock=copy.deepcopy(ore['components'][0]);ore['components']=[rock]
    # Fractured mineral seams lie across the host rock instead of standing like masonry blocks.
    seams=[
        ('iron_front',[[-.21,.15,-.19],[-.02,.19,-.23],[.10,.29,-.13],[-.06,.355,-.13],[-.22,.27,-.13],[-.12,.20,-.05]]),
        ('iron_crown',[[.02,.28,-.11],[.24,.23,-.07],[.24,.30,.10],[.07,.38,.12],[-.02,.34,.025],[.12,.25,.03]]),
        ('iron_rear',[[-.23,.20,.10],[-.10,.24,.22],[.04,.31,.18],[-.05,.37,.13],[-.20,.30,.11],[-.08,.24,.03]])]
    for name,points in seams:ore['components'].append(hull(name,points,'#B8B5AA',False))
    rope=assets['rope'];coil=copy.deepcopy(rope['components'][0]);v=np.array(coil['vertices']);low=v[:,1].min();high=v[:,1].max();cy=(low+high)/2
    # Binding follows the coil height; no lower hanging loop.
    t=np.arange(16)*2*np.pi/16
    points=np.column_stack([np.zeros(16),cy+((high-low)/2-.012)*np.sin(t),-.24+.045*np.cos(t)])
    binding=tube('snug_binding',points,.017,'#795437',closed=True,reference=(1.,0,0))
    # Small crossing clasp conveys the tied area without claiming a physically accurate knot.
    clasp=tube('binding_crossing',[[-.032,cy-.028,-.289],[-.013,cy-.012,-.305],[.014,cy+.013,-.305],[.031,cy+.026,-.289]],.018,'#795437',reference=(1.,0,0))
    rope['components']=[coil,binding,clasp]
    for name,a in assets.items():
        a['revision']='ART_PASS_2_REVIEW_PENDING';a['external_geometry_inputs']=[]
        for p in a['components']:p['color']=PALETTE.get(p['color'].upper(),p['color'].upper())
        # Body/ground shapes stay at first-pass scale. Both passes share the same frame in comparisons.
        a['material_properties']={}
        low=min(np.array(p['vertices'])[:,1].min() for p in a['components'])
        for p in a['components']:
            v=np.array(p['vertices']);v[:,1]-=low;p['vertices']=v.tolist()
        if 'hinge_pivot' in a:a['hinge_pivot'][1]-=low
    return assets

if __name__=='__main__':
    records=[]
    for name,a in build_all().items():
        (R/'sources'/f'{name}.json').write_text(json.dumps(a,indent=2))
        raw,summary=export_glb(a,animated=name=='chest')
        (R/'models'/f'{name}.glb').write_bytes(raw)
        records.append(dict(id=name,triangles=sum(len(p['faces']) for p in a['components']),**summary))
    (R/'manifest.json').write_text(json.dumps(records,indent=2));print(records)
