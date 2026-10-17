"""Two common-board F runs only; frozen artifacts, no source changes."""
from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
index=json.loads((BASE/'source-index.json').read_text())
status={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'completed':[]}
for bot in ('B01','B02'):
 x=index[bot];out=ROOT/x['common_result'];log=ROOT/f'shared-local/logs/common-F-20261017-{bot}.txt'
 assert not out.exists() and not log.exists()
 assert hashlib.sha256((ROOT/x['entrypoint']).read_bytes()).hexdigest()==x['sha256']
 cmd=['./team-work/run-python.sh','team-work/member-3/implementation/run_comparison.py','--a',x['entrypoint'],'--b','shared-local/organizer-kit/examples/f_agent.py','--games','500','--seed0','934000','--chunk-size','20','--out',str(out.relative_to(ROOT))]
 status['active']=bot;(BASE/'status.json').write_text(json.dumps(status,indent=2)+'\n')
 print(json.dumps({'starting':bot,'games':500}),flush=True)
 with log.open('w') as stream:result=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError(f'{bot}: failure; preserve records')
 s=json.loads((out/'summary.json').read_text());assert s['source_unchanged'] and s['a']['games']==500
 for side in ('a','b'):
  for key in ('errors','timeouts','crashes','games_over_budget','random_moves'):assert s[side][key]==0,(bot,side,key)
 status['completed'].append({'bot':bot,'command':cmd,'summary':s});(BASE/'status.json').write_text(json.dumps(status,indent=2)+'\n')
 print(json.dumps({'completed':bot,'wins':s['a']['wins'],'cpu_s':s['a']['mean_cpu_s']}),flush=True)
status.update(status='completed',active=None,completed_utc=datetime.now(timezone.utc).isoformat());(BASE/'status.json').write_text(json.dumps(status,indent=2)+'\n')
print('Completed both new common-board F runs.',flush=True)
