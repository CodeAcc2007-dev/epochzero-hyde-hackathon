# B03/B04 v003: build, regressions and 500-game evaluation

17 October 2026. Owner: **Avadooth (Member 2)**. This round implements the P1 tickets from
the 2026-10-17 independent review (`team-work/reviews/2026-10-17-B03-B08/08-GLM-IMPROVEMENT-CONTEXT.md`,
`IMPLEMENTATION-CONTRACT.md`) against the exact v002 parents at commit
`791e6705d09f62ceba691777e041980d673f1c69` (hashes verified again in
`test_b03_b04_v003.py::ParentHashTests` before any change was made). v001 and v002 are
preserved unchanged; this is a new `v003` directory for each bot. See
`bots/EVIDENCE-INDEX.md` for the v001/v002 provenance corrections (ticket M2-E01).

## What changed and why (ticket by ticket)

| Ticket | Bot(s) | Verified or hypothesis | Fix |
|---|---|---|---|
| M2-C01 | both | verified (failure-injection probe) | Per-candidate try/except instead of one decision-wide try/except; best already-scored action is retained as incumbent when a later candidate fails; internal `self.diagnostics` counters (never printed/written) |
| M2-C02 | both | verified (dominance-argument gap) | Explicit `game_copy.winning_color() == me` short-circuit before heuristic scoring; bypasses base_fn and the bonus term entirely on a confirmed win |
| CPU budgeting | both | contract requirement | `obs.cpu_left` now read; below `CPU_SAFETY_FLOOR=0.05s`, skip the full simulate-and-score loop for a cheap win-only check |
| B03-01 | B03 | **verified** (constructed node-39 fixture) | `_opp_reach` now seeds from the opponent's full connected-component node set, not just their building nodes; filters to `board_buildable_ids` |
| B04-01 | B04 | **verified** (constructed road-prefix fixture) | Newly-reached road endpoint determined from pre-action connectivity, not tuple position |
| B04-02 | B04 | **verified** (exact-threshold probe) | Zero production -> zero bonus (was `scale*0.1`); generic 3:1 port requires real 2x-pip surplus; `PROBA_6` now exact `5/36` |
| B03-02 | B03 | **hypothesis, deferred** | See "Deferred tickets" below |
| B04-03 | B04 | **hypothesis, deferred** | See "Deferred tickets" below |

Every P1 fix above has a regression in `test_b03_b04_v003.py` that reproduces the parent
(v002) defect on the review's own constructed fixture *before* asserting the v003
correction on the identical fixture -- see the test run below. No regression was written
against a hypothesis (B03-02/B04-03), consistent with the contract's instruction that "a
hypothesis is an experiment, not an established improvement."

## Deferred tickets: B03-02 and B04-03 (P2 hypotheses)

Both are explicitly marked P2 ("hypothesis") in the review, not verified defects, and the
contract asks for "one interpretable change at a time" with the P1 correctness tickets
first. Rationale for deferring both in this round:

- **B03-02** (route-cost-aware denial pricing) requires a real shortest-path/resource-cost
  model over the contested node, not just membership in `_opp_reach`. Building and
  validating that model well enough to trust is a comparably sized change to the P1 fix it
  would sit on top of, and the contract explicitly warns against conflating a coefficient
  retune with the spatial identity B03 is supposed to keep ("retain B03's spatial identity
  rather than merely tune F's coefficient scale").
- **B04-03** (bounded port-to-purchase trade-chain search) needs a visited-state/horizon
  search over MARITIME_TRADE sequences with bank-stock and reserved-ingredient bookkeeping.
  That is new search logic, not a correctness fix to existing logic, and the contract
  separately asks to "compare a port-term-disabled control and corrected B04 on fresh paired
  boards before claiming the specialization helps" -- a claim this round is not making.

Both remain open for a subsequent `v004` round, each as its own isolated experiment with its
own ablation control, per the contract's evidence sequence.

## Regressions (run before any main evaluation)

```
./team-work/run-python.sh -m unittest team-work/member-2/implementation/test_b03_b04_v003.py -v
```

All 10 tests pass: parent-hash verification, the B03-01 node-39 reproduction-then-fix, the
B04-01 endpoint reproduction-then-fix, the B04-02 zero-production/exact-5/36
reproduction-then-fix, the M2-OBSERVABILITY total-failure-vs-partial-failure contrast, two
guaranteed-win checks (including a COMMON-01-style near-exhausted-clock case), and a
both-bots/both-seats legality and non-mutation check.

## Smoke (loading/fault diagnosis only, not strength evidence)

```
./team-work/run-python.sh team-work/member-2/implementation/run_v003_smoke.py
```

5 batches x 16 games = 80 games (B03 v003 vs F, B04 v003 vs F, B03 v003 vs B04 v003, each
v003 vs its own v002 parent). **Zero faults** (errors/timeouts/crashes/overruns) across all
80 games on both sides; CPU means 0.18-0.26 s/game, comfortably inside the per-game budget.

## Main evaluation: 500 games per bot vs unchanged F, with matched-parent comparison

Per the contract's evidence sequence (step 5): each v003 bot played 500 games (250 board
pairs, both seats) against unchanged F, and the v002 parent was separately replayed on the
**identical** board group so differences are paired, not just two different samples.
Board groups: B03 uses 933000-933249 (disjoint from the review's own 932000-932249 and
checked against every other member's recorded `seed0` before use); B04 uses 933500-933749.
934000-934249 remains reserved and unused for a later confirmation round.

Exact commands:

```
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-2/bots/B03/v003/agent.py --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 933000 --chunk-size 20 \
  --out team-work/member-2/implementation/results/B03-v003-vs-F-dev-500

./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-2/bots/B03/v002/agent.py --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 933000 --chunk-size 20 \
  --out team-work/member-2/implementation/results/B03-v002-vs-F-dev-500-matched

./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-2/bots/B04/v003/agent.py --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 933500 --chunk-size 20 \
  --out team-work/member-2/implementation/results/B04-v003-vs-F-dev-500

./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-2/bots/B04/v002/agent.py --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 933500 --chunk-size 20 \
  --out team-work/member-2/implementation/results/B04-v002-vs-F-dev-500-matched
```

### Results

| Run | Wins/500 | Win rate | Pair-bootstrap 95% | Mean own CPU/game | Worst own CPU/game |
|---|---:|---:|---|---:|---:|
| **B03 v003 vs F** (boards 933000-933249) | 260 | 52.0% | 48.6%-55.6% | 173.4 ms | 500 ms |
| B03 v002 vs F, matched parent (same boards) | 232 | 46.4% | 42.6%-49.8% | 175.1 ms | 490 ms |
| **B04 v003 vs F** (boards 933500-933749) | 216 | 43.2% | 39.8%-46.6% | 183.9 ms | 420 ms |
| B04 v002 vs F, matched parent (same boards) | 214 | 42.8% | 39.6%-46.2% | 185.2 ms | 490 ms |

**Paired board-pair comparison** (250 board pairs each, identical boards/global indices/seat
swaps for the v003 and matched-v002 runs, per the contract's step 5):

| Bot | Board pairs where v003 > v002 | v003 < v002 | v003 == v002 | Mean paired win-rate difference |
|---|---:|---:|---:|---:|
| B03 | 64 | 39 | 147 | **+0.0560** |
| B04 | 40 | 36 | 174 | **+0.0040** |

### CPU and faults

**Zero faults across all 2,000 games recorded in this round**: 0 errors, 0 timeouts, 0
crashes, 0 games-over-budget, 0 harness random-fallback moves, for both the v003 agents and
both matched-parent v002 replays, on both sides (own and F's). CPU means stayed at
173-184 ms/game, essentially unchanged from v002 (the operational hardening added a
few extra `winning_color()` checks per candidate but no new expensive computation) and well
inside the per-game allowance (`min(0.300 + 0.0125*decisions, 1.500)` s; worst single-game
own CPU recorded was 500 ms).

## Honest interpretation

**B03**: the `_opp_reach` fix (B03-01) plus the operational hardening produced a real, if
modest, improvement on this board sample: 52.0% vs the matched parent's 46.4% on the
identical 250 boards (+5.6 percentage points), with nearly twice as many board-pairs
improving (64) as worsening (39). The two bootstrap intervals barely separate (v003's lower
bound 48.6% just above v002's upper bound 49.8%), so this is suggestive rather than
conclusive at this sample size, but it is the first time either of these bots' win rate
against unchanged F has reached statistical parity with F (the bootstrap interval for v003
includes exactly 50%). This is **one board group, one evaluation round** -- not a claim of
beating F in general, and not yet confirmed on a held-out group (934000-934249 remains
reserved for that).

**B04**: the endpoint fix (B04-01) and the zero-production/exact-threshold fix (B04-02) are
both independently verified correctness fixes (see the regressions above) -- the port bonus
no longer rewards the wrong road endpoint or an unjustified port. But on this board sample
they produced **no measurable change** in B04's win rate against F: 43.2% vs the matched
parent's 42.8% (+0.4 percentage points, well within noise -- 40 board-pairs improved, 36
worsened, 174 unchanged). The honest reading is that these specific defects were real but
apparently did not fire often enough on this board group to move the aggregate win rate;
B04-03 (the deferred port-to-purchase trade-chain hypothesis) remains the more likely lever
for a measurable gain, since the current port bonus still only affects BUILD_SETTLEMENT and
BUILD_ROAD, never MARITIME_TRADE itself. B04 still trails B03 by a wide margin on both the
v002 and v003 comparisons.

**Across both bots**: fixing a verified correctness defect does not automatically produce a
measured strength improvement (B04), and a correctness-plus-hardening round can produce a
real gain even without touching the strategic hypothesis (B03). Neither result should be
read as "B03 now beats F" or "B04's fixes were pointless" -- both are single-round,
single-board-group observations pending a confirmation run and human (Avadooth) review.

## Boundaries kept

No other member's bots/research/files were touched. The shared `run_comparison.py` driver
and the engine/kit were not modified. The shared junior runner change from the
`member-2/avadooth-bots` branch's earlier commit was not re-merged into anything here (per
the contract: "That runner change was not merged here; do not replace the working local
runner/provider as part of a bot improvement" -- it stays as a prior, separate commit on
this branch). No SSH or event-portal action was taken. Human (Avadooth) review of this round
remains pending.
