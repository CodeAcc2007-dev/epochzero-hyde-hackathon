# Avadooth: B03 / B04 v001 build and self-test report

17 October 2026. Owner: **Avadooth (Member 2)**, implemented with coding assistance in this
session (per the working agreement's junior-engineer workflow; all code was executed and
verified locally). Assignment: [`07-TWO-BOT-BUILD-ASSIGNMENT.md`](../07-TWO-BOT-BUILD-ASSIGNMENT.md).
Status: **built and self-tested; independent assistant review not started.**

## Artifacts

| Item | Path | SHA-256 |
|---|---|---|
| B03 v001 entrypoint | `bots/B03/v001/agent.py` | `190ade935a26f4ddc98dba39c62c64e068612fe513d4bf0c56dedf02cf208f0e` |
| B03 manifest | `bots/B03/v001/manifest.json` | (see file) |
| B04 v001 entrypoint | `bots/B04/v001/agent.py` | `75bd348de82418a89e0a51e0ddbe04db71c4a7e492cc082d56e628b748f1e7c5` |
| B04 manifest | `bots/B04/v001/manifest.json` | (see file) |
| Semantic cases | `bots/tests/semantic_cases.py` | `11e6312d5e49981b2fd375f317c7e06f8172709efe000dce3469c5f469dac594` |
| Batch runner | `bots/tests/run_batches.py` | `322e079fa32ae5d9f2714e4583e89bb8f77e6f2a7770376550d65cec4a4c8fd7` |
| Batch results (6 JSON) | `bots/results/*.json` | per-game records inside |

Pins: engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`, kit `04fffac9…` (both verified by
`pip` provenance / kit checkout at those revisions). Interpreter: Python 3.11.17, one thread
per numeric library, `PYTHONHASHSEED=0` (via `team-work/run-python.sh`).

## Environment (recreated locally, following 02-LOCAL-SETUP-AND-VALIDATION.md)

No supplied environment existed on this machine, so one was installed per the setup report's
recipe into `shared-local/` (gitignored, never committed): managed CPython 3.11.17 via uv,
CPU-only torch 2.8.0, and the organizer `requirements.txt` unpinned-except-for-pins. Actual
validated stack: catanatron 3.3.0 from the pinned commit (`direct_url.json` verified), networkx
3.6.1, numpy 2.4.6, scipy 1.17.1, scikit-learn 1.9.1, torch 2.8.0+cpu, `PYTHONHASHSEED=0`.
Organizer `selfcheck`: **all checks passed** (F CPU 137 ms mean/game, repeatability 976/976).
F-vs-random smoke: 20/20 F wins, 0 faults. Nothing in the shared kit/engine was modified.

## Design decisions (both bots)

- Single self-contained `agent.py` per bot; no shared code between the two bots, no
  environment copies. Deterministic: no sampling, no RNG use, pure table lookups
  (19 ms/game mean CPU vs F's ~150 ms — two orders of clock headroom).
- Contract: `decide(obs, playable_actions) -> int` index; never mutates the observation;
  never reads hidden dev identities or seeds; wrapped so any internal error falls back to a
  cheap legal index instead of raising to the harness.
- Opening: chooses from the actual legal node/edge lists each prompt supplies (no
  snake-order assumption; both seats handled from the visible state).
- Distinct objectives: B03 prices expansion + contest/denial of opponent-reachable sites;
  B04 prices port acquisition/conversion with a production-justified threshold, aggressive
  surplus-converting trades, and stops port-chasing when the opponent reaches 9 public VP.
  The two bots disagree on real boards (semantic case t04 shows a hand where B03 never
  trades and B04 converts).

## Commands (exact, from the repository root)

```bash
./team-work/run-python.sh team-work/member-2/bots/tests/semantic_cases.py
./team-work/run-python.sh team-work/member-2/bots/tests/run_batches.py smoke
./team-work/run-python.sh team-work/member-2/bots/tests/run_batches.py screen
./team-work/run-python.sh -m catan_kit.evaluate --a team-work/member-2/bots/B03/v001/agent.py \
  --b shared-local/organizer-kit/examples/f_agent.py --games 4 --seed0 771000
```

Hardware/load: local x86_64 Linux laptop, 24 logical CPUs, sequential runs, launcher pins
one thread per numeric library. These are local timings, not scorer certification.

## Results (all games official harness, unchanged F, both seats per board)

### Eligibility first

- **Faults: zero** across all batches below — 0 errors (illegal index/exception), 0 clock
  overruns, 0 timeouts, 0 crashes, 0 random fallback moves for both bots; load < 0.001 s
  (limit 60 s). Seat-paired records preserved per game in `bots/results/*.json`.
- Semantic cases t01–t06: **all pass** (legality, distance-rule invariant, road-not-to-nowhere,
  surplus-trade difference, port-term behavior incl. the opponent-at-9 cutoff, discard legality).
  t06 notes an INCONCLUSIVE branch when no 7-roll discard occurred in the driven games.

### Smoke batches (8 board pairs per matchup)

| Batch | A wins/games | Seat-paired (Hoeffding 95%) | No-winner |
|---|---|---|---|
| `dev-b03-vs-f-01` (B03 vs F) | 4/16 | 0.25 ± 0.48 | 0 |
| `dev-b04-vs-f-01` (B04 vs F) | 4/16 | 0.25 ± 0.48 | 0 |
| `dev-b03-vs-b04-01` (B03 vs B04) | 10/16 (B03) | 0.625 ± 0.48 | 0 |

### Screen batches (disjoint board groups; 40 boards => 80 games; pairing 20 boards => 40)

| Batch | A wins/games | Seat-paired (Hoeffding 95%) | A CPU mean/game | Faults (either side) |
|---|---|---|---|---|
| `screen-b03-vs-f-01` (B03 vs F) | 29/80 | 0.3625 ± 0.2147 | 0.0198 s | 0 |
| `dev-b04-vs-f-screen-01` (B04 vs F) | 18/80 | 0.225 ± 0.2147 | 0.0179 s | 0 |
| `dev-b03-vs-b04-screen-01` (B03 vs B04) | 22/40 (B03) | 0.55 ± 0.30 | 0.0240 s | 0 |

Interpretation: **smoke/screen evidence only, not final strength.** Both bots are
eligible (zero faults, zero exhausted clocks, genuine legal indices) but lose to unchanged
F at these sample sizes; B03 leads B04 head-to-head and against F. B04's port hypothesis did
not pay for itself on these boards yet. Full per-game records (board seeds, seats, turns,
CPU/wall/decisions/fault counters per seat) are preserved in `bots/results/*.json`.

## Bugs found and fixed during self-testing (kept in history)

1. `_road_score` call signature mismatch (TypeError at first midgame decision) — silently
   degraded the agent to END_TURN loops in the very first unclocked probe; fixed before any
   strength testing.
2. `_trade_value` missing after a rewrite — restored.
3. B04 lost the `CONTEST_PREMIUM` constant during conversion (NameError → fallback
   END_TURN loop, 0/10); restored.
4. B04's deficit metric originally took the min over all goals (insensitive); changed to
   the first unaffordable goal (city > settlement > road > dev). Semantic case t04 asserts
   the intended B03-vs-B04 trade-policy difference.

## Issues and limitations (honest)

- Both bots lose to F. Likely causes and next experiments are recorded in the manifests.
- No sampling of hidden dev worlds and no search: the bots are one-look evaluators on the
  actual legal actions; F samples a hidden world per decision.
- The contest/denial and port weights are hypothesis-level, consistent with the common
  plan's stop-condition (no Phase-2 measurement yet).
- No pip-only ablation and no port-disabled ablation were run (comparison variants are
  proposed, not built — this stays within the first-upload scope).
- Local runs only; O is unavailable locally, and event strength is unknown.
- Batches ran sequentially on a quiet machine; local timing does not certify the scorer.

## Boundaries kept

No other member's files were touched (`git status` shows only
`team-work/member-2/bots/` as new). No shared files changed; engine/kit untouched at the
reviewed pins; no environments, secrets, raw datasets or provider logs committed; the
shared environment lives in gitignored `shared-local/`. No SSH or event-portal actions.
