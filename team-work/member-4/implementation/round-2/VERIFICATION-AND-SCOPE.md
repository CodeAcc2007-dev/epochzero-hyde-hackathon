# Round 2 verification decisions and remaining scope

This round implements bounded corrections for Member 3 and Member 4 at the user's explicit request. All new runtime sources were frozen before the untouched main comparison; no main-result-driven tuning is permitted. Original parents, Member 1/2, research and old results remain unchanged. No GitHub publication or portal action is authorized by this round's handoff.

## Tests actually performed

18 new standalone-artifact regression methods and 36 adapted existing contract methods passed, first on development bytes and then on byte-identical frozen artifacts. They include two independent 18,225-case embedded two-resource exhaustive oracles (single-trade completion and the preserved route conversion helper), plus both-seat low-clock terminal builds, Road bonus from eight, eligible Knight/Army before rolling, new-dev/tie rejection, public simultaneous-qualifier bounds, immutability, chance boundaries, trade threat/denial, bank/port/piece restrictions, reply-family coverage/action-order invariance, control modes and cache equivalence/invalidation/bounds.

The old tests were adapted transparently: the parent-file identity assertion is separately covered by hash inventories; the new Monopoly selector evaluates only the two nonempty resource types in that existing fixture rather than five types; a Road→settlement case now accepts a Road-bonus win earlier in the same line. An initial new both-seat fixture also assumed only settlement could win, but an actual engine Road win was available; that action-type assertion was corrected without changing the policy. The first isolated profiling command mistakenly used system Python and lacked catan_kit; it was rerun using the existing shared launcher, with no installation.

The regression fixture positions include explicit counterfactual hand/dev/piece/VP allocations, not all legally reached histories. The synthetic B05 shortlist ranking isolates pruning: its candidate trade and child are actual legal engine states, while the supplied competing scores are constructed. Tests verify separate actual trade→trade→city execution and unavailable bank behavior. They do not prove every useful enabler survives or that this reservation increases match wins.

Four external 100-action legal-history walks against F were retained for bounded profiling. None completed a game; they are not official clocked match evidence. B05 rescued one root from the original greedy top five in that trace; B08 recorded 117 cache hits, 161 misses and 680 route estimates. B07's 100-action trace had no opposing held dev card at profiled decisions, so its three forecast controls were not invoked there. Their constructed-state legal execution is tested, but useful reached reply attribution remains unestablished. Do not present zero invocation as a successful ablation.

## Ticket status and limits

| Ticket | Completed in this revision | Still unestablished or deferred |
| --- | --- | --- |
| M3-C01 / M4-C01 | Bounded public terminal selection before fallback for all four; both seats; exact copied build effects and strict eligible Army checks | Exhaustive terminal optimality, more than 12 candidate build copies, full reached Road-cut history |
| B05-01 | Three greedy slots plus up to two enablers within existing width five; eight-VP terminal completion candidates; actual two-trade fixture | Component-isolated win-rate attribution, exhaustive deeper completion/route coverage |
| B05-02/03 | External copy/node/root/cutoff/rescued-enabler profiles; safe chance boundaries retained | Historical game303 exact chunk replay, complete cache/transposition timing attribution, reached cut trace |
| B06-01 | Structured direct/one-trade/roll-pending/hidden-conditional categories; integer legal conversion; original direct risk16 and new conditional conversion risk12, hidden8 risk weight0.35 | Multi-trade or new-road opponent threats, calibrated probabilities, certainty after a future roll |
| B06-02/03 | Own immediate terminal priority retained; necessary-resource denial regression | Matched threat-off defense-cost experiment, certified extended Road-race geometry |
| B07-01 | Eight bounded replies share dev families; useful deficit-reducing YOP and nonzero Monopoly ranked deterministically | Free-road shortlist remains six numeric/action-order candidates; deeper/post-roll replies |
| B07-02/03 | Explicit root/own/full controls; incomplete comparisons retain incumbent; constructed control tests | Full 500-game control ablations, useful reached-control attribution, improved posterior/history model and forecast horizon |
| B08-01 | No-held/new-held/old-held/played-this-turn eligibility delay; supply guard; exact engine new-Knight restriction | Delay is own-turn eligibility scaled by two route-score units, not exact elapsed rolls or stochastic acquisition expectation |
| B08-02/03 | Per-decision 128-entry potential cache keyed by complete menu, hand, rates, ratios, bank and VP gap; equivalence/invalidation verified | Full path certificates, balanced deeper Road enumeration, finite-deck expectation and persistence experiments |

No broad exception fallback was added. Diagnostic counters are in memory; external tools write records. Competition artifacts contain no runtime network, provider/API, file I/O or workers. Soft caps, root truncation and approximate mean-income/dev models remain limitations. A correctness fix or cache hit is not a demonstrated strength gain.

## Games and source identity

Twenty-four small official-clock smoke games loaded the four ZIP-extracted standalone files against unchanged F and played four-game member peer batches. All recorded errors, timeouts, crashes, clock overruns and harness random moves were zero. Tiny wins are diagnostic only.

The fixed main plan is 500 games per new candidate and 500 per corresponding parent, all on paired boards934000–934249 with identical global indices and20-game process lifecycle: 4,000 games including parent controls. Every outcome is retained. Final outcome/CPU/paired-difference evidence belongs in BUILD-AND-RESULTS.md after completion. No new complete diagnostic games or extra tournament/ablation batches are pooled into that evaluation.

## Final mechanical inventory review

The accepted [Hyde source inventory](SOURCE-INVENTORY.md) was independently checked and corrected by the primary. Retained limitations include Member4's finite short-completion loop without an inner deadline check and an eight-public-VP threat risk weight that is a design heuristic rather than a fully conditioned hidden-VP probability. Neither is described as a demonstrated cause of match losses. No frozen runtime changes were made in response to ongoing results.

## Pre-freeze development bookkeeping

The initial test script had a Path/string concatenation error, corrected before executing its tests. The first development draft then received a diagnostic-counter correction (count actual rescued roots rather than all reserved positions) and removal of duplicate pure one-trade helper calls. The initial draft is retained locally under ignored shared-local/round2-development-draft-01; it was never a main comparison artifact. All final semantic, ZIP smoke and main results identify the unchanged final frozen hashes.
