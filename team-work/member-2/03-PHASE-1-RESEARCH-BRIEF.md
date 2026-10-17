# Member 2 (Avadooth) — Phase 1: opening placement, expansion and ports

Status: **assigned research; not executed by this planning task**. Read [common context](01-COMMON-CONTEXT.md), the [shared brief](../PHASE-1-COMMON-BRIEF.md) and [your findings worksheet](04-PHASE-1-FINDINGS.md).

## Mission

Develop source-backed alternatives for opening placement and spatial growth. Explain which board features could distinguish good choices and when those features conflict. Our goal is an implementable decision specification later, not a list of generic four-player tips.

You own placement/expansion reasoning. Member 1 (Aroosh) owns Kaggle numerical results; request their audit instead of producing a second incompatible CSV analysis. You can work immediately with explicit provisional economy assumptions.

## Inputs and source targets

1. [Problem analysis](../../01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md) for exact rules and feature gaps; [dataset catalogue](../../03-RESEARCH-AND-DATASET-CATALOGUE.md) for transfer limits.
2. [Gan et al. probabilistic report](../../research/downloads/papers/gan-et-al-probabilistic-approach.pdf): production, ports and expected-time assumptions. Preserve the date discrepancy recorded in the catalogue.
3. [Gendre–Kaneko paper](../../research/downloads/papers/gendre-kaneko-2020-cross-dimensional.pdf): two-player spatial representation, without assuming its training recipe fits our clock.
4. [Pinned F/value source](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/players/value.py) and [feature source](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/features.py).
5. Board/map and legal placement/road functions in the shared installed engine. Record exact file/function/revision for conclusions. Do not infer a board coordinate or port attachment from a diagram alone.

## Work package A — exact opening semantics

Document the placement order, distance constraint, road-placement constraints and resources granted by the second settlement. Confirm actual engine behavior from source. Identify what the agent knows before each opening action and what its opponent can take before its next placement.

Explain why evaluating a single isolated node may miss the interaction between two starting settlements, initial resources and the first expansion direction. Check both seats. The legal-action list is authoritative; a later agent must return one of its indices, not invent a location.

List facts a board evaluator can compute from visible information. Distinguish fixed board data suitable for precomputation from ownership, robber or reachability values that change during play. Do not estimate speed from the fact that a feature sounds simple.

## Work package B — compare placement concepts

For each concept, specify inputs, units, what it rewards, what it omits and a failure example:

- Total expected production pips, with cities/robber status treated correctly when relevant.
- Resource-specific production and complementarity between starting settlements.
- Production concentration on the same number versus diversity of roll outcomes. Distinguish equal expected production from different variance/correlation; do not assume diversification always wins.
- Initial purchase readiness from the resources actually granted, rather than hypothetical full production.
- Future settlement options, distance in roads, contested access and paths the opponent can obstruct.
- Port type, resource surplus, accessibility and the investment required to benefit.
- Opponent denial: lost opportunity to the opponent versus forgone own development in a two-player race.

Use Member 1 (Aroosh)'s economic findings when available, but label four-player statistical associations separately from mathematical production definitions. The Kaggle summaries do not encode a complete board graph or full placement choice set; they cannot directly identify optimal road paths or placement regret.

## Work package C — expansion specifications

Describe at least two plausible expansion policies and their disagreements. Examples to examine include production-first growth, bottleneck/port access, and contested-land denial. They are research candidates, not selected implementations.

For each, explain:

1. How a desirable future settlement is identified and whether it is actually reachable/legal.
2. How road investment, required cards and delay compare with a city/development-card alternative.
3. How you prevent assigning value to impossible or already-blocked paths.
4. How the value changes after an opponent settlement, robber move or depleted expansion space.
5. Which features are available directly versus requiring graph traversal or repeated successor copies.

Keep Longest Road as a contested bonus, not a count of purchased roads. Member 3 (Pranesh) owns exact route/bonus tactics; pass them spatial assumptions rather than duplicating the semantic audit.

## Concrete examples required

Create at least two **hand-worked** contrasting choices using clearly stated hypothetical board/hand assumptions:

- Equal headline pips, different ingredient bottlenecks, roll concentration or initial resources.
- A higher-production interior expansion versus an accessible port/contested expansion after accounting for road cost.

They are illustrative derivations, not empirical game samples or generated exact engine fixtures. State any assumption you have not verified and what a later engine-level fixture would need to establish. Include at least one case where your preferred scoring concept picks the worse-looking alternative under a competing objective.

## Candidate and experiment handoff

Produce up to three hypothesis cards. Each should describe an opening-only or expansion-only change that can later be isolated while keeping the rest of the policy fixed. Specify a baseline, feature ablation, both-seat comparison, outcome metrics and a rejection condition. Include a contrasting candidate so the team can build multiple position strategies rather than immediately combining all features.

Fill [04-PHASE-1-FINDINGS.md](04-PHASE-1-FINDINGS.md) with the semantic reference table, feature specifications, examples, source cards and proposed variants. Optional diagrams/calculation scripts belong under your `phase-1/` folder; do not create a board simulator or bot in Phase 1.

Member 1 (Aroosh) reviews your economic/statistical assumptions. You review Member 3 (Pranesh)'s spatial/bonus claims. Give Member 4 (Anni) the feature-cost dependencies and candidate action-ranking concepts for its search/CPU feasibility review.

## Acceptance and stop

Done means we could later write a bot specification from your feature definitions without guessing their inputs, and we understand when each placement strategy should fail. Leave exact feature weights, beam sizes, bot ownership and claimed win rates undecided. Stop before implementation, new matches or optimization.
