# Avadooth: direct GLM handoff for B03 and B04

17 October 2026. Owner **Member 2, Avadooth**. Primary assistant independently inspected the uploaded code and result records at commit **`791e6705d09f62ceba691777e041980d673f1c69`**, branch `member-2/avadooth-bots`. Your research findings are untouched. This document is new review feedback; it does not rewrite your report or claim your human review is complete.

## Paste this to GLM

> Improve only my B03/B04 bots using `team-work/member-2/08-GLM-IMPROVEMENT-CONTEXT.md` and `team-work/reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md`. Start from the exact v002 files at commit 791e6705d09f62ceba691777e041980d673f1c69 and verify their hashes. Preserve v001/v002; implement new v003 versions if unused. First fix the verified graph/port defects and add truthful exception/clock diagnostics, then test one strategic change at a time. Use the existing shared environment and bounded Hyde junior workflow. Do not modify B01/B02, another member's bots/research, F, the engine or the shared runner. Write regressions which fail on the parent and pass on the new artifact; run small correctness checks before 500 paired-seat games per bot and a matched parent comparison. Provide manifests, full results, CPU/fault evidence, rejected ideas and remaining limits. Do not push or submit to the event without a separate instruction.

Read the [shared review](../reviews/2026-10-17-B03-B08/README.md), [contract](../reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md), [source/result audit](../reviews/2026-10-17-B03-B08/source-and-result-audit.json) and [executable findings](../reviews/2026-10-17-B03-B08/verify_findings.py). The source lives on your branch; the reviewer used a local ignored snapshot rather than merge it into main.

| Parent | SHA-256 of agent.py | Next intended version |
|---|---|---|
| B03 v002 | `1a4a304932718ba2b76af1ff966bb08c55c5c00c7a0ef5c0f9cf788bdcc66e30` | v003 |
| B04 v002 | `763c88df0a815aeb97bf6cc1bb02865f8bb148c58bed6965ffb54911907d0b45` | v003 |

## First repair the evidence boundary — M2-E01, P1

**Verified:** the eight uploaded v002 JSON files contain 408 game records. The five screen files alone contain 360 records, not the report's stated 240. B03 `screen-01` and `screen-02` use the same 40 boards, global indices, winners and turn counts (39/80 each); the two B04 screens likewise repeat 32/80. These repetitions have different CPU measurements but are not independent new board samples. The 16-game B04-vs-F smoke and the B04 side of the 16-game B03-vs-B04 smoke use older hash `be9b3a53...`, not current B04 `763c88df...`. The 40-game B03/B04 screen does match both final hashes. All uploaded per-game harness fault counts recomputed to zero; this does not reveal swallowed internal exceptions.

**Action:** append a version-specific evidence index with exact source hashes and deduplicated board-group identities; keep all original files. Separate repeated measurements, old-hash smoke, final-hash screens and newly reproduced review evaluation. The raw uploaded files do not preserve the report's claimed mis-scaled intermediate outcome as a separately hashed experiment; label that history as narrative, not independently reproduced evidence. Replace the pending commit field in a new manifest with a resolvable parent/freeze identity.

**Acceptance:** every headline number points to the exact artifact, source hash and result file. No result is overwritten. Do not treat a new manifest text as a changed historical artifact. New 500-game review results are linked in the shared README; use those exact frozen hashes when comparing revisions.

## Both bots: operational changes before tuning

### M2-C01 — P1: make internal failures visible and bounded

**Source:** both `Agent.decide` catch every `Exception`, then return ROLL/END_TURN/0. Neither reads `obs.cpu_left`; each evaluates the whole candidate list. **Verified probe:** replacing `_score` with a sentinel exception makes both return END_TURN normally (`M2-OBSERVABILITY` in `verified-findings.json`). This proves hidden-failure observability, not that old games actually contained such exceptions.

**Implementation:** maintain counters for caught exceptions, deadline fallback and evaluated/skipped roots; expose these only to a separate diagnostic harness or in-memory inspection, never spam stdout or write runtime files. In development tests use a strict adapter that re-raises scoring errors. Production fallback should retain the best already evaluated legal action rather than discard it when a later candidate fails. Add a cap derived from `cpu_left` with room for serialization and check it within root/feature loops. Reserve terminal handling first.

**Acceptance:** injected failure after a viable root preserves the incumbent and increments the correct counter; no hidden failure is called a clean diagnostic run. Zero/very-low clock returns a legal action cheaply without doing a full root evaluation. Both seats and large trade/YOP action sets are tested. Measure own CPU distribution plus exhausted games; a mean below 1.5 s is insufficient because the allowance grows per decision.

### M2-C02 — P1: exact own wins; P2: explicit chance handling

**Source:** `_score` executes all actions on `obs._game.copy()` and uses `base_fn(DEFAULT_WEIGHTS)`. The harness has already masked this game, so this is **not a real hidden-information leak**. F itself calls `obs.sample_world(self.rng)` before evaluating. Your unused `self.rng` is not the same sampling mechanism. `base_fn` strongly rewards public VP and does not implement a known-own-actual-terminal guard; sampled deck order and a single random steal/roll are not expected outcomes.

**Implementation:** establish known own terminal actions before heuristic scoring, including eligible Knight/Army, city and legally verified settlement/bonus transitions. Treat uncertain opponent hidden VP and settlement road cuts carefully. Handle BUY, robber and ROLL through explicit chance-boundary rules; start with cheap expectation/cutoff rather than deep stochastic search. For exact F-baseline attribution, add a separately frozen control matching the official `examples/f_agent.py` semantics, including resampling and chance handling, then isolate your strategy term. Do not claim an additive bonus can never worsen play: smaller than a coefficient does not imply smaller than every realized feature difference, and it overwhelms many hand/reach terms.

**Acceptance:** immediate guaranteed own win beats a speculative lottery; newly bought dev restrictions hold; equivalent legal-action permutations map to equivalent decisions except declared ties; original observation remains unchanged; no sampled card is described as observed. Track the effect of chance policy separately from graph/port improvements. This is a modeling/robustness ticket, not evidence of event disqualification.

## B03 — frontier expansion and space denial

### B03-01 — P1 verified: count additional roads from the existing network

**Source:** `Agent._opp_reach`, lines 121–144 in the frozen source, seeds only opponent settlements/cities and counts two graph edges. Existing friendly roads consume its hop budget; their endpoints are not seed frontiers.

**Reproducer:** the invariant-checked six-road constructed fixture in `verify_findings.py` has legal opponent settlement node **39**, already connected by their roads, which `_opp_reach` omits. This is zero new roads away, yet is absent from the contest set. No full reachable-history or observed lost-game claim is made.

**Implementation:** compute legal connection cost from the opponent's actual usable road network. Existing owned edges have zero additional-road cost; a new free land edge costs one; our roads and blocking enemy buildings cannot be crossed. Respect land nodes, settlement distance rules and available pieces. Prefer a small 0–1 shortest-path calculation or bounded legal board expansion with cached geometry. Return legal settlement targets with road count, production and contest relevance, rather than a flat collection of all traversed vertices. Preserve a distinction between physical reach and current affordability.

**Acceptance:** node39 appears with cost zero; add one/two-road fixtures, blocked junction, occupied edge, coast, no road/settlement pieces and mirrored seat cases. Compare the target set against exact legal engine expansions for a bounded collection of constructed states. Verify graph-cost changes do not modify current legal actions. **CPU risk:** low/moderate if geometry is cached per observation; avoid a full all-board search per action.

### B03-02 — P2 hypothesis: connect denial reward to a productive race

**Current limitation:** a fixed 3e6 settlement premium / 1.5e6 road premium rewards membership in `_opp_reach`, without site quality, relative route cost, own settlement affordability or whether a follow-up can ever occupy the site. `_far_end` also needs explicit treatment when both endpoints are already connected. No losing trace proves this caused the uploaded win rate.

**Implementation experiment:** compare (a) corrected graph only, (b) value a target using productive benefit plus contest urgency minus actual road/settlement resource costs. Prioritize shorter feasible paths and avoid dead-end roads. Discount a speculative opponent plan rather than assume it will happen. Keep known wins above denial. Instrument the targeted node, own/opponent extra-road cost, resource deficit and rejected alternative for replay.

**Acceptance:** do not pay for a barren/unbuildable/already-owned target; choose between two routes using full cost; retain a productive uncontested alternative when denial costs too much. Main matched-parent comparison is 500 games; use a graph-corrected/no-denial control to attribute value. Retain B03's spatial identity rather than merely tune F's coefficient scale.

## B04 — port specialization

### B04-01 — P1 verified: road endpoint order is not direction

**Source:** `Agent._port_bonus`, lines 91–93: `_, far = act.value`. The engine's `Board.buildable_edges` returns `(n1,n2)` with `n1 < n2`, not near/far order.

**Reproducer:** after legal road prefix `(6,23) → (22,23) → (22,49)`, legal edge **(48,49)** reaches new port node **48**. Node49 is already connected. B04 scores node49. See the exact probe JSON and source script.

**Implementation:** use pre-action connectivity (and both endpoints) to identify newly reached port nodes, or compute before/after reachable-port deltas. Handle connections between two owned components without inventing a new endpoint. Port approach is still a hypothesis until legal settlement acquisition and its total cost are established.

**Acceptance:** same undirected edge represented in either tuple order produces the same route assessment; add high-to-low port reach, low-to-high, two-owned-endpoints, blocked port and distance-rule cases. The target must be an actual attainable port site. **CPU risk:** small with one connectivity computation per observation.

### B04-02 — P1 verified policy mismatch: value incremental conversion, not merely port labels

**Source:** `_justified_port_value` grants `scale*0.1` even with **zero** specialized production; a generic port gets full credit for any two positive production types. The threshold `PROBA_6=0.1389` is slightly larger than exact `5/36`.

**Probe:** at specialized production 0 or exactly 5/36, the settlement term is 300,000; at 0.14 it jumps to3,000,000. The advertised exact six/eight threshold is not implemented. This is a deterministic policy fact, not a measured win-rate effect. The hardcoded relative `P0` production keys are correct in the pinned engine and should not be 'fixed' to the absolute player index.

**Implementation:** replace the ad hoc threshold with expected **incremental** savings versus currently owned trade ratios, using integer bundles after reserving the chosen build's ingredients. A duplicate or already-superior port should not earn acquisition value. Include road+settlement cost, bank availability, production/robber risk and a remaining-game horizon. If retaining a probability threshold, use exact `5/36` with an explicit tolerance, but that numeric fix alone does not implement specialization. Gate urgency using own remaining VP and plausible opponent threats, not solely a hard public9 switch.

**Acceptance:** zero source production/no surplus grants no economic savings; a hand with 5 cards at 4:1 versus2:1 yields the correct integer difference after ingredient reservation; already-owned2:1 beats a redundant3:1; unavailable bank resources cannot be promised; a weaker coastal site must repay its lost inland production. Add currently owned port, duplicate port and adversarial shortage fixtures. Keep this experiment separate from the endpoint fix.

### B04-03 — P2 hypothesis: implement an actual port-to-purchase route

v002's port term only affects settlement/road actions. MARITIME_TRADE relies entirely on base_fn, so conversion is not optimized toward a named purchase. Search a bounded legal chain of trades leading to city/settlement/dev or retain a conversion-feasibility estimate, always using current legal ratios and bank stock. Use a trade-state visited set and horizon to prevent cycles. Do not spend a reserved build ingredient merely to maximize the number of trades. Compare a port-term-disabled control and corrected B04 on fresh paired boards before claiming the specialization helps.

## Delivery order

1. New frozen evidence index and diagnostic failure counters.
2. Regression-backed B03 network and B04 endpoint fixes, plus cheap terminal/clock safety.
3. Separate spatial/port objective experiments, one interpretable change at a time.
4. New 500-game evaluations and matched parents; package only validated versions. Human Avadooth review remains pending until actually performed.
