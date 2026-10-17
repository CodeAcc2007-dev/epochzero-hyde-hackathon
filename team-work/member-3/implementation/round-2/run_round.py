"""Sequential original-clock evaluation: frozen new artifacts and matched parents."""
import argparse, hashlib, json, subprocess
from datetime import datetime,timezone
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
F='shared-local/organizer-kit/examples/f_agent.py'
BOTS={'B05':(3,'v004','v003'),'B06':(3,'v004','v003'),'B07':(4,'v002','v001'),'B08':(4,'v002','v001')}

def entry(bot,new=True):
    member,version,parent=BOTS[bot]
    return f'team-work/member-{member}/bots/{bot}/{version if new else parent}/agent.py'

def run(label,a,b,games,seed,member,phase,status):
    base=ROOT/f'team-work/member-{member}/implementation/round-2'
    out=base/phase/label
    log=ROOT/f'shared-local/logs/round2-{label}.txt'
    assert not out.exists() and not log.exists(),'Refuse to replace evidence'
    cmd=['./team-work/run-python.sh','team-work/member-3/implementation/run_comparison.py','--a',a,'--b',b,'--games',str(games),'--seed0',str(seed),'--chunk-size','20' if games==500 else '4','--out',str(out.relative_to(ROOT))]
    status.update(active=label)
    save(status)
    print(json.dumps({'event':'starting','label':label,'games':games,'seed0':seed}),flush=True)
    with log.open('w') as stream:result=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{label}: exit {result.returncode}; preserve log/evidence')
    summary=json.loads((out/'summary.json').read_text())
    assert summary['source_unchanged']
    for side in ('a','b'):
        assert summary[side]['games']==games
        for k in ('errors','timeouts','crashes','games_over_budget','random_moves'):
            if summary[side][k]:raise RuntimeError(f'{label}: {side} {k}={summary[side][k]}; investigate before continuing')
    row={'label':label,'command':cmd,'output':str(out.relative_to(ROOT)),'a':summary['a'],'b':summary['b']}
    status['completed'].append(row);save(status)
    print(json.dumps({'event':'completed','label':label,'games':games,'a_wins':summary['a']['wins'],'mean_cpu_s':summary['a']['mean_cpu_s'],'faults':0}),flush=True)

def save(status):
    for member in (3,4):
        (ROOT/f'team-work/member-{member}/implementation/round-2'/('evaluation-status-'+status['phase']+'.json')).write_text(json.dumps(status,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('smoke','main'),required=True);args=p.parse_args()
    status={'phase':args.phase,'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'completed':[]}
    if args.phase=='smoke':
        for bot,(member,version,_) in BOTS.items():run(bot+'-'+version+'-zip-vs-F-4',f'shared-local/round2-package-checks/{bot}/agent.py',F,4,933800,member,'smoke',status)
        for member,a,b in ((3,'B05','B06'),(4,'B07','B08')):run(a+'-vs-'+b+'-4',entry(a),entry(b),4,933820,member,'smoke',status)
    else:
        smoke=json.loads((BASE/'evaluation-status-smoke.json').read_text());assert smoke['status']=='completed'
        for bot,(member,version,parent) in BOTS.items():
            run(bot+'-'+parent+'-parent-vs-F-500',entry(bot,False),F,500,934000,member,'main',status)
            run(bot+'-'+version+'-new-vs-F-500',entry(bot),F,500,934000,member,'main',status)
    status.update(status='completed',active=None,completed_utc=datetime.now(timezone.utc).isoformat());save(status)
    print(json.dumps({'status':'completed','phase':args.phase,'runs':len(status['completed'])}),flush=True)
if __name__=='__main__':main()
