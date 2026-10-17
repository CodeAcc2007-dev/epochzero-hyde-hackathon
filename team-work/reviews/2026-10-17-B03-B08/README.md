# All eight bots: independent review and GLM improvement handoffs

17 October 2026. **Review complete; proposed fixes are not implemented.** Initially scoped to B03–B08; the user subsequently added the completed B01/B02. The directory retains its original name so running evaluation paths and evidence remain stable. All four owner handoffs below cover the current expanded scope. Research findings, older bots, frozen parents and other working changes were preserved. Nothing was merged, committed, pushed or submitted to the event by this review.

**Subsequent publication:** the user authorized sharing this review, owner handoffs and their local frozen parent files on GitHub. See the [publication record](PUBLICATION.md). Earlier local-only/publication-pending statements below describe the review's original completion time; they do not mean that proposed repairs were implemented.

## Give each owner this file

Each document starts with a ready-to-paste GLM prompt, then exact parent hashes, prioritized tickets, source/fixture evidence, proposed changes, acceptance tests, CPU risks and 500-game evaluation requirements.

| Owner | Bots and frozen parents | Direct implementation context |
|---|---|---|
| **Aroosh — Member1** | B01 v001 / B02 v001 | [Aroosh's GLM handoff](../../member-1/08-GLM-IMPROVEMENT-CONTEXT.md) |
| **Avadooth — Member2** | B03 v002 / B04 v002 | [Avadooth's GLM handoff](../../member-2/08-GLM-IMPROVEMENT-CONTEXT.md) |
| **Pranesh — Member3** | B05 v003 / B06 v003 | [Pranesh's GLM handoff](../../member-3/08-GLM-IMPROVEMENT-CONTEXT.md) |
| **Anni — Member4** | B07 v001 / B08 v001 | [Anni's GLM handoff](../../member-4/08-GLM-IMPROVEMENT-CONTEXT.md) |

All four use the [implementation/evidence contract](IMPLEMENTATION-CONTRACT.md). The compact [ZIP packet](B01-B08-GLM-Improvement-Handoffs-2026-10-17.zip) preserves repository-relative paths for the handoffs, review probes and evidence. It contains no runtime environment, credentials, dataset or raw provider logs; implementation sources remain in the owners' repository/workspace versions.

Member2 was fetched from `origin/member-2/avadooth-bots`, immutable commit **791e6705d09f62ceba691777e041980d673f1c69**. Its26 bot/report/test/result files were materialized in an ignored local snapshot; the branch was not merged. The shared runner modifications on that branch were not applied. Other parents are local frozen artifacts, not represented as newly published GitHub commits. All eight manifests match their runtime source hashes.

## Highest-priority findings

| ID / bots | Independently verified observation | Repair direction |
|---|---|---|
| **M1-GOAL-TERMINAL — B01/B02** | At 8 VP, both reject4 ORE→WOOD because it violates the retained city goal, although the next legal Road gains the bonus and wins. Both choose a nonterminal city instead. | Check bounded certain terminal completions before heuristic goal rejection; cover two-point bonuses from 8. |
| **COMMON-01 — B01/B02/B05/B06/B07/B08** | At 9 VP and 0.0009s remaining credit, all six END_TURN despite a legal winning settlement. Their early shortcut only handles a city. | Cheap terminal selection before generic low-clock fallback, with exact bonus/road-cut semantics. |
| **B03-01** | Opponent legal settlement node39 is already connected by a six-road network but absent from the two-hop-from-buildings contest set. | Count additional road cost from the usable existing network, then price real contest targets. |
| **B04-01 / B04-02** | Road(48,49) reaches new port48, but B04 scores already-connected49; zero specialized production still earns credit, and exact5/36 misses the rounded threshold. | Correct endpoint/connectivity logic; value incremental integer conversion and full acquisition cost. |
| **B06-01** | Current threat score0 misses a legal4 WOOD→ORE→city win in an explicit opponent post-roll9-public-VP fixture. | Add bounded conversion-enabled threat categories; keep future-roll uncertainty explicit. |
| **B07-01** | With all dev types, the eight-reply cap includes only YOP(BRICK,BRICK), omitting14 other legal YOP choices. | Deliberate family/goal coverage before more worlds; measure whether reply search helps. |
| **B08-01** | Army route with two Knights played and none held estimates zero delay for a new Knight, which cannot be played that turn. | Separate resource acquisition from earliest eligible own turn. |
| **M2-OBSERVABILITY — B03/B04** | An injected scoring exception returns END_TURN without reaching the harness error counter. Neither agent budgets using `obs.cpu_left`. | Strict diagnostic mode/counters, bounded work and preservation of a scored incumbent. |

These are counterexamples, source-exact limitations or explicit failure-injection probes, **not assertions that they caused the historical losses**. The probes use constructed engine states with checked invariants where applicable; they are not complete reached action histories. Reply truncation and B06's horizon are limited models, not illegal-action bugs. Owner files separately label unproven strategic hypotheses: B01 goal/discard stability, B02 investment payback, B03 productive denial, B04 conversion chains, B05 beam coverage, B06 defense cost, B07 forecast attribution and B08 route cost/caching.

## Verification completed

- **60 existing semantic/helper test methods passed again:** Member1=19, Member3=26, Member4=15. Embedded exhaustive helper oracles are included in those methods, not counted as separate test methods.
- **Nine finding groups reproduced** by [verify_findings.py](verify_findings.py), recorded in [verified-findings.json](verified-findings.json). These assertions intentionally demonstrate frozen defects. They must be converted to desired-behavior tests loading new versions; passing this old probe does not mean a fix passed.
- **68 new clocked smoke games:** seventeen4-game batches covering every bot versus F and selected peer pairs. All completed with zero recorded errors/timeouts/crashes/exhaustion/harness random moves. These small batches are loading/integration evidence, not a strength matrix.
- **1,000 new main games:**500 each for exact B03/B04 v002 versus unchanged F, documented below. All losses and counters retained.
- Recomputed all six existing local main-result win totals, checked their recorded source hashes, checked every Member2 v002 result aggregate/counter and identified repeated boards/old source hashes. Historical main games were not replayed.
- B01/B02/B07/B08 component hashes and assembled/development byte identity verified; B05/B06 manifest helpers verified. Official kit tracked files remain clean at the pinned commit. No bot runtime source changed in this review.

See [verification summary](verification-summary.json), [source and result audit](source-and-result-audit.json), [junior work and primary review](JUNIOR-REVIEW.md). The two bounded Hyde jobs supplied mechanical source checklists only; primary inspected their actual outputs, checked the engine, authored the counterexamples, ran tests/evaluations and wrote the strategy recommendations.

## Fresh main evaluation: Member2 uploaded v002

Both candidates played the same 250 boards **932000–932249**, swapped seats, ten VP, original cumulative clock, public local dice key. Sequential20-game process chunks preserve global game indices. Both reload at each chunk boundary. F and all candidate sources stayed unchanged. This differs from one uninterrupted official CLI process pair. The machine may also have had unrelated user activity; own-process CPU is reported, and no quiet-host or scorer-hardware certification is claimed.

| Candidate | Wins /500 | Win rate | Descriptive pair-bootstrap95% | Mean own CPU/game | Worst own CPU/game | Recorded faults/exhaustion |
|---|---:|---:|---|---:|---:|---|
| **B03 v002** |214|42.8%|39.2%–46.6%|129.8 ms|370 ms|0|
| **B04 v002** |214|42.8%|39.8%–45.6%|126.8 ms|280 ms|0|

Neither run had a no-winner outcome. F also had zero recorded faults/exhaustion. The identical totals do not mean the same games were won or that the policies are equivalent. These data show both lost more often than they won against this F setup; they do not identify which defect caused losses or establish private-event strength. Statistical ranges are descriptive and unadjusted. Internal exceptions swallowed by Member2's wrapper were not counted by the official harness; the new test documents that observability gap without inventing an internal-fault count.

- [B03 full500 game records](main/B03-v002-vs-F-500/games.json), [summary](main/B03-v002-vs-F-500/summary.json), [metadata and exact command](main/B03-v002-vs-F-500/metadata.json).
- [B04 full500 game records](main/B04-v002-vs-F-500/games.json), [summary](main/B04-v002-vs-F-500/summary.json), [metadata and exact command](main/B04-v002-vs-F-500/metadata.json).

The imported Member2 report has provenance issues: duplicate final F screens over the same boards/outcomes, some old-hash B04 smoke, pending manifest commit and an inconsistent 240-game headline. The audit preserves all records; owner ticket M2-E01 explains corrections. Do not count repeat screens as independent boards or treat the narrative mis-scaled experiment as separately reproduced evidence.

## Existing results retained as context, not an eight-bot leaderboard

| Bot | Existing F result | Board group | Verification this review |
|---|---:|---|---|
| B01 v001 |381/500 =76.2%|911000–911249|Hashes and recorded aggregate checked;19-test owner suite plus new probes/smoke|
| B02 v001 |359/500 =71.8%|911000–911249|Same|
| B05 v003 |729/1000 =72.9%|841000–841499|Hashes and recorded aggregate checked;26-test owner suite plus new probes/smoke|
| B06 v003 |695/1000 =69.5%|841000–841499|Same|
| B07 v001 |361/500 =72.2%|891000–891249|Hashes and recorded aggregate checked;15-test owner suite plus new probes/smoke|
| B08 v001 |363/500 =72.6%|891000–891249|Same|

Sources: [Member1 build/results](../../member-1/implementation/BUILD-AND-RESULTS.md), [Member3 build/results](../../member-3/implementation/BUILD-AND-RESULTS.md), [Member4 build/results](../../member-4/implementation/BUILD-AND-RESULTS.md). Different boards, tuning histories and sampling/process details prohibit a direct all-eight ranking from these percentages. No new full round robin, matched component ablations, full reached Road-cut trace, private O run or event validation was completed. Human owner reviews are not marked complete.

## Reproduce this review's counterexamples

From the repository root, with the existing shared environment:

```bash
git fetch origin member-2/avadooth-bots
python3 team-work/reviews/2026-10-17-B03-B08/snapshot_member2.py
./team-work/run-python.sh team-work/reviews/2026-10-17-B03-B08/verify_findings.py
./team-work/run-python.sh -m unittest discover -s team-work/member-1/implementation -p 'test_economy.py' -v
./team-work/run-python.sh -m unittest discover -s team-work/member-3/implementation -p 'test_*.py' -v
./team-work/run-python.sh -m unittest discover -s team-work/member-4/implementation -p 'test_member4.py' -v
```

The snapshot utility pins the exact commit and refuses to overwrite changed snapshot files. No checkout, merge, credential handling or environment install. Counterexamples depend on the pinned existing fixture helpers and all eight parent sources being available in the workspace. Member1/4 local files must be shared by their owner when moving this packet to another machine; the packet does not pretend they are already pushed.

For main reruns, use `run_comparison.py` and exact recorded metadata into new output directories. For next-version improvements, use the 500-game development/parent/confirmation sequence in the contract. Keep all used boards marked used. Improvements belong to their owners in new versions, followed by independent review.
