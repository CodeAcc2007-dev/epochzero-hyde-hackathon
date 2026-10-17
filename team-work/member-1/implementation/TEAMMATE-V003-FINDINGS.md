# B01 teammate-v003: independent upgrade findings

17 October 2026. Branch `member-1/b01-independent-upgrade`, run by Avadooth (Member 2) at the
user's request under `team-work/member-1/B01-UPGRADE-HANDOFF.md`. Owner of B01 remains Aroosh
(Member 1); human owner review is pending. Separate from the primary B01 sprint (which uses
boards 938000/939000 and its own `v003`): this work lives only in `bots/B01/teammate-v003/`,
and no frozen agent (v001, v002, primary v003) or anyone else's working tree was touched or
merged. Time box: about 20 minutes, so exactly one interpretable change was tested.

## Baseline verified

`bots/B01/v002/agent.py` SHA-256 `cc53c58ca1867678ad6be9ca074ed6dabdffb54aa9b1c7ca1d83f52271c723f4`
matches the handoff. F `72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613` matches.
Kit `04fffac9…`, engine `d3f4ad05…`.

## Plan (recorded before editing) and change

The handoff lists "opening resource bottlenecks" among useful directions and notes the primary
sprint is already changing **opening weights**, dynamic purchase goals and deeper search. To
stay independently measurable, this branch did not touch any weight or search bound. Instead it
adds a term v002's opening score does not have at all: **expansion potential**.

v002's non-engine initial-settlement score is immediate production (resource-weighted) plus a
diversity bonus; it never looks at where the next settlement can go. teammate-v003 adds

```
+ 0.25 * max(site_quality(m) for m two edges from the candidate, m in board_buildable_ids)
```

i.e. the best legal site a two-road follow-up can reach, using v002's own `site_quality`
(same resource weights and scarcity bonus). The engine branch (`engine=True`, unused by
`Agent`) and every other code path are byte-identical to v002. The 0.25 weight was chosen once
by reasoning about scale (site quality ~0.1–0.4 vs opening score ~0.5–1.3, so the term
reorders only near-ties); it was **not tuned** on any game results.

## Checks run

- 60 seeded games' full initial-placement phases, both seats: every returned index is an
  `int` in range; game state (player state, buildings, roads) unchanged after `decide`; the
  new term changes **40 of 240** initial-settlement choices versus v002.
- ZIP `artifacts/B01-teammate-v003.zip` contains only `agent.py` (built with Python
  `zipfile`; no `zip` binary on this machine). Extracted file is byte-identical to the source
  (`504f1130…`). The **extracted packaged file** played 4 clocked games vs F (boards
  942900–942901, outside the confirmation range): 0 errors, 0 timeouts/crashes, 0 games over
  budget, load 0.02 s. Loading evidence only, not strength.

## 500-game confirmation vs unchanged F, boards 942000–942249

Both runs used unchanged F, 250 boards × swapped seats, 20-game chunks (both agents reload per
chunk), same global indices. They ran concurrently on the same machine, so absolute CPU is
somewhat inflated for both; the comparison between them is like-for-like.

| Run | Wins/500 | Win rate | Pair-bootstrap 95% | Mean / p95 / worst own CPU per game | Faults (err/timeout/crash/over-budget/random) |
|---|---:|---:|---|---|---|
| **B01 teammate-v003** | 361 | 72.2% | 68.4%–76.0% | 246 / 530 / 760 ms | 0/0/0/0/0 |
| B01 v002, matched baseline | 361 | 72.2% | 68.4%–76.2% | 242 / 520 / 820 ms | 0/0/0/0/0 |

F also had zero faults in both runs; no no-winner games. Seat split: v003 180/250 first,
181/250 second; v002 178/250 first, 183/250 second.

**Paired board comparison (v003 − v002, 250 boards):** 22 boards better, 21 worse, 207
identical; mean difference **0.000**, paired bootstrap 95% [−0.028, +0.026].

### Decision: keep the v002 baseline

The expansion-potential term is **not supported**: it changed about one in six opening picks
but produced exactly the same win total on identical boards, with the paired interval centred
on zero. It costs a few ms of CPU per game for no measured benefit. **Recommendation: submit/keep
B01 v002 (`cc53c58c…`, `artifacts/B01-v002.zip`), not teammate-v003.** teammate-v003 and its
ZIP are kept only as a frozen, rejected experiment with full evidence.

Note on board variation: v002 scored 72.2% on 942000, versus 78.0% on 934000 and 74.2% on
935000 per the handoff. This is another reminder that a single board group's percentage is not
a stable strength estimate; only same-board paired comparisons are meaningful.

Raw records: `implementation/results-teammate/B01-teammate-v003-vs-F-942000/` and
`implementation/results-teammate/B01-v002-vs-F-942000-matched/` (`games.json`, `summary.json`,
`metadata.json` with source fingerprints; the driver asserted sources unchanged at the end).

Commands (repository root):

```
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-1/bots/B01/teammate-v003/agent.py --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 942000 --chunk-size 20 \
  --out team-work/member-1/implementation/results-teammate/B01-teammate-v003-vs-F-942000
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-1/bots/B01/v002/agent.py --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 942000 --chunk-size 20 \
  --out team-work/member-1/implementation/results-teammate/B01-v002-vs-F-942000-matched
```

Boards 942000–942249 are now used confirmation evidence; do not tune on them.

## Limitations

- One change, one board group, one weight, no ablation sweep (time box). Board variation is
  large: the handoff records the same v002 source at 78.0% on 934000 and 74.2% on 935000.
- Distance-2 ring ignores whether the opponent's second placement will take the site first,
  and does not price ports.
- The 4-game packaged smoke ran while the two 500-game runs used the same machine, so its CPU
  figures are inflated; the 500-game files carry the per-game CPU.
- No head-to-head against the primary sprint's v003 or any other bot was run.
