# Ticket decisions and evidence boundaries

17 October 2026, India time. Owner **Aroosh, Member 1**. User authorized primary upgrades of B01/B02; **owner/human review remains pending**. All new work lives in Member1; original sources, earlier agents and v001 freezes stay intact. Read the final [results](BUILD-AND-RESULTS.md) before choosing a version.

## M1-C01 — verified correctness repair

Parent hashes and manifests: [inventory](parent-inventory.json). New hashes: [packages](package-verification.json) and each v002 manifest. The immutable review `verify_findings.py` was rerun on the frozen parents and reproduced the city-goal failure. Its successful exit reproduces defects; it is not a fixed-code acceptance test.

Both v001 bots choose a nonterminal city in the constructed eight-VP `(WOOD, BRICK, SHEEP, WHEAT, ORE)=(0,1,0,2,4)` position. Both v002 bots choose the legal ORE→WOOD trade, then the legal Road that wins. New regression asserts the parent failure and the desired new behavior in both seats, with invariants and masked observations. It also reverses the original root list, then checks the returned original index leads to the exact winning chain. The immediate own win test precedes any trade search.

`terminal_trade` is a targeted certificate before heuristic trade rejection, not a global relaxation of retention or re-export rules. It checks only one maritime trade followed by a deterministic building action at own eight/nine VP. City requires gap≤1; Road candidate eligibility requires an unowned Road bonus and existing own length≥4; settlement may also transfer Road. Exact child legal menus/engine copies enforce bank, owned port ratio, piece/site, blocked endpoint and bonus rules. At most twelve relevant trades and forty-eight total simulated executions, with a four millisecond deadline inside the existing decision budget. A cap/deadline leaves cases unsearched. Longer chains, component-joining Road wins from shorter current lengths and seven-VP trade→settlement bonus chains remain outside this targeted certificate.

An independent oracle enumerates every legal maritime trade and following legal city/settlement/road in 96 constructed hands/seat/opposing-Road configurations, checking exact engine winners, resource/dev/piece/VP invariants and returned certificates. Ties/longer opposing Road, depleted WOOD bank, nonterminal Road and exhausted piece menus are tested. A blocked-endpoint fixture adds an explicit counterfactual opponent isolated settlement, runs ordinary engine endpoint maintenance and checks invariants; it is not a full reached blocking history. The exhausted-piece menu is explicitly counterfactual, not a fifteen-road reached allocation. The earlier reserved-last-wood, owned-port and depleted-bank contracts remain unchanged and pass.

## M1-C02 — verified correctness repair

Both parent bots END_TURN at `cpu_left=0.0009` in the constructed legal nine-VP settlement-win fixture. New standalone bots choose a winning legal build in both seats before sampling/fallback. City, eight-VP Road and eligible old-Knight Army wins before rolling are covered in both seats. New Knight, already-owned Army, strict incumbent tie and already-played-development-card cases are not certified as incremental wins. No-win END_TURN/ROLL fallbacks remain legal and never call `sample_world` at zero credit.

The helper reads public geometry/own exact cards from the harness-masked game. It copies up to twelve legal settlement/Road transitions; legal city and strict eligible Knight cases use arithmetic. It checks engine simultaneous-winner ordering using initial opponent public VP plus an upper bound on hidden VP, without trusting sampled opponent actual VP. Synthetic guard tests cover public increases, ghost hidden actual VP and last-color ordering. No complete reached Road-cut/simultaneous-terminal history is claimed.

Chance guards reject any simulated ROLL, development purchase or random robber movement during decision. Masked hidden allocations are varied without changing deterministic certificates. Normal policy expectation models remain the parent's model and are not claimed to be calibrated posteriors. Constructed timing/profile records are in [terminal-profile.json](terminal-profile.json); they exclude serialization and do not certify scorer timing/zero-credit feasibility.

## B01-03 — bounded diagnostic, no policy change

Twelve complete forced-discard sequences use real engine forced-seven transitions: two bots × three initial hands × own/out-of-turn discard. Each decision uses a newly constructed masked observation and immutable original state; quota, bank returns, phase/current-player restoration and all invariants are checked. For these cases, the final bundle attains the exhaustive small-hand oracle optimum for the **fixed initial goal** and no family switches occur. See [discard diagnostics](discard-diagnostics.json). This is not proof of globally optimal discards or absence of switches in other hands. No persistent discard memory was added.

## Deferred hypotheses and controls

- B01-01: no multi-goal alternative menu or broader retention change. A terminal override resolves the demonstrated failure without claiming the broader hypothesis is solved.
- B01-02: no re-export relaxation or deduplication-key change. A useful reached collision/beneficial chain has not been established here; cycle safety remains the conservative parent policy.
- B02-01: no city-payback or resource-supply threshold changes; opening weights and near-city margin remain unchanged.
- B02-02: no card-type-aware stock policy or investment coefficient changes; parent finite-deck/stock/turn-timing cases are retained.
- B02-03: no component-ablation, extra tournament or direct 500-game B01/B02 match. Only version-level matched F evidence is run, so it cannot separate effects of the two correctness changes or compare other bots' strength.

No strategic variant was adopted or rejected from win-rate tuning; no tuning followed main evaluation. Only test-fixture expectations/allocations were corrected, as recorded in [Hyde review](HYDE-REVIEW.md).

## Executed acceptance and measurement scope

Fifteen new regression methods load actual standalone v002, including the independent 96-case certificate oracle. Nineteen original economic contract methods run against those new standalone classes, preserving the 18,225-case conversion-helper oracle. The original nineteen parent tests also passed before repair. Commands and source hashes are retained in semantic-verification.json; failed test-development allocations are not erased or reported as bot regressions.

ZIPs contain only exact agent.py bytes; CRC, hash, development/frozen/extracted equality, clean standalone import and actual ZIP-extracted clocked F smoke games are checked. B01/B02 retain their distinct bottleneck versus city/dev policy wrapper settings.

Two external 100-action partial legal histories record root coverage, continuation nodes, internal budget cutoffs, terminal scan/cap counters, city commitment frequency and parent-choice controls in [diagnostics](diagnostics.json). Neither completes a game. Neither reaches the new terminal override and no changed choice is observed there. These short diagnostics establish legal instrumentation only, not useful reached repair attribution. Main harness records expose errors/timeouts/crashes/random moves/overruns; they do not expose per-decision internal counters. Do not treat zero harness fallbacks as zero internal cutoffs across all main games.

Main batch IDs: `B01-v001-parent-vs-F-500`, `B01-v002-new-vs-F-500`, `B02-v001-parent-vs-F-500`, `B02-v002-new-vs-F-500` under `main/`. Same fresh boards/global indices, F bytes and reset lifecycle; source freezes precede main. The final report recomputes all recorded outcomes, CPU/fault counts and paired differences. Fault/no-winner games are never discarded. Descriptive ranges are unadjusted across two candidates; a zero-width bootstrap when every observed paired difference is zero does not prove equivalence; the host also had a preexisting Member3/4 evaluator. This task never changes that other evaluation or its review documents; concurrent result/status and report-completion edits outside this task are recorded separately. See preservation-verification.json for specific before/after hashes, and harness-and-hardware.json for provenance and timing limits.

No SSH, portal action, private O/event-score validation, new environment, learned training, runtime LLM or publication. Local user verification is the next approval boundary; the work here is reviewable without publishing it.
