# Anni B07/B08: build and verified results

Completed 2026-10-17T09:15:13.349371+00:00. Primary implementation was explicitly requested by the user. Both v001 agents are standalone Python files, built and verified in the existing shared environment. No SSH, portal submission, environment copy, training or GitHub upload was performed.

## Main evaluation: 500 games per bot

Same 250 fresh boards (891000–891249), swapped seats, unchanged organizer F, 10 VP and original clock. These results do not include the earlier development checks.

| Bot / strategy | Wins / 500 | Win rate | Descriptive paired 95% range | Mean CPU/game | P95 CPU | Worst CPU | Over budget | Errors / timeouts / crashes | Harness random moves |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| B07 — sampled-opponent planning | 361 | 72.20% | 68.00%–76.00% | 118.4 ms | 260 ms | 620 ms | 0 | 0 / 0 / 0 | 0 |
| B08 — adaptive VP-route planning | 363 | 72.60% | 68.80%–76.40% | 411.9 ms | 690 ms | 1070 ms | 0 | 0 / 0 / 0 | 0 |

Seat results: B07 first 182/250, second 179/250; B08 first 189/250, second 174/250.
No-winner outcomes: B07=0, B08=0. Every outcome and fault was retained.

F health in each run: {"B07": {"games_over_budget": 0, "random_moves": 0, "errors": 0, "timeouts": 0, "crashes": 0}, "B08": {"games_over_budget": 0, "random_moves": 0, "errors": 0, "timeouts": 0, "crashes": 0}}.

The F win-rate difference is only two games (0.4 percentage points); do not treat it as a strength ranking. B07 used about 118 ms/game versus B08 about 412 ms/game on this machine, so it is the cheaper first candidate. Retain both distinct strategies for later diverse-opponent comparisons.

Ranges use 2,000 board-pair bootstrap resamples and are descriptive. Time-based cutoffs and process-persistent F RNG affect replay/dependence; these are not private-score guarantees or a multiple-comparison-adjusted winner test. Both processes reload every 20 games, unlike one uninterrupted official CLI process pair. The local public dice key is used.

## Delivery

- [B07 agent.py](../bots/B07/v001/agent.py), [manifest](../bots/B07/v001/manifest.json), [ZIP](../artifacts/B07-v001.zip).
- [B08 agent.py](../bots/B08/v001/agent.py), [manifest](../bots/B08/v001/manifest.json), [ZIP](../artifacts/B08-v001.zip).
- Each ZIP contains only `agent.py`; CRC and exact source-byte checks passed. Helpers are inlined with executable-AST equivalence verified by `build_agents.py`. No sibling helper modules, keys, environment directory or trained weights are required.
- [Package evidence](../artifacts/package-verification.json), [semantic verification](semantic-verification.json), [harness byte verification](harness-verification.json).

## What differs between the bots

**B07:** a visible-state incumbent and fixed shortlist, at most three accepted worlds from twelve attempts, a bounded deterministic own continuation and voluntary turn end, then a capped set of legal pre-roll opponent dev replies. Rejects sampled opponents already at ten. All currently held opponent cards become eligible only in the modeled next turn. Stops before ROLL/BUY and models selected robber steals by exact conditional expectation. A sampled terminal threat gets a bounded risk penalty, not certain-loss truth. Incomplete comparisons preserve the incumbent.

**B08:** compares city, short expansion, dev, Army and demonstrated short Road routes toward the own actual VP gap. Checks pieces, bonus incumbents, integer bank/port bundles, available bank and current robber-adjusted production. Replans every observation and uses bounded same-turn search for enabling trades. Bonus plans add heuristic potential; they never directly award VP. Future collection is a capped mean-income approximation with a design discount, not a probability model or a true expected completion time.

Both borrow verified Member 3 public-context/expectation utilities unchanged; see [provenance](BORROWED-UTILITIES.md). Their mode selects distinct decision logic; they are not renamed copies of B05/B06.

## Verification and junior contribution

- 15 semantic test methods pass, including independent exhaustive trade search over 18,225 two-resource cases embedded in length-five vectors. Tests cover known terminal builds/trades, low-clock no-sample fallback, impossible/nine-public belief bounds, current-vs-next-turn Knight eligibility, conditional sampled Knight victory, hidden Monopoly effect, no unmodeled chance execution, expected enemy robber transfer, bank/piece/blocked-path limits, deck-order invariance, observation immutability and standalone loading.
- These are explicit constructed/counterfactual engine fixtures, not all full reached histories. One fixture needed its setup HAS_ROLLED flag corrected; this was a fixture correction, not a bot workaround. [Detailed verification log](HYDE-AND-VERIFICATION.md).
- Hyde GLM-5.3 Flash supplied only `route_math.py`, accepted after primary review and exhaustive oracle tests. Successful job `20261017T090102Z-6a8f4a7b`; output SHA-256 `d9d31dde395ec2ec4a424d811b1c1094b3fabc4a5e54fb867263ea6b7fae05d6`. Primary designed/implemented both policies and ran all verification. Raw provider logs remain local.
- Separate development smoke: B07 15/20, B08 17/20, zero recorded faults/exhaustion. These small results were not pooled into the frozen 500-game results.
- Separate 12-game instrumented B07 profile: 651 decisions, 87 attempts/accepted samples, 1,865 reply nodes, 25 completed comparisons, 4 changed decisions, 4 time cutoffs. Shows that the feature ran; does not prove it improved wins. Instrumented timing is not main performance evidence. [Profile](development-profile.json).

## Limits and next review

The user reduced the default main evaluation to 500 games per bot. Extra head-to-head games and matched component ablations are deferred for this build. B01/B02 and private O are unavailable. These F results cannot establish that hidden sampling or macro planning causes the gain, or rank either bot against B05/B06/each other in direct play. Keep both as measured first candidates, not certified final submissions.

B07 is deliberately narrow: only a shortlist, one own follow-up and a voluntarily ended forecast; at most eight dev replies, six robber targets and six Road options per free-road step. It can miss deeper/post-roll tactics and suffers ordinary imperfect-information sampling/strategy-fusion limits. Its necessary nonterminal conditioning is not a complete history-calibrated posterior.

B08 can miss Road routes beyond two added roads or its 28 examined board extensions, expansion beyond two roads, long trade chains and inaccessible future bank replenishment. Mean rates plus a fixed safety discount do not model production variance, future robber moves or opponent bank competition. Plan re-evaluation is stateless across decisions; it does not prove absence of every plan-switching cycle.

Neither policy hides exceptions behind a broad random fallback. Deadline fallback is a legal incumbent/static choice; harness counters report only harness faults/random moves. CPU cost is local-machine evidence; peak memory and event scorer hardware were not measured.

For the next round, inspect reached losing decisions, measure component benefit using the provided ablation switches, and test diverse direct opponents on fresh boards. Preserve v001; fixes need v002 and new evidence. No further implementation or tournament was run after these results.

## Reproduction and provenance

- Existing launcher: `./team-work/run-python.sh`; pinned kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`, engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`.
- Hardware: Intel Core i7-14650HX; launcher constrains numerical-library thread settings to one. [Hardware record](hardware.json). Actual Python/platform details are in each main metadata file; no peak-memory measurement.
- Main runner: `python3 team-work/member-4/implementation/run_frozen_evaluation.py`. Existing result folders cannot be overwritten. A repeat needs new output paths; new confirmation after tuning needs fresh seeds.
- Per-game records and exact commands/source hashes/platform/clock/lifecycle are under `results/B07-v001-vs-F-500/` and `results/B08-v001-vs-F-500/`. [Evaluation status](evaluation-status.json), [plan](EVALUATION-PLAN.md), [design decisions](DESIGN-AND-DECISIONS.md).
- Total retained full games for this build: 1,052 (1,000 main, 40 development smoke, 12 diagnostic). No extra tournament games.
