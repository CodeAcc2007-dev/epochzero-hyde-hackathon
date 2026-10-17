# Phase 1 Checklist — Member 3 (Pranesh)

**Checklist only; no completed research.** Source: [Member 3 brief](03-PHASE-1-RESEARCH-BRIEF.md).

## Setup / Context
- [ ] Pin exact sources: obs.py, F adapter, apply_action, state_functions, game/win logic, legal-action generation; note revision per claim.
- [ ] Read Guhe–Lascarides and Deep Catan papers; do not transfer its four-player performance claims.

## Semantic Audit (Work Package A)
Record file/function/revision, observed inputs, legality, uncertainty and counterexample per topic. Evidence: _____
- [ ] Immediate engine-recognized wins; actual vs public VP; city upgrade adds one VP; hidden victory cards.
- [ ] Dev-card purchase/play timing, same-turn play legality, action subphases, per-turn play restriction.
- [ ] Largest Army: thresholds/ties, played vs held Knights.
- [ ] Longest Road: thresholds, ties, branches, loops, settlement interruption — engine semantics, not owned-edge count.
- [ ] Robber: placement/blocking, victim/steal eligibility, Knight use, self-harm to our production.
- [ ] Discard: threshold/count/order, preserving a concrete purchase, opportunity cost per resource.
- [ ] Monopoly / Year of Plenty under bank/hand constraints; Road Building legal follow-ups.
- [ ] Trace call paths when one function is insufficient; document uncertainty, not tabletop convention.

## Same-Turn Sequences (Work Package B)
- [ ] Verify timing + legal-action generation for: trade → purchase; road → new settlement; YOP/Monopoly → purchase or win; Road Building → route/Longest Road swing; Knight → robber relief/Largest Army/purchase protection.
- [ ] Mark dev draws and steals as stochastic; never treat one favorable outcome as guaranteed.
- [ ] Per sequence: where it must end, opponent intervention points, information changes. Evidence link: _____
- [ ] Write plain-language priority spec with exceptions; compare immediate-win vs preservation vs threat prevention when they disagree.

## Opponent Threats (Work Package C)
- [ ] Use exact opponent resources for feasible visible purchases; note legal placement, dev timing, hidden-VP uncertainty (public VP ≠ true distance to victory).
- [ ] Draft threat table with three tiers: deterministic visible, conditional on hidden card/roll, long-horizon risks. Evidence link: _____
- [ ] Hidden-dev-card reasoning from public deck composition, known cards, played cards, unplayed count only; state sampling assumptions and history limits; never equate `sample_world` draws with real state.
- [ ] Compare tactical policies: immediate-win alone vs short same-turn completion vs threat/bonus-race awareness; state when blocking is less valuable than advancing.

## Illustrative Cases
- [ ] At least **two fully hand-worked tactical cases**: one purchase-enabling, one bonus/defense decision (resources, public/actual points where legitimately known, action order, legality assumptions, hidden elements). Case A: _____ Case B: _____
- [ ] One **failure counterexample** to a naive policy: _____
- [ ] If no suitable tactical dataset exists, say so and specify what exact-engine fixtures/trajectories must record; do not manufacture data.

## Handoff / Review
- [ ] Fill 04-PHASE-1-FINDINGS.md: source cards, semantic table, cases, **up to three hypothesis cards**, later experiment/ablation proposals.
- [ ] Specify evaluator-only baseline vs evaluator plus tactical layer, with win/loss tradeoffs, CPU/fault risks, explicit rejection condition.
- [ ] Aroosh (Member 1) checks the economics: send resource-value tradeoffs.
- [ ] Avadooth (Member 2) reviews spatial/route/placement claims: send those claims.
- [ ] Anni (Member 4) receives search-method inputs (depth/action categories, hidden-card method).
- [ ] Pranesh reviews Anni's search/hidden-information proposals and whether the evaluation design would expose tactical failures.

## Stop Boundary
- [ ] Stop before bot implementation, simulation matches, training, or claiming a measured advantage over F/O.

Prepared by Hyde GLM-5.3 Flash; senior-reviewed against the brief and shortened. Review: [work log](06-JUNIOR-WORK-LOG.md).
