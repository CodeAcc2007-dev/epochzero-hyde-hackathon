"""Sequential paired-seat frozen-candidate/parent F comparisons, original clock."""
import argparse,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
F='shared-local/organizer-kit/examples/f_agent.py'
def save(s):(BASE/f'evaluation-status-{s["phase"]}.json').write_text(json.dumps(s,indent=2)+'\n')
def run(label,a,b,games,seed,phase,s):
 out=BASE/phase/label;log=ROOT/f'shared-local/logs/member1-round2-{label}.txt';log.parent.mkdir(exist_ok=True)
 assert not out.exists() and not log.exists()
 cmd=['./team-work/run-python.sh','team-work/member-3/implementation/run_comparison.py','--a',a,'--b',b,'--games',str(games),'--seed0',str(seed),'--chunk-size','20' if games==500 else '4','--out',str(out.relative_to(ROOT))]
 s['active']=label;save(s);print(json.dumps({'starting':label,'games':games}),flush=True)
 with log.open('w') as stream:r=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(f'{label}: exit {r.returncode}, preserve evidence')
 summary=json.loads((out/'summary.json').read_text());assert summary['source_unchanged']
 s['completed'].append({'label':label,'command':cmd,'output':str(out.relative_to(ROOT)),'summary':summary});save(s)
 print(json.dumps({'completed':label,'wins':summary['a']['wins'],'mean_cpu_s':summary['a']['mean_cpu_s']}),flush=True)
 for side in ('a','b'):
  assert summary[side]['games']==games
  for key in ('errors','timeouts','crashes','games_over_budget','random_moves'):
   if summary[side][key]:raise RuntimeError(f'{label} {side} {key}={summary[side][key]}; investigate')
def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=('smoke','main'),required=True);a=p.parse_args()
 assert not (BASE/f'evaluation-status-{a.phase}.json').exists()
 s={'phase':a.phase,'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'completed':[]}
 if a.phase=='smoke':
  for b in ('B01','B02'):run(b+'-v002-zip-vs-F-4',f'shared-local/member1-round2-package-checks/{b}/agent.py',F,4,935800,'smoke',s)
  run('B01-v002-vs-B02-v002-4','team-work/member-1/bots/B01/v002/agent.py','team-work/member-1/bots/B02/v002/agent.py',4,935820,'smoke',s)
 else:
  assert json.loads((BASE/'evaluation-status-smoke.json').read_text())['status']=='completed'
  for b in ('B01','B02'):
   for v,kind in (('v001','parent'),('v002','new')):run(f'{b}-{v}-{kind}-vs-F-500',f'team-work/member-1/bots/{b}/{v}/agent.py',F,500,935000,'main',s)
 s.update(status='completed',active=None,completed_utc=datetime.now(timezone.utc).isoformat());save(s)
if __name__=='__main__':main()
