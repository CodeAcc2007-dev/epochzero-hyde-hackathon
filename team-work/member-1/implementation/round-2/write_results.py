"""Recompute all saved results before reporting the fixed v002 comparison."""
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,random,statistics,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
F='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check_run(folder):
 data=json.loads((folder/'games.json').read_text());s=json.loads((folder/'summary.json').read_text());m=json.loads((folder/'metadata.json').read_text())
 assert len(data)==500 and m['status']=='completed' and s['source_unchanged']
 assert m['games']==500 and m['seed0']==935000 and m['vps']==10
 assert m['process_lifecycle']=='Both agents reload every 20 games, sequential chunks; global indices preserved'
 assert m['clock']=={'base_s':.3,'increment_s':.0125,'max_s':1.5};assert set(m['b']['files'].values())=={F}
 for name,digest in m['a']['files'].items():assert sha(ROOT/name)==digest
 for i,row in enumerate(data):assert (row['game'],row['board_seed'],row['a_first'])==(i,935000+i//2,i%2==0)
 for side in ('a','b'):
  x=s[side];assert x['games']==500 and x['wins']==sum(r['winner']==side for r in data)
  assert x['no_winner']==sum(r['winner'] is None for r in data)
  assert abs(x['mean_cpu_s']-statistics.mean(r[side]['cpu_s'] for r in data))<1e-10
  assert x['worst_cpu_s']==max(r[side]['cpu_s'] for r in data)
  for key in ('errors','timeouts','crashes','random_moves'):assert x[key]==sum(r[side][key] for r in data)
  assert x['games_over_budget']==sum(r[side]['over'] is not None for r in data)
 assert s['cpu_p95_a_s']==sorted(r['a']['cpu_s'] for r in data)[474]
 return data,s,m

def paired(new,parent):
 diffs=[(int(new[i]['winner']=='a')+int(new[i+1]['winner']=='a')-int(parent[i]['winner']=='a')-int(parent[i+1]['winner']=='a'))/2 for i in range(0,500,2)]
 rng=random.Random(20261017);draws=sorted(statistics.mean(rng.choices(diffs,k=250)) for _ in range(2000))
 blocks=[statistics.mean(diffs[i:i+10]) for i in range(0,250,10)];rng=random.Random(20261018)
 chunks=sorted(statistics.mean(rng.choices(blocks,k=25)) for _ in range(2000))
 return {'degenerate_all_paired_differences_zero':all(d==0 for d in diffs),'bootstrap_limit':'A zero-width bootstrap when all observed differences are zero is not proof of equivalence or absence of rare effects.','win_difference':sum(r['winner']=='a' for r in new)-sum(r['winner']=='a' for r in parent),'difference_pp':100*statistics.mean(diffs),'pair_bootstrap_95_difference_pp':[100*draws[49],100*draws[1949]],'process_chunk_bootstrap_95_difference_pp':[100*chunks[49],100*chunks[1949]],'new_only_wins':sum(n['winner']=='a' and p['winner']!='a' for n,p in zip(new,parent)),'parent_only_wins':sum(p['winner']=='a' and n['winner']!='a' for n,p in zip(new,parent)),'scope':'Descriptive unadjusted whole-version comparison across two candidates. 250 board pairs and 25 process-reset chunks, 2000 resamples each. Timing/F process RNG and shared-host effects remain. No component causality or private-event guarantee.'}

def main():
 status=json.loads((BASE/'evaluation-status-main.json').read_text());assert status['status']=='completed' and len(status['completed'])==4
 subprocess.run(['./team-work/run-python.sh','team-work/member-1/implementation/round-2/audit_artifacts.py'],cwd=ROOT,check=True,capture_output=True)
 rows=[];details=[];result={};notes=[]
 for bot in ('B01','B02'):
  nd,ns,nm=check_run(BASE/'main'/f'{bot}-v002-new-vs-F-500');pd,ps,pm=check_run(BASE/'main'/f'{bot}-v001-parent-vs-F-500')
  assert [(r['game'],r['board_seed'],r['a_first']) for r in nd]==[(r['game'],r['board_seed'],r['a_first']) for r in pd]
  delta=paired(nd,pd);manifest=json.loads((ROOT/f'team-work/member-1/bots/{bot}/v002/manifest.json').read_text())
  assert sha(ROOT/nm['a']['entrypoint'])==manifest['agent_sha256'];n=ns['a'];p=ps['a'];lo,hi=delta['pair_bootstrap_95_difference_pp'];cl,ch=delta['process_chunk_bootstrap_95_difference_pp']
  result[bot]={'new_version':'v002','parent_version':'v001','new':ns,'parent':ps,'paired':delta,'new_metadata':str((BASE/'main'/f'{bot}-v002-new-vs-F-500/metadata.json').relative_to(ROOT)),'parent_metadata':str((BASE/'main'/f'{bot}-v001-parent-vs-F-500/metadata.json').relative_to(ROOT)),'manifest':manifest}
  rows.append(f"| {bot} v002 | {n['wins']}/500 ({100*n['win_rate']:.1f}%) | {p['wins']}/500 ({100*p['win_rate']:.1f}%) | {delta['difference_pp']:+.1f} pp [{lo:+.1f}, {hi:+.1f}] | {1000*n['mean_cpu_s']:.1f} / {1000*p['mean_cpu_s']:.1f} ms | {1000*ns['cpu_p95_a_s']:.0f} / {1000*n['worst_cpu_s']:.0f} ms |")
  ci=ns['uncertainty']['pair_bootstrap_95_descriptive']
  details.append(f"- **{bot}:** new win-rate descriptive range {100*ci[0]:.1f}%–{100*ci[1]:.1f}%; first-seat wins {ns['seat_a_first']['wins']}/250, second {ns['seat_a_second']['wins']}/250. New-only wins {delta['new_only_wins']}; parent-only wins {delta['parent_only_wins']}. No-winner counts new/parent {n['no_winner']}/{p['no_winner']}. Difference reset-chunk sensitivity range [{cl:+.1f}, {ch:+.1f}] pp. [New records](main/{bot}-v002-new-vs-F-500/games.json), [matched parent records](main/{bot}-v001-parent-vs-F-500/games.json).")
  if lo>0 and cl>0:interpretation='Both descriptive ranges favor v002 against F on this group; this does not establish component causality or private-event strength.'
  elif hi<0 and ch<0:interpretation='Both descriptive ranges favor v001 against F; v002 fixes the demonstrated defects but should not be promoted on strength from this batch.'
  else:interpretation='A win-rate gain is not established by both descriptive ranges. v002 is a correctness-repaired review candidate; do not call it stronger.'
  notes.append(f'- **{bot}:** {interpretation}')
 faults={}
 for bot,x in result.items():
  for version in ('new','parent'):
   for side in ('a','b'):faults[f'{bot}-{version}-{side}']={k:x[version][side][k] for k in ('errors','timeouts','crashes','games_over_budget','random_moves')}
 all_zero=all(v==0 for x in faults.values() for v in x.values());assert all_zero
 (BASE/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');(BASE/'fault-audit.json').write_text(json.dumps(faults,indent=2)+'\n')
 stamp=datetime.now(ZoneInfo('Asia/Calcutta')).isoformat()
 report=f'''# Aroosh B01/B02 v002: local upgrades and matched results

Completed {stamp} (India time). **Human verification pending; nothing published or submitted.** Frozen v001, earlier Member1 agents and research are preserved. Other members' frozen bot sources were not modified by this task.

Both bots now recognize the reproduced winning trade→Road sequence before strategic city-goal filtering and recognize immediate legal wins before the low-clock fallback. B01 retains its bottleneck economy policy and B02 its city/dev investment policy; no strategic coefficients, opening weights or search widths/depths were changed.

## Fresh frozen comparison

| Candidate | New vs unchanged F | Matched v001 vs F | Change [paired descriptive 95%] | Mean CPU new / parent | New p95 / max CPU |
| --- | --- | --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

All four 500-game runs recorded **zero errors, timeouts, crashes, clock overruns and harness random moves for both agents**. Every outcome was retained and the report independently recomputed wins, seats, CPU and fault counts from the individual records.

'''+ '\n'.join(details)+f'''

Both versions used the same 250 fresh boards **935000–935249**, swapped seats/global indices 0–499, ten VP and original cumulative clock: 300 ms + 12.5 ms/decision, maximum 1.5 s/game. Processes reload every twenty games, matching parent/candidate lifecycle; this differs from one uninterrupted official CLI run. F hash `{F}`. Kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`; engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Exact commands, source hashes, platform and lifecycle are in each metadata.json. [Hardware/harness audit](harness-and-hardware.json).

Two thousand main games = 500 per candidate + 500 per matched parent. Twelve ZIP/F/peer smoke games are separate. Two 100-action partial diagnostic histories did not finish games and are not pooled. No extra tournament, strategic ablation or event/private-O test. Source bytes were frozen before the first main game; this untouched first evaluation also serves as confirmation, and no tuning followed it.

Ranges resample the 250 board-pair win differences 2,000 times; the reset-chunk sensitivity range resamples 25 ten-pair process chunks. Both are descriptive and unadjusted across two candidates. If every observed paired difference is zero, the bootstrap collapses to [0, 0]; that does not prove equivalence or exclude unobserved rare differences. Time cutoffs, F persistent process RNG and a shared host affect replay/dependence. The preexisting Member3/4 evaluation was already running during early batches and was left untouched; timing is not an isolated hardware benchmark. Local F results on other groups are not an eight-bot ranking.

## Verification and accepted scope

- Fifteen new regression methods passed on frozen standalone files and again on exact ZIP-extracted modules. Nineteen original economic contracts passed against the new standalone classes, including the independent 18,225-case conversion oracle. The original parent nineteen also passed before repair; new regressions explicitly reproduce parent failures. [Semantic evidence](semantic-verification.json).
- New coverage includes both seats, reordered original action indices, immutable original and masked observations, low-clock city/settlement/Road/old-Knight wins, new-card eligibility, strict/owned Army, already-played dev, Road ties/longer rivals, bank/piece/blocking constraints, chance boundaries and an independent 96-fixture trade certificate oracle. These are constructed/counterfactual engine states, not claims of full reached histories. Full reached Road-cut/simultaneous-terminal acceptance remains open.
- Twelve complete forced-seven discard sequences had zero fixed-initial-goal oracle regret and no observed family switches, covering three hands and own/out-of-turn discards per bot. This bounded diagnostic does not establish globally optimal discards or justify new persistent memory. [Discard evidence](discard-diagnostics.json).
- The immediate selector copies at most twelve legal settlement/Road transitions, with cheap city/eligible Knight checks. Trade completion examines at most twelve relevant trades and forty-eight simulated actions, with a four millisecond deadline inside the existing budget. These caps leave cases unsearched; this is not exhaustive tactical search. Emergency timing excludes serialization/scorer hardware: [terminal profile](terminal-profile.json).
- Short external histories record internal counters/root coverage, but reached neither repair and observed no changed parent decisions. Main harness records do not expose per-decision internal cutoffs. Zero harness random moves is not a claim of zero internal fallback/cutoff decisions. [Diagnostics](diagnostics.json).
- Hyde GLM-5.3 Flash job `20261017T102336Z-a90a4d35` timed out after a read-permission/session error, produced no files and contributed no accepted revision. Primary completed and independently verified the tests. No provider switch or runtime LLM. [Exact job/review record](HYDE-REVIEW.md).

[Precommitted plan](PLAN-AND-DECISIONS.md), [ticket decisions and explicitly deferred hypotheses](VERIFICATION-AND-SCOPE.md), [source review](source-review.json). Broader multi-goal/re-export, city-payback and dev-stock tuning remain separate experiments; no gain is claimed for deferred work.

## Files and interpretation

- [B01 v002 agent](../../bots/B01/v002/agent.py), [manifest](../../bots/B01/v002/manifest.json), [ZIP](../../artifacts/B01-v002.zip).
- [B02 v002 agent](../../bots/B02/v002/agent.py), [manifest](../../bots/B02/v002/manifest.json), [ZIP](../../artifacts/B02-v002.zip).

Each ZIP contains only the exact standalone agent.py. CRC, hashes, development/frozen/extracted equality, clean loading, executable-AST assembly and actual extracted F smoke games passed. [Package checks](package-verification.json). Stdlib plus the pinned engine only; no key, data, environment, sibling module, network, worker or runtime logging.

'''+ '\n'.join(notes)+'''

Human acceptance remains pending. Do not overwrite either v001 or v002; future changes need a new version and fresh boards. No SSH, event portal action, automatic GitHub upload or publication occurred. [Preservation audit](preservation-verification.json) verifies original Member1 files and frozen runtime/research files while separately recording concurrent Member3/4 evidence/status and review-documentation updates by their existing work.

Reproduce through `./team-work/run-python.sh`; the main driver is `team-work/member-1/implementation/round-2/run_round.py --phase main`, which refuses existing outputs. New runs require new evidence paths/namespaces. `verify_semantics.py` checks both frozen and extracted forms; `audit_artifacts.py` and `write_results.py` recompute preservation/provenance and saved result validity. Keep raw provider sessions, dependencies and local logs out of Git.
'''
 (BASE/'BUILD-AND-RESULTS.md').write_text(report)
 print(json.dumps({b:{'new_wins':x['new']['a']['wins'],'parent_wins':x['parent']['a']['wins'],'paired':x['paired']} for b,x in result.items()},indent=2))
if __name__=='__main__':main()
