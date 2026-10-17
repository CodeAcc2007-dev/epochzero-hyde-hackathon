# C01 v001: combined best traits of B01, B05 and B02 — full test results

17 October 2026. Built by Avadooth (Member 2) at the user's request on branch
`combined/best-of-b01-b02-b05`. No existing bot, result or other member's file was changed
(hash-checked in `verification.json`). Human review pending; no event submission was made.

## What was combined, and why

Only traits with non-negative matched-board evidence were used.

| Source | Trait | Matched evidence in the repo | In C01 |
|---|---|---|---|
| B01 v001/v002 | Bottleneck-economy value function, goal-guarded trades, purchase-completion search, exact steal expectation, terminal safety | 72–78% vs F; 2.8 pp above B02 on identical boards 935000 | yes (base) |
| B01 v004 | 4:1-trade + two-Road win certificate | +0.4 pp vs v002; fixes a reproduced missed win | yes |
| B01 v005 | Production-aware purchase priority | +0.4 pp vs v004 | yes (C01 starts from v005) |
| B05 v004 | Reserve up to 2 search roots that make real purchase progress (deficit-reducing trade/YOP/Monopoly, site-opening Road) | +0.8 pp [0.0, +1.8], 5 vs 1 unique wins | **transplanted** |
| B05 v004 | Completion scan from 8 VP incl. Road/Knight bonuses | part of the same +0.8 pp | **transplanted** (B01 checked only City/Settlement from 9 VP) |
| B02 v001/v002 | City-investment window, wheat/ore opening, Army buy bonus (`engine=True`) | −2.8 pp vs B01 on identical boards; v002 +0.0 | excluded |
| B01 sprint / teammate-v003 | Opening weight or expansion tweaks, deeper search | 0 measured gain | excluded |

Code changes versus B01 v005: `EconomyPolicy.reserve_enablers` (new), the root frontier in
`complete_purchases` (greedy 3 + up to 2 enablers; B01's alternative-family rule when none),
and the endgame completion scan (from 8 VP, adds Road/Knight, deadline-checked). Everything
else is B01 v005 byte-for-byte.

## Results

All runs: unchanged F, 10 VP, original clock min(.300+.0125·decisions, 1.500) s, swapped
seats, both processes reset every 20 games, `team-work/member-3/implementation/run_comparison.py`.
Runs overlapped on a shared host, so absolute CPU is somewhat inflated.

| Run | Boards | Result | Pair-bootstrap 95% | Own CPU mean / p95 / max | Faults |
|---|---|---|---|---|---|
| **C01 vs F** | 947000–947249 | **398/500 (79.6%)** | 76.2%–83.0% | 279 / 490 / 950 ms | 0 |
| B01 v005 vs F (matched) | 947000–947249 | 401/500 (80.2%) | 76.8%–83.6% | 275 / 480 / 930 ms | 0 |
| **C01 vs B01 v004** (head-to-head) | 948000–948099 | **101/200 (50.5%)** | 46.5%–54.5% | 219 / 420 / 660 ms | 0 |

Faults = errors, timeouts, crashes, over-budget games and harness random moves, for both
sides of every run. No no-winner games. C01 seat split vs F: 196/250 first, 202/250 second.

**Paired C01 − B01 v005 on 250 identical boards:** 6 better, 9 worse, 235 identical; mean
−0.6 pp, bootstrap 95% [−2.0, +0.8]. The transplanted B05 traits changed the outcome on only
15 of 250 boards and produced **no measurable gain** over B01 v005.

## Correctness and packaging

`verify_c01.py` ran 46 methods on the frozen file and again on the ZIP-extracted file, all
passing: 15 terminal-win regressions, 18 economic contracts (including the exhaustive
conversion oracle), 4 sprint contracts (stale goals, reordered indices, observation
immutability, trade certificates), 6 two-Road win regressions, and 3 new C01 tests (enabler
reservation keeps only positive-progress roots and at most two; no-progress gives none; an
8-VP two-Road Longest-Road win is taken in both seats). ZIP contains only `agent.py`,
byte-identical to the tested source. Imports: math, random, time, catanatron only. The
extracted ZIP played 4 official-evaluator games vs F (boards 947900–947901): 0 errors,
0 timeouts, load 0.01 s (`zip-smoke-vs-F-4.txt`).

## Conclusion for submission

C01 is a **safe, fully verified submission**: ~80% vs F on these boards, zero faults, even
with B01 v004 head-to-head. It is **not stronger** than B01 v004/v005; it is statistically
indistinguishable from them. Choose between C01 and B01 v004 on other grounds (B01 v004 has
more review history and slightly lower CPU). 80% here vs 78% on 934000 reflects board
variation, not a gain.

Limitations: one 250-board group vs F and one 100-board head-to-head; no private-O or event
hardware test; component effects of the two transplanted traits are not separated.
