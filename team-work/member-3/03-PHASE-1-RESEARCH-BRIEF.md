# Member 3 — Phase 1: tactical sequences, opponent threats and VP races

Status: **assigned research; not executed by this planning task**. Read [common context](01-COMMON-CONTEXT.md), the [shared brief](../PHASE-1-COMMON-BRIEF.md) and [your findings worksheet](04-PHASE-1-FINDINGS.md).

## Mission

Find tactical decisions that a one-action evaluator can miss and specify how a later bot could recognize them using legal visible information. Own the exact rules for immediate wins, development cards, robber/discards and contested bonuses. Separate deterministic threats from uncertainty about hidden cards.

The output is a tactical research dossier and proposed decision policies, not an implemented searcher. Do not make new game runs or read hypothetical sampled cards as actual hidden truth.

## Inputs and source targets

1. [Pinned observation/masking code](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/obs.py) and [F adapter](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/examples/f_agent.py).
2. Exact engine [action execution](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/apply_action.py), [state functions](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/state_functions.py), [game/win logic](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/game.py), and legal-action generation in the shared installation.
3. [Guhe–Lascarides strategy paper](../../research/downloads/papers/guhe-lascarides-2014-strategies.pdf): explicit build plans and estimated win-time choices.
4. [Deep Catan paper](../../research/downloads/papers/driss-cazenave-deep-catan.pdf): imperfect-information planning concepts; do not transfer its four-player performance claims.
5. [Catalogue](../../03-RESEARCH-AND-DATASET-CATALOGUE.md) and Member 1/2 findings as they become available.

## Work package A — semantic audit table

For each topic, record exact file/function/revision, observable inputs, legal constraints, hidden/stochastic parts and a counterexample to a naive policy:

- Immediate engine-recognized wins; own actual versus public VP; a city upgrade adds one VP; hidden victory cards.
- Development-card purchase/play timing, whether a card acquired this turn can be played, action subphases and the per-turn play restriction.
- Largest Army thresholds/ties and played versus held Knights.
- Longest Road thresholds, ties, branches, loops and opponent-settlement interruption. Use engine semantics; do not replace them with total owned edge count.
- Robber placement/blocking, eligible victim/steal, Knight use and whether a move harms our own production.
- Discard threshold/count/order, preserving a concrete purchase and the opportunity cost of discarding each resource.
- Monopoly and Year of Plenty under bank/hand constraints; Road Building with its legal follow-up actions.

If the semantics require more than one source function, trace the relevant call path. Document uncertainty instead of assuming tabletop convention.

## Work package B — same-turn sequences

Identify short sequences whose first action may have weak immediate heuristic value but enables a stronger continuation, for example:

- Bank/port trade → city/settlement/development purchase.
- Road → newly legal settlement.
- Year of Plenty / Monopoly → a purchase or terminal win.
- Road Building → a route/settlement opportunity or Longest Road swing.
- Knight → robber relief / Largest Army change / purchase protection.

Check timing and legal-action generation for every example. A development draw or stolen resource is stochastic; do not treat one favorable outcome as guaranteed. Identify where the sequence must end, whether the opponent can intervene and what information changes along it.

Give a plain-language sequence-priority specification with exceptions, not a universal hard-coded order. Compare immediate-win priority, resource preservation and threat prevention when they disagree. Pass Member 4 the smallest depth/action categories that might distinguish these sequences; do not choose a search width or claim it fits the CPU budget.

## Work package C — opponent threats and hidden cards

Use exact opponent resources to identify **feasible visible purchases** while acknowledging legal placement, resource spending, dev timing and hidden VP uncertainty. Public VP alone does not establish the opponent's true distance to victory.

Propose a threat table that separates:

1. Visible, deterministic opportunities if the opponent gets a turn.
2. Conditional threats requiring a particular hidden card or future roll.
3. Long-horizon strategic risks such as lost land or a bonus race.

Study count-based hidden-development-card reasoning only from public deck composition, our known cards, played cards and opponent unplayed-card count. If you derive a probability, state the sampling assumptions and card-history limitations. Member 4 reviews how this relates to `sample_world`; neither of you may identify sampled hidden contents with the real state.

Compare plausible tactical policies: immediate-win awareness alone, short same-turn completion, and opponent-threat/bonus-race awareness. State when blocking is less valuable than advancing our own win. For adaptive cross-game behavior, describe lifecycle/overfitting risks as an optional later idea; do not implement adaptation now.

## Concrete cases required

Give at least two fully specified hand-worked tactical cases and one failure counterexample. Include resources, public/actual points where legitimately known, action order, required legality assumptions, and hidden/random elements. Cover a purchase-enabling sequence and a bonus/defense decision. These are illustrative cases, not observed match results or validated engine fixtures.

The aggregate Kaggle CSV cannot reveal exact tactical action order, and neither HF corpus is yet an exact-rules tactical benchmark. If there is no suitable tactical dataset, say so and specify what later exact-engine fixtures/trajectories would need to record. Do not manufacture a dataset during this phase.

## Required handoff and review

Fill [04-PHASE-1-FINDINGS.md](04-PHASE-1-FINDINGS.md) with source cards, semantic table, cases, up to three hypothesis cards and later experiment/ablation proposals. Specify an evaluator-only baseline versus the same evaluator plus the proposed tactical layer. Include win/loss tradeoffs, CPU/fault risks and an explicit rejection condition.

Member 2 reviews spatial/route/placement claims. Give Member 1 resource-value tradeoffs to check. You review Member 4's search/hidden-information proposals and whether its evaluation design would expose tactical failures.

## Acceptance and stop

Done means each tactical proposal has a source-backed legal trigger, visible inputs, uncertainty treatment and a failure case. Terminal-win and bonus semantics must be precise enough for later tests. Stop before bot implementation, simulation matches, training or claiming a measured advantage over F/O.
