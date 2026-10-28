"""Original v1 embedded-palette contract. No external URIs are allowed in this profile."""
from pathlib import Path,PurePosixPath
import argparse,json,struct,hashlib,copy,io
from PIL import Image

def unpack(raw):
    if len(raw)<28 or struct.unpack_from('<4sII',raw)!=(b'glTF',2,len(raw)):raise ValueError('G001')
    n,t=struct.unpack_from('<I4s',raw,12)
    if t!=b'JSON':raise ValueError('G001')
    doc=json.loads(raw[20:20+n]);length,kind=struct.unpack_from('<I4s',raw,20+n)
    if kind!=b'BIN\0' or 28+n+length!=len(raw):raise ValueError('G001')
    return doc,raw[28+n:]

def inspect(doc,binary):
    # This deliberately stricter v1 profile forbids even relative/data URIs.
    if any('uri' in x for k in ('images','buffers') for x in doc.get(k,[])):return ['X001']
    if len(doc.get('images',[]))!=1:return ['M001']
    try:
        image=doc['images'][0]
        if image.get('mimeType')!='image/png':return ['M001']
        view=doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0);end=start+view['byteLength']
        if view.get('buffer',0)!=0 or start<0 or end>len(binary):return ['M001']
        with Image.open(io.BytesIO(binary[start:end])) as im:
            im.verify()
    except (KeyError,IndexError,TypeError,OSError,ValueError,Image.DecompressionBombError):return ['M001']
    return []

def audit(root):
    theme=root/'creation/theme_output';manifest=json.loads((theme/'manifest.json').read_text());results=[]
    for entry in manifest['entries']:
        rel=PurePosixPath(entry['file'])
        if rel.is_absolute() or '..' in rel.parts or ':' in str(rel) or '\\' in str(rel):results.append({'file':str(rel),'errors':['X001']});continue
        path=theme/str(rel);errors=[]
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p!=theme.parent):
            results.append({'file':str(rel),'errors':['X001']});continue
        if not path.is_file():results.append({'file':str(rel),'errors':['M001']});continue
        raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha!=entry['sha256']:errors.append('H001')
        try:
            doc,binary=unpack(raw);errors+=inspect(doc,binary)
        except (ValueError,KeyError,struct.error,json.JSONDecodeError):errors.append('G001')
        results.append({'file':str(rel),'sha256':sha,'errors':sorted(set(errors))})
    assert len(results)==327,'Unexpected catalog size; review this fixed profile before changing count'
    return {'profile':'TW_V1_EMBEDDED_PALETTE','passed':all(not x['errors'] for x in results),'files':results}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('repository',type=Path);p.add_argument('--out',type=Path,default=Path(__file__).parent/'reports/preflight.json');a=p.parse_args()
    r=audit(a.repository.resolve());a.out.write_text(json.dumps(r,indent=2));print('PREFLIGHT',r['passed'],len(r['files']));raise SystemExit(0 if r['passed'] else 2)
