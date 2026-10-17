# Eight strategies, four owners, repeated independent verification

17 October 2026. **Build assignments prepared; no bots implemented or matches run by this task.** The user explicitly asks each human member to build/test/upload two bots, followed by assistant verification, comparisons and feedback, then repeat. This supersedes earlier planning documents that deferred implementation ownership. It does not claim that teammates have started, accepted findings or uploaded bots.

## Research handoff

Assistant research is now documented for [Aroosh](team-work/member-1/04-PHASE-1-FINDINGS.md), [Pranesh](team-work/member-3/04-PHASE-1-FINDINGS.md) and [Anni](team-work/member-4/04-PHASE-1-FINDINGS.md). Human/cross-member review is still pending. **Avadooth's research was excluded at the user's request and left untouched.** His two build assignments below are provisional strategy specifications based on shared evidence; he supplies his own spatial research and corrections.

The CSV reproduces a small set of four-player descriptive claims, not winning 1v1 policies. Both text corpora were fully decoded but rejected for direct exact-rules training now. Pranesh's source/math findings remain valid within their stated limits; Road-cut runtime behavior, sampler consistency fixtures and all performance are untested. Sources, hashes and data verdicts are linked in the member reports.

## Two distinct bots per member

All eight are hypotheses with common legality/terminal/fallback requirements. Distinct strategy means distinct decision logic/objective, not merely eight coefficient files. Common scaffolding is allowed later; preserve independent frozen versions and ablations.

| Bot | Human owner | Strategy and distinguishing behavior | Key evidence / risk | Independent review |
|---|---|---|---|---|
| **B01 — Bottleneck economy** | **1 Aroosh** | Choose purchases, trades and retention by complete ingredient deficits and actual conversion; prevent unusable surplus | Exact costs and hand visibility; mean production estimates can mislead | Assistant; Anni may inspect statistical assumptions |
| **B02 — City/dev engine** | **1 Aroosh** | Invest in wheat/ore/sheep, legal productive city upgrades and eligible dev/Army progress; expansion remains an escape route | Different economic commitment from B01; chance draws, blocking and excess dev spending can fail | Assistant; Pranesh may inspect timing/terminal rules |
| **B03 — Frontier expansion and space denial** | **2 Avadooth** | Choose productive openings and cheap legal paths to valuable/contested settlement sites; value occupancy before opponent access | Spatial alternative to concentrated upgrades; no own spatial research completed here | Assistant; Aroosh may inspect resource economics |
| **B04 — Port specialization** | **2 Avadooth** | Match surplus production to owned/justified ports and convert in integer bundles toward purchases | Different conversion/route commitment from B03; coast/path costs can dominate | Assistant; Anni may inspect comparison controls |
| **B05 — Same-turn completion planner** | **3 Pranesh** | Search a bounded set of legal enabling chains such as trade→city, road→settlement and YOP→purchase; execute only the first current legal index | Pranesh M3-H2; phase/chance boundaries, cycles and CPU are central | Assistant; Avadooth may inspect geometry when available |
| **B06 — Opponent threats and bonus races** | **3 Pranesh** | Price visible enemy completion threats, targeted robber/Monopoly denial and strict Army/Road takeovers without deep hidden-world search | Pranesh M3-H3; exact hand ≠ certain future win; excessive defense can lose | Assistant; Aroosh may inspect opportunity costs |
| **B07 — Sampled-opponent planning** | **4 Anni** | On a shortlist, compare own progress with plausible opposing replies across consistent hidden-dev worlds; bounded work, explicit chance cutoff | Anni M4-H1; sampler terminal/eligibility limits and compute risk; higher-risk candidate | Assistant; Pranesh may inspect hidden-info semantics |
| **B08 — Adaptive VP-route planner** | **4 Anni** | Replan among city, expansion, dev/Army and Road routes using estimated completion cost and production gain as VP gap changes | Anni M4-H2 and planning literature; approximate estimates and plan thrashing can fail | Assistant; Avadooth may later inspect spatial routes |

Teammate review suggestions are handoffs, not messages sent or prerequisites that stop owners. The assistant independently verifies all uploaded versions. First build priority: each member's simpler candidate B01/B03/B06/B08, then their second. This creates useful opponents early while the search candidates are being bounded. It is an engineering risk order, not a proven strength ranking.

## Shared minimal contract

Return the index of an existing current legal action. Reuse the supplied environment and official 10-VP/no-peer-trade rules. Own actual VP is known; opposing dev identities are not. Known own terminal moves and phase eligibility are common correctness concerns, even if a bot's strategic objective differs. Random dev/steal outcomes are not guaranteed wins. No runtime LLM/network/worker process. Hyde is a development junior only; owners/assistant verify every accepted change.

Freeze untouched F as an anchor. A custom-weight candidate must verify that the weights are actually used; this engine's `get_value_fn('base_fn', params)` ignores supplied params. Do not silently alter F or the common engine to improve a result. Keep dependencies/weights/configuration inside each bot's permitted artifact, never copy an environment.

Every owner uses the [detailed round protocol](team-work/member-4/phase-1/03-ITERATION-AND-TEST-PROTOCOL.md) for self-testing/upload packets. Start with small legality/profile checks, then paired F/peer comparisons; do not require a slow search bot to finish hundreds of random-fallback games before diagnosing its clock failure. Numerical sample sizes there are planning defaults and depend on actual throughput/time remaining.

## Individual specifications and acceptance

Each owner's `07-TWO-BOT-BUILD-ASSIGNMENT.md` gives inputs, minimum decision rules, counterexamples, ablations and upload requirements:

- [Aroosh: B01 / B02](team-work/member-1/07-TWO-BOT-BUILD-ASSIGNMENT.md)
- [Avadooth: B03 / B04](team-work/member-2/07-TWO-BOT-BUILD-ASSIGNMENT.md)
- [Pranesh: B05 / B06](team-work/member-3/07-TWO-BOT-BUILD-ASSIGNMENT.md)
- [Anni: B07 / B08](team-work/member-4/07-TWO-BOT-BUILD-ASSIGNMENT.md)

The first upload must include a versioned entrypoint, hypothesis, manifest, exact tests/results, parent/control, faults/CPU counters and known weaknesses. A bot's builder is not its sole verifier. The assistant will compare immutable uploads; owners then implement fixes rather than all four changing a shared bot at once. Separate member branches reduce merge collisions; coordinate shared helpers explicitly. No branch, bot skeleton or runner was created here.

## Improvement rounds and the eight-bot target

`owner builds two → owner self-tests → GitHub upload → assistant audits/retests/clashes → written improvement tickets → owner revises/uploads → repeat`.

Keep frozen parents, all matchup results and unsuccessful variants. Use new development board groups across rounds and reserved selection/confirmation groups. Select improvements on strength, weak matchups and reliability; preserve uncertain ties. If fewer than eight satisfy quality gates, repair/drop candidates rather than pad the finalist list. Distinguish initial eight assigned strategies from eight proven finalists.

The official event accepts at most **7 scored submissions and 10 total uploads**. The eight local bots are a comparison portfolio; choose event artifacts using the actual remaining submission ledger. No GitHub upload is an event submission, and no SSH/portal work occurs in this task.

## Decisions made and work still needed

Chosen now: eight interpretable initial strategies, two per human, no external-corpus training dependency, independent assistant verification after uploads, explicit owner feedback/retest loop, shared stable environment. Deferred until real code/evidence: coefficients/search limits, exact fixtures, measured CPU/memory/throughput, final rankings, learned replacements and event upload selection. Full optimality or exhaustive coverage of Catan strategies is not claimed.

See [synthesis](team-work/PHASE-1-REVIEW-AND-SYNTHESIS.md) and [task verification/provenance](team-work/PHASE-1-COMPLETION-AND-VERIFICATION.md). No new agent performance is reported.
