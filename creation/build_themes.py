"""Replace only embedded palette bytes; preserve geometry and socket nodes."""
from pathlib import Path
import json,struct,hashlib,io,shutil
import numpy as np
from PIL import Image
from build_rocks import COLORS,dump
from verify_glb import load_glb

ROOT=Path(__file__).parent;OUT=ROOT/'theme_output'
PALETTES={
 'MOSS_01':COLORS,
 'DRY_01':[
 '423326','715439','A07A4E','D5B785','574629','88703B','B59B53','D4C27D',
 '504C45','797366','A49B85','B29B78','62502C','958045','BDA15C','C9B887',
 '493526','82603D','B38D5E','DBBC8D','625342','34312B','746E5D','D3CAB5',
 'A4764F','C5A071','6C4B32','A49D7C','625342','34312B','746E5D','D3CAB5'],
 'DUSK_01':[
 '38303D','594C62','83718A','B6A0B3','303B4E','4C5C70','788A93','A9B1B0',
 '414452','666D7D','9299A7','8A8094','414459','666B85','9295A6','ADA6B8',
 '3C303F','68516B','937793','C1A1B7','514757','2B2C38','626777','BABCC8',
 '89677F','B394A8','574459','89899E','514757','2B2C38','626777','BABCC8']}

def png(colors):
    image=Image.new('RGB',(256,256))
    for i,color in enumerate(colors):image.paste(tuple(bytes.fromhex(color)),((i%8)*32,(i//8)*64,(i%8+1)*32,(i//8+1)*64))
    stream=io.BytesIO();image.save(stream,format='PNG');return stream.getvalue()

def replace(data,palette,theme):
    jl=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+jl]);blob=data[28+jl:]
    view_index=doc['images'][0]['bufferView'];view=doc['bufferViews'][view_index]
    assert view_index==len(doc['bufferViews'])-1
    off=view.get('byteOffset',0)
    assert off+view['byteLength']==doc['buffers'][0]['byteLength']
    geometry=blob[:off];nodes=json.dumps(doc['nodes'],sort_keys=True).encode()
    blob=geometry+palette;view['byteLength']=len(palette);doc['buffers'][0]['byteLength']=len(blob)
    doc['images'][0]['name']=theme;doc['extras']['palette_id']=theme
    raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);blob+=b'\0'*((-len(blob))%4)
    result=struct.pack('<4sII',b'glTF',2,28+len(raw)+len(blob))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(blob),b'BIN\0')+blob
    return result,hashlib.sha256(geometry).hexdigest(),hashlib.sha256(nodes).hexdigest()

def main():
    sources=[]
    for folder in ['output','trees_output_v2','fences_output','wood_props_output','vegetation_output','camp_props_output','path_props_output','furniture_props_output','wood_modules_output','stone_modules_output','natural_catalog_output','lod_output']:
        sources.extend(sorted((ROOT/folder/'models').glob('*.glb')))
    sources.append(ROOT/'fences_output/fixtures/TW_TERMINAL_POST.glb')
    if len(sources)<31 or not all(p.exists() for p in sources):
        sources=sorted((ROOT.parent/'standalone_assets/MOSS_01/models').glob('*.glb'))
    assert len(sources)>=31 and len({p.name for p in sources})==len(sources)
    lod1_count=sum('_LOD1' in p.stem for p in sources)
    unique_count=sum('_LOD0' in p.stem for p in sources)
    manifest=[]
    for theme,colors in PALETTES.items():
        palette=png(colors);path=OUT/'palettes'/f'{theme}.png';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(palette)
        for source in sources:
            target=OUT/theme/'models'/source.name;target.parent.mkdir(parents=True,exist_ok=True)
            data,geometry_hash,socket_hash=replace(source.read_bytes(),palette,theme);target.write_bytes(data)
            old=load_glb(source);new=load_glb(target)
            for key in ['positions','normals','uv','indices']:assert np.array_equal(old[key],new[key])
            assert old['doc']['nodes']==new['doc']['nodes'] and old['doc']['materials']==new['doc']['materials']
            assert new['png']==palette
            manifest.append(dict(file=str(target.relative_to(OUT)),theme=theme,model=source.stem,triangles=len(new['indices'])//3,geometry_buffer_sha256=geometry_hash,nodes_sha256=socket_hash,sha256=hashlib.sha256(data).hexdigest()))
    for name in {x['model'] for x in manifest}:
        group=[x for x in manifest if x['model']==name]
        assert len({x['geometry_buffer_sha256'] for x in group})==1 and len({x['nodes_sha256'] for x in group})==1
    dump(OUT/'manifest.json',dict(unique_models=unique_count,lod1_variants=lod1_count,terminal_fixtures=1,themes=3,glb_files=len(manifest),entries=manifest))
    dump(OUT/'validation.json',dict(status='PASS',geometry_uv_normals_indices_unchanged=True,sockets_unchanged=True,materials_unchanged=True,files_checked=len(manifest),art_approval='PENDING'))
    dump(OUT/'palettes/palette_slots.json',dict(slot_order='8 columns x 4 rows; same UV centers across themes',palettes=PALETTES))
    project=ROOT.parent/'trailwood_godot'
    if project.exists():
        (project/'palettes').mkdir(exist_ok=True)
        for path in (OUT/'palettes').glob('*.png'):shutil.copyfile(path,project/'palettes'/path.name)
    render();print(f'{len(manifest)} GLBs / {unique_count} unique models / 3 themes: geometry and sockets unchanged')

def render():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    names=['TW_TREE_ROUND_SMALL_A_LOD0','TW_ROCK_UPRIGHT_A_LOD0','TW_STUMP_CUT_SMALL_A_LOD0','TW_GRASS_TALL_A_LOD0']
    fig=plt.figure(figsize=(12,13),facecolor='#eeeae2')
    for row,name in enumerate(names):
        for col,theme in enumerate(PALETTES):
            m=load_glb(OUT/theme/'models'/f'{name}.glb');v=m['positions'][:,[0,2,1]]*np.array([1,-1,1]);f=m['indices'].reshape(-1,3);uv=m['uv'][f[:,0]]
            colors=np.array(m['image'].convert('RGB'))[(uv[:,1]*256).astype(int),(uv[:,0]*256).astype(int)]/255
            ax=fig.add_subplot(4,3,row*3+col+1,projection='3d');ax.add_collection3d(Poly3DCollection(v[f],facecolors=colors,edgecolors='none'))
            mid=(v.min(0)+v.max(0))/2;half=np.ptp(v,axis=0).max()*.55
            ax.set(xlim=(mid[0]-half,mid[0]+half),ylim=(mid[1]-half,mid[1]+half),zlim=(mid[2]-half,mid[2]+half),title=theme if row==0 else '')
            ax.set_box_aspect((1,1,1));ax.view_init(25,-55);ax.set_axis_off()
    fig.suptitle('TRAILWOOD / Moss - Dry - Dusk\nIdentical geometry, palette variants',fontsize=18)
    fig.tight_layout(rect=(0,0,1,.94));fig.savefig(OUT/'theme_preview.png',dpi=145);plt.close(fig)

if __name__=='__main__':main()
