# Opponent threats, hidden VP and candidate tactical strategies

Evidence labels: **SOURCE** and **RISK** from [the semantic audit](01-SOURCE-AND-SEMANTIC-AUDIT.md); **DERIVATION** below; **HYPOTHESIS** for candidate strategies. No game outcomes, training or measured runtime are reported.

## Threat classification

An exact opposing resource hand is unusually valuable in this hackathon. It establishes current affordability, not the opponent's intended move or a certain future victory. Always attach the phase, legal location, remaining piece, bank and dev-timing conditions.

| Threat class | What is known | What remains conditional | Possible response to investigate |
|---|---|---|---|
| Visible purchase opportunity | Exact current cards, public board, public VP, known stock/pieces derivable from board | Future roll, legality at the future decision, player choice; hidden VP changes its terminal significance | Identify terminal thresholds; compare taking our win, stealing a key card or taking a contested location |
| Visible Army race | Played Knight totals and incumbent are public | Whether a held hidden Knight is eligible, whether it is played | Distinguish tying from overtaking; value an eligible own terminal Knight separately |
| Visible Road race | Board edges, incumbent, route values in sampled public state | Future legal expansion and the cut-path risk R1 | Compare cost to overtake, defend or abandon; no raw-road-count heuristic |
| Hidden VP / progress threat | Public VP, number of unplayed devs, our cards, played cards and deck composition | Actual opposing identities and their policy/selection history | Use feasible bounds and explicitly assumed probabilities; no sampled identity is truth |
| Monopoly exposure | Own concentration and visible opposing hand | Whether opponent holds an eligible Monopoly and chooses that resource | Price concentration and timing without assuming the hidden card exists |
| Robber exposure | Current blocked tile and exact victim resource distribution | Destination/steal choice and later rolls; random stolen card unless its type is determined | Separate production denial from removing a purchase ingredient; account for self-blocking |
| Long-horizon loss | Contested nodes, expansion corridors, sustainable production | Several later actions and random events | Hand to Avadooth's positional analysis; do not call a speculative land loss an immediate forced win |

If an opponent has 9 public VP and a legal, affordable city, the city supplies the tenth point under the stated future phase conditions. At 8 public VP, the same city wins only if one hidden VP is present (or another scoring change occurs). It is wrong to assign the same certainty to both cases.

## Hidden-card bounds from real ongoing play

Let `p` be opponent public VP, `k` their unplayed-dev count, and `V` the number of VP cards in the unseen pile. At an observation in the real continuing 10-VP game:

`0 ≤ H ≤ min(k, V, 9 − p)`

Here `H` is opposing hidden VP. The final bound follows from `Game.play` checking for a winner before requesting another action. In particular, at `p=9`, `H=0`. At `p=8`, at most one hidden VP is currently possible. This does not mean the opponent cannot draw another VP or gain public VP later.

The bound is for the **real nonterminal state**, not a guarantee the supplied masker preserves it. It applies when the target is 10 and the standard harness loop supplies the observation. Artificially constructed/terminal states and future hypothetical successors require separate treatment.

## Optional exchangeable-card model: assumptions visible

The original deck is 14 Knights, 5 VP, and 2 each of Road Building/YOP/Monopoly. Subtract our held cards and publicly played cards to obtain an unseen multiset of size `N`; it consists of the opposing `k` cards plus the undrawn deck. This uses public counts, not the real hidden deck order.

Under an **exchangeable allocation assumption**, before incorporating game-history constraints:

`P(H=h) = C(V,h) × C(N−V,k−h) / C(N,k)`

where impossible combinations have probability zero. Condition this distribution on `H ≤ 9−p` for an ongoing game and renormalize. This captures a necessary consistency constraint missing from the unconditional masker. It is **not** a complete Bayesian opponent model: retaining/playing cards, prior public VP histories, known purchase timing and policy choices can change the posterior. A Knight-type count alone also does not establish current eligibility.

### Toy numerical illustration, not empirical data

Assume a possible unseen pile with `N=10`, `V=2`, opponent `k=2`, and public VP `p=8`:

| H | Unconditioned probability | Compatible with real ongoing play? |
|---|---:|---|
| 0 | 28/45 | Yes |
| 1 | 16/45 | Yes |
| 2 | 1/45 | No: that opponent would already have 10 actual VP |

Unconditioned `P(H≥1)=17/45`; conditioned `P(H=1 | ongoing)=16/44=4/11`. These are exact combinatorial results under the toy assumptions, **not** dataset frequencies, tactical win probabilities or a calibrated forecast for an observed opponent. The arithmetic is checked in the accompanying verification script/output; no worlds or games were sampled.

## Steal and denial reasoning

S `player_deck_random_select` draws a random resource card, so for visible opposing counts `o_r`, `P(steal r)=o_r/sum(o)`. If all cards are ore, the steal's type is certain; if the desired ingredient is one of five mixed cards it is not selectable merely by choosing that victim.

Monopoly's immediate resource transfer is deterministic from exact opposing counts. Neither fact proves the resulting denial prevents all wins: the opponent may have alternative purchases, ports, a later productive roll or hidden cards. A known immediate own win outranks resource-denial speculation in the proposed specification, while nonterminal alternatives need comparison.

## Three candidate strategies for later implementation planning

These are **research recommendations to test**, not bots or proven improvements. Use the same economic/position evaluator as the control when testing a tactical layer; otherwise the contribution cannot be isolated.

### M3-H1 — own terminal awareness and prompt correctness

- **Evidence:** S01–S07 and cases A/B; F lacks an explicit actual-VP/terminal objective.
- **Proposal:** explicitly distinguish our exact actual VP and legal phase, detect known terminal actions/short deterministic completions, and avoid treating sampled opposing VP as observed truth.
- **Inputs:** own actual/public VP, legal actions, known eligible devs, bank/pieces and public board; exact flags from an authorized consistent view where needed.
- **Alternative/control:** unchanged evaluator without the explicit layer. F already recognizes many wins through public-point reward, so this may be redundant in common positions.
- **Failure/cost risk:** sampled terminal artifacts; declaring a random draw guaranteed; spending excessive copy/evaluation CPU on an already obvious legal action.
- **Future test:** exact-engine fixtures for Case A, Case B, new VP purchase, new-versus-old Knight, and pre-roll restrictions; then paired held-out F/peer comparisons with and without the layer. No fixture or game was run here.
- **Reject/revise if:** it produces illegal phase assumptions, changes no relevant decisions, cannot justify its CPU cost, or fails to improve selected diagnostics without harming match outcomes. No strength claim before that evidence.

### M3-H2 — bounded purchase-completion planning

- **Evidence:** S06/S10–S13 and cases A/C; one action is not one complete purchase plan.
- **Proposal:** compare immediate economic choices with a small set of complete same-turn trade/build/progress chains; preserve a legal fallback and re-evaluate after observations change.
- **Inputs:** exact own hand, bank, ports, legal builds/edges, pieces and dev eligibility. Road geometry from Avadooth remains necessary.
- **Alternative/control:** direct one-action evaluator with identical features; an opening-only/positional alternative from Member 2.
- **Failure/cost risk:** trade branching, paid/free-road restrictions, pre-roll interruptions, blind commitment after a random steal and duplicated successors.
- **Future test:** isolate trade completion, paid-road completion and progress-card completion in separate ablations. Anni chooses a measurable search/clock policy later; the chain lengths in this report are not chosen depths. Benchmark on the unchanged harness, track clock exhaustion and faults as well as wins.
- **Reject/revise if:** promising enabling chains cannot be distinguished cheaply, the layer mostly duplicates F, or local gains disappear under equal-clock held-out comparisons/weak matchups.

### M3-H3 — observed-threat and contested-bonus awareness

- **Evidence:** exact opposing resource visibility; strict Army/normal-Road ties; four-point relative transfer swing; hidden-card and cut-path risks.
- **Proposal:** classify available opposing winning continuations, conditional hidden threats and longer-term races separately. Compare affordable own progress with targeted denial; cap spending on a bonus race that no longer pays back.
- **Inputs:** opposing resources/public VP/dev count, public played cards, incumbent bonuses and geometry, own eligible actions and feasible hidden-card bounds.
- **Alternative/control:** own-win/completion policy without opponent lookahead; simple economic progress rather than universal blocking.
- **Failure/cost risk:** defensive overreaction, inaccurate hidden-card calibration, treating a tie as transfer, relying on R1 cut behavior or attributing certain wins to future rolls.
- **Future test:** visible city threats, old/new Knights, Army ties/takeovers, Road ties/cuts, self-blocking robber destinations and concentrated hands. Compare against varied later candidate bots; report weak matchups and CPU/fault effects.
- **Reject/revise if:** it sacrifices own wins, spends more on defense than a justified threat warrants, relies on impossible sampled worlds, or fails compared with the simpler parent in reserved comparisons.

## Experiment handoff; not execution

For all three candidates, Phase 2 must decide exact fixtures, builder/reviewer ownership, data/split policy, seed groups, game counts and acceptance criteria. Use even game counts, paired seats, unchanged kit/clock, and distinct development/selection/final evidence. Keep per-game CPU, exhaustion, faults and no-winner losses visible. F is available; O is not supplied locally.

The multiple-bot tournament may combine or isolate these ideas after review. No beam width, coefficient, probability cutoff, expected win rate or winning bot was selected. Do not build all three merely because they have IDs; test whether each adds distinct value.

## Dataset fit and handoffs

The collected Kaggle resource is four-player aggregate summaries, not tactical state/action histories. The inspected g8967 example is 7-VP 1v1 with different visibility; the VVantim preview is four-player. Their full corpora/labels were not audited by this task. Therefore **no exact-rules tactical dataset was verified**; no new one was manufactured. See [the catalogue](../../../03-RESEARCH-AND-DATASET-CATALOGUE.md) for source URLs, pins and licenses. Member 4 owns deeper corpus suitability.

For later tactical fixtures/trajectories, record kit/engine revisions; complete public board/topology and bonus owners/lengths; bank and both resource hands; own held/eligible devs and actual/public VP; opposing public VP/dev count/played cards; turn owner, acting player, prompt and subphase; remaining building pieces; the exact ordered legal-action list; tested continuation and expected score/prompt transitions. Chance cases need an explicitly identified outcome or an outcome distribution, not a lucky unlabelled draw. Store any offline ground-truth hidden state separately from observable agent inputs and labels to prevent leakage. These are proposed recording requirements; no fixtures or trajectories were generated here.

- **Aroosh:** check purchase-goal resource retention and the cost of denial versus economic progress. No new regression or Kaggle analysis was done by Member 3.
- **Avadooth:** review legal spatial assumptions, route continuity and R1's interruption/tie cases. This cross-review is pending; nothing was messaged to teammates automatically.
- **Anni:** consider terminal-conditioned hidden worlds, short chain categories, forced subphases and the need to treat actual own wins independently of fictional sampled opponents. Profile candidate costs later; no clock-fit claim exists now.
- **Pranesh:** review Anni's later search/hidden-information proposals against these semantics, then bring disagreements to synthesis. No other member's findings file was edited.
