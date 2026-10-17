# Anni: Phase 1 findings — data, methods and repeated comparisons

17 October 2026. **Assistant research completed for Anni's track; human/team review pending.** No bots, training, generated games or tournament runner. User's latest workflow: every member builds/tests/uploads two bots; the assistant independently verifies, clashes and returns improvement instructions; repeat.

## Decision summary

Both text corpora were fully decoded with an isolated research reader. Neither is ready for direct training/evaluation under our exact rules. Start with interpretable heuristics and bounded planning candidates; keep compact learning conditional on compatible future labels. Do not force RL or imitate a corpus because it is downloadable.

Anni owns **B07 sampled-opponent planning** and **B08 adaptive VP-route planning**, with B08 the simpler starting point. She builds/tests these two like everyone else; independent cross-bot verification belongs to the assistant after uploads. All new CPU costs and strength remain unmeasured.

## Reports and assigned questions

| Question | Completed finding / report |
|---|---|
| What do the actual corpus contents establish? | [Full decoding and specified audits](phase-1/01-DATASET-AUDIT.md): D2 has 1,000 multi-message rows, uniformly 1v1/7-VP/hidden resource-type prompts. D3 has 2,668 decision rows, uniformly four-color/10-VP prompts, ten seed groups, repeated prompts and complete model/color confounding. Labels/terms and exact compatibility remain inadequate. |
| What fits the clock in principle? | [Method/source comparison](phase-1/02-METHODS-AND-SOURCES.md): fast evaluation, bounded same-turn search, sampled replies, chance search, learned ranking, large RL/MCTS and adaptive plans, with operation-count costs and failure conditions. No measured-fit claim. |
| How do owners iterate fairly? | [Detailed protocol](phase-1/03-ITERATION-AND-TEST-PROTOCOL.md): upload manifests, eligibility, frozen artifacts, paired seats/board groups, process lifecycle, uncertainty, full matchup matrix, owner feedback and submission constraints. |

## Evidence and limitations

- [Auditor](phase-1/audit_text_corpora.py) and [actual aggregate JSON](phase-1/corpus-audit.json) include schema, nulls, duplicates, roles, rule markers, textual action checks, seeds and model/player counts. Raw text stays local; no action adapter/replay performed.
- D2 exact action text matches 49,770/49,996 parsed message/list pairs; the 226 mismatches are diagnostics, not certified illegal actions. No state text was shared **between rows** under the exact matching definition; within-row repetition exists, and approximate/episode dependence is still unresolved.
- D3 action tags parse and type-match metadata for all rows; that does not validate geometry or legality. All publisher validity flags are true; they are not independent evidence of good play.
- No explicit dataset license/proven expert labels were established. No training or redistribution of raw examples was assumed.
- Primary-source reviews distinguish two-player self-play, four-player neural MCTS, general imitation/search methods and simpler build-plan literature. Paper success and organizer timings are source reports, not our outcomes.
- Current upstream kit changes only README paths/URLs relative to our pin; problem statement/harness/requirements unchanged. Game environment kept stable. An isolated ignored pyarrow reader was the only new research dependency.

## Candidate hypotheses and counterexamples

M4-H1/B07 asks whether consistent hidden-world reply planning helps when hidden devs genuinely change decisions; averaging visible-only F scores is a counterexample where more samples only add cost. M4-H2/B08 asks whether adaptive VP routes beat fixed preferences; mean production can conceal burst/denial risk and cause plan thrashing. M4-H3 compact distillation remains deferred until exact expert labels and grouped splits exist. See the method report for controls and rejection criteria.

Proposed screening/comparison/shortlist stages total 6,080 games before smoke, ablations and repeated rounds; this is a planning example, not a required feasible commitment. Throughput must be measured and workload cut to leave packaging time. The optional eight-finalist evidence batch is extra. Official O/private boards are unavailable locally. Eight local bots do not override 7 scored/10 total official uploads.

## Review and handoff

The primary checked the economic report's leakage/group dependence and Anni's hidden-world assumptions against Pranesh's source audit. Human Anni/Pranesh reviews remain pending. Avadooth's research was excluded and is not marked completed. A Hyde harness-extraction job timed out with no deliverable; primary source inspection supplied the accepted report. See [verification/work log](../PHASE-1-COMPLETION-AND-VERIFICATION.md).

Next human work: [Anni's two-bot assignment](07-TWO-BOT-BUILD-ASSIGNMENT.md). Full vector dimensionality/profile, legal reachable Road/masking fixtures, exact dataset reconstruction, learning and all strength claims remain explicit future work.

## Completion status

- [x] Both full tables decoded and the specified text/metadata audit run.
- [x] Dataset roles, training rejection and unresolved terms/provenance recorded.
- [x] Methods, costs, assumptions, alternatives and failure cases compared.
- [x] Repeated owner-build/assistant-review protocol and budget specified.
- [ ] Anni/Pranesh human review and corrections.
- [ ] Bots, runner, training, fixtures and matches — not implemented by this task.
