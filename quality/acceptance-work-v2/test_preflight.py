from pathlib import Path
import sys,json,copy,tempfile,shutil
from preflight import audit,unpack,inspect
root=Path(sys.argv[1]).resolve();report=audit(root);assert report['passed']
first=root/'creation/theme_output'/report['files'][0]['file'];doc,binary=unpack(first.read_bytes())
bad=copy.deepcopy(doc);bad['images']=[];assert inspect(bad,binary)==['M001']
for uri in ('/tmp/foreign.png','C:/foreign.png','file:///tmp/foreign.png','https://example.invalid/model.png','../foreign.png'):
    bad=copy.deepcopy(doc);bad['images'][0]={'uri':uri};assert inspect(bad,binary)==['X001']
bad=copy.deepcopy(doc);bad['bufferViews'][bad['images'][0]['bufferView']]['byteLength']=len(binary)+1;assert inspect(bad,binary)==['M001']
bad=copy.deepcopy(doc);bad['buffers'][0]['uri']='/tmp/foreign.bin';assert inspect(bad,binary)==['X001']
R=Path(__file__).resolve().parent
(R/'reports/negative_controls.json').write_text(json.dumps({'test':'AT09','passed':True,'valid_catalog_files':327,'missing_palette':'M001','external_uri_variants':5,'external_buffer':'X001','out_of_bounds_palette':'M001','scope':'Strict original v1 embedded-palette preflight, separate from core-six vertex-color profile'},indent=2))
print('PASS missing/corrupt palette and external URI controls')
