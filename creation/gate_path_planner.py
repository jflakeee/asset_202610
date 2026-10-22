"""Reserve actual gate-frame spans before splitting a straight wood boundary."""
import math,json
from pathlib import Path
from boundary_assembly import split_length
from verify_glb import load_glb
from build_rocks import dump

ROOT=Path(__file__).parent;OUT=ROOT/'gate_path_output'

def plan(length,reservations):
    if not math.isfinite(length) or length<=0:raise ValueError('INVALID_LENGTH')
    path=ROOT/'wood_modules_output/models/TW_WOOD_GATE_FRAME_A_LOD0.glb'
    nodes={n['name']:n for n in load_glb(path)['doc']['nodes']}
    width=nodes['SOCKET_END']['translation'][0]-nodes['SOCKET_START']['translation'][0]
    spans=sorted((float(x),float(x)+width) for x in reservations)
    for i,(start,end) in enumerate(spans):
        if not math.isfinite(start) or start<0 or end>length+1e-9:raise ValueError('GATE_OUT_OF_BOUNDS')
        if i and start<spans[i-1][1]-1e-9:raise ValueError('OVERLAPPING_GATES')
    pieces=[];residuals=[];cursor=0.
    def fill(start,end):
        if end-start<=1e-9:return
        split=split_length(end-start);x=start
        for mm in split['modules_mm']:
            pieces.append(dict(asset_id=f'TW_WOOD_RAIL_{mm//1000}M_A',start_m=x,end_m=x+mm/1000,scale=1.))
            x+=mm/1000
        if split['status']!='EXACT_WITHIN_1MM':residuals.append(dict(start_m=x,end_m=end,status=split['status']))
    for start,end in spans:
        fill(cursor,start);pieces.append(dict(asset_id='TW_WOOD_GATE_FRAME_A',start_m=start,end_m=end,scale=1.,protected=True))
        cursor=end
    fill(cursor,length)
    for piece in pieces:
        if 'RAIL' in piece['asset_id']:
            assert all(min(piece['end_m'],b)-max(piece['start_m'],a)<=1e-9 for a,b in spans)
    # Only clean rails are emitted; damage/end-cap selection is not allowed inside a reservation.
    return dict(status='READY_FOR_STRAIGHT_PLACEMENT' if not residuals else 'NEEDS_MANUAL_RESIDUAL',
        length_m=length,gate_span_m=width,reservations=spans,pieces=pieces,residuals=residuals,
        scope='Straight interval planning only; no leaf animation, navigation or engine collision test')

def main():
    exact=plan(7.6,[2]);assert exact['status']=='READY_FOR_STRAIGHT_PLACEMENT'
    assert [p['asset_id'] for p in exact['pieces']]==['TW_WOOD_RAIL_2M_A','TW_WOOD_GATE_FRAME_A','TW_WOOD_RAIL_4M_A']
    residual=plan(7.73,[2]);assert residual['residuals'][0]['status']=='NEEDS_CUSTOM_END'
    rejected=[]
    for label,total,res in [('overlap',8,[2,3]),('outside',7,[6]),('negative',7,[-1]),('zero',0,[])]:
        try:plan(total,res)
        except ValueError:rejected.append(label)
        else:raise AssertionError(label)
    dump(OUT/'exact_7_6m.json',exact);dump(OUT/'residual_7_73m.json',residual)
    dump(OUT/'validation.json',dict(status='PASS',reserved_span_source='exported gate-frame SOCKET_START/END',
        exact_plan='2m rail + 1.6m gate frame + 4m rail',protected_interval_overlap=0,negative_controls=rejected,
        scale_applied=False,engine_passage='NOT_RUN',gate_animation='NOT_IMPLEMENTED'))
    print('Gate reservation, residual preservation and overlap rejection: PASS')

if __name__=='__main__':main()
