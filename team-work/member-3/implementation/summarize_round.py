#!/usr/bin/env python3
"""Verify retained records and summarize frozen Round1 comparisons; no games."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

BASE=Path(__file__).resolve().parent


def load(name,n):
    path=BASE/'results'/name
    meta=json.loads((path/'metadata.json').read_text())
    rows=json.loads((path/'games.json').read_text())
    summary=json.loads((path/'summary.json').read_text())
    assert meta['status']=='completed' and len(rows)==meta['games']==n
    assert summary['source_unchanged'] and sum(r['winner']=='a' for r in rows)==summary['a']['wins']
    assert len({r['game'] for r in rows})==n
    assert all(rows[i]['board_seed']==rows[i+1]['board_seed'] and rows[i]['a_first'] and not rows[i+1]['a_first'] for i in range(0,n,2))
    for side in ['a','b']:
        for f in ['errors','timeouts','crashes','random_moves']:
            assert sum(r[side][f] for r in rows)==summary[side][f]
        assert sum(r[side]['over'] is not None for r in rows)==summary[side]['games_over_budget']
    return rows,summary


def diff(a,b):
    assert len(a)==len(b)
    assert all((x['board_seed'],x['a_first'],x['game'])==(y['board_seed'],y['a_first'],y['game']) for x,y in zip(a,b))
    pairs=[(sum(r['winner']=='a' for r in a[i:i+2])-sum(r['winner']=='a' for r in b[i:i+2]))/2 for i in range(0,len(a),2)]
    rng=random.Random(8317)
    samples=sorted(statistics.mean(rng.choices(pairs,k=len(pairs))) for _ in range(4000))
    mean=statistics.mean(pairs);eps=math.sqrt(2*math.log(40)/len(pairs))
    return {'games_each':len(a),'board_pairs':len(pairs),'win_rate_difference':mean,
            'paired_bootstrap_95_descriptive':[samples[99],samples[3899]],
            'hoeffding_95_independent_pairs':[max(-1,mean-eps),min(1,mean+eps)],
            'caution':'Three exploratory comparisons; intervals unadjusted, no simultaneous superiority claim.'}


def main():
    a,sa=load('B05-v003-vs-F',1000);b,sb=load('B06-v003-vs-F',1000)
    control,sc=load('greedy-control-vs-F',400);head,sh=load('B05-vs-B06',200)
    report={'status':'completed','frozen_versions':{'B05':'v003','B06':'v003'},
      'main_comparisons':{'B05_vs_F':sa,'B06_vs_F':sb,'control_vs_F':sc,'B05_vs_B06':sh},
      'matched_board_differences':{'B05_minus_B06_vs_F':diff(a,b),
         'B05_minus_control_first400':diff(a[:400],control),'B06_minus_control_first400':diff(b[:400],control)},
      'records_total_main':len(a)+len(b)+len(control)+len(head),
      'evidence_sha256':{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted((BASE/'results').glob('*/*.json'))},
      'limits':['Local public-key boards only, no O/scorer result','20-game process chunks recorded','Pair intervals assume independent board groups','No main candidate code/weights tuned after final freeze']}
    (BASE/'ROUND-1-SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,s in report['main_comparisons'].items():
        print(name,s['a']['wins'],s['a']['games'],s['a']['mean_cpu_s'],s['a']['games_over_budget'],s['a']['errors'])
    print(json.dumps(report['matched_board_differences'],indent=2))


if __name__=='__main__':main()
