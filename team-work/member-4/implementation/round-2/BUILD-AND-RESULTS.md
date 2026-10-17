# Member 4 round 2: corrections and matched results

Completed 2026-10-17T16:03:39.505267+05:30 (India time). User-authorized local implementation; **human verification pending, not published or submitted to the event**. Parent files are preserved. These are measured new candidates; correctness repairs and a headline win rate do not prove broad strategic superiority.

## Fresh frozen comparison

| Candidate | New vs unchanged F | Matched parent vs F | Change [descriptive paired95%] | Mean CPU new / parent | New p95 / max CPU |
| --- | --- | --- | --- | --- | --- |
| B07 v002 | 369/500 (73.8%) | 369/500 (73.8%) | +0.0 pp [+0.0, +0.0] | 125.0 / 120.8 ms | 290 / 550 ms |
| B08 v002 | 359/500 (71.8%) | 355/500 (71.0%) | +0.8 pp [-1.8, +3.6] | 363.4 / 414.2 ms | 590 / 1050 ms |

Every listed new/parent/F run recorded **zero errors, timeouts, crashes, clock overruns and harness random moves**. All outcomes were retained; counts and means were recomputed from 500 individual records for every run.

- **B07:** new descriptive win-rate range 70.0%–77.4%; first-seat wins 188/250, second 181/250. New-only wins 0, parent-only wins 0. No-winner counts new/parent 0/0. Reset-chunk sensitivity range for the win-rate difference: [+0.0, +0.0] pp. [New records](main/B07-v002-new-vs-F-500/games.json), [parent records](main/B07-v001-parent-vs-F-500/games.json).
- **B08:** new descriptive win-rate range 68.0%–75.4%; first-seat wins 178/250, second 181/250. New-only wins 26, parent-only wins 22. No-winner counts new/parent 0/0. Reset-chunk sensitivity range for the win-rate difference: [-1.6, +3.4] pp. [New records](main/B08-v002-new-vs-F-500/games.json), [parent records](main/B08-v001-parent-vs-F-500/games.json).

Both versions use exactly the same 250 fresh boards 934000–934249, swapped seats, global indices 0–499, ten VP and original cumulative clock (300 ms + 12.5 ms/decision, max 1.5 s/game). Both agent processes reload every 20 games. This lifecycle differs from one uninterrupted official CLI pair. Unchanged F SHA-256 `72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613`. Kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`; engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Per-run metadata includes exact commands, source hashes, interpreter, platform and lifecycle. [Harness/hardware verification](harness-and-hardware.json) records unchanged source bytes and the installed engine commit.

The main comparison was specified before running and all source bytes were frozen. These are untouched first-evaluation/confirmation boards for this revision; no tuning followed these outcomes. Across both members: 2,000 new-candidate games + 2,000 matched-parent games = 4,000 main games, plus 24 separate smoke games. The four 100-action external diagnostic histories did not finish games and are not pooled. No extra full tournament or component-ablation games were run.

Paired intervals resample 250 board-pair win differences 2,000 times. They are descriptive, unadjusted across four candidates and affected by time-based cutoffs/process RNG. An interval containing zero does not establish a gain; an interval excluding zero is still not private-event certification. A second descriptive sensitivity range resamples the 25 process-reset chunks (ten board pairs each), acknowledging within-process RNG dependence; it is also unadjusted and does not certify independence from host effects. Multiple changes within a bot cannot be causally separated by this version-level comparison. Historical results on other boards are not an eight-bot leaderboard.

B06 and B07 had identical 500 paired win/loss labels between revisions in this batch, so their resampled differences degenerate to [0, 0] by construction. This does not prove equivalent policies or equal future strength: resampling cannot generate unobserved disagreements, and other boards/opponents may differ.

## What changed

B07/B08 v002 share a bounded public terminal selector before emergency fallback, including copied engine settlement/Road bonus changes and strict eligible Army wins. At most 12 build copies are examined; this is not exhaustive.

B07 distributes its existing eight-reply budget across dev families, ranks YOP by feasible purchase deficits and removes zero-theft Monopoly choices. Three explicit root/own/full forecast controls exist for diagnostics; the submitted candidate keeps full sampled replies. The six-option free-road shortlist and pre-roll forecast horizon remain bounded limitations. B08 adds eligibility delay when a required Knight is not already playable, and a 128-entry per-decision potential cache keyed by full plan menu, hand, production rates, port ratios, bank and VP gap. The two-roll-unit scaling is a route heuristic, not exact elapsed dice rolls or an expected time-to-Army model.

[Precommitted plan](PLAN-AND-DECISIONS.md), [ticket-by-ticket verification and remaining scope](VERIFICATION-AND-SCOPE.md), [Hyde review](HYDE-REVIEW.md). Broader suggested experiments remain explicitly deferred; this round does not claim every research hypothesis is solved.

## Verification and diagnostics

- 18 new regression methods plus 36 adapted existing contract methods passed on actual standalone artifacts. Independent 18,225-case single-trade and 18,225-case preserved conversion-helper oracles are embedded in these methods. [Semantic evidence](semantic-verification.json). Constructed fixture allocations are not all reached histories.
- Parent low-clock failures were reproduced before asserting corrected behavior in both seats. New Knight purchase restrictions and strict Army ties, actual eight-VP Road wins, chance boundaries, immutability, bank/piece/port checks, reply ordering and cache invalidation are covered. Two test expectations were broadened to accept an earlier legal Road-bonus win; the engine winner still must match.
- The bounded terminal selector was profiled over 200 constructed calls per bot: see [isolated CPU measurements](terminal-profile.json). These omit serialization and do not certify scorer timing or zero-credit feasibility.
- [External partial-history profiles](diagnostics.json) record copies, nodes/roots, cutoffs and route-cache counts. B05 rescued one enabler in its short trace; B08 had 117 cache hits. B07's short trace never reached the held-opponent-dev gate, so useful reached reply attribution remains unestablished despite constructed control tests. No Road-cut full-history acceptance claim.
- Hyde GLM-5.3 Flash job 20261017T100054Z-841863a8 supplied pure trade/eligibility math. Primary reviewed every statement, corrected only misleading timing-unit documentation and independently verified the code. No API call is made by any bot. A second 104.589 s Hyde mechanical source inventory was independently checked/corrected; see SOURCE-INVENTORY.md. Provider logs remain local.

## Files and handoff

- [B07 v002 agent.py](../../bots/B07/v002/agent.py), [manifest](../../bots/B07/v002/manifest.json), [ZIP](../../artifacts/B07-v002.zip).
- [B08 v002 agent.py](../../bots/B08/v002/agent.py), [manifest](../../bots/B08/v002/manifest.json), [ZIP](../../artifacts/B08-v002.zip).

## Interpretation and next review

- **B07:** A win-rate gain is not established by both descriptive ranges; retain this as a correctness-repaired review candidate, without claiming it is stronger. Next bounded question: compare root/own/full controls with useful reached reply traces, after human review and using fresh boards. No further tuning was performed here.
- **B08:** A win-rate gain is not established by both descriptive ranges; retain this as a correctness-repaired review candidate, without claiming it is stronger. Next bounded question: separate eligibility-delay correction from cache/performance changes, after human review and using fresh boards. No further tuning was performed here.

Each ZIP contains only the exact standalone agent.py; CRC, hash, clean extraction/load, development/frozen byte identity and executable-AST assembly checks passed. [Package evidence](package-verification.json). Reuse the supplied environment; no key, dataset, network, worker, installed dependency tree or sibling Python module is required by the package. No runtime file logging was added.

The original parent/component sources and organizer tracked files were verified unchanged after evaluation. New files are identified by hashes, while metadata repository_base_commit is the existing parent publication, not a claim these uncommitted revisions already exist on GitHub. Peak memory and event hardware/private O were not measured. Host may have unrelated user activity; own-process CPU is reported. Additional dynamic parent timing differences should not be interpreted as a cache-only speedup.

Run the existing shared launcher for reproduction. The main runner is `team-work/member-3/implementation/round-2/run_round.py --phase main`; it refuses existing output paths and needs a new namespace/output for another run. Actual commands are retained in per-run metadata and evaluation-status-main.json. The verification entrypoints are `test_round2.py` and `verify_contracts.py` in Member 3's round-2 folder; they cover both authorized members and load the new frozen versions when present. Keep parents and these freezes intact; further changes need a new version and untouched boards.
