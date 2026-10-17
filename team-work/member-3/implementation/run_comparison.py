#!/usr/bin/env python3
"""Sequential unchanged official-harness comparisons with full per-game records.

External experiment driver, never imported by competition bots. Even chunks reset
both processes; lifecycle and ordering are recorded, not hidden from the report.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import subprocess
import time

import catan_kit
from catan_kit import match
from catan_kit.evaluate import summarise

ROOT = Path(__file__).resolve().parents[3]


def artifact(path):
    path=path.resolve()
    files=[path] if path.name=='f_agent.py' else sorted(path.parent.glob('*.py'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    digest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    return {'entrypoint':str(path.relative_to(ROOT)),'files':hashes,'fingerprint':digest}


def intervals(records):
    pairs=[sum(r['winner']=='a' for r in records[i:i+2])/2 for i in range(0,len(records),2)]
    rng=random.Random(20261017)
    samples=sorted(sum(rng.choices(pairs,k=len(pairs)))/len(pairs) for _ in range(2000))
    p=statistics.mean(pairs)
    eps=math.sqrt(math.log(40)/(2*len(pairs)))
    return {'board_pairs':len(pairs),'pair_bootstrap_95_descriptive':[samples[49],samples[1949]],
            'hoeffding_95_independent_pairs':[max(0,p-eps),min(1,p+eps)],
            'assumptions':'Fixed nonadaptive policies, independent board pairs; lifecycle/chance sampling and timing can affect replay. Bootstrap is descriptive and degenerates at extremes.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--a',type=Path,required=True);p.add_argument('--b',type=Path,required=True)
    p.add_argument('--games',type=int,required=True);p.add_argument('--seed0',type=int,required=True)
    p.add_argument('--chunk-size',type=int,default=20);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    assert args.games>0 and args.games%2==0 and args.chunk_size>0 and args.chunk_size%2==0
    args.out.mkdir(parents=True,exist_ok=False)
    a,b=artifact(args.a),artifact(args.b)
    metadata={'started_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
              'platform':platform.platform(),'processor':platform.processor(),
              'repository_base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'a':a,'b':b,'games':args.games,'seed0':args.seed0,'vps':10,
              'kit_commit':subprocess.check_output(['git','-C',str(ROOT/'shared-local/organizer-kit'),'rev-parse','HEAD'],text=True).strip(),
              'engine_commit':'d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816',
              'process_lifecycle':f'Both agents reload every {args.chunk_size} games, sequential chunks; global indices preserved',
              'dice_key_id':'official-public-default; no private key/board prediction',
              'clock':{'base_s':match.CPU_BASE_S,'increment_s':match.CPU_PER_DECISION_S,'max_s':match.CPU_MAX_S},
              'command_arguments':{'a':str(args.a),'b':str(args.b),'games':args.games,'seed0':args.seed0,'chunk_size':args.chunk_size,'out':str(args.out)},
              'status':'running'}
    (args.out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    records=[];loads=[];start=time.monotonic()
    for offset in range(0,args.games,args.chunk_size):
        indices=list(range(offset,min(offset+args.chunk_size,args.games)))
        seeds=[args.seed0+i//2 for i in indices]
        chunk,load=match.play_chunk(str(args.a.resolve()),str(args.b.resolve()),seeds,indices,vps=10)
        records.extend(chunk);loads.append(load)
        (args.out/'games.json').write_text(json.dumps(records,indent=2)+'\n')
        metrics=summarise(records)
        print(json.dumps({'games_done':len(records),'wins':metrics['wins'],'over':metrics['games_over_budget'],
                          'errors':metrics['errors'],'timeouts':metrics['timeouts'],'crashes':metrics['crashes'],
                          'mean_cpu_s':metrics['mean_cpu_s'],'elapsed_s':round(time.monotonic()-start,2)}),flush=True)
    assert artifact(args.a)==a and artifact(args.b)==b, 'Source changed during experiment'
    summary={'a':summarise(records),'b':summarise(records,'b'),'uncertainty':intervals(records),
             'cpu_p95_a_s':sorted(r['a']['cpu_s'] for r in records)[math.ceil(.95*len(records))-1],
             'wall_elapsed_s':time.monotonic()-start,'loads':loads,'source_unchanged':True,
             'seat_a_first':{'games':sum(r['a_first'] for r in records),'wins':sum(r['a_first'] and r['winner']=='a' for r in records)},
             'seat_a_second':{'games':sum(not r['a_first'] for r in records),'wins':sum(not r['a_first'] and r['winner']=='a' for r in records)}}
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    metadata.update(status='completed',completed_utc=datetime.now(timezone.utc).isoformat())
    (args.out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':
    main()
