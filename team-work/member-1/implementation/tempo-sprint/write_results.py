"""Audit complete saved matches, compute paired differences and write the decision."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,random,statistics,math
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
F='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'
def read(folder):
 d=BASE/folder;r=json.loads((d/'games.json').read_text());s=json.loads((d/'summary.json').read_text());m=json.loads((d/'metadata.json').read_text())
 assert len(r)==500 and m['status']=='completed' and s['source_unchanged']
 assert [x['game'] for x in r]==list(range(500))
 assert all(x['board_seed']==945000+x['game']//2 and x['a_first']==(x['game']%2==0) for x in r)
 assert list(m['b']['files'].values())==[F]
 for agent in (m['a'],m['b']):
  for path,sha in agent['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
 for side in ('a','b'):
  assert sum(x['winner']==side for x in r)==s[side]['wins']
  for field in ('errors','timeouts','crashes','random_moves'):assert sum(x[side][field] for x in r)==s[side][field]
  assert sum(bool(x[side]['over']) for x in r)==s[side]['games_over_budget']
  assert math.isclose(statistics.mean(x[side]['cpu_s'] for x in r),s[side]['mean_cpu_s'])
 return r,s,m
def bootstrap(values):
 rng=random.Random(1743);draws=sorted(statistics.mean(rng.choices(values,k=len(values)))*100 for _ in range(4000));return [draws[99],draws[3899]]
n,ns,nm=read('candidate-vs-F');p,ps,pm=read('parent-vs-F')
diff=[int(a['winner']=='a')-int(b['winner']=='a') for a,b in zip(n,p)]
ci=bootstrap([sum(diff[i:i+2])/2 for i in range(0,500,2)])
chunk=bootstrap([sum(diff[i:i+20])/20 for i in range(0,500,20)])
faults=sum(s[side][k] for s in (ns,ps) for side in ('a','b') for k in ('errors','timeouts','crashes','random_moves','games_over_budget','no_winner'))
recommend='v005' if faults==0 and ci[0]>0 else 'v004'
v=json.loads((BASE/'verification.json').read_text());assert all(x['terminal_passed'] and x['economic_passed'] and x['extra_passed'] for x in v['verification'].values())
record={'finished_utc':datetime.now(timezone.utc).isoformat(),'candidate':ns['a'],'parent':ps['a'],'difference_pp':statistics.mean(diff)*100,'paired_board_bootstrap_95_pp':ci,'reset_chunk_bootstrap_95_pp':chunk,'candidate_only_wins':sum(a['winner']=='a' and b['winner']!='a' for a,b in zip(n,p)),'parent_only_wins':sum(a['winner']!='a' and b['winner']=='a' for a,b in zip(n,p)),'candidate_first_seat_wins':sum(x['a_first'] and x['winner']=='a' for x in n),'candidate_second_seat_wins':sum(not x['a_first'] and x['winner']=='a' for x in n),'all_fault_counter_sum':faults,'recommended_version':recommend,'agent_sha256':v['agent_sha256'],'zip_sha256':v['zip_sha256'],'seed0':945000,'games_per_bot':500,'records_sha256':{x:hashlib.sha256((BASE/x/'games.json').read_bytes()).hexdigest() for x in ('candidate-vs-F','parent-vs-F')}}
(BASE/'results.json').write_text(json.dumps(record,indent=2)+'\n')
a,b=ns['a'],ps['a']
text=f'''# B01 eight-minute experiment: production-aware purchase priorities

Completed {record['finished_utc']}. **Recommendation: B01 {recommend}.**

| Exact frozen source | Wins against unchanged F | Mean CPU / game | Maximum CPU / game |
|---|---:|---:|---:|
| New v005 | {a['wins']}/500 ({100*a['win_rate']:.1f}%) | {1000*a['mean_cpu_s']:.1f} ms | {1000*a['worst_cpu_s']:.0f} ms |
| Matched v004 | {b['wins']}/500 ({100*b['win_rate']:.1f}%) | {1000*b['mean_cpu_s']:.1f} ms | {1000*b['worst_cpu_s']:.0f} ms |

Difference: {record['difference_pp']:+.1f} percentage points; paired-board bootstrap 95% interval [{ci[0]:+.1f}, {ci[1]:+.1f}] points. Reset-chunk sensitivity interval: [{chunk[0]:+.1f}, {chunk[1]:+.1f}]. Candidate-only wins: {record['candidate_only_wins']}; parent-only wins: {record['parent_only_wins']}. New bot seat wins: {record['candidate_first_seat_wins']}/250 first, {record['candidate_second_seat_wins']}/250 second. Aggregate errors, crashes, timeouts, random fallback moves, budget overruns and no-winner counters across both sides of both runs: {faults}.

The predeclared promotion gate requires zero faults and a positive lower paired-board interval. {'The gate passed on these local games; this is not a guarantee against other opponents or on the scorer host.' if recommend=='v005' else 'The gate did not pass. A strength improvement is not established; retain v004 for submission. v005 remains an experimental alternative, not the recommended replacement.'} No parameter sweep or additional matches followed the result.

## Different strategy tested

v005 discounts readiness for a purchase whose missing ingredients have slow public production. Other-resource production contributes an optimistic maritime conversion rate; existing conversion credits reduce each bottleneck. A capped multiplier in [0.625, 1] limits the change. Currently affordable or bank-convertible goals retain full value. This is a fluid heuristic, not an exact expected completion time: it ignores dice correlation, competition among simultaneous conversion requirements and future bank changes. The exact bank-aware base score still applies. Opening, tactical win certificates, legal trade guards and search caps are inherited unchanged from v004. [AST scope audit](source-diff-audit.json) confirms only the new helper and `EconomyContext.priority` changed. The inherited module docstring still says v004; the v005 directory, manifest and exact digest identify this frozen experiment.

## Verification and limits

47 regression/contract methods passed on the exact frozen module and again on the ZIP-extracted module: 15 terminal, 18 economic, 4 earlier strategy, 6 road-certificate and 4 new production tests. The economic suite includes exhaustive conversion-oracle cases. Original v004 and F hashes are unchanged. ZIP contains exactly the tested agent.py; CRC and byte equality passed. Imports remain math/random/time and the pinned catanatron engine. [Verification](verification.json), [test runner](verify.py), [Hyde review](HYDE-REVIEW.md).

Each bot played 500 games on the same fresh 250 boards 945000–945249, both seats, with module/process lifecycle resets every 20 games. Original clock: min(0.300 + 0.0125 × decisions, 1.500) seconds per game. The two match processes ran concurrently on a shared host; process CPU is measured, but hardware timing and search cutoffs need not reproduce exactly. These are local F comparisons, not an official tournament or direct v005-v004 match. Uncertainty is descriptive and clustered by board, with reset-chunk sensitivity. Historical 78% belongs to other boards and is not the matched baseline here.

[Candidate raw games](candidate-vs-F/games.json), [parent raw games](parent-vs-F/games.json), [candidate metadata/command](candidate-vs-F/metadata.json), [parent metadata/command](parent-vs-F/metadata.json), [audited comparison](results.json).

[Recommended agent](../../bots/B01/{recommend}/agent.py). [Experimental v005 agent](../../bots/B01/v005/agent.py), [v005 ZIP](../../artifacts/B01-v005.zip). Candidate SHA256 `{v['agent_sha256']}`.

All work reused the existing local environment. No SSH, event submission, downloaded dataset, environment or secret upload. Hyde drafted a small arithmetic review; the primary corrected two claims and independently implemented and verified the experiment. Preserve all frozen versions; future experiments require new versions and evidence.
'''
(BASE/'RESULTS.md').write_text(text)
p=ROOT/'team-work/member-1/bots/B01/v005'
manifest={'bot':'B01','version':'v005','parent_version':'v004','parent_sha256':'a0ed4450b3aa23eff97ab44fbe185e2d089ddc9516a1703e4b483389ed8ff2fb','agent_sha256':v['agent_sha256'],'zip_sha256':v['zip_sha256'],'changes':['Bounded production-aware purchase readiness multiplier'],'confirmation':'completed','confirmation_seed0':945000,'confirmation_games':500,'confirmation_wins':a['wins'],'matched_parent_wins':b['wins'],'recommended':recommend=='v005','kit_commit':'04fffac90e00610f60e0b06d919f262f4b3ed9db','engine_commit':'d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816'}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(p/'README.md').write_text(f"# B01 v005 — production-aware experiment\n\n[Full verified results](../../../implementation/tempo-sprint/RESULTS.md). Scored {a['wins']}/500 against unchanged F; matched v004 scored {b['wins']}/500. Recommended version remains **{recommend}** under the predeclared confidence gate.\n\nSHA256 `{v['agent_sha256']}`. [ZIP](../../../artifacts/B01-v005.zip) contains only this exact standalone agent.py. Preserve this frozen version.\n")
print(json.dumps(record,indent=2))
