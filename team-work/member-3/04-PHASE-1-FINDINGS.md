# Pranesh: Phase 1 findings — tactics, opponent threats and VP races

**Status: research draft ready for your verification.** Date: **17 October 2026 (IST)**. Owner: **Pranesh, Member 3**. Primary-assistant source/math verification completed; **your review and Avadooth's cross-review are pending**. No bots, new game simulations, training or match experiments were made.

## Decision summary

The proposed direction is to distinguish **known own wins**, **complete legal purchase sequences**, and **conditional opposing threats**, then test those as separate tactical layers later. This is a research recommendation, not a demonstrated improvement over F/O.

Five findings matter most:

1. **Phase and actual VP matter.** Old action devs can be played before rolling; ordinary builds/trades cannot. A bought VP card contributes immediately. A Knight completing Army can reach ten before a robber move or roll is requested. See S01–S07.
2. **One action can be only the start of a plan.** Trade → city and road → settlement have exact combined costs; Road Building has a forced free-road subphase. A pre-roll progress card cannot guarantee a purchase because a roll intervenes. See S06/S10–S13 and cases A–C.
3. **Opponent affordability is visible; future victory is conditional.** Exact cards identify purchase opportunities, but locations, pieces, public/hidden VP, dev timing, rolls and other routes still matter. Blocking production does not remove resources already held.
4. **Hidden-card samples can contradict ongoing play.** In a real continuing 10-VP game, opposing hidden VP is at most `9 − public VP`; at nine public points, they currently hold zero hidden VP. The supplied masker does not enforce that condition. A sampled winning opponent is not observed truth. See R2 and the toy probability derivation.
5. **Road interruption needs validation.** Its settlement-cut branch lacks normal five-road/strict-tie guards, and scoring follows the returned owner. This is a verified source-level risk; a legally reached runtime failure has **not** been demonstrated. Do not promise textbook cut scoring. See R1.

F already rewards many public-point wins. These findings do not prove it misses the examples or that a tactical layer improves win rate. No new strategy has measured clock compliance.

## Review pack

| Document | What to inspect |
|---|---|
| [1. Source and semantic audit](phase-1/01-SOURCE-AND-SEMANTIC-AUDIT.md) | 15 findings, exact function/line citations, two source-level risks and short literature cards |
| [2. Sequences and cases](phase-1/02-TACTICAL-SEQUENCES-AND-CASES.md) | Trade/city, pre-roll Army, road/settlement, Road takeover and failure cases; explicit assumptions |
| [3. Threats and hypotheses](phase-1/03-THREATS-VP-RACES-AND-HYPOTHESES.md) | Threat matrix, hidden-card bounds/probability assumptions, three candidate cards and rejection tests |
| [4. Verification and junior review](phase-1/04-VERIFICATION-AND-REVIEW.md) | Actual checks, Hyde corrections/timeout, arithmetic execution, limits and review questions |
| [Source verification](phase-1/source-verification.json) | Eleven installed source files compared with pinned source/Git objects |
| [Arithmetic script](phase-1/verify_derivations.py) and [results](phase-1/derivations.json) | Five deterministic checks; no engine/game execution |

## Candidate recommendation, pending review

| Candidate | What to try later | Main reason it could fail |
|---|---|---|
| **M3-H1: terminal/prompt awareness** | Exact own actual-VP wins, phase eligibility and separation of fictional opponent scores | Could duplicate F; wrong terminal handling can harm |
| **M3-H2: purchase-completion planning** | Short legal trade/build/progress chains versus the same one-step evaluator | Branching/copies can exhaust the clock; chance/phase changes invalidate plans |
| **M3-H3: threats and bonus races** | Separate visible winning continuations, conditional dev threats and longer races | Excessive defense, poor calibration or unvalidated road cuts |

Compare each layer with the **same parent evaluator without it**, then F and varied later peer bots. Fixtures precede matches; use paired seats, held-out board groups, weak-matchup reporting, CPU and fault counters. The budget remains `min(0.300 + 0.0125 × decisions, 1.500)` seconds/game, one core/2 GB. **No depth, width, weights, cutoff, expected gain or timing was selected or measured.**

## Evidence limits and handoff

These are static source checks, mathematical derivations and hypothetical cases, not observed match results or complete engine fixtures. Relevant paper passages were reviewed; their results do not validate our candidates. No exact-rules tactical dataset was verified, full text corpora were not newly audited, and no replacement data was generated. The environment and organizer source were unchanged.

**Verify first:** R1 (Road cut path), R2 (nonterminal hidden-VP constraint), and Case B's terminal timing. Exact reachable-state fixtures remain future work.

**Aroosh:** retention/denial economics. **Avadooth:** spatial legality and road topology; cross-review pending. **Anni:** sampled-world consistency, forced phases and later profiling/fixtures. These are prepared handoffs, not messages sent or reviews received. Other members' findings were not edited.

## Completion check

- [x] Questions answered or bounded by named evidence gaps.
- [x] Facts, derivations and hypotheses distinguished with traceable evidence.
- [x] Counterexamples, alternatives and refutable future experiments recorded.
- [ ] Pranesh verifies this draft.
- [ ] Avadooth cross-review and other-member responses received.
- [x] Stopped before bot implementation, training, new games or tournaments.

Pranesh authorized sharing this draft on GitHub on 17 October 2026. User verification and Avadooth cross-review remain pending. Publication does not authorize bot implementation or game experiments.
