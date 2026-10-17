# Phase 1 Checklist — Member 3 (Pranesh)

**Source/math research completed for review; cross-member review pending.** Checked items refer to the evidence pack, not proven bot performance. Source: [Member 3 brief](03-PHASE-1-RESEARCH-BRIEF.md).

## Setup / Context
- [x] Pin exact sources: obs.py, F adapter, apply_action, state_functions, game/win logic, legal-action generation; note revision per claim.
- [x] Read relevant Guhe–Lascarides and Deep Catan passages; retain player/rule differences.

## Semantic Audit (Work Package A)
Record file/function/revision, observed inputs, legality, uncertainty and counterexample per topic. Evidence: [semantic audit](phase-1/01-SOURCE-AND-SEMANTIC-AUDIT.md).
- [x] Immediate engine-recognized wins; actual vs public VP; city upgrade adds one VP; hidden victory cards.
- [x] Dev-card purchase/play timing, same-turn play legality, action subphases, per-turn play restriction.
- [x] Largest Army: thresholds/ties, played vs held Knights.
- [x] Longest Road source paths inspected: thresholds, ties, branches, loops, settlement interruption. R1 still needs later reachable-state fixtures.
- [x] Robber: placement/blocking, victim/steal eligibility, Knight use, self-harm to our production.
- [x] Discard: threshold/count/order, preserving a concrete purchase, opportunity cost per resource.
- [x] Monopoly / Year of Plenty under bank/hand constraints; Road Building legal follow-ups.
- [x] Trace call paths when one function is insufficient; document uncertainty, not tabletop convention.

## Same-Turn Sequences (Work Package B)
- [x] Verify timing + legal-action generation for: trade → purchase; road → new settlement; YOP/Monopoly → purchase or win; Road Building → route/Longest Road swing; Knight → robber relief/Largest Army/purchase protection.
- [x] Mark dev draws and steals as stochastic; never treat one favorable outcome as guaranteed.
- [x] Per sequence: end/intervention/information changes. Evidence: [sequence table](phase-1/02-TACTICAL-SEQUENCES-AND-CASES.md).
- [x] Write plain-language priority spec with exceptions; compare immediate-win vs preservation vs threat prevention when they disagree.

## Opponent Threats (Work Package C)
- [x] Use exact opponent resources for feasible visible purchases; note legal placement, dev timing, hidden-VP uncertainty (public VP ≠ true distance to victory).
- [x] Draft visible/conditional/long-horizon threat table. Evidence: [threat analysis](phase-1/03-THREATS-VP-RACES-AND-HYPOTHESES.md).
- [x] Hidden-dev-card reasoning from public deck composition, known cards, played cards, unplayed count only; state sampling assumptions and history limits; never equate `sample_world` draws with real state.
- [x] Compare tactical policies: immediate-win alone vs short same-turn completion vs threat/bonus-race awareness; state when blocking is less valuable than advancing.

## Illustrative Cases
- [x] Hand-worked purchase and bonus/defense cases with resources, VP, legality assumptions and uncertainty: [cases A/B](phase-1/02-TACTICAL-SEQUENCES-AND-CASES.md).
- [x] Failure counterexamples: pre-roll progress, resource retention, production denial and sampled hidden wins in the same cases document.
- [x] If no suitable tactical dataset exists, say so and specify what exact-engine fixtures/trajectories must record; do not manufacture data.

## Handoff / Review
- [x] Fill 04-PHASE-1-FINDINGS.md: source cards, semantic table, cases, **up to three hypothesis cards**, later experiment/ablation proposals.
- [x] Specify evaluator-only baseline vs evaluator plus tactical layer, with win/loss tradeoffs, CPU/fault risks, explicit rejection condition.
- [ ] Aroosh (Member 1) checks the economics: send resource-value tradeoffs.
- [ ] Avadooth (Member 2) reviews spatial/route/placement claims: send those claims.
- [ ] Anni (Member 4) receives search-method inputs (depth/action categories, hidden-card method).
- [ ] Pranesh reviews Anni's search/hidden-information proposals and whether the evaluation design would expose tactical failures.

## Stop Boundary
- [x] Stop before bot implementation, simulation matches, training, or claiming a measured advantage over F/O.

Prepared by Hyde GLM-5.3 Flash; senior-reviewed against the brief and shortened. Review: [work log](06-JUNIOR-WORK-LOG.md).

Evidence: [findings and appendices](04-PHASE-1-FINDINGS.md). User verification remains pending.
