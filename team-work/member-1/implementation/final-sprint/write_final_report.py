"""Independently audit saved outcomes and write the sprint handoff; no matches."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,random,statistics,math,re
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
F='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'

def readable(text):
 text=re.sub(r'(?<=\d)(ms|pp|VP|games|wins|calls|copied|enabling|intermediate|main|development|separate|boards|minutes)\b',r' \1',text)
 text=re.sub(r'\b(boards|wins|from|every|within|depth|width|before|CPU|maximum|about|max|All|on|plus|only|new|old|level)(?=\d)',r'\1 ',text)
 text=text.replace('budget:25','budget: 25').replace('to11:16:45UTC','to 11:16:45 UTC').replace('10:51:45UTC','10:51:45 UTC')
 text=text.replace('shared-host','shared host')
 for a,b in {'bootstrap95%':'bootstrap 95%', 'range[':'range [','sensitivity[':'sensitivity [',']pp':'] pp',',+':', +','tenVP,250':'10 VP, 250','the25':'the 25','The85%':'The 85%','The78%':'The 78%','used100':'used 100','parent75':'parent 75','menu77':'menu 77','combined77':'combined 77','search77':'search 77','constructed8':'constructed 8','length3':'length 3','hand(':'hand (','winning.4ORE':'winning. 4 ORE','to80':'to 80',',12 enabling':', 12 enabling',',8 intermediate':', 8 intermediate','an8':'an 8','v003:37':'v003: 37','v004:43':'v004: 43',',18 inherited':', 18 inherited',',4 sprint':', 4 sprint',',6 new':', 6 new','for100':'for 100','and0.95':'and 0.95','host,10':'host, 10','preserved78%':'preserved 78%','historical934000':'historical 934000','2,000F':'2,000 F','500direct':'500 direct', '),500 development':'), 500 development','and4 separate':'and 4 separate'}.items():text=text.replace(a,b)
 return text

def read_run(folder,seed,opponent_hash=F):
 records=json.loads((folder/'games.json').read_text());summary=json.loads((folder/'summary.json').read_text());meta=json.loads((folder/'metadata.json').read_text())
 assert len(records)==500 and meta['status']=='completed' and summary['source_unchanged']
 assert [r['game'] for r in records]==list(range(500))
 assert all(r['board_seed']==seed+r['game']//2 and r['a_first']==(r['game']%2==0) for r in records)
 for side in ('a','b'):
  for field in ('errors','timeouts','crashes','random_moves'):assert sum(r[side][field] for r in records)==0
  assert sum(bool(r[side]['over']) for r in records)==0
  assert sum(r['winner']==side for r in records)==summary[side]['wins']
  assert math.isclose(statistics.mean(r[side]['cpu_s'] for r in records),summary[side]['mean_cpu_s'])
 assert not any(r['winner'] not in ('a','b') for r in records)
 assert list(meta['b']['files'].values())==[opponent_hash]
 for artifact in (meta['a'],meta['b']):
  for path,sha in artifact['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
 return records,summary,meta

def bootstrap(values):
 rng=random.Random(1743)
 draws=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(4000))
 return [draws[99]*100,draws[3899]*100]

comparisons={}
for version,directory,seed in [('v003','confirmation',939000),('v004','tactical-confirmation',943000)]:
 n,ns,nm=read_run(BASE/directory/'candidate',seed);p,ps,pm=read_run(BASE/directory/'parent',seed)
 diff=[int(a['winner']=='a')-int(b['winner']=='a') for a,b in zip(n,p)]
 pairs=[sum(diff[i:i+2])/2 for i in range(0,500,2)]
 chunks=[sum(diff[i:i+20])/20 for i in range(0,500,20)]
 comparison={'version':version,'seed0':seed,'candidate':ns['a'],'baseline':ps['a'],'difference_pp':statistics.mean(diff)*100,'paired_board_bootstrap_95_pp':bootstrap(pairs),'reset_chunk_bootstrap_95_pp':bootstrap(chunks),'candidate_only_wins':sum(a['winner']=='a' and b['winner']!='a' for a,b in zip(n,p)),'parent_only_wins':sum(a['winner']!='a' and b['winner']=='a' for a,b in zip(n,p)),'candidate_first_seat_wins':sum(r['a_first'] and r['winner']=='a' for r in n),'candidate_second_seat_wins':sum(not r['a_first'] and r['winner']=='a' for r in n),'candidate_p95_cpu_s':sorted(r['a']['cpu_s'] for r in n)[474],'candidate_source_sha256':next(iter(nm['a']['files'].values())),'records_sha256':{x:hashlib.sha256((BASE/directory/x/'games.json').read_bytes()).hexdigest() for x in ('candidate','parent')}}
 comparisons[version]=comparison
 manifest_path=ROOT/f'team-work/member-1/bots/B01/{version}/manifest.json';manifest=json.loads(manifest_path.read_text());manifest['confirmation']='completed';manifest['confirmation_seed0']=seed;manifest['confirmation_games']=500;manifest['confirmation_wins']=ns['a']['wins'];manifest['matched_v002_wins']=ps['a']['wins'];manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')

direct,ds,dm=read_run(BASE/'direct-v004-vs-v002',944000,'cc53c58ca1867678ad6be9ca074ed6dabdffb54aa9b1c7ca1d83f52271c723f4')
direct_pairs=[sum(r['winner']=='a' for r in direct[i:i+2])/2 for i in range(0,500,2)]
direct_result={'candidate':ds['a'],'baseline':ds['b'],'seed0':944000,'board_bootstrap_95_win_rate_percent':bootstrap(direct_pairs),'records_sha256':hashlib.sha256((BASE/'direct-v004-vs-v002/games.json').read_bytes()).hexdigest()}
v=comparisons['v004'];recommended='v004' if v['candidate']['wins']>=v['baseline']['wins'] and ds['a']['wins']>=250 else 'v002'
record={'finished_utc':datetime.now(timezone.utc).isoformat(),'comparisons':comparisons,'direct_comparison':direct_result,'recommended_version':recommended,'recommendation_rule':'Prefer the correctness-repaired final v004 when its fault-free fresh F point estimate is at least baseline and it scores at least250/500 directly against v002; otherwise retain v002 for submission. Point-estimate selection is not a proof of superiority.','main_games':2500,'development_games':500,'separate_zip_smoke_games':4,'no_event_submission':True}
(BASE/'final-results.json').write_text(json.dumps(record,indent=2)+'\n')
lines=['# B01 final improvement sprint — verified results','',f"Completed {record['finished_utc']}. User budget:25minutes from10:51:45UTC to11:16:45UTC. Recommendation: **B01 {recommended}**. No event submission.",'','## Fresh matched comparisons','','| Candidate | New vs unchanged F | Same-board v002 baseline | Difference | Board bootstrap95% | Mean CPU new / old |','|---|---:|---:|---:|---|---|']
for version,x in comparisons.items():
 a,b=x['candidate'],x['baseline'];ci=x['paired_board_bootstrap_95_pp']
 lines.append(f"| {version} | {a['wins']}/500 ({100*a['win_rate']:.1f}%) | {b['wins']}/500 ({100*b['win_rate']:.1f}%) | {x['difference_pp']:+.1f}pp | [{ci[0]:+.1f}, {ci[1]:+.1f}]pp | {a['mean_cpu_s']*1000:.1f} / {b['mean_cpu_s']*1000:.1f}ms |")
lines += ['',f"Direct fresh comparison: **v004 {ds['a']['wins']}–{ds['b']['wins']} v002** on944000–944249; candidate board-bootstrap win-rate range[{direct_result['board_bootstrap_95_win_rate_percent'][0]:.1f}%,{direct_result['board_bootstrap_95_win_rate_percent'][1]:.1f}%]. [Direct records](direct-v004-vs-v002/games.json), [metadata](direct-v004-vs-v002/metadata.json). Zero recorded faults/clock overruns for both. This result is separate from F scores."]
lines+=['','Every candidate, matched baseline and F recorded zero errors, timeouts, crashes, clock overruns, harness random moves and no-winner games. All500 records in each run were independently audited, including source hashes, board/seat alignment, win counts and CPU. See [machine-readable audit](final-results.json).','']
for version,x in comparisons.items():
 directory='confirmation' if version=='v003' else 'tactical-confirmation';ci=x['reset_chunk_bootstrap_95_pp']
 lines.append(f"- **{version}:** boards{x['seed0']}–{x['seed0']+249}; first/second-seat wins {x['candidate_first_seat_wins']}/250 and {x['candidate_second_seat_wins']}/250. Candidate-only wins{x['candidate_only_wins']}, parent-only wins{x['parent_only_wins']}. Reset-chunk sensitivity[{ci[0]:+.1f},{ci[1]:+.1f}]pp. p95 CPU{x['candidate_p95_cpu_s']*1000:.0f}ms; max{x['candidate']['worst_cpu_s']*1000:.0f}ms. [Candidate records]({directory}/candidate/games.json), [matched baseline records]({directory}/parent/games.json), [metadata]({directory}/candidate/metadata.json).")
lines+=['','These are descriptive paired-board bootstrap intervals (4,000 resamples), unadjusted for development selection and multiple comparisons. Reset-chunk sensitivity resamples the25 process chunks because F maintains RNG state inside each chunk. If an interval includes zero, a win-rate improvement is not established. Different board groups cannot isolate v003 versus v004 effects; the new terminal repair is independently demonstrated in constructed states. The direct comparison is a local baseline match only; no private-O or private-event strength is claimed.','',
'All runs use the unchanged original cumulative clock min(.300+.0125*decisions,1.500)s, tenVP,250 boards with swapped seats, public local dice key and process reload every20 games. This differs from a single uninterrupted official process pair. The host was shared; some comparisons overlapped. CPU is measured per process, but these are not isolated CPU/scorer-hardware or peak-memory benchmarks. Exact kit/engine/OS/commands are in metadata.','',
'## Selection and actual changes','',
'Development used100games each on938000–938049: v002 parent75wins, flexible menu77, opening-only75, combined77, deeper search77; all fault-free. Opening and deeper-search variants did not add observed wins and were not selected. This small development screen is selection evidence only. v003 retained the original opening, width4/depth3/52-expansion/22ms caps. It dynamically reconsiders feasible purchase goals, allows ingredient-preserving trades toward alternatives within85% of the best goal priority, reserves one root from another action family, and includes bank/trade history in continuation deduplication. The85% margin is a hand-chosen policy constant, not a learned probability.','',
'While v003 was frozen, an independent constructed8-VP fixture exposed a missed certain win in both seats: Road length3, hand(1,2,0,2,6), no port. Old policy builds a city, one road, and ends without winning.4ORE→WOOD followed by two legal roads wins immediately. v004 adds a public/own-state certificate before heuristic search, bounded to80 copied executions,12 enabling roots,8 intermediate road states and an8ms total elapsed decision CPU sub-deadline. Legal resource cards and free Road Building are supported. Chance actions are not followed. The copied engine transitions and public hidden-VP bound determine certainty; cutoff/omission never proves no win exists. v003 and v004 were frozen before their respective fresh runs; no coefficients changed after confirmation.','',
'## Correctness and package evidence','',
'- v003:37 methods passed on actual frozen and exact ZIP-extracted modules. v004:43 methods on each form (15 terminal regressions,18 inherited economic contracts,4 sprint contracts,6 new Road-chain regressions). Embedded exhaustive conversion and trade-certificate cases are included in those method counts. [v003 package audit](package-verification.json), [v004 package audit](tactical-package-verification.json).',
'- New coverage includes stale-goal switching, both-seat missed wins, original/reversed action indices, observation immutability, reserved ingredients, bank depletion, dev eligibility, strict opponent Road threshold, expired deadlines and free-road costs. Fixtures are constructed; repaired-event frequency in the main games was not instrumented.',
'- Four separately counted complete matches loaded the actual extracted v004 ZIP against F with zero faults. They are a packaging smoke check, not additional strength evidence. [Smoke metadata](zip-smoke/metadata.json).',
'- The two-road certificate was also profiled for100calls per constructed seat: about1.15ms and0.95ms mean, maximum1.31ms on this host,10copied executions per successful certificate. This excludes serialization and does not certify scorer timing. [Profile](two-road-profile.json).',
'- No runtime network, model, file I/O, dynamic execution or worker imports. Runtime uses math/random/time plus the pinned catanatron engine. ZIP contains exactly the tested agent.py; bytes and CRC verified. Original v002/F source hashes remain unchanged.',
'- Hyde GLM-5.3 Flash produced a mechanical invariant checklist and whitespace-only handoff cleanup; primary reviewed both, authored strategy/code and verified results. No junior code was accepted. [Hyde review](HYDE-REVIEW.md). The test-side-effect isolation correction and original diagnostic regeneration are recorded in [decision log](PLAN.md).','',
'## Files and reproducibility','',
f"Recommended [B01 {recommended} agent.py](../../bots/B01/{recommended}/agent.py) and [ZIP](../../artifacts/B01-{recommended}.zip).",'',
'[v004 agent](../../bots/B01/v004/agent.py), [v004 manifest](../../bots/B01/v004/manifest.json), [v003 agent](../../bots/B01/v003/agent.py), [preserved78% v002](../../bots/B01/v002/agent.py). The78% figure belongs to the historical934000 board group; it must not be pasted onto new files or compared as if it were this fresh baseline.',
'',
'Use `./team-work/run-python.sh team-work/member-1/implementation/final-sprint/package_verify_tactical.py` for repeatable actual-package correctness checks. It creates only an agent ZIP/extract, never another environment. Main run commands are in each metadata.json; experiment drivers intentionally refuse existing frozen/output directories. Do not rerun benchmark drivers without a new request and new evidence paths. All2,500main games (2,000F comparisons plus500direct),500development games and4separate ZIP smoke games are retained; no partial run is represented as complete.','',
'Publication was explicitly authorized during the sprint. Only B01 scope and the separately requested B05 baseline/handoff are included in publication. Other pending teammate work remains local. No SSH, event submission, environment, credential, downloaded dataset or raw provider log upload.']
lines.insert(lines.index('## Selection and actual changes'), 'The final v004 edges are only two wins in each comparison, so a strength gain is not established. The recommendation follows the predeclared point-estimate gates and the demonstrated tactical repair. Mean F-game CPU rose about 14.3% (239.3 ms versus 209.4 ms), with no recorded budget exhaustion. Preserve v002 as a lower-cost fallback.\n')
(BASE/'RESULTS.md').write_text(readable('\n'.join(lines)+'\n'))
for version in ('v003','v004'):
 x=comparisons[version];a=x['candidate'];b=x['baseline']
 text=f'''# B01 {version} — tested sprint candidate

[Full results and recommendation](../../../implementation/final-sprint/RESULTS.md). This exact standalone file scored{a['wins']}/500 against unchanged F; matched v002 scored{b['wins']}/500 on the same boards. Do not compare directly with the historical78% on different boards. A statistical strength gain may remain unestablished; read the intervals.

SHA256 `{x['candidate_source_sha256']}`. [Manifest](manifest.json), [ZIP](../../../artifacts/B01-{version}.zip). ZIP contains only the exact tested agent.py. No sibling source, environment or secret required. Reuse the pinned engine.

Current sprint recommendation: **{recommended}**. Preserve this version and evidence; further changes need a new version. No event submission.
'''
 (ROOT/f'team-work/member-1/bots/B01/{version}/README.md').write_text(readable(text))
print(json.dumps(record,indent=2))
