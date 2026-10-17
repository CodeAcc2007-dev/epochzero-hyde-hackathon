# Member 1 (Aroosh) — Phase 1: statistical evidence and resource economics

Status: **assigned research; not executed by this planning task**. Read [common context](01-COMMON-CONTEXT.md), the [shared Phase 1 brief](../PHASE-1-COMMON-BRIEF.md) and [your findings worksheet](04-PHASE-1-FINDINGS.md).

## Mission

Inspect the existing numerical study and its underlying data, identify what can actually be supported, and translate defensible patterns into economy hypotheses for our two-player, no-peer-trade game. You own the team's primary Kaggle analysis so that everyone uses one documented interpretation of the columns and sample.

Your output is research evidence and candidate decision concepts. Do not implement or train a bot. Do not claim that a four-player association proves the strongest two-player strategy.

## Inputs and reading order

1. [Dataset catalogue: D1, S1–S3](../../03-RESEARCH-AND-DATASET-CATALOGUE.md).
2. [Original Kaggle description](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games) and [saved publisher metadata](../../research/metadata/kaggle-lumins.json).
3. [Shared CSV](../../research/downloads/datasets/catanstats.csv) and [original ZIP](../../research/downloads/datasets/lumins-catan-games.zip). Record the input hash from the catalogue.
4. [Chabot's numerical article](https://duddhawork.com/blog/catan-analytics-how-to-win-with-data-driven-strategies/). Locate the exact calculations and denominators before reproducing them.
5. [Guhe–Lascarides paper](../../research/downloads/papers/guhe-lascarides-2014-strategies.pdf), particularly estimated build/win time and the experimental setting.
6. Exact engine resource-cost/production source and F's value function, accessed through the shared installation. Relevant upstream [state functions](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/state_functions.py) and [value function](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/players/value.py).

The statistical article and dataset contributor are distinct sources. Keep the contributor's reported 40/50 regression result separate from the article's associations and your own reproductions.

## Work package A — audit before interpreting

Write a data dictionary using column position and original header together. Preserve blank/duplicate headers in a mapping table; do not silently let a reader rename them and then infer meaning. Explain settlement resource encoding from publisher documentation. If unclear, label it unresolved.

Verify game/player IDs, rows per game, missing values, duplicates, point/winner interpretation and whether seating order is documented. Record exclusions and how they affect the denominator. Distinguish 50 independent game groups from 200 dependent player records. Audit the `me` field for player-identity confounding; do not assume it is a neutral feature.

Make a decision-time availability table. Initial settlement fields may support opening descriptors; end-of-game production/trading totals cannot be available to an opening agent. Dice totals contain realized future luck. Document which proposed input would leak future outcomes.

## Work package B — reproduce the actual numerical claims

Prioritize a small reproducible set:

- Placement-order win shares and game-length summaries reported by the article. Confirm the definition of a roll/game length rather than assuming any sum of columns has that meaning.
- Initial production-pip and resource-diversity descriptors only where the encoding is verified. Keep expected initial production separate from realized total collection.
- Associations involving wheat access, city/development-card economy, roads and resource totals **only if the CSV actually contains sufficient fields**. Do not invent build-order or purchase-count variables from an aggregate that cannot identify them.
- The contributor's regression claim: identify its target, input timing, fitting/evaluation method and whether source code/specification permits reproduction. If the model specification is absent, mark the result unreplicated; do not fit an arbitrary substitute and label it the original model.

For each result, state the sample/unit, calculation, uncertainty or sampling limitation, confounders and what transfer to 1v1 would require. If you fit an exploratory model, use game-grouped resampling/splits, keep post-game predictors out of decision-time models and label model selection optimism. With only 50 games, descriptive findings may be the most honest output. Do not spend the entire phase searching model combinations for a flattering number.

## Work package C — economics questions for strategy design

Address these questions with sources, derivations or explicit hypotheses:

1. When does balanced access to build ingredients matter more than total expected production? Contrast a bottlenecked hand with abundant but poorly convertible production.
2. How do bank/port conversion rates change the value of surplus production when peer trades are absent? Distinguish an available port from the cost/time of reaching it.
3. What assumptions are needed to turn expected production per roll into estimated time to afford a settlement, city or development card? Resource dependence, bank supply, robber blocking and discard risk may invalidate a simple inverse-rate estimate.
4. What evidence would distinguish a city/development-card route from expansion/port strategies, rather than assuming one is universally best?
5. How should resource value change near an immediate purchase, above the discard threshold, and near 10 actual VP? Separate opportunity cost from current card quantity.

Do not state a causal effect from post-game totals. Write down a competing explanation: winning players may collect more because they build earlier, rather than the observed total identifying the correct opening choice.

## Candidate outputs

Produce up to three hypothesis cards, for example: bottleneck-aware resource valuation; a city/development-card purchase plan; or port-adjusted surplus conversion. These are options to investigate, not predetermined conclusions. Each card needs observable inputs, a clear trigger/decision concept, a counterexample and a later F/peer-bot comparison.

Include at least two counterexamples: high total pips with a missing essential ingredient, and a seemingly valuable surplus/port combination whose access cost or discard exposure reverses the decision. Hand-worked arithmetic is allowed; no new bot matches in Phase 1.

## Required files and handoff

Fill [04-PHASE-1-FINDINGS.md](04-PHASE-1-FINDINGS.md) with:

- A one-page summary: supported findings, non-transferable claims, strongest economy hypothesis and uncertainty.
- Data dictionary/quality audit, decision-time availability table and reproducible result records.
- Optional `phase-1/` analysis scripts/notebooks, derived tables/figures and exact commands. Raw data stays shared and unchanged.
- Up to three hypothesis cards, two counterexamples and future experiment/ablation designs.
- Questions for Avadooth, Pranesh and Anni, and a response to Member 4 (Anni)'s review.

Give Member 2 (Avadooth) production/bottleneck assumptions and known statistical limits. Give Member 3 (Pranesh) purchase-cost/discard tradeoffs. Review Member 2 (Avadooth)'s economic reasoning. Ask Member 4 (Anni) to inspect leakage, group dependence and the proposed uncertainty method.

## Acceptance and stop

Done means the numerical source has been checked against actual available fields, reproductions are separated from new results, and the proposed strategies remain testable hypotheses. It is acceptable to conclude that a claim cannot be reproduced or that data is inadequate. Stop before bot code, parameter tuning through games, new self-play generation or declaring a strategy the winner.
