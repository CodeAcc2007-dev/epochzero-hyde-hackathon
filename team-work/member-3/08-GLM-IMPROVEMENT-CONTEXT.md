# Pranesh: direct GLM handoff for B05 and B06

17 October 2026. Owner **Member 3, Pranesh**. Frozen parents are **B05 v003 / B06 v003**. This is a new independent review and implementation brief. Parent runtime files, old results and research are preserved. Start with `implementation/BUILD-AND-RESULTS.md`, manifests and this document; v001/v002 are superseded development evidence.

## Paste this to GLM

> Improve only my B05/B06 using `team-work/member-3/08-GLM-IMPROVEMENT-CONTEXT.md` and `team-work/reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md`. Preserve the frozen v003 files and implement new v004 versions if unused. First reproduce and fix the low-clock winning-settlement defect with correct terminal/road-cut semantics. Keep B05 as a bounded same-turn planner and B06 as a cheaper threat/bonus-race policy. Then test search shortlist coverage for B05 and deterministic trade-enabler threat recognition for B06, one change at a time. Use the existing launcher and Hyde junior workflow, independently check drafts, and add new-version regressions before 500 paired-seat games per bot plus matched frozen-parent evidence. Do not alter other owners, F, engine, old evidence or event state. Deliver code, manifests, standalone package checks, full results, CPU/fault counters and unresolved hypotheses.

Read the [common contract](../reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md), [review overview](../reviews/2026-10-17-B03-B08/README.md), [verified probes](../reviews/2026-10-17-B03-B08/verified-findings.json) and [reproducer](../reviews/2026-10-17-B03-B08/verify_findings.py).

| Runtime file | SHA-256 |
|---|---|
| B05/v003/agent.py | `27813f37d9ff4d794115b19b193b3d03fb64673465555062bc9595702dafa03b` |
| B06/v003/agent.py | `7369f4f0ef4eed12794075257d6a2f630c426428982a65a5ca871b43bd2ebb66` |
| Both member3_core.py | `4fdabf1b1bb282a225701b8078b9135dc26e0622fc25e1ed9fd516bf56a6b4bd` |
| Both race_math.py | `e9b43a4610714cd1b79954d6b070782e0c53e36f4efb1b0d8c8d8602c51a3b98` |

Existing evidence: B05 729/1000 vs F, B06 695/1000 on the same 500 paired boards841000–841499; their direct200-game match was103–97, inconclusive. These historical results were not rerun in this review. Source hashes and result aggregates were checked, and all 26 existing semantic/helper tests passed again. The review adds small official-harness loading/peer checks and new constructed counterexamples. None establishes improvement from a proposed fix yet.

## M3-C01 — P1 verified in both bots: terminal guard before the clock fallback

**Source:** `member3_core.Policy.decide`, approximately lines247–268. Only a city at actual9 VP is recognized before `budget < .001` returns the generic ROLL/END_TURN fallback. The eligible Knight guard comes later; there is no corresponding cheap winning-settlement guard at that point.

**Reproducer:** `COMMON-01` constructs an invariant-checked nine-actual-VP state with legal `BUILD_SETTLEMENT(19)`, no affordable city, and `cpu_left=0.0009`. Executing the settlement wins; B05 and B06 return END_TURN. This is a constructed phase/board fixture, not a reached tournament loss. It verifies missed terminal priority, not illegal output or exhausted CPU.

**Implementation:** create one bounded terminal-action selector before generic fallback, then use it in the new copies of both policies. A legal city at 9 is cheap. An eligible Knight must use played-card counts, current holder and strict Army takeover. Settlement/road actions can change Road ownership; verify the engine winner or the existing public/hidden-bound terminal logic rather than blindly assume every settlement gives a safe net+1. The initial real state is nonterminal; sampled opponent actual VP must not veto a proven own win. Keep resource chance actions out of guaranteed-terminal classification. Avoid copying/scoring every action when only a handful are terminal candidates.

**Acceptance:** the old fixture fails the desired selection assertion; new B05 and B06 choose the winning settlement at low clock in both seats. Add Knight/Army before roll, no eligible new Knight, ties, own Road loss/cut, opponent Road gain and uncertain simultaneous qualifiers. Preserve a cheap legal fallback when no win can be established within budget. Tests measure CPU and avoid setting an unrealistic requirement to finish arbitrary search with zero time. No new broad exception handler should hide defects.

## B05 — same-turn completion planner

### B05-01 — P2 hypothesis: protect useful enablers from root pruning

**Source:** `Policy.decide` roots are scored greedily, `candidates[:5]` becomes the beam, depth2–4 keeps five states, and all nonroot work shares an80-expansion cap. The special terminal-enabler sweep at actual9 only checks an immediately following city/settlement. A root that temporarily sacrifices hand score can disappear before a two/three-step purchase completion is explored. These are verified bounds; their loss contribution is not measured.

**Implementation experiment:** reserve a small number of beam slots for legal actions that reduce a concrete complete-purchase deficit: port/bank trade→trade→city, road→road→settlement, YOP→trade→purchase, eligible Road Building free-road sequence. Compare against the unchanged greedy shortlist. Use actual legal child states, piece/bank constraints and current-turn flags; each search root retains its original legal index. Track resource deficit/target feasibility instead of keeping every trade. Avoid circular conversions with a state key covering all relevant phase/resources/board flags. Retain the current boundary before random steal/dev draw/roll.

**Acceptance:** meaningful fixtures require a temporarily lower-scoring enabler and show a correct legal completion; add an unavailable-bank and unavailable-piece negative case. Include8-VP two-point Road/Army outcomes and forced-road subphases, not only 9-VP buildings. Preserve the low-clock incumbent and bound work independently of root-list size. Replay a reached decision to establish usefulness before declaring a strength fix. **CPU risk:** moderate; reserve slots within current cap before increasing width/depth.

### B05-02 — P2: profile repeated evaluation and explain search benefit

**Evidence:** historical mean CPU160.2 ms/game, max 530 ms; greedy control273/400 vs B05 298/400 on matched boards. This supports the original whole tactical layer, not a particular new branch rule. Existing counters expose total nodes/cutoffs but do not attribute copy cost, root coverage, transpositions or useful action changes.

**Implementation:** add an external diagnostic wrapper reporting prompt, legal-root count, roots examined, retained-enabler types, copied states, feature-cache hit/miss, terminal search hits, depth, elapsed own CPU, fallback reason and deviation from one-step control. Do not put decision traces or file I/O in the submitted agent. Use the original maximum-CPU case game303/board841151 with its 20-game chunk/global indices, plus fresh stress positions. A replay differs if F's process RNG or global index is reset.

**Acceptance:** show where time goes and whether added enabler slots change meaningful decisions. Compare one optimization at a time against frozen v003 on fresh500-game paired batches. Retain all cutoff/fault outcomes. An action change or higher score alone is not a win-rate gain.

### B05-03 — P2 test gap: reached Road-cut and stochastic-boundary cases

Current semantic tests construct valid engine states; they do not provide a full reached Road-cut trace. Extend a separate diagnostic replay to save a legal action history for settlement cutting a Road, including holder/tie transfer and terminal ordering. Test only public guarantees when hidden opponent VP could change the outcome. Verify `BUY_DEVELOPMENT_CARD` and robber values remain expectations and never become deterministic beam continuations. A failure to find a reached example is an explicit remaining gap, not a passed test. Preserve the existing deck-order-invariance/steal/eligibility tests.

## B06 — opponent threats and bonus races

### B06-01 — P1 verified horizon gap: include a bounded deterministic trade enabler

**Source:** `Context.threat`, lines126–140, only calls `can_afford` on the current enemy hand for city or settlement. It gives confidence1 at public9, design weight0.35 at public8 with dev cards, otherwise0. These weights are not fitted probabilities.

**Reproducer:** `B06-01` gives the opponent public9, a remaining settlement and city piece, and hand `(WOOD,BRICK,SHEEP,WHEAT,ORE)=(4,0,0,2,2)`. `Context.threat` returns0. In the explicit post-roll fixture, legal4 WOOD→ORE followed by BUILD_CITY wins. The current classifier misses this exact conversion. The fixture does **not** claim the opponent is certain to win after the next random roll, which may change resources/discard obligations.

**Implementation:** add a bounded bank/owned-port conversion feasibility check for a small set of viable goals, with legal pieces/sites and bank availability. Start with one trade→building; add multi-trade feasibility only when validated. Return structured categories such as `affordable_now`, `deterministically_convertible_if_hand_persists`, `roll_dependent`, `hidden_dev_conditional`, plus minimum deficit and relevant resources. Map categories to separately tunable penalties. Preserve exact opponent resources and uncertain dev identities. Do not execute an opponent roll in a single sampled world and call it known.

**Acceptance:** recognize the given trade-city; handle2:1/3:1 ratios, reserved build ingredients and integer leftovers; reject bank shortage, no city piece, no legal settlement site and blocked routes. Verify a theft/Monopoly that removes a necessary resource actually breaks the modeled line. Show confidence changes when a 7/discard or future roll is involved. Own certain terminal moves retain priority over defense. **CPU risk:** low for integer feasibility; moderate for enumerating many legal trade chains.

### B06-02 — P2 hypothesis: quantify the opportunity cost of defense

Current penalties can favor robber/Monopoly denial when the bot should advance its own VP. Expand the threat horizon without blindly increasing its weight. Compare new threat-on to threat-off using the same evaluator and frozen parent. Add states with own immediate win, own one-trade win, enemy public8 with ambiguous hidden VP, enemy public9 but no feasible piece/site, and a cheap denial versus an expensive lost purchase. Report whether defensive actions change the modeled threat and what own progress they sacrifice. Use actual weak-peer cases once available; do not infer a loss cause from total F win rate.

### B06-03 — P2: legal geometry for Road races; preserve strict Army rules

**Source:** `Context.value` adds Road-race potential from a scalar length gap ≤3 and awards small buffer credit when already holding Road. A scalar gap alone does not establish a legal, affordable continuation; opponent buildings can cut a route and a branching network can require more edges. This is heuristic potential, not fake awarded VP, but can misprice a race.

**Implementation experiment:** use a bounded legal one/two-edge route certificate for close races, factoring pieces and road resources; otherwise keep a discounted potential explicitly marked uncertain. Distinguish own bonus capture, retaining an existing bonus and reducing an opponent's bonus. Do not conflate total roads with longest simple route or count a tie as a takeover. Reuse pure helper tests only when their assumptions match the real board. Compare the geometry cost with B06's current speed advantage before broadening search.

**Acceptance:** forks/cycles, enemy settlement cuts, exhausted road pieces, exact holder ties and Army incumbent ties; ensure no bonus is added to actual VP by a heuristic. Keep new route checks bounded and optional if they cannot beat the parent in controlled evidence.

## Run and deliver

```bash
./team-work/run-python.sh -m unittest discover -s team-work/member-3/implementation -p 'test_*.py' -v
./team-work/run-python.sh team-work/reviews/2026-10-17-B03-B08/verify_findings.py
```

The first command checks the old implementation suite; the second reproduces frozen defects. Add a separate new-version regression entrypoint and package-load tests. The old26 passing tests plus reproduced defects do not certify v004. Use the contract's500-game driver with explicit B05/B06 v004 paths, matched v003 parents, fresh seeds and new output directories. Package all three runtime modules (or independently verified standalone assembly); do not ship only the tiny `agent.py` wrapper. Do not overwrite v003 ZIPs/manifests. Human Pranesh review remains separate from assistant checks.

## Subsequent local round 2 implementation

The user authorized implementation of this prompt for Members 3 and 4. New B05/B06 v004 standalone candidates, manifests, ZIPs, regressions and matched 500-game results are complete locally. Read [the round 2 report](implementation/round-2/BUILD-AND-RESULTS.md) and [remaining ticket scope](implementation/round-2/VERIFICATION-AND-SCOPE.md) before follow-up work. Do not overwrite these freezes or rerun used boards as fresh evidence. Proposed broader experiments remain deferred. Human review and GitHub publication are pending.
