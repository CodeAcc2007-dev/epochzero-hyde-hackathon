# B01 eight-minute experiment: production-aware purchase priorities

Completed 2026-10-17T11:19:08.724151+00:00. **Recommendation: B01 v004.**

| Exact frozen source | Wins against unchanged F | Mean CPU / game | Maximum CPU / game |
|---|---:|---:|---:|
| New v005 | 383/500 (76.6%) | 262.1 ms | 750 ms |
| Matched v004 | 381/500 (76.2%) | 238.2 ms | 660 ms |

Difference: +0.4 percentage points; paired-board bootstrap 95% interval [-2.0, +2.8] points. Reset-chunk sensitivity interval: [-2.0, +2.8]. Candidate-only wins: 23; parent-only wins: 21. New bot seat wins: 193/250 first, 190/250 second. Aggregate errors, crashes, timeouts, random fallback moves, budget overruns and no-winner counters across both sides of both runs: 0.

The predeclared promotion gate requires zero faults and a positive lower paired-board interval. The gate did not pass. A strength improvement is not established; retain v004 for submission. v005 remains an experimental alternative, not the recommended replacement. No parameter sweep or additional matches followed the result.

## Different strategy tested

v005 discounts readiness for a purchase whose missing ingredients have slow public production. Other-resource production contributes an optimistic maritime conversion rate; existing conversion credits reduce each bottleneck. A capped multiplier in [0.625, 1] limits the change. Currently affordable or bank-convertible goals retain full value. This is a fluid heuristic, not an exact expected completion time: it ignores dice correlation, competition among simultaneous conversion requirements and future bank changes. The exact bank-aware base score still applies. Opening, tactical win certificates, legal trade guards and search caps are inherited unchanged from v004. [AST scope audit](source-diff-audit.json) confirms only the new helper and `EconomyContext.priority` changed. The inherited module docstring still says v004; the v005 directory, manifest and exact digest identify this frozen experiment.

## Verification and limits

47 regression/contract methods passed on the exact frozen module and again on the ZIP-extracted module: 15 terminal, 18 economic, 4 earlier strategy, 6 road-certificate and 4 new production tests. The economic suite includes exhaustive conversion-oracle cases. Original v004 and F hashes are unchanged. ZIP contains exactly the tested agent.py; CRC and byte equality passed. Imports remain math/random/time and the pinned catanatron engine. [Verification](verification.json), [test runner](verify.py), [Hyde review](HYDE-REVIEW.md).

Each bot played 500 games on the same fresh 250 boards 945000–945249, both seats, with module/process lifecycle resets every 20 games. Original clock: min(0.300 + 0.0125 × decisions, 1.500) seconds per game. The two match processes ran concurrently on a shared host; process CPU is measured, but hardware timing and search cutoffs need not reproduce exactly. These are local F comparisons, not an official tournament or direct v005-v004 match. Uncertainty is descriptive and clustered by board, with reset-chunk sensitivity. Historical 78% belongs to other boards and is not the matched baseline here.

[Candidate raw games](candidate-vs-F/games.json), [parent raw games](parent-vs-F/games.json), [candidate metadata/command](candidate-vs-F/metadata.json), [parent metadata/command](parent-vs-F/metadata.json), [audited comparison](results.json).

[Recommended agent](../../bots/B01/v004/agent.py). [Experimental v005 agent](../../bots/B01/v005/agent.py), [v005 ZIP](../../artifacts/B01-v005.zip). Candidate SHA256 `63ab59c8b302a863dab38e07c461338be7cbbbe91b254b96fe359c8786fb9bd5`.

All work reused the existing local environment. No SSH, event submission, downloaded dataset, environment or secret upload. Hyde drafted a small arithmetic review; the primary corrected two claims and independently implemented and verified the experiment. Preserve all frozen versions; future experiments require new versions and evidence.
