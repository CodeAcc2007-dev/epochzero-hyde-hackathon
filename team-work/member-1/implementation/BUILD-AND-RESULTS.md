# Aroosh B01/B02: build and verified results

Completed 2026-10-17T15:11:11.102946+05:30 (India time). Built by the primary assistant at the user's explicit request. Both standalone first candidates use the existing environment. Earlier Member 1 files/research and other members' frozen bots were preserved. No SSH, portal submission, training, environment copy or GitHub upload.

## Main results: 500 games per bot against unchanged F

Both use the same fresh 250 boards, 911000–911249, once from each seat. Ten VP, original cumulative clock. No source/config tuning after this test began. Development checks are separate.

| Bot | Wins / 500 | Win rate | Descriptive paired 95% range | Mean CPU/game | P95 CPU | Worst CPU | Over budget | Errors / timeouts / crashes | Harness random moves |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| B01 | 381 | 76.20% | 72.60%–79.60% | 205.9 ms | 370 ms | 650 ms | 0 | 0 / 0 / 0 | 0 |
| B02 | 359 | 71.80% | 67.60%–75.80% | 202.9 ms | 360 ms | 480 ms | 0 | 0 / 0 / 0 | 0 |

Seat wins: B01 first 198/250, second 183/250; B02 first 175/250, second 184/250.
No-winner counts: B01=0, B02=0. No loss/fault/outcome was dropped.
F counters by matchup: {"B01": {"games_over_budget": 0, "random_moves": 0, "errors": 0, "timeouts": 0, "crashes": 0}, "B02": {"games_over_budget": 0, "random_moves": 0, "errors": 0, "timeouts": 0, "crashes": 0}}.

Intervals are descriptive board-pair bootstrap ranges from 2,000 resamples. Both processes reload every 20 games, preserving global indices, which differs from one uninterrupted official CLI run. Time cutoffs and process-persistent F RNG affect replay/dependence. Public local dice key, not private event scoring. No multiple-comparison-adjusted winner claim.

## Files to use

- [B01 agent.py](../bots/B01/v001/agent.py), [manifest](../bots/B01/v001/manifest.json), [ZIP](../artifacts/B01-v001.zip).
- [B02 agent.py](../bots/B02/v001/agent.py), [manifest](../bots/B02/v001/manifest.json), [ZIP](../artifacts/B02-v001.zip).
- Each is self-contained and requires only stdlib plus the supplied pinned engine. No environment/key/dataset/weights. Each ZIP contains only its exact frozen agent.py; CRC and byte/hash checks passed. Assembly verifies preservation of all executable AST nodes. [Package evidence](../artifacts/package-verification.json).

## Strategy differences and decisions

**B01 — bottleneck economy.** Selects a feasible city/expansion/dev purchase family using reserved ingredients, integer conversion shortfall, current bank/owned port rates and readiness. Replaces the generic hand score with feasible retained-goal value and discard exposure. A maritime trade must reduce raw shortage without increasing conversion shortage; resources imported earlier this turn cannot be exported again. Discards preserve the selected goal one legal resource at a time. Bounded same-turn search can complete enabling purchases.

**B02 — city/dev engine.** Uses different wheat/ore/sheep opening priorities, conditionally commits to city goals/near-equivalent productive upgrades, and values dev/Army investment with guarded draw-model probabilities, legal card timing, a timing discount after an existing dev play and strict incumbent targets. It limits unused non-VP cards to avoid endless buying, while allowing a near-win VP draw when justified. Known legal wins override investment. It retains legal expansion when an upgrade cannot be supported. These are different investment decisions, not renamed earlier bots. A semantic fixture verifies different goal-family choice.

Core public position/expectation utilities and the bounded city/expansion geometry are reused unchanged with [source provenance](BORROWED-UTILITIES.md). No sampled opposing hidden identities or deck order is evaluated as true information. Robber steals and dev buys use conditional expectation; Monopoly is deterministic; dice and random draws are not executed as known futures.

## Independent verification and Hyde contribution

- 19 semantic methods passed, including an independent reachable-trade oracle over 18,225 two-resource cases in five-resource vectors. Cases cover wheat/card-count bottlenecks, reserved last wood, depleted banks, owned versus merely present ports, retained discards, piece/site limits, ore denial escape, old/new Knights, strict Army takeover/owned Army, one-card remaining deck, unused-dev cap, free roads, known terminal city/trade/Army choices, different goal selection, legal standalone returns, observation immutability and no unmodeled chance execution.
- Fixtures are constructed/counterfactual engine states, not all complete reached histories. A fixture initially assumed settlement was best; inspection showed a road awarded two VP instead of one. The expectation was corrected without altering the policy. [Verification log](HYDE-AND-VERIFICATION.md), [test evidence](semantic-verification.json).
- Hyde GLM-5.3 Flash supplied only the pure goal_math.py helper. Job 20261017T092811Z-4fd5fb95 completed in 53.972 s, output SHA-256 46a3e1e47cc8000fabff463f00b6595cff1bbd7f9484993641e92869dd80b89e. Accepted unchanged after primary review and oracle checks. Primary designed/implemented both policies and ran all verification; raw provider logs remain local.
- Development load/play checks: B01 6/12, B02 7/12, zero recorded faults/exhaustion, on 901000–901005. These tiny results were not used as strength claims or pooled into the frozen main test.
- Earlier seven Member 1 bots match the original evaluation hashes and were not overwritten, renamed into B01/B02 or tuned. [Preservation evidence](earlier-bots-preservation.json).

## Limits and next review

These are measured first candidates, not final-submission certification. Under the 500-game default, no extra tournament, direct B01/B02 match or matched component ablations were run. Comparisons with older bots, B05/B06, B07/B08 and private O are not established by these F results; earlier rounds used different board sets. No causal component benefit is claimed.

B01 can overcommit to a goal family, omit useful re-export trades, ignore long expansion routes and miss deeper enabling sequences. Family selection is recomputed per observation; within a decision, the retained family stabilizes trades/discards. The strict trade rule is a conservative policy restriction, not a theorem that every rejected trade is bad.

B02 concentration can be vulnerable to ore/wheat denial, bursts/discards and hostile opponents. Its investment threshold, near-equivalent city margin, dev stock limit and probability-weighted Knight bonus are explicit hand-chosen heuristics, not learned probabilities or calibrated future-win values. Mean production does not model stochastic completion times; opponents may change bonus targets before delayed plays.

Both use a depth-three, width-four same-turn purchase search, at most 52 continuation nodes, with a 22 ms/22%-of-remaining-credit soft budget and an 11 ms root-pass limit. Geometry stops at two potential roads. Cutoffs can miss good actions; there is no exhaustive tactical-optimality claim. No broad exception handler hides failures as random moves. Deadline fallback returns a legal incumbent/static choice.

For the next round, inspect reached losing decisions, separately ablate retention/city/dev choices, and test diverse direct opponents on fresh boards. Preserve v001 and create v002 for changes. No further implementation or tournament was run after this comparison.

## Reproduction and provenance

- Existing shared launcher ./team-work/run-python.sh. Kit 04fffac90e00610f60e0b06d919f262f4b3ed9db; engine d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816. [Unchanged harness/F source check](harness-verification.json). Original clock is 300 ms + 12.5 ms/decision, maximum 1.5 s/game.
- Hardware Intel Core i7-14650HX; [hardware record](hardware.json). Exact Python/platform settings are in per-run metadata. Peak memory and event scorer hardware were not measured.
- Run python3 team-work/member-1/implementation/run_frozen_evaluation.py. Existing outputs are protected: repeats need new output paths; confirmation after tuning needs fresh seeds.
- Full records: results/B01-v001-vs-F-500/ and results/B02-v001-vs-F-500/, each with games.json, summary.json and metadata.json containing commands, source hashes and lifecycle. [Status](evaluation-status.json), [plan](EVALUATION-PLAN.md), [design decisions](DESIGN-AND-DECISIONS.md).
- Total retained full games: 1,024 (1,000 main plus 24 separate development checks). No extra tournament games.
