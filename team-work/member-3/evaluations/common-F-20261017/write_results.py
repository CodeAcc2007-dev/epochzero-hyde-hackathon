"""Audit six identical-board F runs and separate newer uploaded Member2 evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,random,statistics,subprocess
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
F='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'


def paired(a,b):
    values=[(int(a[i]['winner']=='a')+int(a[i+1]['winner']=='a')-int(b[i]['winner']=='a')-int(b[i+1]['winner']=='a'))/2 for i in range(0,500,2)]
    rng=random.Random(20261017)
    samples=sorted(statistics.mean(rng.choices(values,k=250)) for _ in range(2000))
    blocks=[statistics.mean(values[i:i+10]) for i in range(0,250,10)]
    rng=random.Random(20261018)
    grouped=sorted(statistics.mean(rng.choices(blocks,k=25)) for _ in range(2000))
    return {'difference_pp':100*statistics.mean(values),'pair_descriptive95_pp':[100*samples[49],100*samples[1949]],'reset_chunk_sensitivity95_pp':[100*grouped[49],100*grouped[1949]],'a_only_wins':sum(x['winner']=='a' and y['winner']!='a' for x,y in zip(a,b)),'b_only_wins':sum(y['winner']=='a' and x['winner']!='a' for x,y in zip(a,b))}


def main():
    assert json.loads((BASE/'status.json').read_text())['status']=='completed'
    index=json.loads((BASE/'source-index.json').read_text());audited={};games={}
    for bot,x in index.items():
        folder=ROOT/x['common_result'];meta=json.loads((folder/'metadata.json').read_text());s=json.loads((folder/'summary.json').read_text());rows=json.loads((folder/'games.json').read_text())
        assert len(rows)==500 and meta['status']=='completed' and s['source_unchanged']
        assert meta['seed0']==934000 and meta['games']==500 and meta['vps']==10
        assert meta['process_lifecycle']=='Both agents reload every 20 games, sequential chunks; global indices preserved'
        assert meta['clock']=={'base_s':.3,'increment_s':.0125,'max_s':1.5}
        assert meta['kit_commit']=='04fffac90e00610f60e0b06d919f262f4b3ed9db' and meta['engine_commit']=='d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816'
        assert list(meta['b']['files'].values())==[F] and list(meta['a']['files'].values())==[x['sha256']]
        assert hashlib.sha256((ROOT/x['entrypoint']).read_bytes()).hexdigest()==x['sha256']
        for i,row in enumerate(rows):assert (row['game'],row['board_seed'],row['a_first'])==(i,934000+i//2,i%2==0)
        for side in ('a','b'):
            assert s[side]['wins']==sum(r['winner']==side for r in rows)
            assert abs(s[side]['mean_cpu_s']-statistics.mean(r[side]['cpu_s'] for r in rows))<1e-10
            assert s[side]['no_winner']==sum(r['winner'] not in ('a','b') for r in rows)
            for k in ('errors','timeouts','crashes','random_moves'):assert s[side][k]==sum(r[side][k] for r in rows)==0
            assert s[side]['games_over_budget']==sum(r[side]['over'] is not None for r in rows)==0
        games[bot]=rows
        audited[bot]={**x,'wins':s['a']['wins'],'win_rate':s['a']['win_rate'],'pair_descriptive95':s['uncertainty']['pair_bootstrap_95_descriptive'],'mean_cpu_ms':1000*s['a']['mean_cpu_s'],'p95_cpu_ms':1000*s['cpu_p95_a_s'],'worst_cpu_ms':1000*s['a']['worst_cpu_s'],'summary':s,'platform':meta['platform'],'python':meta['python']}
    assert hashlib.sha256((ROOT/'shared-local/organizer-kit/examples/f_agent.py').read_bytes()).hexdigest()==F
    assert not subprocess.check_output(['git','-C','shared-local/organizer-kit','status','--porcelain'],cwd=ROOT,text=True).strip()
    rank=sorted(audited,key=lambda b:(-audited[b]['wins'],audited[b]['mean_cpu_ms']))
    pairs={a+'-minus-'+b:paired(games[a],games[b]) for i,a in enumerate(rank) for b in rank[i+1:]}
    uploaded=json.loads((BASE/'member2-upload-audit.json').read_text())
    record={'ranking_by_observed_F_wins':rank,'common_board_seed_range':[934000,934249],'bots':audited,'paired_differences':pairs,'member2_uploaded_separate':uploaded,'F_sha256':F,'new_full_games':1000,'existing_common_games_reused':2000,'no_bot_changes':True}
    (BASE/'comparison.json').write_text(json.dumps(record,indent=2)+'\n')
    table=[]
    for i,b in enumerate(rank,1):
        x=audited[b];lo,hi=x['pair_descriptive95']
        relative=f"../../../member-{x['member']}/bots/{b}/{x['version']}/agent.py"
        table.append(f"| {i} | {b} {x['version']} | {x['wins']}/500 | {100*x['win_rate']:.1f}% | {100*lo:.1f}%–{100*hi:.1f}% | {x['mean_cpu_ms']:.1f} ms | [agent.py]({relative}) |")
    first,second=rank[:2];top=pairs[first+'-minus-'+second]
    stamp=datetime.now(ZoneInfo('Asia/Calcutta')).isoformat()
    text=f'''# Latest candidates against unchanged F: common-board comparison

Completed {stamp} (India time). User requested checking the completed B01/B02 upgrades and deciding which bots are strongest. No strategy source was changed, no SSH/event action was taken and nothing was pushed.

## Six current candidates on identical boards

This is an **observed F-score order**, not a proven ordering of true strength or a peer-clash result. Every row uses exactly the same 250 boards934000–934249, both seats/global indices0–499, ten VP, unchanged clock and20-game process resets. B01/B02 v002 were newly run here (1,000 games); the four unchanged Member3/4 results were audited and reused (2,000 existing games).

| Observed order | Frozen candidate | Wins | Win rate | Descriptive board-pair95% | Mean own CPU | File |
| --- | --- | ---: | ---: | --- | ---: | --- |
'''+ '\n'.join(table)+f'''

Every candidate and F side has **zero recorded errors, timeouts, crashes, clock overruns and harness random moves**. No-winner outcomes were retained. All wins, fault counters, means, board/global indices, source hashes, baseline hash and lifecycle were independently recomputed/checked. Runtime sources remain unchanged.

The highest observed F score is **{first}**, followed by **{second}**. Their paired difference is {top['difference_pp']:+.1f} percentage points, with unadjusted descriptive board-pair range [{top['pair_descriptive95_pp'][0]:+.1f}, {top['pair_descriptive95_pp'][1]:+.1f}] and reset-chunk sensitivity range [{top['reset_chunk_sensitivity95_pp'][0]:+.1f}, {top['reset_chunk_sensitivity95_pp'][1]:+.1f}] pp. Selecting a leader after viewing six candidates adds selection uncertainty. These ranges are not multiplicity-adjusted and do not prove a universal winner.

## Practical recommendation

Prioritize **B05, B01 and B07** for the next diverse-opponent clashes: they cover same-turn tactics, bottleneck economy and sampled replies. Use the common-board table to identify the current point leader. B07 is a useful fast candidate in this leading group; CPU cost and behavior diversity matter alongside a small F-score difference. B02/B06/B08 remain alternative styles worth preserving, not demonstrated weak policies merely because they trail by a few wins. All six clear F's50% point mark in these batches; that does not certify private O or performance against one another.

Do not promote a tiny top-score gap into a final submission decision. The next discriminating evidence is bounded diverse peer testing, especially disagreements/loss traces, rather than another coefficient change tuned on these used boards. No such tournament or further bot implementation was performed here.

## Latest Member2 upload: separate evidence

Git fetch found newer B03/B04 **v003** at commit `{uploaded['B03']['commit']}`. Their published 500-game records were audited directly from that immutable Git object; no branch merge, shared-runner changes or environment copy. They were **not replayed on this machine or the common board group**.

| Uploaded candidate | Wins /500 | F rate | Board group | Qualification |
| --- | ---: | ---: | --- | --- |
| B03 v003 | {uploaded['B03']['summary']['a']['wins']} | {100*uploaded['B03']['summary']['a']['win_rate']:.1f}% | 933000–933249 | Uploaded WSL run, record/hash audit only |
| B04 v003 | {uploaded['B04']['summary']['a']['wins']} | {100*uploaded['B04']['summary']['a']['win_rate']:.1f}% | 933500–933749 | Uploaded WSL run, record/hash audit only |

**B04 remains the weakest priority on current F evidence. B03 has improved from its older v002 result but is approximately F-level in this upload, far less promising than the current70%+ cohort.** Its interval includes50%; that does not prove statistical equivalence/parity with F. The uploaded narrative also incorrectly suggests48.6% and49.8% interval endpoints are separated; they overlap. No fix is attributed causally to a win-rate difference without a suitable controlled comparison.

Both v003 metadata files record the same F SHA-256 as ours, and per-game harness fault counters recompute to zero. Source hashes match their commit. Internal caught-error counts are not established by zero harness errors. Different machines/board groups and source versions prevent a direct matched eight-bot ranking. See [immutable-upload audit](member2-upload-audit.json) for exact URLs, commit, source identities and metadata.

## Provenance and limits

Unchanged F SHA-256 `{F}`; kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`, engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Original cumulative clock300 ms +12.5 ms/decision, max1.5 s/game. Both processes reset every20 games; persistent F RNG within a chunk affects dependence. All existing common runs and these new runs use the same lifecycle and global indices. Shared-host timing is not quiet-host/event-hardware certification.

Board group934000–934249 was already used by other candidates; it is a common reference group, **not globally untouched confirmation**. Candidate bytes were frozen before this comparison and no tuning followed. Descriptive paired intervals resample250 board pairs2,000 times; sensitivity intervals resample25 reset chunks. They are unadjusted across the15 pairwise comparisons and depend on the observed sample; zero-width empirical ranges do not prove equivalence. F-only performance does not reveal exploitability or matchup cycles.

[Source index and prior-run audit](source-index.json), [comparison and all paired differences](comparison.json), [fixed plan](PLAN.md), [new-run status/commands](status.json). Full new records live under results/, existing records remain at their original owner paths. Preserve all frozen versions and all losses; further work needs separately labelled used/fresh board groups. No publication or environment/secret upload in this task.
'''
    for a,b in {'boards934000':'boards 934000','indices0':'indices 0','and20-game':'and 20-game',"F's50%":"F's 50%",'current70%':'current 70%','includes50%':'includes 50%','suggests48.6%':'suggests 48.6%','and49.8%':'and 49.8%','clock300':'clock 300','+12.5':'+ 12.5','max1.5':'max 1.5','every20':'every 20','group934000':'group 934000','resample250':'resample 250','pairs2,000':'pairs 2,000','resample25':'resample 25','the15':'the 15'}.items():text=text.replace(a,b)
    (BASE/'RESULTS-AND-RECOMMENDATION.md').write_text(text)
    print(json.dumps({'observed_order':rank,'wins':{b:audited[b]['wins'] for b in rank},'top_two_paired':top},indent=2))
if __name__=='__main__':main()
