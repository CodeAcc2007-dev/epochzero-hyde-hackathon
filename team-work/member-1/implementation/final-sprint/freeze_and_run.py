from pathlib import Path
import json,hashlib,ast,subprocess
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
source=BASE/'candidates/menu/agent.py';dest=ROOT/'team-work/member-1/bots/B01/v003'
assert not dest.exists()
s=source.read_text();s=s.replace('final sprint development menu','standalone v003 flexible-purchase revision')
# Only the module docstring differs from the screened candidate.
assert [ast.dump(n,include_attributes=False) for n in ast.parse(s).body[1:]]==[ast.dump(n,include_attributes=False) for n in ast.parse(source.read_text()).body[1:]]
dest.mkdir(parents=True);(dest/'agent.py').write_text(s)
manifest={'bot':'B01','version':'v003','parent_version':'v002','parent_sha256':'cc53c58ca1867678ad6be9ca074ed6dabdffb54aa9b1c7ca1d83f52271c723f4','agent_sha256':hashlib.sha256((dest/'agent.py').read_bytes()).hexdigest(),'development_variant':'menu','development_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'executable_ast_equal_to_screened_candidate':True,'frozen_utc':datetime.now(timezone.utc).isoformat(),'changes':['Dynamic best feasible purchase goal','Monotone trades toward competitive alternatives with no-reexport preserved','One distinct action-family root within original width4','Bank and trade history included in continuation deduplication'],'clock_limits_unchanged':True,'kit_commit':'04fffac90e00610f60e0b06d919f262f4b3ed9db','engine_commit':'d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816','confirmation':'pending'}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
selection={'selected':'menu','reason':'Tied highest screen wins; prefer original opening and smaller search over extra changes without observed win gain. Screen alone does not establish improvement.','screen':{n:json.loads((BASE/'screen'/n/'summary.json').read_text())['a'] for n in ('parent','menu','opening','combined','search')},'frozen_manifest':manifest}
(BASE/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
status={'status':'running','completed':[]}
for name,path in [('candidate',dest/'agent.py'),('parent',ROOT/'team-work/member-1/bots/B01/v002/agent.py')]:
 cmd=['./team-work/run-python.sh','team-work/member-3/implementation/run_comparison.py','--a',str(path.relative_to(ROOT)),'--b','shared-local/organizer-kit/examples/f_agent.py','--games','500','--seed0','939000','--chunk-size','20','--out',str((BASE/'confirmation'/name).relative_to(ROOT))]
 status['active']=name;(BASE/'status.json').write_text(json.dumps(status,indent=2)+'\n')
 print('START '+name,flush=True)
 with (ROOT/f'shared-local/logs/b01-sprint-confirmation-{name}.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 summary=json.loads((BASE/'confirmation'/name/'summary.json').read_text());status['completed'].append({'name':name,'summary':summary})
 print(json.dumps({'name':name,'summary':summary['a']}),flush=True)
status.update(status='completed',active=None,finished_utc=datetime.now(timezone.utc).isoformat());(BASE/'status.json').write_text(json.dumps(status,indent=2)+'\n')
