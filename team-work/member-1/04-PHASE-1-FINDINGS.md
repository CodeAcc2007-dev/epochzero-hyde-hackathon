# Aroosh: Phase 1 findings — statistics and resource economics

17 October 2026. **Assistant research completed for Aroosh's track; human/team review pending.** No bots, training or game experiments. The user excluded Avadooth's research; his files were not used as completed findings.

## Decision summary

The original CSV supports narrow descriptive reproductions, not a winning two-player policy. It has 50 four-player game groups and one repeated contributor, not 200 independent matches. Seat wins and game length reproduce the article; development-card/road purchase effects and the contributor's regression do not have sufficient specifications/fields for reproduction here. Two undocumented zero-number B tokens remain unresolved.

Recommend testing **B01 bottleneck economy** against **B02 city/dev engine**, with a port-conversion handoff to Avadooth. Exact purchase costs, observed hands and integer trades justify the hypotheses more directly than post-game correlations. No strategy is measured as stronger yet.

## Evidence pack and answers

| Assigned question | Completed answer / evidence |
|---|---|
| What can be reproduced? | Seat wins 8/18/14/10 and rolls mean64.28/sampleSD12.7408, using one histogram per game. [Dictionary, quality and statistics](phase-1/01-DATA-AND-STATISTICS.md) distinguish these from new complete-case descriptors. |
| What leaks or confounds? | Final points, collection/trade/discard totals and realized dice are unavailable at opening. The observed me flag has 25/50 flagged wins versus 25/150 unflagged; seat/person selection matters. Within-game player dependence is explicit. |
| What economy alternatives deserve bots? | Complete-ingredient valuation versus concentrated productive city/dev investment, with port access conditional on route cost. [Hypotheses and cases](phase-1/02-ECONOMY-AND-HYPOTHESES.md) provide inputs, assumptions, counterexamples and rejection tests. |

Source links and exact input hash are in the data audit; raw data stays local. Published/source statements, our descriptive calculations, hand-worked arithmetic and untested hypotheses are labelled separately. No arbitrary regression was substituted for the contributor's reported 40/50 result.

## Reproducible outputs

- [CSV auditor](phase-1/audit_csv.py), standard-library only, and [actual aggregate JSON](phase-1/csv-audit.json).
- Data dictionary preserves all 36 original header positions and blanks. Duplicate/group/winner checks and gain/loss identities pass; settlement parsing retains unresolved tokens.
- Complete-case initial descriptors use 198 player records /49 winners; all 200 remain in placement/roll audits. Resource associations are not causal effects or exact reproductions of every article chart.
- Focused planning-paper/source review, four concrete economy cases and three hypothesis cards are in the [economics report](phase-1/02-ECONOMY-AND-HYPOTHESES.md).

The primary independently recomputed winners, dice summaries and token inventories before reconciling the script results. A Hyde draft task timed out with no output; no junior code was accepted. See [shared verification/work log](../PHASE-1-COMPLETION-AND-VERIFICATION.md).

## Handoff and review

Avadooth supplies spatial/port legality and his own pending research. Pranesh supplies terminal/timing and denial semantics. Anni's dataset/method findings support grouped evaluation and no immediate imitation dependency. The primary cross-checked these reports for consistency; no human reviewer response is invented. Anni's requested human review remains pending.

Future assignment: [Aroosh builds, self-tests and uploads B01/B02](07-TWO-BOT-BUILD-ASSIGNMENT.md). The assistant later verifies uploaded versions and gives specific fixes. That loop is planned, not executed here.

## Completion status

- [x] Numerical study checked against actual fields, groups and encodings.
- [x] Reproductions, new descriptors, confounding and unresolved claims separated.
- [x] Economic alternatives, cases, counterexamples and future ablations documented.
- [x] Research scripts run; raw inputs preserved and excluded from Git.
- [ ] Aroosh/Anni human review and requested corrections.
- [ ] Exact-rules fixtures, bots, CPU profiles and comparative games — future work.
