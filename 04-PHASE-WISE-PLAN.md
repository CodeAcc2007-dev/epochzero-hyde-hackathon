# Phase-wise plan: research, multiple bots, fair comparison

Prepared: **17 October 2026 (IST)**. Current stage: **Phase 1 briefs assigned; research has not been carried out by this planning task.**

## 1. What this plan authorizes now

The user asked for a phased roadmap and detailed research/strategy instructions for four teammates. Phase 1 is now divided below. Its purpose is to obtain evidence and strategy proposals before choosing an implementation plan.

This task creates instructions and editable handoff documents only. It does not run dataset analysis, train models, create competition bots, play new games, publish a repository, upload a submission or use SSH. The earlier resource-collection stop point is complete; teammates may now perform the research and offline analysis specified in their Phase 1 briefs. Bot implementation and bot-building assignments belong to later phases.

The environment and downloaded datasets remain in their existing shared locations. No member receives a copied environment or organizer clone.

## 2. The phases and their completion gates

| Phase | Purpose | Work and outputs | Gate before advancing |
|---|---|---|---|
| **0 — completed groundwork** | Establish a reliable starting point | Pinned kit and engine, validated shared Python, four workspaces, source/dataset catalogue | Setup and provenance reports already exist; setup results are not competitive strength evidence |
| **1 — research and strategy development: current** | Find defensible insights and candidate strategies | Four member findings reports, source cards, dataset/rule audits, hypotheses, failure cases and proposed experiments | All four handoffs reviewed; assumptions and disagreements visible; shortlist remains provisional |
| **2 — synthesis and experiment design** | Turn the findings into an implementation plan | Agree on candidate bots, shared interfaces, research-derived features, development/validation/final seed policy, logging schema, CPU policy and four-person build/test assignments | Concrete bot specifications and comparison protocol accepted; each candidate has a baseline and a rejection criterion |
| **3 — implement several independent candidates** | Build alternatives with comparable evidence | Small versioned bots with manifests, unit-level semantic checks where useful, smoke games, profiling and a legal fallback | Every candidate loads and plays legally under the unchanged official harness; preserve an untouched F reference |
| **4 — test, compare and ablate** | Learn what improves results and what costs too much | Paired-seat tests versus F and peer bots; component ablations; held-out validation; CPU/fault/memory records | A candidate has repeatable evidence, reported uncertainty and acceptable operational behavior; random-only wins do not qualify |
| **5 — select and integrate** | Select the strongest dependable submission | Finalist comparison, optional evidence-supported combination, regression checks, untouched final evaluation | Choose a frozen artifact on strength, weak matchups and reliability; an integration must beat its own simpler parent to justify inclusion |
| **6 — package and hand off** | Deliver the frozen bot and explain it | Explicit-file-list ZIP, clean unpack/load check, size and dependency checks, concise report and submission ledger | Local artifact is reviewable and traceable; existing portal/SSH teammate handles remote actions in a separately authorized task |

Phases 3–5 may repeat on **development** data. Do not repeatedly revisit the final seed set or call it untouched after using it to select changes. A dataset audit can conclude that a corpus is unsuitable; that is a valid Phase 1 result, not a reason to fabricate matching data.

## 3. Phase 1 division among four teammates

Member numbers identify stable working folders: **1 — Aroosh; 2 — Avadooth; 3 — Pranesh; 4 — Anni**. These are **research ownership assignments**, not permanent implementation roles.

| Member | Research ownership | Main evidence | Required contribution to later planning | Reviewer |
|---|---|---|---|---|
| **1 — Aroosh** | Statistical evidence, resource economics and interpretation of the existing numerical study | Kaggle 50-game CSV, original metadata, Chabot article, Guhe–Lascarides | Reproducible statistical findings with limits; economy/production hypotheses; which claims survive basic leakage and dependence checks | Member 4 (Anni) |
| **2 — Avadooth** | Opening placement, spatial expansion, ports and production risk | Exact board/feature/value source, probabilistic report; Member 1 (Aroosh)'s evidence when available | Opening and expansion decision specifications; useful board features; tradeoffs and counterexamples | Member 1 (Aroosh) |
| **3 — Pranesh** | Tactical sequences, opponent threats and victory races | Exact legal-action/application/win source, observation/masking source, heuristic planning literature | Tactical priority proposals, threat/bonus rules and hand-worked legal cases; boundaries on hidden information | Member 2 (Avadooth) |
| **4 — Anni** | Search/learning feasibility, text-dataset audit and fair evaluation design | Two-player RL paper, search/imitation references, both HF corpora, exact harness/clock | Dataset suitability verdicts; feasible method options with unmeasured cost labelled; comparison and logging specification | Member 3 (Pranesh) |

Each teammate can start immediately. Member 2 (Avadooth) does not wait for Member 1 (Aroosh)'s final statistics; it marks any economic premise as provisional. Member 3 (Pranesh) owns tactical semantics; Member 4 (Anni) checks their implications for search and measurement. Review is a written check of claims, not permission to edit someone else's raw data or results.

Shared instructions: [Phase 1 common brief](team-work/PHASE-1-COMMON-BRIEF.md). Individual briefs:

1. [Member 1 (Aroosh): statistical evidence and economy](team-work/member-1/03-PHASE-1-RESEARCH-BRIEF.md)
2. [Member 2 (Avadooth): opening and expansion](team-work/member-2/03-PHASE-1-RESEARCH-BRIEF.md)
3. [Member 3 (Pranesh): tactics and threats](team-work/member-3/03-PHASE-1-RESEARCH-BRIEF.md)
4. [Member 4 (Anni): methods, datasets and evaluation](team-work/member-4/03-PHASE-1-RESEARCH-BRIEF.md)

## 4. How Phase 1 feeds multiple later bots

Keep competing explanations alive. A city/development-card economy, expansion/port economy, tactical sequence planner and compact learned evaluator are **candidate families to investigate**, not chosen bots or claims of strength. A candidate may combine research from several members.

At Phase 2, turn each shortlisted idea into a specification with:

- Candidate ID and hypothesis; precise observed inputs and legal outputs.
- Minimal standalone version and one meaningful baseline comparison.
- Features, decision order and any search/training dependency.
- Which rules, data and opponent assumptions it relies on.
- Expected failure situations; CPU/memory risks; deterministic fallback.
- Proposed ablation, development experiment and evidence needed to continue or reject it.

Prefer independently testable versions before combining ideas. For example, an opening-only change can be compared with the same later-game policy; a tactical layer can be compared with the same evaluator without that layer. A learned approach remains conditional on suitable data, a justified target and measured inference cost. Neither the four-player CSV nor a single 7-VP 1v1 example establishes that condition.

The four-person build/test division will be made in Phase 2 after the findings. Each later bot needs a named builder and an independent reviewer/tester. All four can contribute candidate bots; shared test-protocol ownership must not prevent a teammate from pursuing a justified alternative. Avoid having a bot's author be the sole interpreter of its comparison.

### User's tournament direction: repeat clashes, then retain eight finalists

The user subsequently specified a portfolio approach: build bots for the promising strategies, clash them, select candidates, improve/create variants, and repeat until **eight working local finalists** remain. This is the intended structure of Phases 3–5. It is a target for later work, not a claim that eight bots now exist or that any bot is optimal.

1. **Candidate round:** implement the research-supported families and justified variants. Register each bot before testing: immutable ID/version, parent, strategy hypothesis, configuration and builder. A parameter change is a variant; it is not automatically a distinct strategy.
2. **Eligibility round:** check loading, legal decisions, faults, clock behavior and packaging assumptions. A failing bot goes back for repair and a new version; keep its failed records. Never advance on win rate alone.
3. **Clash round:** compare eligible bots head-to-head and against the same F anchor, using paired seats and common documented seed groups. Preserve the full win matrix and operational counters. O remains unavailable locally.
4. **Selection round:** retain strong candidates and useful alternatives with evidence against different styles. Record why each bot survives, is dropped or needs more games. Distinguish uncertain ties and cyclic matchups from a clear winner; a bracket alone can hide those effects.
5. **Improvement round:** create evidence-motivated variants or new strategies to address weaknesses, then repeat eligibility and clashes on new development batches. Keep a frozen prior champion to detect regressions. Change one interpretable component for ablations.
6. **Finalist selection:** use a reserved selection batch under predeclared criteria to choose **eight local finalists**, if eight satisfy the quality gates. Do not pad the list with broken or unvalidated bots. F is an anchor/fallback reference; do not count it as a novel strategy.
7. **Freeze and confirm:** save all eight manifests, weights/configs and packaging records; run the planned final confirmation. Rank readiness and document weak matchups. If the confirmation is used to choose or revise candidates, disclose that use rather than calling it an untouched unbiased test.

The Phase 2 protocol must specify how many bots and games each round can afford, how many survive, how extra games resolve uncertainty, and when to stop. A full round robin scales as `B × (B − 1) / 2` pairings; eight bots have 28 pairings, before anchor matches. Use broad screening followed by larger finalist comparisons to keep the tournament within available time. Small screening samples do not support strong strength claims.

All plausible **research-supported** strategy families may enter; this is not a promise to exhaust every possible Catan strategy. Strong results, complementary matchups, clock reliability and available development time determine the portfolio. Do not add a voting ensemble or stochastic mixture merely because eight bots exist; that is a separate candidate requiring measurement and eligibility checks.

**Submission constraint:** eight local finalists do not mean eight scored uploads. The pinned rules permit **7 scored submissions and at most 10 total uploads**, including failures. Inspect the teammate's submission ledger in Phase 6 and use only remaining slots; do not assume the allowance is unused. The official event advances the team's best private-score submission, not an eight-bot roster. A documented organizer rule change would supersede this limit; none is assumed here.

## 5. Evaluation principles to specify before implementation

These are planning requirements, not results from new matches.

1. Use the unchanged pinned harness, 10 VP and the same observation contract for every candidate. F is public; **O is not locally available in the supplied examples**. Do not relabel another bot as O or infer the private strength score from F alone.
2. Use even game counts and the harness's paired boards/alternating seats. Its keyed dice setup is preserved; do not predict hidden rolls from seeds. Shared initial dice setup does not make divergent policies experience identical trajectories.
3. Separate development, model/parameter selection and final evaluation by board-seed groups. Record game order and whether cross-game opponent adaptation is enabled; one process spans multiple games.
4. Log per-game outcomes and operating counters as well as summaries. No-winner games count as losses. Record opponent/configuration, code/data hashes, seed group, seat, load time, decisions, own CPU, over-budget games, fallback moves, faults, timeouts and crashes. Supplemental diagnostics must not change the rules.
5. Treat the board/seat pair as a dependence unit in uncertainty analysis. Do not use a zero-width normal interval at 0% or 100% as proof of certainty. Member 4 (Anni) proposes the method; Member 1 (Aroosh) reviews its statistical assumptions.
6. Use small tests for legality and profiling, then larger comparisons for selection. The organizer recommends at least 400 games for training comparisons and 1,000 before submission; these are planning targets subject to actual resources, not evidence of guaranteed statistical power.
7. Compare across distinct opponent styles, report weak matchups and run component ablations. A team-internal worst-matchup result is a robustness proxy, not the official group-stage score.
8. Measure CPU under controlled local load, initially running matches sequentially. Keep a safety reserve and document hardware; local milliseconds do not certify scorer compliance. Target zero faults and exhausted-clock games, rather than treating the disqualification threshold as an acceptable error allowance.

Official strength is the mean win rate against F and O on private boards. Official group robustness uses the five weakest matchups among nine opponents. Sources: [pinned problem statement](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/PROBLEM_STATEMENT.md), [pinned evaluator](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/evaluate.py).

## 6. Time and scope management

The supplied event schedule lists 17 October 2026, submissions closing at **17:00 IST**, reports at **17:30 IST**. This document does not establish the current remaining time or any deadline extension. The portal teammate should use the operative schedule when budgeting the later phases; do not schedule more research past a confirmed upload cutoff.

For Phase 1, a suggested first pass is **60–90 minutes per member in parallel**, followed by a short team synthesis. This is a proposed timebox, not a researched duration estimate. If time is short, each member first produces: one verified source card, its highest-priority question, one candidate strategy, one failure case and one experiment proposal. Preserve the deeper work as explicit open items. Protect packaging/testing time before expanding the scope.

Each Phase 1 report should have a one-page decision summary followed by evidence appendices. Stop when its assigned questions are answered or bounded by a documented data limitation. More reading is useful only when it changes a candidate or resolves an important uncertainty.

## 7. Phase 1 handoff and decision record

Each member fills their existing `04-PHASE-1-FINDINGS.md`. Use the [research template](team-work/PHASE-1-RESEARCH-TEMPLATE.md) for source, result and hypothesis records. Put optional analysis code, figures and derived tables in that member's own `phase-1/` folder; keep raw downloads in the shared research directory unchanged.

At synthesis, fill the [team review and synthesis worksheet](team-work/PHASE-1-REVIEW-AND-SYNTHESIS.md). Phase 1 is complete when all four handoffs have a reviewer response and the worksheet identifies: supported findings, transfer limits, conflicting evidence, candidate alternatives, missing evidence, and the next planning decisions. Agreement is not required where evidence is insufficient.

Planning decisions made here:

| Decision | Reason | Deferred decision |
|---|---|---|
| Divide by evidence/economy, position, tactics, and methods/evaluation | Covers distinct parts of play while giving every member a strategy contribution | Later bot owners and exact implementation modules |
| Give the numerical CSV one main analysis owner | Prevents duplicate incompatible analyses and lost provenance | Whether any inferred relationship deserves a bot feature |
| Give both text corpora one audit owner | Their rule mismatch and unverified full contents need a consistent verdict | Training use, labels, conversion and model choice |
| Require counterexamples and competing hypotheses | Reduces premature commitment to one strategy | Which bot families survive the research |
| Keep the official environment shared and stable | Existing setup already passed validation | Any additional research-only reader dependency, coordinated before installation |
| Keep old reports as historical records | Preserves what was actually done at each stage | No historical result is rewritten as a new finding |

No gameplay analysis or candidate performance was produced by creating this plan.

## 8. Documentation handoff verification

The planning task checked 21 current Markdown files and 124 local links: no missing targets or unbalanced code fences. All four common-context files are identical; each member has an assignment, detailed brief and explicitly unstarted findings worksheet. The organizer checkout remains clean at its pinned revision, and all 12 originally downloaded resources/metadata files listed in the acquisition manifest still match their recorded SHA-256 checksums. No agent file, environment copy, training result or tournament run was created.

## Subsequent authorized handoff

On 17 October, the user requested completing research for Aroosh/Pranesh/Anni while excluding Avadooth, then assigning eight strategies to four human builders. See [current synthesis](team-work/PHASE-1-REVIEW-AND-SYNTHESIS.md) and [two-bots-per-member plan](07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md). Each member builds, self-tests and uploads; on receiving uploaded versions here, the assistant independently verifies/compares them and returns improvements; owners revise and repeat. Earlier deferred-ownership statements describe the original planning stage. Human reviews remain pending; no bots or new matches were produced by this research task.
