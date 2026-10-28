from pathlib import Path
import json
from export import export_glb
R=Path(__file__).resolve().parent
if __name__=='__main__':
    records=[]
    for name in ('chest','ore'):
        asset=json.loads((R/'sources'/f'{name}.json').read_text())
        raw,summary=export_glb(asset,animated=name=='chest');(R/'models'/f'{name}.glb').write_bytes(raw)
        records.append(dict(id=name,triangles=sum(len(p['faces']) for p in asset['components']),**summary))
    (R/'manifest.json').write_text(json.dumps(records,indent=2));print(records)
