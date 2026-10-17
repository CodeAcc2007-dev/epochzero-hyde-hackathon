# Member 4 — Phase 1: search/learning, dataset suitability and tournament design

Status: **assigned research; not executed by this planning task**. Read [common context](01-COMMON-CONTEXT.md), the [shared brief](../PHASE-1-COMMON-BRIEF.md) and [your findings worksheet](04-PHASE-1-FINDINGS.md).

## Mission

Determine what the text datasets can support, compare plausible search/learning methods against our interface and CPU contract, and propose a fair repeated-tournament protocol. You contribute strategy candidates as well as evaluation design. You are not assigned to implement all testing infrastructure or train a model during Phase 1.

## Inputs and source targets

1. [Catalogue D2/D3 and agent-method table](../../03-RESEARCH-AND-DATASET-CATALOGUE.md); both shared Parquet files under `../../research/downloads/datasets/`.
2. [g8967 metadata](../../research/metadata/hf-g8967.json) and [preview](../../research/metadata/g8967-first-row.json); [VVantim metadata](../../research/metadata/hf-vvantim.json) and [preview](../../research/metadata/VVantim-first-row.json). Source revisions and hashes are already recorded.
3. [Gendre–Kaneko two-player RL paper](../../research/downloads/papers/gendre-kaneko-2020-cross-dimensional.pdf) and [Deep Catan](../../research/downloads/papers/driss-cazenave-deep-catan.pdf).
4. [Expert Iteration](https://arxiv.org/abs/1705.08439), [DAgger](https://proceedings.mlr.press/v15/ross11a.html), and [PIMC](https://ojs.aaai.org/index.php/AAAI/article/view/7562) as needed to distinguish methods. Cite what you actually read, not the presence of a link.
5. Exact [evaluator](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/evaluate.py), [harness](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/match.py), [observation](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/obs.py), requirements and F adapter.

## Work package A — full dataset audit if a reader is available

First check existing reader availability without modifying the shared environment. A previous acquisition check validated Parquet markers and hosted schema/previews, **not full decoding**. If blocked, record what reader is missing and which conclusions remain unverified. Do not silently install/upgrade packages or repeat a preview-based count as a completed audit.

For each corpus, inspect and report:

- Actual row count/schema, null/duplicate patterns, whether rows are decisions or complete episodes and whether reliable episode IDs exist.
- Rule strings and player/VP/visibility variation across rows. Quantify verified patterns with denominators; distinguish explicit metadata from inferred prompt text and unparseable cases.
- Prompt/completion structure, action representation and whether legal-action choices/state are sufficient to reconstruct a valid target. Text action labels are not our legal-action index.
- Origin of labels/rewards and model/expert provenance where documented. A numeric reward or `meta_is_valid` field is not independent evidence of strategic quality.
- Duplicate states, continuation/outcome leakage, related rows across episodes and a plausible group split if later training were considered. If episode identity is absent, state the resulting limitation.
- License/terms and whether an intended training/redistribution use is established. Missing license information stays unresolved; do not upload raw text or train by assumption.

Conclude separately for each possible use: exploratory examples, representation/feature ideas, supervised training, tactical tests, and exact-rules evaluation. A useful verdict may be **not suitable for training**, with reasons. Do not convert labels, train a policy, generate exact-rules replacement data or assert whole-corpus uniformity without completing the audit.

## Work package B — compare methods under the actual clock

Create a feasibility table for at least these families, grouping related variants if useful:

| Family | Questions to answer |
|---|---|
| Fast heuristic / greedy successor evaluation | Which missing visible features or wasted computations might matter? How is actual weight use verified given the factory bug? |
| Bounded same-turn search / beam shortlist | Which Member 3 sequences become expressible? What causes branching explosions in trades, roads, discards or development actions? |
| Sampled-world / opponent-aware planning | When can hidden-card uncertainty change action ranking? Why might extra samples add no value to a visible-only evaluator? |
| Compact learned value/action ranking / imitation | What exact target, compatible data and legality mask would be required? What information is absent from the default 614-vector? |
| Larger self-play RL / MCTS / Expert Iteration | What data-generation, training and inference requirements exist? Which must be deferred given available evidence and clock constraints? |

Distinguish offline training cost from per-game inference cost. The two-player paper's reported compute is not an estimate for our laptop. The organizer's supplied generic search bots exhausted their clock; that is evidence about those implementations, not proof that every bounded search is impossible.

For each option, document inputs, hidden/chance treatment, legal-action mapping, engine copies/feature evaluations, game-state caching/invalidation, CPU reserve/fallback concept and expected failure modes. Cost models may use operation counts and explicit assumptions. All milliseconds and memory estimates remain **unmeasured** until later profiling; no new bot benchmark in Phase 1.

## Work package C — repeated clash protocol and eight finalists

Write a protocol specification for the user's later cycle: **many candidates → eligibility → clashes → selection → new/improved variants → repeat → eight validated local finalists**.

Specify:

1. Bot/version/parent registry, frozen artifacts and how author/reviewer/test roles are recorded. Distinguish new strategy families from weight variants.
2. A broad small-sample screening stage, larger comparison stage and finalist selection/confirmation stages. Propose sizes and resource estimates as planning assumptions, not power guarantees or measured throughput.
3. Head-to-head matrix plus F anchor, paired boards/seats and game order. Preserve no-winner losses and all faults. O is unavailable locally; no substitute is O.
4. Development/selection/confirmation separation, no row/seed leakage, fresh development batches across repeated rounds, and explicit handling of adaptive agents/process history.
5. Pair-aware uncertainty and uncertain ties. Ask Member 1 to review statistical assumptions. The CLI's normal interval can be misleading at extremes; a bracket and a single mean win rate can hide cyclic matchups.
6. A selection rule balancing anchor strength, head-to-head results, weak matchups and operational reliability. Do not retain a broken candidate merely to reach eight or assume diversity alone makes a candidate strong.
7. Eligibility/rejection criteria for CPU exhaustion, errors, timeouts, crashes, load time, memory and prohibited dependencies. Measure initially without concurrent matches on this laptop; scorer timing is the reference.
8. Per-game logging schema with code/config/data hashes, opponents, seeds/pairs, seat, outcome, turns, CPU, decisions and fault counters. Explain which fields the harness already returns and which require a later wrapper.
9. Tournament cost: pairings scale quadratically; budget all requested rounds and anchor games, plus profiling/packaging time. Avoid spending the entire event on a full round robin of weak variants.
10. Submission ledger: eight local finalists versus **7 scored / 10 total upload** maximum, remaining slots unknown until checked. Official selection uses the team's best private score; we do not submit an eight-bot team roster under the current statement.

Do not implement the runner or create bots during this phase. The deliverable is detailed enough to assign implementation/testing work in Phase 2.

## Required handoff and review

Fill [04-PHASE-1-FINDINGS.md](04-PHASE-1-FINDINGS.md) with dataset verdicts, method/source cards, up to three strategy hypothesis cards, cost assumptions, two failure counterexamples, and the tournament/logging specification. Give a serious alternative to your preferred method, including a simple non-learning fallback if data is unsuitable.

Review Member 1's data leakage/group-dependence reasoning. Member 3 reviews your tactics/hidden-card assumptions. Ask Members 1 and 2 which economy/position features require expensive recomputation; do not block their research while reader availability is unresolved.

## Acceptance and stop

Done means the team knows what the corpora do and do not support, which method prerequisites remain missing, and how later bot rounds could be compared fairly. A paper win rate is never labelled our result, an estimate is never labelled a profile, and an unparsed dataset is never labelled audited. Stop before training, bot/runner implementation, new match rounds or upload actions.
