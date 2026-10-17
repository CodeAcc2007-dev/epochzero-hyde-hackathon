# Pranesh B05/B06: strategy, implementation and decision record

17 October 2026. The user explicitly authorized the primary assistant to implement Pranesh's two bots, test against F, document and publish. This supersedes the earlier human-build-only boundary for **Member3 only**. Other members' bots/research remain outside scope. No SSH, portal or scored event submission.

## Active candidates

Use `bots/B05/v003/agent.py` and `bots/B06/v003/agent.py`, relative to Member3. Each standalone directory has its own entrypoint, common policy module and small math helper. Common modules are byte-identical; wrappers choose genuinely different algorithms, not merely different coefficients. v001/v002 are retained internal development snapshots, not the current recommendation.

**B05: deterministic same-turn completion.** Scores legal root actions, then searches a width-five/depth-four beam with up to80 non-root expansions. At nine own actual VP it checks legal one-action enablers for a terminal next building before beam pruning. Only deterministic build/trade/YOP/Monopoly/dev activation transitions enter that tree. It stops at a different player, turn boundary, unsupported prompt, stochastic continuation or terminal own state. Each real call replans and returns the original legal-action index. Resource/bank/phase/piece legality comes from engine execution, not handcrafted future actions. State deduplication prevents maritime cycles within a decision.

**B06: visible threats and bonus races.** Uses the same one-step base but no beam. It penalizes an opponent's currently affordable legal city/settlement near10, values strict Road/Army progress and transfer conditions, and compares denial with lost own progress. At nine opposing public VP, a currently affordable legal one-point build is a serious visible opportunity. At eight plus held devs, the .35 multiplier is an explicitly chosen risk weight, **not a calibrated hidden-VP probability or guaranteed future win**. Future roll/trade chains and unknown opposing action-dev eligibility are not solved by this fast classifier.

## Shared evaluation and chance treatment

- Own actual VP40/point, enemy public VP−30/point, weighted production/diversity30, enemy production−22, ingredient retention and limited road-reach potential. Coefficients are hand-selected engineering choices, not fitted to the external CSV or held-out games. Early source review/fixtures changed guards, not tuned win-rate weights.
- Wheat/ore production weight1.15; wood/brick .95 and sheep .9. Diversity credits usable rates rather than treating a tiny rate as full coverage. City/settlement ingredient retention, integer owned-port surplus conversion and discard exposure shape trade/discard choices. Expansion terms estimate potential at up to two additional roads; they do not certify a multi-turn target remains available.
- Samples one engine copy with a fixed local RNG for the allowed API. It ignores sampled opponent actual VP, hidden card identities and deck order in evaluation. Public opposing dev **count** is obtained as a sum; public multiset counts subtract own held cards and both public played counts. No private board-seed prediction or real hidden-state access.
- A roll is a chance boundary, never executed to pick a lucky root. Before rolling, non-Knight devs are saved for known post-roll needs. A Knight is evaluated through its deterministic Army change and the best immediate robber placement's **exact expected steal** over the visible resource-card distribution; no further random branch is expanded.
- Robber destinations include own production loss. The expected hand/threat score enumerates resource types weighted by visible card counts. Monopoly's resource transfer is deterministic and goes through the engine. A development purchase is an explicit expected score over possible types, not the sampled top card. Its draw model assumes exchangeability and conditions on the necessary nonterminal hidden-VP bound; this is not a full policy/history-calibrated posterior.
- Known own terminal actions outrank ordinary progress. Simultaneous qualifiers are checked against the engine's color-iteration rule using public changes and hidden-VP bounds. A known opponent public10 successor scores as a loss. Ambiguous Road-cut terminal effects are treated conservatively; no legally reached Road-cut exploit/failure has been demonstrated.

## Clock and runtime

Soft decision cap22ms B05 /16ms B06, further limited to22% of reported remaining game allowance. The official cumulative clock remains unchanged. The best legal incumbent is retained as work stops. A very low clock returns a cheap legal fallback before copying a world; a known immediate city win is checked first. These are soft caps, not real-time guarantees: one operation may run over a soft boundary, and CPU cutoffs can vary search breadth by machine. Actual harness counters decide eligibility.

No workers, network calls, LLM, files or training inside `decide`. State/evaluation caches live only within one decision; diagnostic counters do not influence action choice across games. Public map data is read; observation objects are not mutated. The declared runtime dependencies are the existing Python3.11/pinned engine and its networkx dependency, plus stdlib. No environment is duplicated.

## Development chronology and corrections

1. Primary authored architecture/core, fixture design and experiment driver. Hyde produced a small arithmetic helper and unit-test draft; both were inspected and independently tested. See [junior record](JUNIOR-AND-VERIFICATION-LOG.md).
2. v001 smoke: twelve games each on development boards, retained with exact source fingerprints. Those small results are diagnostics, not final strength.
3. Source review added conservative own-terminal handling for Road ownership changes and all short terminal enablers before beam pruning (v002). A road→settlement fixture initially failed because its geometry had **no** one-road settlement available; enumeration demonstrated that assumption was wrong. Corrected the fixture by finding/executing a legal road prefix, then checking the intended one-road continuation. The initial failure was not hidden or misreported as a passed policy case.
4. Stopped the preliminary B05/v002 run deliberately after240 completed records when reviewing the symmetric known-opponent-terminal guard. The next chunk was incomplete and is not counted. No claim a match discovered that source-level issue. v003 adds the explicit known-opponent10 loss score and a pre-copy low-clock fallback; tests cover both. v001/v002 source snapshots and partial metadata remain for provenance.
5. v003 runtime code is frozen before final tests on a new disjoint board range. Do not edit it after looking at results; later improvements require a new version and new development/selection evidence.

## Independent checks and limits

22 primary engine/policy tests plus four reviewed helper tests cover phase correctness, terminal chains, Knight eligibility/Army timing, VP draws, bank-limited YOP, forced second free road, fixed out-of-turn discard quota, exact Monopoly transfer, expected robber values, strict bonus ties/transfers, sampled-allocation invariance, observation preservation and low-clock behavior. Helper tests enumerate486 hand/cost combinations. Fixtures use genuine legal setup actions plus explicit synthetic resource/dev/building allocation with bank/deck/piece/VP invariants. **They are not complete reachable game histories**, and guard-only synthetic terminal probes are not advertised as a Road-cut trace.

The unchanged harness provides real full games under the clock; those are distinct from constructed fixtures. Results and remaining limits belong in [build/results report](BUILD-AND-RESULTS.md). There is no O/private-board evidence, no measured scorer-machine compliance and no guarantee these are final tournament winners.
