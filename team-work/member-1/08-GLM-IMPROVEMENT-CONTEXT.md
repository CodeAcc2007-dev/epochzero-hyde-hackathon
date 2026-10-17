# Aroosh: direct GLM handoff for B01 and B02

17 October 2026. Owner **Member 1, Aroosh**. The user added these bots to the active review after their build completed. Parents are the new standalone **B01 v001 / B02 v001**, not the older collection under `earlier bots/`. Read `implementation/BUILD-AND-RESULTS.md`, the two manifests and this context. Preserve old research, old agents, frozen v001 and all test records.

## Paste this to GLM

> Improve only my B01/B02 using `team-work/member-1/08-GLM-IMPROVEMENT-CONTEXT.md` and `team-work/reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md`. Verify the exact v001 hashes and create v002 if unused. First fix the reproduced city-goal filter that rejects an immediate trade→Road-bonus win, and the low-clock winning-settlement fallback. Keep B01 a bottleneck economy policy and B02 a city/dev investment policy. Add regressions that fail on the parents, test the actual new standalone artifacts, then run small correctness checks and 500 paired-seat games per bot with matched frozen-parent evidence on fresh boards. Use the shared launcher and bounded Hyde junior workflow with primary review. Do not touch another member's bots/research, earlier agents, F, engine, old evidence or event submission state. Deliver code, manifests, ZIP byte checks, complete results, CPU/fault counts, rejected experiments and remaining uncertainties.

Read the [shared review](../reviews/2026-10-17-B03-B08/README.md), [contract](../reviews/2026-10-17-B03-B08/IMPLEMENTATION-CONTRACT.md), [executable counterexamples](../reviews/2026-10-17-B03-B08/verify_findings.py) and [probe results](../reviews/2026-10-17-B03-B08/verified-findings.json). The review directory retains its original B03–B08 name, but its current scope is all eight bots.

| Parent standalone source | SHA-256 |
|---|---|
| B01/v001/agent.py | `e3c951ab2a9a1ca7b8e63fa04b955caade84133c7da206a7a1561bd705986a57` |
| B02/v001/agent.py | `6e9a3324449a46119c3e94c60bc1ed7528644d8efffa1f457590d5036973020c` |

The two manifests pin the component sources, including `economy_policies.py` hash `c3250bf6a8c6978e52090ba5f6054957d9bf89cfc5e8c2d8ee9bae65bf1a4095`. Primary review verified those component hashes and byte-identical development/frozen artifacts, recomputed main wins and reran19 semantic tests. These passes did not catch the two new reproduced defects below.

Historical main evidence: B01 **381/500 (76.2%)**, B02 **359/500 (71.8%)**, on paired boards911000–911249. Mean own CPU205.9 ms and 202.9 ms; no recorded harness faults/exhaustion. These batches were not replayed in this review. Their22-win difference is a matched-F observation, not proof B01 beats B02 directly or beats the other six bots. No old bot's results should be attached to these new names. New review smoke includes actual standalone loading, F, B01/B02 and B05 peer games; it is diagnostic only.

## M1-C01 — P1 verified: a retained city goal blocks a certain Road win

**Source:** `EconomyContext.__init__/goal`, `trade_allowed/action_value`, and `EconomyPolicy.decide/complete_purchases` in `implementation/economy_policies.py`. A trade which fails `improves_goal` is returned as `(-inf, None)` before search can explore its child. The terminal enabler special case only runs at actual9 and only checks following city/settlement actions.

**Reproducer:** `M1-GOAL-TERMINAL` constructs actual8 VP, own longest road4 without the bonus, a city upgrade available, and hand `(WOOD,BRICK,SHEEP,WHEAT,ORE)=(0,1,0,2,4)`. Both contexts retain the city goal. Legal **4 ORE→WOOD**, followed by **BUILD_ROAD(52,53)**, takes Road and wins at 10. Both trade evaluators reject the first action as `-inf`; both policies instead BUILD_CITY(8), reaching9 and giving up this immediate line. The engine confirms the two-action win and all resource/dev/piece/VP invariants. This is a constructed counterexample, not a claim about a historical loss.

**Implementation:** do not allow a heuristic goal-family filter to suppress a proven terminal chain. Put a small terminal-completion check before strategic trade rejection, covering Road/Army two-point gains from 8 as well as buildings from 9. Preserve root indices, exact bank/piece feasibility, strict bonus-holder rules and chance boundaries. Prefer targeted goal certificates/terminal candidates over globally enabling every bad trade. A broader alternative is to include legal close-bonus goals in the feasible purchase menu; keep it distinct from the minimum correctness repair.

**Acceptance:** both v002 agents choose the winning trade and then the winning road in this fixture; parent v001 fails. Test an opponent's longer Road, a tie, no road pieces, blocked extension, unavailable bank, a nonterminal road and an immediate own win which must take precedence. Confirm the chosen simulated root remains legal in the original list. Keep existing reserved-last-wood and depleted-bank tests passing. **CPU risk:** bounded extra terminal candidates; do not add an unbounded trade×road search to every early-game decision.

## M1-C02 — P1 verified: low-clock settlement win is missed

**Source:** `EconomyPolicy.decide` checks only a city at actual9 before `budget < .001` returns ROLL/END_TURN. In `COMMON-01`, legal settlement19 from actual9 wins, but both frozen policies END_TURN at `cpu_left=0.0009`.

**Implementation:** run a cheap bounded known-terminal selector before generic fallback. Include eligible Knight/Army before rolling and safe settlement/road transitions. A settlement may cut a Road, so do not blindly assume net+1 or trust sampled opponent actual VP. Use engine/public-bound terminal semantics. Keep stochastic draw/theft outcomes out of guaranteed-win classification.

**Acceptance:** low-clock city, settlement, Knight and no-win fallback in both seats; new-Knight ineligibility, strict bonus ties and road-cut cases. Test actual packaged agents and time the emergency path. A legal END_TURN is not acceptable merely because the old low-clock test asserted it on a different nonwinning fixture.

## B01 — bottleneck economy

### B01-01 — P2 hypothesis: retain a useful goal without hiding better feasible purchases

The initial goal family is selected once per observation, then retained through simulated successors whenever that family remains available. Its score is `reward / (1 + conversion_gap + 0.35*raw_missing + bank_blocked)`. This avoids treating every card as interchangeable, but does not itself prove the retained family remains best after a purchase, a changed port or a bonus opportunity. The terminal case above is verified; broader overcommitment is still a hypothesis.

**Experiment:** retain a small menu of feasible alternatives, each with a named target/cost and legal reachability, while preserving ingredient protection for the current intended purchase. Reconsider the family after completing it or losing feasibility; allow a switch only with a documented reason/value margin. Do not introduce cross-game persistent commitments. Track raw shortage, conversion shortage, bank shortage, selected family and discarded alternatives in an external replay wrapper.

**Acceptance:** tests where a city becomes impossible, a settlement becomes directly buildable, a port changes integer conversion, and a bonus route becomes terminal. A new family should not induce a wasteful trade just because the scoring denominator changes. Compare retained-family parent versus bounded multi-goal variant on fresh matched500-game batches before claiming benefit.

### B01-02 — P2 hypothesis: replace blanket re-export rejection with proven cycle safety

`trade_allowed` scans current-turn history and forbids exporting any resource imported earlier in the turn; `improves_goal` also requires strictly reducing raw ingredient shortage. These are conservative restrictions, not a theorem that all rejected trade chains are bad. They can omit routes after a goal or port changes. Conversely, relaxing them naively can generate repetitive conversion and budget waste.

**Implementation experiment:** keep the current restriction as a control. Only permit a rejected chain when a bounded exact legal search proves a superior complete purchase or terminal result. Use resource/bank/ratio/phase/board state and the policy-relevant imported-resource history in any deduplication key. The current continuation key does not include the imported-resource set even though `trade_allowed` consults it; investigate an actual colliding path before claiming that omission has changed a game. Do not remove a safety rule solely because it looks restrictive.

**Acceptance:** no positive cycles; no reselling a reserved ingredient without a better complete goal; retained legality under bank depletion and changed port ownership; cap total expanded trade states. Show a reached beneficial case and a rejected bad cycle. Measure internal cutoffs separately from harness random fallbacks.

### B01-03 — P2 test gap: validate the entire forced discard sequence

The existing discard test verifies one choice. The policy reconstructs a new `EconomyContext` for every observation, so its 'retained' family need not persist across all cards discarded after one7. A sequence can switch families even if each one-card choice looks locally reasonable; no reproduced failing sequence is claimed yet.

**Action:** build several full engine discard phases, including out-of-turn discards, and execute until the quota is exhausted. Compare the final retained bundle against an exhaustive small-hand oracle for feasible immediate purchases/conversion gap. Record any family switches and whether they destroy a complete affordable goal. Correct quota handling, bank returns and observation immutability are mandatory; the objective tradeoff remains a policy choice. Use this evidence before adding persistent discard-state memory.

## B02 — city/dev investment

### B02-01 — P2 hypothesis: make commitment sensitive to resource supply and payback

`investment_window` requires own actualVP≤7 and combined wheat+ore rate≥0.09; a city with conversion gap≤2 can override the normal goal family. The root choice may prefer a city within5 heuristic points of the best alternative. These are hand-chosen rules. Combined wheat+ore can pass with one ingredient absent, and raw conversion gap does not say how quickly the missing resource arrives or whether city production is worth delaying expansion.

**Experiment:** evaluate the candidate city's incremental useful production, exact missing wheat/ore after reserving resources, owned port conversion, robber exposure and remaining VP horizon. Distinguish upgrading a weak site from a productive one, and city completion from replenishing for a second city. Keep a legal expansion escape when ore/wheat access is poor. Avoid simply increasing ore/wheat opening weights: assess correlated number/tile exposure and actual exchange routes.

**Acceptance:** ore absent but surplus/port available, ore absent without conversion, wheat blocked by robber, weak versus productive city site, limited city pieces, short remaining VP gap and contested valuable expansion. Preserve the earlier ore-denial escape test and both new terminal overrides. Ablate commitment separately from opening weights and dev bonuses. **CPU risk:** prefer cached production/feasibility arithmetic to increasing search depth.

### B02-02 — P2 hypothesis: value dev stock by ability to use it

`specs` stops adding a dev goal when non-VP stock reaches3; `buy_value` makes END_TURN preferable at that cap except a near-win VP lottery. Below the cap, Army investment uses current played/held Knights, an extra probability-weighted bonus and a 0.5 discount if a dev was played this turn. A stock of three useful Knights and a stock of stranded Road Building cards have different value. Bought cards are delayed; the opponent can move the Army target. No main causal ablation has established these constants.

**Implementation experiment:** estimate eligible play opportunities and route value by card type. Preserve the one-dev-per-turn/new-card rules and exact strict Army threshold. Consider whether spending one held utility card opens a better dev route; do not force a useless card play merely to lower the stock count. Keep the VP-draw chance explicit and a guaranteed own win first. A useful Knight at a delayed Army threshold is not worth immediate2 VP.

**Acceptance:** already-owned Army, exact incumbent tie, newly bought versus old Knight, one dev already played, no useful Road extension, empty/near-empty deck, own9 VP draw lottery and guaranteed alternative win. The existing finite-deck test is constructed and is not a calibrated belief model. Record stock-cap and investment decisions for reached losses before changing thresholds. Compare stock/type-aware and frozen parent policies on matched boards.

### B02-03 — P2 measurement: separate opening, city, dev and search effects

B02 differs from B01 in multiple choices; their 76.2% versus71.8% F results do not identify which component helped or hurt. Add explicit bounded controls for opening weights, forced city commitment and dev bonus while holding the common evaluator/search fixed. Record root coverage,52-node continuation cap, cutoff count and city commitment frequency. Evaluate one interpretable change at a time; avoid optimizing several constants on board911000–911249 and then calling those boards fresh confirmation. A direct B01/B02 main comparison is separate work, not inferred from the four-game review smoke.

## Build/test delivery

```bash
./team-work/run-python.sh -m unittest discover -s team-work/member-1/implementation -p 'test_economy.py' -v
./team-work/run-python.sh team-work/reviews/2026-10-17-B03-B08/verify_findings.py
```

These execute parent tests and reproduce frozen defects; add a new-version suite with desired behavior. Verify `build_agents.py` destination handling before using it: never overwrite the current v001 freeze. Assemble separate v002 standalone sources with component hashes and executable-AST checks; ZIP only the verified frozen `agent.py`, then independently extract/load it. Use the common contract's500-game runner for both candidates and same-board parent controls. Keep former bots and research untouched, preserve human review status, and report precise evidence rather than 'all tests pass' alone.
