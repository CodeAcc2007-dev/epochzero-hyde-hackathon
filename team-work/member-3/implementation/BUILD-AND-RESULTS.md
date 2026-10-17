# Pranesh: B05/B06 build and verified local results

17 October 2026. **Completed and ready for team review.** Active versions: **v003**. Primary assistant implemented strategy/core and verified results at Pranesh's explicit request; Hyde supplied reviewed helper/test drafts. No SSH, portal action or scored event submission. No runtime LLM, training, external-corpus labels or environment copy.

## Main result: 1,000 clocked games per bot against unchanged F

| Candidate | Wins/games | Win rate | Pair-bootstrap95% (descriptive) | Mean CPU/game | CPU p95 | Worst CPU/game | Exhausted games | Faults |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| **B05 v003** | 729/1000 | 72.9% | 70.3%–75.7% | 160.2 ms | 300 ms | 530 ms | 0 | 0 |
| **B06 v003** | 695/1000 | 69.5% | 66.9%–72.2% | 100.2 ms | 170 ms | 300 ms | 0 | 0 |

Both used the same500 paired boards (841000–841499), alternating seats, original ten-VP rules and original clock. **No no-winner games or harness random fallback moves** in either main run. B05 seat wins:363/500 first and366/500 second. B06 seat wins:334/500 first and361/500 second. Inspect every game; no loss/fault was dropped.

The driver calls the unchanged official `match.play_chunk` and reloads both processes every20 games, preserving original global indices. That lifecycle is explicit and differs from a single uninterrupted CLI1,000-game run. Local public-key results do not establish O/private-board strength or AMD scorer timing. Hardware: Intel i7-14650HX; no peak-memory measurement claimed. Original F/harness/evaluator/observation files were byte-checked against the pinned organizer commit and the checkout stayed clean.

## Control and direct comparison

The shared one-step greedy control won **273/400 (68.25%)** versus F, mean CPU100.5ms/game. On the same first400 games, B05 won298 (74.5%) and B06 won292 (73.0%). This separates the new tactical layers from the shared base; it does not credit all improvement over F to the layers.

| Matched comparison | Observed difference | Paired bootstrap95%, unadjusted/descriptive |
|---|---:|---|
| B05 minus B06, 1,000 games each | +3.40 pp | +0.90 to +5.90 pp |
| B05 minus control, first400 | +6.25 pp | +2.50 to +10.25 pp |
| B06 minus control, first400 | +4.75 pp | +1.75 to +7.75 pp |

These are three exploratory comparisons, not multiplicity-adjusted simultaneous guarantees. Conservative independent-pair Hoeffding bounds are also in the JSON and are wider. Bootstraps depend on pair/lifecycle assumptions; confidence is not proof that all opponents favor the same candidate.

A separate200-game direct matchup on boards855000–855099 ended **B05 103 wins, B06 97 wins**, no draws/no-winners/faults/exhaustion. B05 win rate51.5%; descriptive paired interval46.0%–57.0%. **This does not establish a decisive head-to-head winner.**

Recommendation: carry B05 as the stronger observed F-anchor candidate and B06 as a faster distinct alternative. Retain both for clashes with the other six bots; do not declare either the final event winner from this evidence. No runtime weights/code changed after the v003 test freeze.

## Ready-to-use code and packages

- [B05 v003 source/manifest](../bots/B05/v003/README.md) · [standalone ZIP](../artifacts/B05-v003.zip)
- [B06 v003 source/manifest](../bots/B06/v003/README.md) · [standalone ZIP](../artifacts/B06-v003.zip)
- [Package verification and SHA-256](../artifacts/package-verification.json): each ZIP contains only `agent.py`, `member3_core.py`, `race_math.py`, `manifest.json`; CRC/hash checks passed. Each clean extraction completed four additional clocked F smoke games without faults/exhaustion. The 2/4 wins each are loading checks, not strength evidence, and are not pooled into the main result.

Reuse the supplied environment. No environment, raw dataset, secret, provider reasoning/log or compiled binary is included. ZIPs are around8KB, far below the event artifact size limit; no event upload was made.

## Verification and development history

- **22 primary semantic/policy tests +4 reviewed helper tests passed**, including486 card-enumeration subcases. [Exact methods/hashes](semantic-verification.json), [primary tests](test_policies.py), [reviewed helper tests](test_race_math.py).
- Constructed engine fixtures check legal transitions plus resource/deck/piece/VP invariants. They are **not complete reachable histories**; the synthetic terminal guard probes are not a demonstrated Road-cut trace. Tested cases include trade→city, road→settlement, YOP→city, Knight terminal before roll/robber, new-dev restrictions, forced free roads, out-of-turn discard quota, random steal expectation, Monopoly, bank-limited YOP and strict bonus ties/transfers.
- v001 development smoke: B05 9/12, B06 10/12 on711000–711005; tiny samples retained separately. v002 B05 was deliberately interrupted for source-review guard correction after240 retained games (170 wins); next unfinished chunk excluded. This was not a match-discovered bug or a finished1,000-game result. A fixture's initial road geometry assumption failed and was corrected by actual legal-path enumeration; it is documented in the decision record.
- Main comparisons contain2,600 completed games; package checks add8. Including264 retained preliminary records gives**2,872 retained completed harness game records**. Fixtures/initial partial API plies and the interrupted unfinished chunk are not added to that count.
- Frozen source fingerprints were checked after each full run. The final ZIPs match those Python files exactly. No environment upgrade or source patch was used to obtain a win rate.

## Evidence and reproducibility

[Evaluation plan/commands](EVALUATION-PLAN.md) · [strategy and decisions](STRATEGY-AND-DECISIONS.md) · [Hyde jobs/review](JUNIOR-AND-VERIFICATION-LOG.md) · [machine-readable round summary](ROUND-1-SUMMARY.json) · [hardware](hardware.json).

| Run | Full per-game records | Summary / metadata |
|---|---|---|
| B05 vs F | [1,000 records](results/B05-v003-vs-F/games.json) | [Summary](results/B05-v003-vs-F/summary.json), [metadata](results/B05-v003-vs-F/metadata.json) |
| B06 vs F | [1,000 records](results/B06-v003-vs-F/games.json) | [Summary](results/B06-v003-vs-F/summary.json), [metadata](results/B06-v003-vs-F/metadata.json) |
| Greedy control | [400 records](results/greedy-control-vs-F/games.json) | [Summary](results/greedy-control-vs-F/summary.json) |
| B05 vs B06 | [200 records](results/B05-vs-B06/games.json) | [Summary](results/B05-vs-B06/summary.json) |
| v001 development | [B05](results/B05-dev-v001/games.json), [B06](results/B06-dev-v001/games.json) | Kept separate from final evidence |
| Interrupted v002 | [240 retained records](results/B05-v002-vs-F-heldout/games.json) | [Partial summary](results/B05-v002-vs-F-heldout/partial-summary.json), [interruption metadata](results/B05-v002-vs-F-heldout/metadata.json) |

Replay original board/seat pairs and **global game indices** in the same20-game process chunks. F owns an RNG that persists within a chunk; an isolated game with a reset process is not necessarily identical. The driver refuses to overwrite evidence; use a new output directory. Soft CPU cutoffs may vary search breadth by machine. `repository_base_commit` in metadata identifies the parent checkout at start; actual new bot source is pinned by per-file/fingerprint hashes, and is published alongside the results.

## Next improvement round

Use [specific improvement tickets](ROUND-1-IMPROVEMENTS.md) after other members upload. Main remaining gaps: broader opponent styles/private O, full Road-cut reachable fixtures, deeper chance/hidden-card-history models, search-cost attribution and stronger per-decision replay traces. Future revisions need new versions and fresh seed groups. These used evaluation boards are not untouched future confirmation data.

Teammates can start from the [GLM context prompt](../../GLM-START-PROMPT.md), changing their member name. This task implemented only Pranesh's two bots and prepared that shared prompt.
