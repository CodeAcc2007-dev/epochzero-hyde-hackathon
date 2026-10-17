"""Validate every saved result and write honest member-specific round-two reports."""
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib, json, math, random, statistics, subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
BOTS={'B05':(3,'v004','v003'),'B06':(3,'v004','v003'),'B07':(4,'v002','v001'),'B08':(4,'v002','v001')}
F='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'
FAULTS=('errors','timeouts','crashes','games_over_budget','random_moves')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check_run(path):
    data=json.loads((path/'games.json').read_text());summary=json.loads((path/'summary.json').read_text());meta=json.loads((path/'metadata.json').read_text())
    assert len(data)==500 and meta['status']=='completed' and summary['source_unchanged']
    assert meta['games']==500 and meta['seed0']==934000 and meta['vps']==10
    assert meta['process_lifecycle']=='Both agents reload every 20 games, sequential chunks; global indices preserved'
    assert meta['clock']=={'base_s':.3,'increment_s':.0125,'max_s':1.5}
    assert set(meta['b']['files'].values())=={F}
    for name,digest in meta['a']['files'].items():assert sha(ROOT/name)==digest,name
    for i,row in enumerate(data):assert (row['game'],row['board_seed'],row['a_first'])==(i,934000+i//2,i%2==0)
    for side in ('a','b'):
        s=summary[side]
        assert s['games']==500 and s['wins']==sum(r['winner']==side for r in data)
        assert s['no_winner']==sum(r['winner'] not in ('a','b') for r in data)
        assert abs(s['mean_cpu_s']-statistics.mean(r[side]['cpu_s'] for r in data))<1e-10
        assert s['worst_cpu_s']==max(r[side]['cpu_s'] for r in data)
        for key in ('errors','timeouts','crashes','random_moves'):assert s[key]==sum(r[side][key] for r in data)==0
        assert s['games_over_budget']==sum(r[side]['over'] is not None for r in data)==0
    return data,summary,meta


def paired(new,parent):
    diffs=[(int(new[i]['winner']=='a')+int(new[i+1]['winner']=='a')-int(parent[i]['winner']=='a')-int(parent[i+1]['winner']=='a'))/2 for i in range(0,500,2)]
    rng=random.Random(20261017)
    draws=sorted(statistics.mean(rng.choices(diffs,k=250)) for _ in range(2000))
    blocks=[statistics.mean(diffs[i:i+10]) for i in range(0,250,10)]
    block_rng=random.Random(20261018)
    block_draws=sorted(statistics.mean(block_rng.choices(blocks,k=25)) for _ in range(2000))
    return {'process_chunk_bootstrap_95_difference_pp':[100*block_draws[49],100*block_draws[1949]],'win_difference':sum(r['winner']=='a' for r in new)-sum(r['winner']=='a' for r in parent),'percentage_point_difference':100*statistics.mean(diffs),'pair_bootstrap_95_difference_pp':[100*draws[49],100*draws[1949]],'new_only_wins':sum(n['winner']=='a' and p['winner']!='a' for n,p in zip(new,parent)),'parent_only_wins':sum(p['winner']=='a' and n['winner']!='a' for n,p in zip(new,parent)),'interpretation':'Descriptive board-pair resampling; unadjusted across four candidates. Timing and F lifecycle stochasticity remain. Not a causal component attribution/private-event guarantee.'}


def main():
    status=json.loads((BASE/'evaluation-status-main.json').read_text());assert status['status']=='completed' and len(status['completed'])==8
    result={}
    for bot,(member,version,parent) in BOTS.items():
        folder=ROOT/f'team-work/member-{member}/implementation/round-2/main'
        pn=folder/f'{bot}-{version}-new-vs-F-500';pp=folder/f'{bot}-{parent}-parent-vs-F-500'
        new,ns,nm=check_run(pn);old,ps,pm=check_run(pp)
        assert [(r['game'],r['board_seed'],r['a_first']) for r in new]==[(r['game'],r['board_seed'],r['a_first']) for r in old]
        manifest=json.loads((ROOT/f'team-work/member-{member}/bots/{bot}/{version}/manifest.json').read_text())
        assert sha(ROOT/nm['a']['entrypoint'])==manifest['agent_sha256']
        result[bot]={'new_version':version,'parent_version':parent,'new':ns,'parent':ps,'paired':paired(new,old),'new_metadata':str((pn/'metadata.json').relative_to(ROOT)),'parent_metadata':str((pp/'metadata.json').relative_to(ROOT)),'manifest':manifest}
    inventory=json.loads((ROOT/'team-work/reviews/2026-10-17-B03-B08/source-and-result-audit.json').read_text())
    for row in inventory['review_sources']:
        if row['owner_member'] not in (3,4):continue
        for name,h in row['files_sha256'].items():assert sha(ROOT/row['source_path']/name)==h
    assert sha(ROOT/'shared-local/organizer-kit/examples/f_agent.py')==F
    assert not subprocess.check_output(['git','-C','shared-local/organizer-kit','status','--porcelain'],cwd=ROOT,text=True).strip()
    stamp=datetime.now(ZoneInfo('Asia/Calcutta')).isoformat()
    for member in (3,4):
        folder=ROOT/f'team-work/member-{member}/implementation/round-2'
        selected={b:x for b,x in result.items() if BOTS[b][0]==member}
        (folder/'comparison.json').write_text(json.dumps(selected,indent=2)+'\n')
        rows=[];details=[];recommendations=[]
        for bot,x in selected.items():
            n=x['new']['a'];p=x['parent']['a'];delta=x['paired'];lo,hi=delta['pair_bootstrap_95_difference_pp']
            rows.append(f"| {bot} {x['new_version']} | {n['wins']}/500 ({100*n['win_rate']:.1f}%) | {p['wins']}/500 ({100*p['win_rate']:.1f}%) | {delta['percentage_point_difference']:+.1f} pp [{lo:+.1f}, {hi:+.1f}] | {1000*n['mean_cpu_s']:.1f} / {1000*p['mean_cpu_s']:.1f} ms | {1000*x['new']['cpu_p95_a_s']:.0f} / {1000*n['worst_cpu_s']:.0f} ms |")
            chunk_ci=delta['process_chunk_bootstrap_95_difference_pp']
            if lo>0 and chunk_ci[0]>0:
                conclusion='Both descriptive ranges favor this whole revision against F; component attribution and private-event strength remain unestablished.'
            elif hi<0 and chunk_ci[1]<0:
                conclusion='Both descriptive ranges favor the parent against F; do not promote this composite revision on strength. Preserve the correctness fixes in a separately versioned safety-only comparison next.'
            else:
                conclusion='A win-rate gain is not established by both descriptive ranges; retain this as a correctness-repaired review candidate, without claiming it is stronger.'
            experiment={'B05':'isolate enabler reservation from terminal safety','B06':'isolate the conversion-threat risk term from terminal safety','B07':'compare root/own/full controls with useful reached reply traces','B08':'separate eligibility-delay correction from cache/performance changes'}[bot]
            recommendations.append(f'- **{bot}:** {conclusion} Next bounded question: {experiment}, after human review and using fresh boards. No further tuning was performed here.')
            interval=x['new']['uncertainty']['pair_bootstrap_95_descriptive']
            chunk_lo,chunk_hi=delta['process_chunk_bootstrap_95_difference_pp']
            details.append(f"- **{bot}:** new descriptive win-rate range {100*interval[0]:.1f}%–{100*interval[1]:.1f}%; first-seat wins {x['new']['seat_a_first']['wins']}/250, second {x['new']['seat_a_second']['wins']}/250. New-only wins {delta['new_only_wins']}, parent-only wins {delta['parent_only_wins']}. No-winner counts new/parent {n['no_winner']}/{p['no_winner']}. Reset-chunk sensitivity range for the win-rate difference: [{chunk_lo:+.1f}, {chunk_hi:+.1f}] pp. [New records](main/{bot}-{x['new_version']}-new-vs-F-500/games.json), [parent records](main/{bot}-{x['parent_version']}-parent-vs-F-500/games.json).")
        changes='''B05/B06 v004 share a bounded public terminal selector before emergency fallback. Legal city and eligible strict Army wins are cheap; up to 12 settlement/Road copies apply exact engine bonus changes with public nonterminal hidden-VP bounds. The scan is deliberately incomplete rather than an exhaustive win oracle.

B05 protects up to two useful purchase/expansion enablers while retaining three greedy roots within width 5 and the existing 80-expansion/depth 4/22 ms caps. The bounded completion scan now considers eight-VP Road/Army cases. B06 adds exact one-trade building feasibility using the public hand, owned port ratios, bank and legal piece/site availability. Direct/convertible/roll-pending/hidden-conditional categories are distinct. Conversion risk 12 and hidden 8 VP risk weight 0.35 are hand-chosen weights, not fitted probabilities or certainty through the next roll.''' if member==3 else '''B07/B08 v002 share a bounded public terminal selector before emergency fallback, including copied engine settlement/Road bonus changes and strict eligible Army wins. At most 12 build copies are examined; this is not exhaustive.

B07 distributes its existing eight-reply budget across dev families, ranks YOP by feasible purchase deficits and removes zero-theft Monopoly choices. Three explicit root/own/full forecast controls exist for diagnostics; the submitted candidate keeps full sampled replies. The six-option free-road shortlist and pre-roll forecast horizon remain bounded limitations. B08 adds eligibility delay when a required Knight is not already playable, and a 128-entry per-decision potential cache keyed by full plan menu, hand, production rates, port ratios, bank and VP gap. The two-roll-unit scaling is a route heuristic, not exact elapsed dice rolls or an expected time-to-Army model.'''
        lines=f'''# Member {member} round 2: corrections and matched results

Completed {stamp} (India time). User-authorized local implementation; **human verification pending, not published or submitted to the event**. Parent files are preserved. These are measured new candidates; correctness repairs and a headline win rate do not prove broad strategic superiority.

## Fresh frozen comparison

| Candidate | New vs unchanged F | Matched parent vs F | Change [descriptive paired95%] | Mean CPU new / parent | New p95 / max CPU |
| --- | --- | --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

Every listed new/parent/F run recorded **zero errors, timeouts, crashes, clock overruns and harness random moves**. All outcomes were retained; counts and means were recomputed from 500 individual records for every run.

'''+ '\n'.join(details)+f'''

Both versions use exactly the same 250 fresh boards 934000–934249, swapped seats, global indices 0–499, ten VP and original cumulative clock (300 ms + 12.5 ms/decision, max 1.5 s/game). Both agent processes reload every 20 games. This lifecycle differs from one uninterrupted official CLI pair. Unchanged F SHA-256 `{F}`. Kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`; engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Per-run metadata includes exact commands, source hashes, interpreter, platform and lifecycle. [Harness/hardware verification](harness-and-hardware.json) records unchanged source bytes and the installed engine commit.

The main comparison was specified before running and all source bytes were frozen. These are untouched first-evaluation/confirmation boards for this revision; no tuning followed these outcomes. Across both members: 2,000 new-candidate games + 2,000 matched-parent games = 4,000 main games, plus 24 separate smoke games. The four 100-action external diagnostic histories did not finish games and are not pooled. No extra full tournament or component-ablation games were run.

Paired intervals resample 250 board-pair win differences 2,000 times. They are descriptive, unadjusted across four candidates and affected by time-based cutoffs/process RNG. An interval containing zero does not establish a gain; an interval excluding zero is still not private-event certification. A second descriptive sensitivity range resamples the 25 process-reset chunks (ten board pairs each), acknowledging within-process RNG dependence; it is also unadjusted and does not certify independence from host effects. Multiple changes within a bot cannot be causally separated by this version-level comparison. Historical results on other boards are not an eight-bot leaderboard.

B06 and B07 had identical 500 paired win/loss labels between revisions in this batch, so their resampled differences degenerate to [0, 0] by construction. This does not prove equivalent policies or equal future strength: resampling cannot generate unobserved disagreements, and other boards/opponents may differ.

## What changed

{changes}

[Precommitted plan](PLAN-AND-DECISIONS.md), [ticket-by-ticket verification and remaining scope](VERIFICATION-AND-SCOPE.md), [Hyde review](HYDE-REVIEW.md). Broader suggested experiments remain explicitly deferred; this round does not claim every research hypothesis is solved.

## Verification and diagnostics

- 18 new regression methods plus 36 adapted existing contract methods passed on actual standalone artifacts. Independent 18,225-case single-trade and 18,225-case preserved conversion-helper oracles are embedded in these methods. [Semantic evidence](semantic-verification.json). Constructed fixture allocations are not all reached histories.
- Parent low-clock failures were reproduced before asserting corrected behavior in both seats. New Knight purchase restrictions and strict Army ties, actual eight-VP Road wins, chance boundaries, immutability, bank/piece/port checks, reply ordering and cache invalidation are covered. Two test expectations were broadened to accept an earlier legal Road-bonus win; the engine winner still must match.
- The bounded terminal selector was profiled over 200 constructed calls per bot: see [isolated CPU measurements](terminal-profile.json). These omit serialization and do not certify scorer timing or zero-credit feasibility.
- [External partial-history profiles](diagnostics.json) record copies, nodes/roots, cutoffs and route-cache counts. B05 rescued one enabler in its short trace; B08 had 117 cache hits. B07's short trace never reached the held-opponent-dev gate, so useful reached reply attribution remains unestablished despite constructed control tests. No Road-cut full-history acceptance claim.
- Hyde GLM-5.3 Flash job 20261017T100054Z-841863a8 supplied pure trade/eligibility math. Primary reviewed every statement, corrected only misleading timing-unit documentation and independently verified the code. No API call is made by any bot. A second 104.589 s Hyde mechanical source inventory was independently checked/corrected; see SOURCE-INVENTORY.md. Provider logs remain local.

## Files and handoff

'''
        for bot,x in selected.items():
            v=x['new_version'];lines+=f"- [{bot} {v} agent.py](../../bots/{bot}/{v}/agent.py), [manifest](../../bots/{bot}/{v}/manifest.json), [ZIP](../../artifacts/{bot}-{v}.zip).\n"
        lines+='\n## Interpretation and next review\n\n'+'\n'.join(recommendations)+'\n'
        lines+='''
Each ZIP contains only the exact standalone agent.py; CRC, hash, clean extraction/load, development/frozen byte identity and executable-AST assembly checks passed. [Package evidence](package-verification.json). Reuse the supplied environment; no key, dataset, network, worker, installed dependency tree or sibling Python module is required by the package. No runtime file logging was added.

The original parent/component sources and organizer tracked files were verified unchanged after evaluation. New files are identified by hashes, while metadata repository_base_commit is the existing parent publication, not a claim these uncommitted revisions already exist on GitHub. Peak memory and event hardware/private O were not measured. Host may have unrelated user activity; own-process CPU is reported. Additional dynamic parent timing differences should not be interpreted as a cache-only speedup.

Run the existing shared launcher for reproduction. The main runner is `team-work/member-3/implementation/round-2/run_round.py --phase main`; it refuses existing output paths and needs a new namespace/output for another run. Actual commands are retained in per-run metadata and evaluation-status-main.json. The verification entrypoints are `test_round2.py` and `verify_contracts.py` in Member 3's round-2 folder; they cover both authorized members and load the new frozen versions when present. Keep parents and these freezes intact; further changes need a new version and untouched boards.
'''
        (folder/'BUILD-AND-RESULTS.md').write_text(lines)
    print(json.dumps({b:{'new_wins':x['new']['a']['wins'],'parent_wins':x['parent']['a']['wins'],'paired':x['paired']} for b,x in result.items()},indent=2))
if __name__=='__main__':main()
