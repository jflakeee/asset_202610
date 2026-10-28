"""Required preflight followed by the existing gate; never upgrades approval state."""
from pathlib import Path
import argparse,json,subprocess,sys
from preflight import audit
p=argparse.ArgumentParser();p.add_argument('repository',type=Path);p.add_argument('--channel',choices=('review','sales'),default='review');a=p.parse_args();root=a.repository.resolve();out=Path(__file__).resolve().parent/'reports'
r=audit(root);(out/'gated_preflight.json').write_text(json.dumps(r,indent=2))
if not r['passed']:
    print('BLOCKED: embedded palette/file-integrity preflight');sys.exit(2)
result=subprocess.run([sys.executable,str(root/'creation/release_gate.py'),'--channel',a.channel,'--out',str(out/'legacy_gate.json')])
sys.exit(result.returncode)
