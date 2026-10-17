# Phase 1 review and synthesis worksheet

Status: **NOT STARTED — template prepared during planning.** No research finding, winner or algorithm selection is implied by this file.

## Handoff status

| Research track | Findings | Reviewer | Review status |
|---|---|---|---|
| Member 1 (Aroosh): statistics/economy | [Findings](member-1/04-PHASE-1-FINDINGS.md) | Member 4 (Anni) | Pending |
| Member 2 (Avadooth): opening/expansion | [Findings](member-2/04-PHASE-1-FINDINGS.md) | Member 1 (Aroosh) | Pending |
| Member 3 (Pranesh): tactics/threats | [Findings](member-3/04-PHASE-1-FINDINGS.md) | Member 2 (Avadooth) | Pending |
| Member 4 (Anni): methods/data/evaluation | [Findings](member-4/04-PHASE-1-FINDINGS.md) | Member 3 (Pranesh) | Pending |

## Evidence to consolidate after research

| Finding ID / claim | Source or offline result | Exact-rules applicability | Confidence and limitation | Review / unresolved disagreement |
|---|---|---|---|---|
| Pending research | — | — | — | — |

Keep published claims, reproduced results, mathematical derivations and untested strategy hypotheses distinguishable. Statistical significance alone is not an implementation priority.

## Candidate comparison for Phase 2

| Candidate / hypothesis IDs | Proposed minimal bot | Baseline and differentiating experiment | Data/feature needs | CPU/memory risk | Counterexample / rejection condition | Next decision |
|---|---|---|---|---|---|---|
| Pending research | — | — | — | — | — | — |

Consider at least two distinct alternatives if evidence permits. Do not force a learned model, search method or combination if its prerequisite evidence is missing. A simple, well-specified candidate is a valid outcome.

## Dataset verdicts to accept or challenge

| Dataset | Whole-corpus audit completed? | Rule/observation match | Decision-time fields / leakage | License / proposed permitted use | Suitable role and limits |
|---|---|---|---|---|---|
| Kaggle 50 games | Pending Member 1 (Aroosh) | Known four-player/peer-trade mismatch | Pending | CC BY-NC-SA 4.0 metadata; verify conditions for intended use | Pending |
| g8967 HF corpus | Pending Member 4 (Anni) | Inspected example 1v1 / 7 VP / hidden resource types | Pending | Unconfirmed | Pending |
| VVantim HF corpus | Pending Member 4 (Anni) | Inspected example four-player / 10 VP | Pending | Unconfirmed | Pending |

## Phase 2 decisions still to make

- Shortlisted candidate bots and fallback if a research dependency fails.
- Coverage of promising alternative strategies, repeated clash/selection/improvement rounds and the route to eight validated local finalists.
- Candidate-specific decision rules/features; common interfaces and configuration boundaries.
- Allowed data/labels, whether exact-rules data must be generated later, and what target it would support.
- Development, selection and final board-seed groups; game-order/adaptation policy.
- Opponent set, per-game logging, uncertainty method, ablations and evaluation size/budget.
- CPU reserve policy and reliable fallback behavior; local/scorer timing limits.
- Four-person bot-building, test ownership and cross-review assignments.
- Artifact names/versioning, integration gate, submission/report time reserved.
- Remaining official submission slots: 7 scored / 10 total maximum; eight local finalists are a local portfolio, not eight guaranteed scored uploads.

## Gate checklist

- [ ] Four findings reports distinguish completed work from open questions.
- [ ] All four reviews are recorded; disagreements remain explicit.
- [ ] Dataset limitations and intended uses are recorded; no unverified corpus is labelled exact-match.
- [ ] Proposed strategies have observable inputs, counterexamples and refutable tests.
- [ ] Evaluation design covers pairing, held-out data, weak matchups, CPU and faults.
- [ ] Candidate choices are justified by evidence or explicitly labelled exploratory.
- [ ] A concrete Phase 2 implementation plan is written before bot work starts.

This planning task leaves every checkbox unchecked.
