# Methods under the hackathon clock

17 October 2026. **Research and proposed designs, not measured agent performance.** Primary-assistant review for Anni; teammate review pending.

## What the evidence supports

Use fast, interpretable alternatives first. Bounded planning is worth testing, but no new search fits the clock until profiled. Defer large RL and dataset imitation: neither has a compatible, verified training corpus today. A compact learned ranker remains a later option after exact-rules labels exist, not one of the eight initial deliverables.

| Source and passages actually reviewed | Relevant method | Transfer limit and implication |
|---|---|---|
| [Gendre–Kaneko](https://arxiv.org/abs/2008.07079), §§3–4, input/output tables and hardware/results, PDF pp. 3–11 | Self-play actor–critic with spatial/scalar inputs | Two-player/no-peer-trade reference; separate simulator, action abstraction and bank/discard differences. Reported long training on substantial hardware is not our runtime evidence. Useful representation ideas; no ready weights or exact-rules corpus accepted. |
| [Deep Catan](https://www.lamsade.dauphine.fr/~cazenave/papers/DeepCatanEvo.pdf), §§3–4, PDF pp. 4–9 | Value/local-action networks plus Expert Iteration and MCTS | Four-player setting; training and rollout budgets differ. Learning to replace rollouts is a method idea, not proof of a deployable bot here. |
| [Expert Iteration](https://arxiv.org/abs/1705.08439), abstract/method overview | Alternate search-generated targets and policy generalization | General Hex result; no Catan or clock guarantee. Requires an expert, generated targets and a repeated training loop. Full paper not newly reproduced. |
| [DAgger](https://proceedings.mlr.press/v15/ross11a.html), publisher abstract | Query expert on learner-visited states | Addresses distribution shift; copying static text examples is not DAgger. Needs a compatible expert and repeated rollout labels. |
| [Long et al.](https://ojs.aaai.org/index.php/AAAI/article/view/7562), publisher abstract | Analyze perfect-information sampling in imperfect-information search | More hidden worlds do not automatically fix strategy fusion or an incorrect belief model. Publisher-level review only; no theorem application claimed for our game. |
| [Guhe–Lascarides](https://www.pure.ed.ac.uk/ws/portalfiles/portal/19351482/CIG2014_GS.pdf), build-plan framework and development-card experiments, PDF pp. 3–6 | Estimated time to build/win; choose among settlement, city, dev and bonus plans | Four-player/trading setting. Supports comparing state-dependent plans, not copying fixed preferences. |
| [Gan et al.](https://eric-gan.github.io/files/catan.pdf), pp. 1–3 | Production-based hitting-time approximation and surplus conversion | Simplified tails/rounding, fixed port threshold and exposed-plan failure. Replan after opponent occupation; do not copy coordinate-distance or production thresholds. |

Downloaded PDFs and their hashes remain in the [catalogue](../../../03-RESEARCH-AND-DATASET-CATALOGUE.md). The primary also visually checked Guhe PDF p. 6 to verify its table/figure: penalizing excessive development-card plans improved that particular agent. This conflicts with a universal “always buy devs” reading and motivates separate candidates.

## Exact source contract

Organizer pin `04fffac90e00610f60e0b06d919f262f4b3ed9db`; engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. On this task, upstream HEAD `efaa27e7aef628994313bf4080deb4e191491d1e` was fetched for comparison only. The diff changes README paths/clone URLs; problem statement, requirements and `catan_kit` are identical. No checkout or dependency upgrade occurred.

Source anchors: [match clock/process](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/match.py#L23-L59), [decision handling](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/match.py#L276-L334), [summary](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/evaluate.py#L22-L45), [masking](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/obs.py), [F](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/examples/f_agent.py).

The budget is cumulative `min(0.300 + 0.0125*k, 1.500)` seconds per game. Forced singleton actions bypass the agent and do not add increments. Reaching the ceiling at 96 calls is arithmetic, not 96 guaranteed decisions. At call 20 allowance is 0.550 s; at 56 it is 1.000 s. `cpu_left` is remaining allowance including this call; it is not a fresh per-call allocation. Current costs, including observation handling, must fit. Initial loading has a separate limit, and a process can span many games. A persistent bot-owned RNG/cache is not automatically cleared by reseeding global `random`.

## Feasibility comparison

All costs below are **unmeasured**; operation counts guide future profiling only.

| Family | Concrete inputs and treatment | Work/caching | Failure/fallback and decision |
|---|---|---|---|
| One-step heuristic | Legal indices, own actual VP, hands, bank, production and geometry | Roughly A successor copies/evaluations; deduplicate visible production computation, cache static map topology | Cheap candidate baseline. Custom weights must reach `base_fn(weights)` or a verified equivalent: `get_value_fn('base_fn', weights)` discards supplied weights in this pin. Keep untouched F unchanged. |
| Same-turn beam | Current legal prompt, enabling trades/roads/YOP; stop at turn boundary or unresolved chance | A roots plus at most `(d−1)*b*k` selected expansions in a capped design; deduplicate equivalent states and prevent trade cycles | Width/depth are later profile choices. Forced free-road/discard subphases need exact handling; short search can miss distant enabling chains. Fall back to cached legal incumbent. |
| Hidden-world opponent lookahead | Public opposing resources/VP, dev count, known deck multiset and history constraints | Roughly M worlds × A shortlisted own moves × R replies; resample only when relevant, never reuse hidden identities as truth | Necessary nonterminal VP conditioning from Pranesh; old-card timing is still uncertain. Treat sampled replies as conditional threats. Stop before an unmodeled dice branch; fall back to visible threat/economy rule. |
| Chance-aware shallow search | Above plus outcome probabilities for dice, steals and card draws | A decision can branch into up to 11 dice totals and further robber/discard choices; enumerate only well-defined cheap subproblems | One stochastic `execute` is one sample, not an expectation. Comparing roots under unrelated lucky draws is noisy. Defer full chance expansion until after the simpler bots. |
| Compact learned ranking | Observable state/action features, exact legal mask, compatible targets and grouped splits | Feature extraction plus a small matrix/linear score; load once; invalidate dynamic caches by state | Training prerequisites absent. Default vector omits explicit production/reachability and exact opposing resource types. Full feature-vector audit/profiling remains pending; do not assume 614 raw inputs contain all of F's features. |
| Large self-play RL/MCTS/ExIt | Exact simulator, compatible observations, generated trajectories, frozen experts and training/eval split | Offline generation/training plus online inference/search | Defer. Paper success is not a data, time or compute budget. Organizer search failures concern supplied configurations, not every bounded search. |
| Adaptive macro-plan heuristic | Legal route costs, estimated resource deficits, production, remaining VP and contested bonuses | Evaluate a small set of VP routes; cache topology, invalidate after any board/hand/phase change | Strong simple alternative to sampling; approximate time-to-win can ignore variance, blocking and dev randomness. Replan every decision rather than persist with an impossible target. |

Cache keys must include all dynamic inputs used: perspective, board/buildings/roads, robber, hands, bank, phase/acting player, pieces, bonuses and relevant dev eligibility. State keys for sampled searches must not merge distinct hidden worlds accidentally. Across games, detect boundaries using documented observable phase/history or design no persistent dynamic cache; `obs.turn` alone is not a unique game ID. No cache implementation was made.

## Candidate cards and falsifiers

- **M4-H1 / B07: small sampled-opponent planner.** Ask whether uncertainty-aware short replies improve visible-only choices. Use a small shortlist and interruptible work; stop at unexpanded chance. Counterexample: more worlds with F's visible-only evaluation change nothing but CPU cost. Reject if invalid sampled terminal states, hidden eligibility guesses or exhausted clocks drive choices, or the simpler threat bot is as strong on reserved comparisons.
- **M4-H2 / B08: adaptive VP-route planner.** Recompute whether the next viable route is city, expansion, dev/Army or Road; compare estimated completion costs and production gains instead of one fixed preference. Counterexample: a low mean completion estimate hides a large probability of never drawing the needed ore soon enough. Reject if plan thrashing, speculative bonus points or overvalued random VP draws erase gains against the balanced economy control.
- **M4-H3 / deferred: compact distillation.** Only after a stronger, stable exact-rules expert and grouped labels exist. Counterexample: excellent random-row validation accuracy can memorize related game states. No current corpus accepted, no trainer or learned bot assigned now.

Reviewer checks by the primary assistant: hidden-card assumptions cross-checked with [Pranesh's source audit](../../member-3/phase-1/01-SOURCE-AND-SEMANTIC-AUDIT.md); CPU accounting checked directly against harness code; dataset prerequisites checked against the full [corpus audit](01-DATASET-AUDIT.md). These are assistant checks, not statements that Anni or Pranesh supplied human approval.
