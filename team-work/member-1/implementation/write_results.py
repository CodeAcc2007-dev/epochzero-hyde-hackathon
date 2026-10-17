"""Validate frozen match/packaging evidence and write the Member1 handoff."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]

def main():
    status=json.loads((BASE/'evaluation-status.json').read_text())
    assert status['status']=='completed' and len(status['runs'])==2
    old=json.loads((BASE/'earlier-bots-preservation.json').read_text())
    for item in old:assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
    rows=[]
    for bot in ('B01','B02'):
        folder=BASE/'results'/f'{bot}-v001-vs-F-500'
        s=json.loads((folder/'summary.json').read_text())
        m=json.loads((folder/'metadata.json').read_text())
        records=json.loads((folder/'games.json').read_text())
        source=BASE.parent/'bots'/bot/'v001/agent.py'
        manifest=json.loads((source.parent/'manifest.json').read_text())
        assert len(records)==500 and s['source_unchanged'] and m['status']=='completed'
        assert [r['game'] for r in records]==list(range(500))
        assert [r['board_seed'] for r in records]==[911000+i//2 for i in range(500)]
        assert sum(r['a_first'] for r in records)==250
        assert s['a']['wins']==sum(r['winner']=='a' for r in records)
        assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['agent_sha256']==m['a']['files'][str(source.relative_to(ROOT))]
        for name,digest in manifest['source_inputs'].items():
            assert hashlib.sha256((BASE/name).read_bytes()).hexdigest()==digest
        rows.append({'bot':bot,**s['a'],'range':s['uncertainty']['pair_bootstrap_95_descriptive'],
                     'p95_cpu_s':s['cpu_p95_a_s'],'first':s['seat_a_first'],'second':s['seat_a_second'],'f':s['b']})
    lines=['# Aroosh B01/B02: build and verified results','',
           'Completed '+datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()+' (India time). Built by the primary assistant at the user\'s explicit request. Both standalone first candidates use the existing environment. Earlier Member 1 files/research and other members\' frozen bots were preserved. No SSH, portal submission, training, environment copy or GitHub upload.','',
           '## Main results: 500 games per bot against unchanged F','',
           'Both use the same fresh 250 boards, 911000–911249, once from each seat. Ten VP, original cumulative clock. No source/config tuning after this test began. Development checks are separate.','',
           '| Bot | Wins / 500 | Win rate | Descriptive paired 95% range | Mean CPU/game | P95 CPU | Worst CPU | Over budget | Errors / timeouts / crashes | Harness random moves |',
           '| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |']
    for r in rows:
        lo,hi=r['range']
        lines.append(f"| {r['bot']} | {r['wins']} | {r['win_rate']:.2%} | {lo:.2%}–{hi:.2%} | {1000*r['mean_cpu_s']:.1f} ms | {1000*r['p95_cpu_s']:.0f} ms | {1000*r['worst_cpu_s']:.0f} ms | {r['games_over_budget']} | {r['errors']} / {r['timeouts']} / {r['crashes']} | {r['random_moves']} |")
    lines += ['', 'Seat wins: '+'; '.join(f"{r['bot']} first {r['first']['wins']}/250, second {r['second']['wins']}/250" for r in rows)+'.',
              'No-winner counts: '+', '.join(f"{r['bot']}={r['no_winner']}" for r in rows)+'. No loss/fault/outcome was dropped.',
              'F counters by matchup: '+json.dumps({r['bot']:{k:r['f'][k] for k in ('games_over_budget','random_moves','errors','timeouts','crashes')} for r in rows})+'.','',
              'Intervals are descriptive board-pair bootstrap ranges from 2,000 resamples. Both processes reload every 20 games, preserving global indices, which differs from one uninterrupted official CLI run. Time cutoffs and process-persistent F RNG affect replay/dependence. Public local dice key, not private event scoring. No multiple-comparison-adjusted winner claim.','',
              '## Files to use','',
              '- [B01 agent.py](../bots/B01/v001/agent.py), [manifest](../bots/B01/v001/manifest.json), [ZIP](../artifacts/B01-v001.zip).',
              '- [B02 agent.py](../bots/B02/v001/agent.py), [manifest](../bots/B02/v001/manifest.json), [ZIP](../artifacts/B02-v001.zip).',
              '- Each is self-contained and requires only stdlib plus the supplied pinned engine. No environment/key/dataset/weights. Each ZIP contains only its exact frozen agent.py; CRC and byte/hash checks passed. Assembly verifies preservation of all executable AST nodes. [Package evidence](../artifacts/package-verification.json).','',
              '## Strategy differences and decisions','',
              '**B01 — bottleneck economy.** Selects a feasible city/expansion/dev purchase family using reserved ingredients, integer conversion shortfall, current bank/owned port rates and readiness. Replaces the generic hand score with feasible retained-goal value and discard exposure. A maritime trade must reduce raw shortage without increasing conversion shortage; resources imported earlier this turn cannot be exported again. Discards preserve the selected goal one legal resource at a time. Bounded same-turn search can complete enabling purchases.','',
              '**B02 — city/dev engine.** Uses different wheat/ore/sheep opening priorities, conditionally commits to city goals/near-equivalent productive upgrades, and values dev/Army investment with guarded draw-model probabilities, legal card timing, a timing discount after an existing dev play and strict incumbent targets. It limits unused non-VP cards to avoid endless buying, while allowing a near-win VP draw when justified. Known legal wins override investment. It retains legal expansion when an upgrade cannot be supported. These are different investment decisions, not renamed earlier bots. A semantic fixture verifies different goal-family choice.','',
              'Core public position/expectation utilities and the bounded city/expansion geometry are reused unchanged with [source provenance](BORROWED-UTILITIES.md). No sampled opposing hidden identities or deck order is evaluated as true information. Robber steals and dev buys use conditional expectation; Monopoly is deterministic; dice and random draws are not executed as known futures.','',
              '## Independent verification and Hyde contribution','',
              '- 19 semantic methods passed, including an independent reachable-trade oracle over 18,225 two-resource cases in five-resource vectors. Cases cover wheat/card-count bottlenecks, reserved last wood, depleted banks, owned versus merely present ports, retained discards, piece/site limits, ore denial escape, old/new Knights, strict Army takeover/owned Army, one-card remaining deck, unused-dev cap, free roads, known terminal city/trade/Army choices, different goal selection, legal standalone returns, observation immutability and no unmodeled chance execution.',
              '- Fixtures are constructed/counterfactual engine states, not all complete reached histories. A fixture initially assumed settlement was best; inspection showed a road awarded two VP instead of one. The expectation was corrected without altering the policy. [Verification log](HYDE-AND-VERIFICATION.md), [test evidence](semantic-verification.json).',
              '- Hyde GLM-5.3 Flash supplied only the pure goal_math.py helper. Job 20261017T092811Z-4fd5fb95 completed in 53.972 s, output SHA-256 46a3e1e47cc8000fabff463f00b6595cff1bbd7f9484993641e92869dd80b89e. Accepted unchanged after primary review and oracle checks. Primary designed/implemented both policies and ran all verification; raw provider logs remain local.',
              '- Development load/play checks: B01 6/12, B02 7/12, zero recorded faults/exhaustion, on 901000–901005. These tiny results were not used as strength claims or pooled into the frozen main test.',
              '- Earlier seven Member 1 bots match the original evaluation hashes and were not overwritten, renamed into B01/B02 or tuned. [Preservation evidence](earlier-bots-preservation.json).','',
              '## Limits and next review','',
              'These are measured first candidates, not final-submission certification. Under the 500-game default, no extra tournament, direct B01/B02 match or matched component ablations were run. Comparisons with older bots, B05/B06, B07/B08 and private O are not established by these F results; earlier rounds used different board sets. No causal component benefit is claimed.','',
              'B01 can overcommit to a goal family, omit useful re-export trades, ignore long expansion routes and miss deeper enabling sequences. Family selection is recomputed per observation; within a decision, the retained family stabilizes trades/discards. The strict trade rule is a conservative policy restriction, not a theorem that every rejected trade is bad.','',
              'B02 concentration can be vulnerable to ore/wheat denial, bursts/discards and hostile opponents. Its investment threshold, near-equivalent city margin, dev stock limit and probability-weighted Knight bonus are explicit hand-chosen heuristics, not learned probabilities or calibrated future-win values. Mean production does not model stochastic completion times; opponents may change bonus targets before delayed plays.','',
              'Both use a depth-three, width-four same-turn purchase search, at most 52 continuation nodes, with a 22 ms/22%-of-remaining-credit soft budget and an 11 ms root-pass limit. Geometry stops at two potential roads. Cutoffs can miss good actions; there is no exhaustive tactical-optimality claim. No broad exception handler hides failures as random moves. Deadline fallback returns a legal incumbent/static choice.','',
              'For the next round, inspect reached losing decisions, separately ablate retention/city/dev choices, and test diverse direct opponents on fresh boards. Preserve v001 and create v002 for changes. No further implementation or tournament was run after this comparison.','',
              '## Reproduction and provenance','',
              '- Existing shared launcher ./team-work/run-python.sh. Kit 04fffac90e00610f60e0b06d919f262f4b3ed9db; engine d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816. [Unchanged harness/F source check](harness-verification.json). Original clock is 300 ms + 12.5 ms/decision, maximum 1.5 s/game.',
              '- Hardware Intel Core i7-14650HX; [hardware record](hardware.json). Exact Python/platform settings are in per-run metadata. Peak memory and event scorer hardware were not measured.',
              '- Run python3 team-work/member-1/implementation/run_frozen_evaluation.py. Existing outputs are protected: repeats need new output paths; confirmation after tuning needs fresh seeds.',
              '- Full records: results/B01-v001-vs-F-500/ and results/B02-v001-vs-F-500/, each with games.json, summary.json and metadata.json containing commands, source hashes and lifecycle. [Status](evaluation-status.json), [plan](EVALUATION-PLAN.md), [design decisions](DESIGN-AND-DECISIONS.md).',
              '- Total retained full games: 1,024 (1,000 main plus 24 separate development checks). No extra tournament games.','']
    (BASE/'BUILD-AND-RESULTS.md').write_text('\n'.join(lines))
    (BASE/'comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps({'rows':[{'bot':r['bot'],'games':500,'wins':r['wins'],'rate':r['win_rate']} for r in rows],
                      'report':str(BASE/'BUILD-AND-RESULTS.md')},indent=2))
if __name__=='__main__':main()
