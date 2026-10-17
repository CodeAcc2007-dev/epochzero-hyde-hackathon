"""Sequential 500-game-per-bot main comparisons; no code changes or extra tournament."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent

def main():
    status={'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),'runs':[]}
    for bot in ('B01','B02'):
        source=BASE.parent/'bots'/bot/'v001/agent.py'
        manifest=json.loads((source.parent/'manifest.json').read_text())
        assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['agent_sha256']
        out=BASE/'results'/f'{bot}-v001-vs-F-500'
        log=ROOT/'shared-local/logs'/f'member1-{bot}-v001-vs-F-500.txt'
        command=['./team-work/run-python.sh','team-work/member-3/implementation/run_comparison.py',
                 '--a',str(source.relative_to(ROOT)),'--b','shared-local/organizer-kit/examples/f_agent.py',
                 '--games','500','--seed0','911000','--out',str(out.relative_to(ROOT))]
        print(json.dumps({'event':'starting','bot':bot,'games':500}),flush=True)
        with log.open('w') as stream:
            result=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['agent_sha256']
        row={'bot':bot,'exit_code':result.returncode,'command':command,'output':str(out.relative_to(ROOT))}
        if result.returncode==0:
            summary=json.loads((out/'summary.json').read_text());row['a']=summary['a'];row['f']=summary['b']
        status['runs'].append(row)
        (BASE/'evaluation-status.json').write_text(json.dumps(status,indent=2)+'\n')
        print(json.dumps(row),flush=True)
        if result.returncode:
            raise RuntimeError('Evaluation failed; preserve records and investigate')
    status.update(status='completed',completed_utc=datetime.now(timezone.utc).isoformat())
    (BASE/'evaluation-status.json').write_text(json.dumps(status,indent=2)+'\n')
if __name__=='__main__':main()
