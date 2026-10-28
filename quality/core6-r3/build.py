"""Re-export art pass 2 without changing its geometry or material profiles."""
from pathlib import Path
import argparse,json
from export import export_glb
R=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=R.parent/'core6-r2');args=p.parse_args()
    previous=json.loads((args.source/'manifest.json').read_text());records=[]
    (R/'models').mkdir(exist_ok=True)
    for record in previous:
        a=json.loads((args.source/'sources'/f"{record['id']}.json").read_text())
        raw,summary=export_glb(a,animated=record['animated'])
        (R/'models'/f"{record['id']}.glb").write_bytes(raw)
        records.append(dict(id=record['id'],triangles=record['triangles'],**summary))
    (R/'manifest.json').write_text(json.dumps(records,indent=2));print(records)
