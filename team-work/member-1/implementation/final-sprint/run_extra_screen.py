from pathlib import Path
import subprocess,json
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
for name in ('combined','search'):
 cmd=['./team-work/run-python.sh','team-work/member-3/implementation/run_comparison.py','--a',str((BASE/'candidates'/name/'agent.py').relative_to(ROOT)),'--b','shared-local/organizer-kit/examples/f_agent.py','--games','100','--seed0','938000','--chunk-size','20','--out',str((BASE/'screen'/name).relative_to(ROOT))]
 print('START '+name,flush=True)
 with (ROOT/f'shared-local/logs/b01-sprint-screen-{name}.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(json.dumps({'name':name,'summary':json.loads((BASE/'screen'/name/'summary.json').read_text())['a']}),flush=True)
