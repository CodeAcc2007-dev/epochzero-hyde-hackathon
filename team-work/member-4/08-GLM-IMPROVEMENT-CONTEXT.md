# Anni: direct GLM handoff for B07 and B08

17 October 2026. Owner **Member 4, Anni**. Frozen parents are **B07 v001 / B08 v001**. Read `implementation/BUILD-AND-RESULTS.md` before changing anything. This review preserves those standalone artifacts, your research findings and all existing evidence; fixes belong in new v002 versions if unused.

## Paste this to GLM

> Improve only my B07/B08 from the exact v001 parents, following `team-work/member-4/08-GLM-IMPROVEMENT-CONTEXT.md` and `team-work/reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md`. First add regression-backed low-clock terminal selection to both, fix B08's new-Knight delay model, and make B07's bounded reply coverage intentional. Keep B07 sampled-opponent planning and B08 adaptive VP-route planning distinct. Profile and ablate before increasing search or sampling. Use the existing environment and bounded Hyde junior workflow; preserve old versions and other owners. Test actual new standalone artifacts, use 500 paired-seat games per bot with matched parent evidence on fresh development boards, and deliver manifests, packages, full records, CPU/fault counters and explicit unresolved limits. No SSH/event submission or unrequested publication.

Read the [shared contract](../reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md), [overview](../reviews/2026-10-17-B03-B08/README.md), [probes](../reviews/2026-10-17-B03-B08/verified-findings.json), [source audit](../reviews/2026-10-17-B03-B08/source-and-result-audit.json) and `implementation/DESIGN-AND-DECISIONS.md`.

| Parent standalone source | SHA-256 |
|---|---|
| B07/v001/agent.py | `9e471d1b89a2357e20e168b222347ca4901dbebd1d6ab01359a47ce84961c588` |
| B08/v001/agent.py | `7470a4040f4cef80b101ceae144be93d820f8ed317c0f6bb22886e2ba30cb8eb` |

Existing500-game results: B07 361/500 (72.2%), mean 118.4 ms/game; B08 363/500 (72.6%), mean 411.9 ms/game, on the same 250 boards891000–891249. No recorded harness faults/exhaustion. Two additional wins do not establish a strength ranking; B08 costs about 3.5 times as much CPU in this historical batch. No direct peer/main component ablation was performed in that build. This review reran all 15 semantic tests, verified component hashes and byte-identical assembled/development agents, added frozen-artifact counterexamples and small clocked peer/loading checks. Historical500-game batches were not replayed.

## M4-C01 — P1 verified in both: terminal selection must survive low clock

**Source:** `implementation/member4_policies.py`, `Member4Policy.decide` (inlined into each artifact). A city at actual9 is the only terminal shortcut before the low-budget fallback. `COMMON-01` in the review reproducer constructs legal `BUILD_SETTLEMENT(19)` from actual9, proves it wins in the engine, then observes END_TURN from both frozen agents when `cpu_left=0.0009`.

**Implementation:** place a cheap, bounded known-terminal selector before generic ROLL/END_TURN fallback. Cover eligible Knight/Army and settlement/road bonus changes as well as city. Do not assume settlement always nets exactly+1: a road cut can transfer VP and the engine has particular simultaneous-qualifier ordering. Reuse the public/hidden-bound guard in the copied context rather than trusting sampled opponent actual VP. Separate certain terminal actions from chance-valued draws/thefts.

**Acceptance:** frozen parents fail a new desired-behavior test and both v002 artifacts pass; test both seats, low clock, Knight before roll, new-dev ineligibility, strict ties and road-cut counterexamples. Inspect actual standalone agent imports/hashes. No broad exception handler, runtime tracing I/O or unbounded search in the emergency path. These are valid constructed engine fixtures, not claims that this failure occurred in prior matches.

## B07 — sampled-opponent planning

### B07-01 — P2 verified coverage limitation: diversify the bounded reply list

**Source:** `Member4Policy.opponent_reply` sorts Knight, all five Monopoly resources, Road Building, then YOP actions and truncates to8. The frozen probe gives22 legal pre-roll dev replies; the selected eight leave **only YOP(BRICK,BRICK)** and omit the other14 YOP choices. The production-ranked robber shortlist and six-option free-road lists have their own coverage limits. This is a verified candidate-selection effect; no lost game is attributed to it yet.

**Implementation experiment:** choose a bounded, meaningful representative set per dev family. Include Monopoly candidates with nonzero relevant theft, YOP combinations which reduce an actual completion deficit, and Road options leading toward a bonus/valuable connection. Deduplicate dominated or equivalent replies before spending the global cap. Preserve exact legal choices and card/turn eligibility. Compare all retained root candidates over the same worlds and reply policy. Raising sample count does not repair a systematically omitted reply.

**Acceptance:** a YOP wheat/ore enabler appears when brick/brick cannot help, empty Monopoly resources do not crowd out every other family, a useful Road edge outside early numeric order survives, and tied/equivalent action ordering does not decide which strategy is considered. Include a negative bank-shortage case. Record which families/options were omitted. Do not classify a pre-roll YOP→purchase as certain immediate victory: purchasing still requires the roll boundary.

### B07-02 — P1 measurement prerequisite: isolate whether belief replies help

**Evidence:** historical12-game instrumentation recorded 651 decisions,25 completed reply comparisons and 4 changed decisions, with 4 cutoffs. Most decisions never use the reply selector. This establishes that the feature ran, not that it improved outcomes. The current `sampled_replies=False` control still runs the own-continuation forecast over three repeated worlds, so it is not identical to returning the one-step incumbent.

**Implementation:** instrument an external wrapper with root eligibility reasons, valid/rejected sample counts, per-root coverage, forecast failures, nodes, cap exhaustion and changes from the root incumbent. Define three explicit controls: root evaluator only; deterministic own-follow-up/end forecast without hidden replies; full sampled-reply candidate. Keep caps/evaluator and frozen sources documented. Compare complete paired candidates; preserve incumbent if any planned comparison is incomplete. Do not let one candidate receive more samples or a longer reply horizon merely because it was visited first.

**Acceptance:** report feature invocation and useful changed decisions with reached traces, not just node totals. Use a matched500-game main evaluation against the parent; extra control batches are separately identified and bounded. If no gain is supported, keep the simpler parent/control rather than expand to dozens of worlds. **CPU risk:** new reply ranking must fit the 24 ms/22%-credit budget including root work and sampling.

### B07-03 — P2 hypothesis: improve the forecast horizon only after coverage/attribution

Current `forecast_end` considers at most one own deterministic follow-up from the first 12 ordered actions, voluntarily ends the turn, then models a pre-roll opponent dev reply. It does not model post-roll purchases, several own enabling actions, or every useful free-road line. Truncation can penalize a promising root for an artificially unfinished own turn; a sampled opponent response is conditional, not a certain future.

**Experiment:** first improve the own follow-up shortlist using complete-purchase deficits while retaining the same bounded horizon. Only then consider a tiny exact roll-outcome expectation or explicit conditional threat categories after ROLL. Keep buy/steal randomness explicit; no hidden actual identity may affect the real policy as known truth. Test immediate own completion before an imagined enemy reply, partial own turn, empty/invalid belief sets and unchanged-incumbent cutoffs.

**Posterior limit:** rejecting sampled already-terminal opponents is necessary but is not full public-history conditioning. A future history model needs public card counts/plays, acquired-card timing and feasible remaining deck counts; it must not reconstruct hidden opponent purchase identities from masked records. Keep this a separate high-risk experiment and do not infer calibration from three valid samples.

## B08 — adaptive VP-route planning

### B08-01 — P1 verified: a newly purchased Knight requires a later turn

**Source:** `RouteContext.plans` computes `delay=2*max(0,to_play-1)` and adds2 only if a currently held Knight is new or a dev has already been played. With no Knight in hand, two already played and one more needed, a future purchase receives delay0.

**Reproducer:** `B08-01` constructs that invariant-checked state. The Army plan is `('army',(0,0,2,2,2),2,0.0,0)`: estimated two dev purchases, two potential VP, **zero delay**. A controlled engine purchase of a Knight confirms PLAY_KNIGHT_CARD is not legal that turn. This is an inaccurate route valuation; the agent still returns legal moves.

**Implementation:** represent earliest eligible own turn separately from resource acquisition and expected purchase count. A Knight not already held/eligible incurs at least a next-own-turn wait after acquisition; multiple required plays obey one action-dev per turn. Old playable cards, new held cards, no held cards, and already-used dev turn need distinct cases. If retaining 'rolls' units, document how own-turn waits convert to the two-player roll timeline without double-counting collection time. Moving opponent Army targets remain uncertain.

**Acceptance:** no-held/new-held/old-held/played-this-turn cases, strict opponent incumbent ties, no remaining Knight supply, multiple needed plays and already-owned Army. Known terminal eligible Knight remains immediate; a newly bought one is never valued as an immediate guaranteed terminal. Keep route potential distinct from actual VP.

### B08-02 — P1 profiling prerequisite: reduce repeated route evaluation cost

**Evidence:** B08's historical CPU mean 411.9 ms, p95690 ms and max 1070 ms versus B07's118.4 ms mean; both had zero exhaustion. `RouteContext.value` calls `potential`, which rebuilds a plan menu and runs `estimate_rolls` for each plan. Each nontrivial estimate uses18 bisection steps. Geometry caching helps board features but does not cache every hand/bank/plan forecast. Search repeatedly evaluates related states, including conditional robber hands and buy values.

**Implementation:** instrument counts/time for `plans`, `spatial_plans`, `road_steps`, `estimate_rolls`, root versus continuation and cache hits. Cache only by sufficient inputs: hand, bank, trade ratios, robber-adjusted rates, piece availability, dev eligibility/played flags, bonus holder/target and own VP gap as relevant. Do not key solely by board or raw hand if a dev play or depleted bank can change the answer. Preserve current soft caps and use a bounded cache per decision; no cross-game unbounded growth.

**Acceptance:** exact scoring equivalence for cache hits on a diverse fixture set; invalidation for bank, robber, holder and new-dev changes; lower own CPU or more completed comparisons at comparable CPU. Compare revised route logic versus parent on fresh500-game batches; a local speedup alone is not a strength improvement.

### B08-03 — P2 hypothesis: preserve target feasibility and uncertainty

`spatial_plans` stores a family/cost/gain but not a chosen target/path; expansion stops at two additional roads. `road_steps` searches at most28 extensions and retains four first-step states. Many first-step options can exhaust the 28-node total before second-step exploration. Dev/Army expected buys use `ceil(k/p)` as a heuristic and cap purchases by deck length. Mean-income projection with a 0.85 rate factor and current-bank cap is not a stochastic completion probability and can over/understate a route.

**Implementation experiment:** retain the target node/path certificate for promising spatial plans and reserve some Road budget for deeper candidates, rather than allowing all root edges to consume it. Record the top two routes and why the choice changed. Use conservative comparable uncertainty estimates or a justified finite-deck model for dev purchases; do not claim `ceil(k/p)` is exact without-replacement expectation. Handle duplicate/owned bonuses, blocked sites, no piece, bank depletion and production concentrated on one robber-vulnerable tile.

**Acceptance:** relabeling/sorting board edges does not arbitrarily erase the only short winning path; impossible routes get no credited VP; competing route selection can switch when board/bank/bonus feasibility genuinely changes. Explore whether stateless per-decision replanning wastes committed resources using reached traces before adding persistent plan state. Add a reset mechanism and history validity tests if persistence is introduced. Compare fixed-city versus adaptive routes as a controlled experiment, separately from cache/eligibility fixes.

## Assembly, tests and final packet

```bash
./team-work/run-python.sh -m unittest discover -s team-work/member-4/implementation -p 'test_member4.py' -v
./team-work/run-python.sh team-work/reviews/2026-10-17-B03-B08/verify_findings.py
```

These verify the parents/reproduce findings; they do not test a future v002. The current `build_agents.py --freeze` targets **v001**. Do not run it expecting a new version. Add an explicit new-version destination or a separate bounded build procedure, preserve executable-AST equivalence and verify new assembled bytes against the component manifest. Load/test the actual ZIP-extracted single `agent.py` for each bot. Main checks use 500 games per bot; fresh confirmation must follow tuning. Keep every outcome and distinguish ablations, timing instrumentation, smoke and main evaluation. Anni's human review remains pending until actually performed.
