# Next owner improvement tickets — not implemented in this round

Owner: **Pranesh**, with later independent assistant review. Frozen baseline: B05/v003 and B06/v003. These tickets use observed results and explicitly separate hypotheses from established causes. Do not change a frozen version in place or reuse841000–841499 as untouched confirmation.

## M3-01 — explain shared losses before adding complexity

**Evidence:** both candidates lose game1/board841000 from second seat and game2/board841001 from first seat. B05 additionally loses game8/board841004; B06 loses game6/board841003. See original records and fingerprints. A loss alone does not identify the bad decision.

**Action:** replay the original20-game batch with original global indices and F lifecycle, then capture a separate diagnostic decision trace outside the competition artifact. A fresh one-game process may change F's owned RNG state. Call official `match.play_chunk` with the saved board/index arrays; merely resetting `--seed0` while resetting game indices does not replay a later chunk's dice key.

**Acceptance:** establish a reproducible mistaken choice/forecast, add a meaningful exact-engine fixture or controlled diagnostic, propose one change in a new version and compare against frozen v003 on fresh development groups. Keep losses that remain unexplained. Do not claim production/defense/search caused them without traces.

## M3-02 — measure useful search work and retain clock safety

**Evidence:** B05 mean160.2ms/game versus B06 mean100.2ms. B05's largest observed own CPU is530ms, game303/board841151,81 decisions; no exhausted clock. B06's maximum is300ms, game760/board841380,106 decisions. Direct matchup103–97 is inconclusive, so extra compute does not establish broad superiority.

**Hypothesis:** B05 may gain from cheaper enabling-chain prioritization, less repeated state copying or a better nonterminal beam shortlist rather than deeper search.

**Action:** separately profile nodes/copies/evaluations by prompt and source fingerprint, especially the stated B05 case. Compare a smaller or selective beam against the same evaluator. Preserve the existing deterministic terminal checks and chance boundaries.

**Acceptance:** no faults/exhaustion on original semantic/clock checks; same or better fresh-board F/peer evidence with lower CPU or a documented strength/cost tradeoff. Local gains still require scorer-machine validation through the portal teammate's separate process. No SSH by this assistant.

## M3-03 — test B06's threat horizon and opportunity cost

**Evidence:** B06 wins695/1,000 against F and292/400 in the control-matched subset, versus273/400 for the threat-free greedy control. Its .35 eight-public-VP risk weight is a design choice, not a learned/calibrated probability. Current classifier recognizes affordable legal buildings, not every enabling trade/future roll.

**Hypothesis:** carefully bounded purchase-enabler threats could help, but broad pessimistic blocking could sacrifice own progress.

**Action:** add explicit fixtures distinguishing an existing affordable enemy city, a port-enabled city, bank shortage, conditional post-roll completion and an available own terminal move. Test one threat-model change at a time, with the threat-free control and B05 retained. Do not assume hidden action-card eligibility.

**Acceptance:** correct classifications with explicit certainty/conditions, preserved known own wins, no material clock/fault regression, and fresh-board weak-matchup evidence rather than only a higher heuristic score.

## M3-04 — broader opponent coverage before final selection

**Evidence:** only F, own peer and common control were tested; O/private boards and the other six member bots were unavailable. B05 has3.4pp higher observed F win rate, while the direct matchup is nearly even. Pair-bootstrap differences are descriptive/unadjusted.

**Action:** when others upload, freeze all versions and run the planned mixed-style matrix and targeted component ablations. Preserve full faults/CPU and cyclic matchups. Both current candidates remain useful opponents; do not drop B06 solely because its F point estimate is lower.

**Acceptance:** documented new seed groups, paired uncertainty and version-specific owner feedback. No voting ensemble, reweighting or final-event winner claim without new evidence. Road-cut reachable-state fixtures and hidden-card history consistency remain separate correctness work.
