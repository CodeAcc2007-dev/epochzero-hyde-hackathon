# B01 final improvement sprint — verified results

Completed 2026-10-17T11:09:55.832534+00:00. User budget: 25 minutes from 10:51:45 UTC to 11:16:45 UTC. Recommendation: **B01 v004**. No event submission.

## Fresh matched comparisons

| Candidate | New vs unchanged F | Same-board v002 baseline | Difference | Board bootstrap 95% | Mean CPU new / old |
|---|---:|---:|---:|---|---|
| v003 | 374/500 (74.8%) | 375/500 (75.0%) | -0.2 pp | [-2.6, +2.2] pp | 228.5 / 214.5 ms |
| v004 | 390/500 (78.0%) | 388/500 (77.6%) | +0.4 pp | [-1.6, +2.4] pp | 239.3 / 209.4 ms |

Direct fresh comparison: **v004 251–249 v002** on 944000–944249; candidate board-bootstrap win-rate range [47.6%,52.8%]. [Direct records](direct-v004-vs-v002/games.json), [metadata](direct-v004-vs-v002/metadata.json). Zero recorded faults/clock overruns for both. This result is separate from F scores.

Every candidate, matched baseline and F recorded zero errors, timeouts, crashes, clock overruns, harness random moves and no-winner games. All 500 records in each run were independently audited, including source hashes, board/seat alignment, win counts and CPU. See [machine-readable audit](final-results.json).

- **v003:** boards 939000–939249; first/second-seat wins 182/250 and 192/250. Candidate-only wins 19, parent-only wins 20. Reset-chunk sensitivity [-2.8, +2.6] pp. p95 CPU 420 ms; max 580 ms. [Candidate records](confirmation/candidate/games.json), [matched baseline records](confirmation/parent/games.json), [metadata](confirmation/candidate/metadata.json).
- **v004:** boards 943000–943249; first/second-seat wins 193/250 and 197/250. Candidate-only wins 14, parent-only wins 12. Reset-chunk sensitivity [-1.2, +2.0] pp. p95 CPU 420 ms; max 710 ms. [Candidate records](tactical-confirmation/candidate/games.json), [matched baseline records](tactical-confirmation/parent/games.json), [metadata](tactical-confirmation/candidate/metadata.json).

These are descriptive paired-board bootstrap intervals (4,000 resamples), unadjusted for development selection and multiple comparisons. Reset-chunk sensitivity resamples the 25 process chunks because F maintains RNG state inside each chunk. If an interval includes zero, a win-rate improvement is not established. Different board groups cannot isolate v003 versus v004 effects; the new terminal repair is independently demonstrated in constructed states. The direct comparison is a local baseline match only; no private-O or private-event strength is claimed.

All runs use the unchanged original cumulative clock min(.300+.0125*decisions,1.500)s, 10 VP, 250 boards with swapped seats, public local dice key and process reload every 20 games. This differs from a single uninterrupted official process pair. The host was shared; some comparisons overlapped. CPU is measured per process, but these are not isolated CPU/scorer-hardware or peak-memory benchmarks. Exact kit/engine/OS/commands are in metadata.

The final v004 edges are only two wins in each comparison, so a strength gain is not established. The recommendation follows the predeclared point-estimate gates and the demonstrated tactical repair. Mean F-game CPU rose about 14.3% (239.3 ms versus 209.4 ms), with no recorded budget exhaustion. Preserve v002 as a lower-cost fallback.

## Selection and actual changes

Development used 100 games each on 938000–938049: v002 parent 75 wins, flexible menu 77, opening-only 75, combined 77, deeper search 77; all fault-free. Opening and deeper-search variants did not add observed wins and were not selected. This small development screen is selection evidence only. v003 retained the original opening, width 4/depth 3/52-expansion/22 ms caps. It dynamically reconsiders feasible purchase goals, allows ingredient-preserving trades toward alternatives within 85% of the best goal priority, reserves one root from another action family, and includes bank/trade history in continuation deduplication. The 85% margin is a hand-chosen policy constant, not a learned probability.

While v003 was frozen, an independent constructed 8-VP fixture exposed a missed certain win in both seats: Road length 3, hand (1,2,0,2,6), no port. Old policy builds a city, one road, and ends without winning. 4 ORE→WOOD followed by two legal roads wins immediately. v004 adds a public/own-state certificate before heuristic search, bounded to 80 copied executions, 12 enabling roots, 8 intermediate road states and an 8 ms total elapsed decision CPU sub-deadline. Legal resource cards and free Road Building are supported. Chance actions are not followed. The copied engine transitions and public hidden-VP bound determine certainty; cutoff/omission never proves no win exists. v003 and v004 were frozen before their respective fresh runs; no coefficients changed after confirmation.

## Correctness and package evidence

- v003: 37 methods passed on actual frozen and exact ZIP-extracted modules. v004: 43 methods on each form (15 terminal regressions, 18 inherited economic contracts, 4 sprint contracts, 6 new Road-chain regressions). Embedded exhaustive conversion and trade-certificate cases are included in those method counts. [v003 package audit](package-verification.json), [v004 package audit](tactical-package-verification.json).
- New coverage includes stale-goal switching, both-seat missed wins, original/reversed action indices, observation immutability, reserved ingredients, bank depletion, dev eligibility, strict opponent Road threshold, expired deadlines and free-road costs. Fixtures are constructed; repaired-event frequency in the main games was not instrumented.
- Four separately counted complete matches loaded the actual extracted v004 ZIP against F with zero faults. They are a packaging smoke check, not additional strength evidence. [Smoke metadata](zip-smoke/metadata.json).
- The two-road certificate was also profiled for 100 calls per constructed seat: about 1.15 ms and 0.95 ms mean, maximum 1.31 ms on this host, 10 copied executions per successful certificate. This excludes serialization and does not certify scorer timing. [Profile](two-road-profile.json).
- No runtime network, model, file I/O, dynamic execution or worker imports. Runtime uses math/random/time plus the pinned catanatron engine. ZIP contains exactly the tested agent.py; bytes and CRC verified. Original v002/F source hashes remain unchanged.
- Hyde GLM-5.3 Flash produced a mechanical invariant checklist and whitespace-only handoff cleanup; primary reviewed both, authored strategy/code and verified results. No junior code was accepted. [Hyde review](HYDE-REVIEW.md). The test-side-effect isolation correction and original diagnostic regeneration are recorded in [decision log](PLAN.md).

## Files and reproducibility

Recommended [B01 v004 agent.py](../../bots/B01/v004/agent.py) and [ZIP](../../artifacts/B01-v004.zip).

[v004 agent](../../bots/B01/v004/agent.py), [v004 manifest](../../bots/B01/v004/manifest.json), [v003 agent](../../bots/B01/v003/agent.py), [preserved 78% v002](../../bots/B01/v002/agent.py). The 78% figure belongs to the historical 934000 board group; it must not be pasted onto new files or compared as if it were this fresh baseline.

Use `./team-work/run-python.sh team-work/member-1/implementation/final-sprint/package_verify_tactical.py` for repeatable actual-package correctness checks. It creates only an agent ZIP/extract, never another environment. Main run commands are in each metadata.json; experiment drivers intentionally refuse existing frozen/output directories. Do not rerun benchmark drivers without a new request and new evidence paths. All 2,500 main games (2,000 F comparisons plus 500 direct), 500 development games and 4 separate ZIP smoke games are retained; no partial run is represented as complete.

Publication was explicitly authorized during the sprint. Only B01 scope and the separately requested B05 baseline/handoff are included in publication. Other pending teammate work remains local. No SSH, event submission, environment, credential, downloaded dataset or raw provider log upload.
