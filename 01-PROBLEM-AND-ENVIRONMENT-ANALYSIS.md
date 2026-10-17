# Catan Hyde hackathon: problem and environment analysis

Reviewed: **17 October 2026, IST**. Status: **Task 1 complete: source review and written analysis.**

## 1. Scope and current status

This document is the shared starting context for our team. It records requirements, source-backed findings, proposed decisions and their reasons, uncertainties, and the order of later work.

The user's instruction to do one task and stop is interpreted as: first read the supplied problem repository and PDF, inspect the environment's relevant source, and write this analysis. Local installation is a later task. No SSH connection, remote-machine configuration, package installation, agent implementation, training, evaluation, submission, or new GitHub repository was performed. Research into external Catan strategy and papers, and division of work between four people, are also deferred.

Repository and PDF instructions are reference material, not commands to execute automatically. In particular, their SSH, account, upload, and coding-assistant setup instructions do not override the user's scope.

**Evidence labels used below:**

- **Verified source:** read in the supplied documents or exact pinned source; not necessarily run locally.
- **Local observation:** measured through read-only inspection of this computer.
- **Proposal / hypothesis:** a candidate to test, not a demonstrated improvement.
- **Open:** requires later inspection, execution, research, or organizer clarification.

## 2. Sources and reproducibility

The supplied repository was downloaded over HTTPS into a temporary review directory. The workspace itself was initially empty and has not been initialized as a Git repository.

| Source | Version / location | Use |
|---|---|---|
| Organizer starter kit | [lyric-hyde/catan-hackathon-agent](https://github.com/lyric-hyde/catan-hackathon-agent), commit `04fffac90e00610f60e0b06d919f262f4b3ed9db` | Event rules, API, runtime, evaluation, examples |
| Attached introduction | [Hyde@IITB.pdf](/home/CodeAcc2007/Downloads/Hyde@IITB.pdf), 11 pages | Introductory game explanation; all pages visually inspected |
| Pinned game engine | [bcollazo/catanatron](https://github.com/bcollazo/catanatron/tree/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816), commit `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816` | Actual F heuristic, features, costs, scoring and game semantics |

PDF SHA-256: `3b2439be69e715b36e22f05336c0be97cea58a60a9900336c5ebad93a973b7a4`.

Source abbreviations throughout this document:

- [S1: Problem statement](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/PROBLEM_STATEMENT.md)
- [S2: README / setup](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/README.md)
- [S3: requirements](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/requirements.txt)
- [S4: observation and sampling](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/obs.py)
- [S5: match harness](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/match.py)
- [S6: evaluator](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/evaluate.py)
- [S7: F adapter](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/examples/f_agent.py)
- [E1: F value function](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/players/value.py)
- [E2: feature extraction](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/features.py)
- [E3: state functions](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/state_functions.py)
- [E4: action execution](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/apply_action.py)
- [E5: game loop and win condition](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/game.py)

The README's installation example names `pbhar-hyde/catan-agent-hackathon`, a different repository from the URL supplied by the user. This review uses the user's `lyric-hyde` repository. Do not silently switch repositories during setup. Record any later source revision and rerun compatibility checks.

## 3. What we must build

**Verified source — S1:** a Python agent that wins two-player Catan games under a very small CPU budget. It competes against the public baseline **F**, an organizer-trained bot **O**, and other teams' agents.

The deliverable is an agent folder packaged into a ZIP, with `agent.py` at the ZIP root and its required helper/data files alongside it. Maximum ZIP size: **100 MB**. It is not a website, game UI, custom game engine, or online LLM application.

The engine is authoritative when its rules differ from the general Catan rulebook. Use the exact engine commit in S3, including the starter kit's patches. Do not substitute a PyPI release or newer upstream version.

## 4. Game model we are solving

### Rules and resource economy

**Verified source — S1, PDF pages 3–11, E3–E5:**

- Two players; first engine-recognized winner reaches 10 actual victory points.
- Official spiral number layout with randomized board seeds.
- Player-to-player trading is disabled. Bank trades and ports remain available.
- Five resources: wood, brick, sheep, wheat, ore.
- Settlements receive one resource per producing adjacent tile; cities receive two. The robber blocks its occupied tile.
- On a seven, a player above seven resource cards discards half, rounded down. The engine requests discards one resource at a time.
- Development cards include Knight, Road Building, Year of Plenty, Monopoly, and Victory Point.

| Purchase | Resource cost | Points / purpose |
|---|---|---|
| Road | 1 wood + 1 brick | No direct VP; expansion and Longest Road |
| Settlement | 1 wood + 1 brick + 1 sheep + 1 wheat | 1 VP plus production |
| City upgrade | 3 ore + 2 wheat | City is worth 2 VP total; upgrade adds **1** VP |
| Development card | 1 sheep + 1 wheat + 1 ore | Hidden point or tactical ability |

The PDF's “+2 VP” city label must not be implemented as a two-point increase on upgrading an existing settlement. `build_city` explicitly adds one point to public and actual totals. The PDF also omits Monopoly from its introductory card slide; S4 includes two Monopoly cards in the full deck.

Largest Army is worth two points, first requires three **played** Knights, and changes owner only when a challenger exceeds the holder's army. Longest Road is worth two points with a minimum qualifying length of five; branching, ties, and interruption must be handled through engine rules, not by simply counting owned roads. Exact route edge cases remain a later verification item.

The engine's `winning_color()` checks actual points across players; do not assume every tabletop timing detail applies. Use simulated engine terminal states for tactical win checks.

### What is known and unknown

**Verified source — S1, S4:**

| Information | Available? | Consequence |
|---|---|---|
| Board, roads, settlements, cities, ports, robber | Yes | Compute production, expansion and blocking features |
| Own resources and development-card identities | Yes | Evaluate concrete purchases and known tactics |
| Own public and actual points | Yes | Detect our true distance to victory |
| Opponent resource counts by type | Yes | Assess immediate purchases and Monopoly opportunities |
| Bank resource counts | Yes | Respect supply and trade feasibility |
| Opponent public points | Yes | Visible score only |
| Opponent number of unplayed development cards | Yes | Estimate hidden-point and tactical uncertainty |
| Opponent unplayed card identities / actual hidden points | No | Must not treat sampled identities as facts |
| Development-deck order and future random outcomes | No | Search must account for uncertainty |

The resource-hand identity is `opponent[r] = 19 - bank[r] - mine[r]`. There is no need to build a hidden-resource inference system for this variant.

The deck has 25 cards: 14 Knights, 5 Victory Points, and 2 each of Road Building, Year of Plenty and Monopoly. `obs.sample_world(rng)` produces a consistent hypothetical world, replacing hidden cards and deck order. The supplied history masks the opponent's development-card purchases. Sampled worlds are legitimate planning tools, not access to hidden truth.

### Initial strategic implications — hypotheses, not results

1. **Opening placement should balance production and usable resource combinations.** A high-output opening can still be slow if it cannot turn its resources into settlements, cities or trades. Consider the pair of placements and reachable expansion sites, not just each node separately.
2. **Bank and port efficiency matter more without player trading.** A port is valuable when our likely surplus matches it; its existence alone is insufficient.
3. **Wheat/ore and expansion are competing routes, not a fixed universal priority.** Cities and development cards use wheat/ore, while expansion requires wood/brick and settlement resources. Board layout should influence the choice.
4. **Robber placement is an economic decision.** Evaluate opponent production denied, our production blocked, immediate steal value, and the opponent's next likely purchase.
5. **Monopoly can use exact opponent resource counts.** Choose based on what the cards enable, rather than always maximizing the raw count taken.
6. **Points become more urgent near the finish.** A certain immediate win should outrank an attractive long-term production improvement. Bonus ownership and opponent hidden-point risk affect urgency.
7. **Avoid pointless roads and trades.** Each should enable a useful site, purchase, bonus, or win sequence.

For fair two-dice production, the counts out of 36 for totals 2 through 12 are `1,2,3,4,5,6,5,4,3,2,1`. A basic expected-production feature sums each unblocked adjacent tile's roll probability times its building multiplier. This is a mathematical starting feature, not a complete value function: it omits shortages, resource usefulness, variance, and future robber movement.

## 5. Agent contract and runtime constraints

**Verified source — S1, S4, S5 and `host.py`:**

```python
class Agent:
    def __init__(self):
        # Load and warm up required models/tables once per process.
        pass

    def decide(self, obs, playable_actions) -> int:
        # Return the chosen action's index in THIS supplied list.
        ...
```

This is an interface illustration, not implemented agent code. Never return an action object, stale index, float, or boolean. The host accepts integer-like indices but explicitly rejects booleans. Exactly one legal action is executed by the harness without calling the agent.

Actions include roll/end turn, road/settlement/city, development purchase/play, robber movement, one-resource discard, and maritime trade. The pinned engine uses `DISCARD_RESOURCE` with a resource value and a two-part robber value `(coordinate, victim_or_None)`; incompatible engine releases change these shapes. Always select from the supplied legal list.

| Constraint | Value |
|---|---|
| Scoring interpreter | Python 3.11 |
| CPU allocation | One core per game |
| Agent memory | 2 GiB in harness constant (`2 * 1024**3`); described as 2 GB in statement |
| Initial per-game CPU allowance | 300 ms |
| Increment per actual agent decision | 12.5 ms |
| Maximum total allowance | 1,500 ms per game |
| One-call wall timeout | 3 seconds |
| Additional per-game waiting allowance | 3 seconds beyond CPU allowance |
| Import and constructor timeout | 60 seconds; excluded from game CPU |

After `k` calls, cumulative CPU allowance is `min(0.300 + 0.0125*k, 1.500)` seconds. The first call includes its increment, giving 312.5 ms before charged work. At 56 calls the total allowance is 1 second; at 96 calls it reaches the ceiling. `obs.cpu_left` is the current remaining allowance, not an independent budget to spend afresh on every call.

Exhausting the clock causes random legal moves for the rest of that game. An exception or illegal index causes a random action and a recorded fault; errors above 2% of decisions disqualify a submission under S1. The team should target zero errors, crashes, timeouts and budget-exhausted games.

The agent cannot access the network, invoke an LLM service, start other programs, or create worker processes. Standard library and organizer-installed dependencies are the runtime boundary. Agent files are read-only on the scorer; temporary writes belong in `tempfile.gettempdir()`. Load files relative to `__file__`.

One Agent object plays multiple games against the same opponent. Cross-game adaptation is allowed, but game-specific state must not leak accidentally. The host reseeds global `random` per game; an agent-owned `random.Random` object is not automatically reset. A reproducibility claim must account for object lifecycle and game ordering. Local parallelism belongs in an external experiment runner, not inside `decide`.

## 6. What F actually does, and possible improvement directions

**Verified source — S7, E1:** F samples one world, copies it for each legal action, executes that action and selects the highest heuristic value. Its evaluation uses 13 named weights.

The relative scales strongly prioritize public points (`3e14`), then own production (`1e8`) and enemy production (`-1e8`), then reachable production (`1e4`), buildable nodes (`1e3`), hand synergy (`1e2`), and smaller terms for roads, cards, Knights, resource quantity and tile coverage. These are organizer/upstream parameters, not our tuned values.

### Source findings that affect implementation

- **Weight-tuning trap:** `get_value_fn("base_fn", custom_weights)` returns `base_fn(DEFAULT_WEIGHTS)` in this pinned engine. Passing modified weights this way does not tune F. Later experiments must use a path that actually consumes the weights, such as `base_fn(custom_weights)`, and verify changed scores on fixed positions.
- **Terminal-value gap:** F's return expression directly rewards public VP, not an explicit terminal win or own actual VP. Hidden VP cards enter through the count of development cards. Hypothesis: explicit terminal wins and actual-point awareness could improve endgame choices.
- **Feature-vector gap:** E2's default extractor list excludes explicit production, expansion and reachability extractors. Opponent resources appear as a total, not separate resource counts, in its hand features. A model using only that vector does not automatically get the useful engineered features F uses or all information exposed by `Obs`. The statement reports 614 features; the count has not been measured locally.
- **Redundant computation:** F computes the same production extractor twice for the same world and perspective, then reads our and their features separately. Computing it once is a candidate optimization; any speedup remains unmeasured.
- **Sampling is not automatically valuable:** F's deterministic-action evaluation mostly uses visible features. Repeating hidden-card sampling for an unchanged evaluation can add cost without changing rankings. Multiple worlds become more useful when a search/value model depends on hidden-card consequences.
- **One action is not one turn:** A trade can enable a build, and a road can enable a settlement. A one-action evaluator can miss these sequences. Bounded same-turn search is a candidate, with strict time and branching limits.

### Provisional direction

**Proposal:** establish the untouched F baseline, then investigate a fast heuristic agent with explicit tactical win checks, better resource/expansion features, and a small budget-aware search over promising action sequences. Keep learning-based value models as an option after throughput and feature coverage are measured.

The problem statement reports that its generic MCTS and deeper alpha-beta baselines repeatedly exceed the clock. Those published numbers are organizer evidence, not our experiments. They justify measuring search cost early; they do not prove that all search approaches are unsuitable.

A candidate design would cheaply rank legal actions, preserve a legal fallback, expand only a small shortlist, and stop with CPU headroom. Chance outcomes must be sampled or averaged appropriately; one favorable stolen card or development draw is not reliable value. Never spend the entire opening reserve without considering subsequent decisions.

No beam width, depth, feature weights, model size, training method, or expected win rate is selected yet. These require the next research and experiment stages.

## 7. Scoring, deadlines and submission implications

**Verified source — S1; dates/times below are the published schedule for 17 October 2026, IST.**

| Time | Event |
|---|---|
| 10:00 | Event starts |
| 11:00 | Uploads open |
| 15:30 | Checkpoint, not elimination |
| 17:00 | Final agent upload deadline |
| 17:30 | Reports due from top-30 teams |
| 17:50 | Top 30 and group-stage results announced |
| 18:00 | Presentations start |
| 19:30 | Event ends |

- Strength is `0.5 * win_rate_vs_F + 0.5 * win_rate_vs_O` on private boards.
- Each team advances using its best submission by this private score, not necessarily its latest upload or best public leaderboard result.
- Top 30 enter three groups of ten. Each group opponent pairing gets 1,000 games.
- Robustness is the mean win rate against the five weakest matchups out of nine opponents. The top two teams in each group by robustness present.
- A game that reaches the 1,000-turn limit without a winner counts as a loss for both sides.
- There are 7 scored agent submissions and at most 10 total uploads, including failed uploads. Preflight failures do not consume a scored slot but do consume an upload attempt. Confirm whether report uploads count toward that overall cap; do not assume an exemption.
- Report: at most four A4 single-column pages excluding references, minimum 11-point text. Presentation: six minutes plus four minutes of questions.
- Reports and presentations together matter about as much as strength and robustness together; exact detailed weights are not published. Do not invent a four-way percentage split.

**Schedule ambiguity:** reports are due before the published top-30 announcement. Prepare the report before results; the teammate dealing with organizers should clarify eligibility notification and upload-count treatment. This review did not contact organizers or access the portal.

## 8. Local environment: observed state and future setup

### Read-only observations

At review time, in the current shell:

- Default `python3`: **3.14.8**.
- `python3.11` and `uv`: **not found on PATH**. This does not prove there is no installation elsewhere.
- Git: **2.56.0**.
- `nproc`: **24 logical processing units**; this is not a physical-core count or scorer equivalence.
- RAM: about **15 GiB total**, **3.6 GiB available** at that moment.
- Workspace filesystem: about **74 GiB free**.

No environment has been installed or validated. Available memory and disk are time-specific observations. Begin future evaluation with low concurrency and measure memory before scaling.

### Exact dependency recipe supplied by the repository

**Verified source — S3; install availability has not been tested:**

| Package | Pin |
|---|---|
| catanatron | Git commit `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816` |
| networkx | 3.6.1 |
| psutil | 7.2.2 |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| scikit-learn | 1.9.1 |
| torch | 2.8.0, CPU build |

Use the supplied requirements unchanged initially. If a pin fails to resolve, preserve the exact error and establish whether the supplied source, package index or platform is responsible. Silently selecting another version undermines reproducibility.

The repository provides code and an installation recipe, not a portable prebuilt local environment or a credentials file. Its file tree contains no `.env` or `.env.example`. Public game evaluation does not require the team's SSH password or optional inference-service API key.

### Proposed next setup procedure — not executed

1. Obtain an isolated Python 3.11 runtime without replacing the system interpreter. Locate an existing runtime first; otherwise choose a local installation method.
2. Clone the user-specified organizer repository over HTTPS into a separate local dependency checkout. Record its commit and compare it with this review.
3. Create a Python 3.11 virtual environment. On Linux, install the CPU Torch build before the supplied requirements, as instructed by S2.
4. Run `python -m catan_kit.selfcheck` from the kit root. Preserve the full output and package versions.
5. Run an untouched F-versus-random smoke evaluation, then baseline matches. Log errors and clock metrics, not just wins.
6. Repeat a fixed-seed baseline to check reproducibility. Diagnose differences before training or tuning.

Illustrative commands after a local Python 3.11 runtime is available, executed one at a time from the workspace:

```bash
git clone https://github.com/lyric-hyde/catan-hackathon-agent.git organizer-kit
cd organizer-kit
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python -m catan_kit.selfcheck
python -m catan_kit.evaluate --a examples/f_agent.py --b examples/random_agent.py --games 20
```

These are instructions for a later task, not evidence of successful setup. The organizer's self-check verifies engine/action compatibility and determinism, but does not check every dependency pin; record installed versions and engine Git provenance too.

Do not enable the scorer's privileged sandbox/cgroup setup locally just to start development. Its isolation configuration is scorer infrastructure. Local harness success does not certify scorer timing, memory or filesystem behavior.

## 9. Future team repository and environment separation

**User requirement:** create the team's GitHub repository later; do not share the environment there. The initial interpretation is to share our code, documentation and reproducible setup instructions while leaving installed environments and the organizer engine outside the team repository.

Proposed repository contents: our agent modules, experiment scripts, configuration, decision notes, reproducibility records and source attribution. Reference the official kit URL and commit instead of copying its whole implementation. Keep the dependency checkout separate from the team repo.

Exclude `.venv/`, `venv/`, `.env`, `.env.*`, API keys, passwords, SSH files, machine-specific configuration, caches, and downloaded dependency trees. Only a deliberately safe example config should ever be an exception. Review artifacts and logs before committing them, and use an explicit file list when packaging a submission.

**Proposal:** make the later team repository private because S1 prohibits sharing team code, weights, data or submissions with other teams. Preserve upstream license/attribution when reusing public material; the kit identifies itself as GPL-3.0-or-later. No repository or visibility setting has been created.

SSH, organizer-machine uploads and portal credentials remain with the teammate already handling them. No login details need to be copied into this document or a repository.

## 10. Evidence and experiment policy for later work

**Proposal informed by S1 and S6:** record a hypothesis and comparison before each run. Keep an immutable baseline and change one meaningful component at a time.

Every completed experiment should record:

| Field | Reason |
|---|---|
| Agent/code revision, kit/engine revisions and configuration | Identify exactly what ran |
| Python/dependency versions, CPU and concurrency | Interpret speed and reproduce behavior |
| Opponent, game count, seeds and seat pairing | Make comparisons fair |
| Wins, no-winner games, interval and raw per-game records | Quantify evidence and investigate failures |
| Mean/worst CPU, exhausted games, errors, timeouts, crashes, load time | Check practical eligibility |
| Training vs validation/test split | Prevent seed and leaderboard overfitting |
| Interpretation, limitation and next decision | Build a defensible report |

The supplied evaluator pairs boards and alternates seats, and reports a normal-approximation 95% interval. Use even game counts for complete pairs. Because games share boards and seat-swapped conditions, a later statistical analysis should account for pairing; a small apparent lead is not proof. All-winning/all-losing samples can produce a zero-width interval in the supplied formula, which is not zero uncertainty.

S1 recommends at least 400 games during training comparisons and 1,000 before submission. Tiny runs are only smoke tests. Compare versions on common held-out seeds, retain different opponent styles for robustness checks, and keep a final untouched validation set.

`evaluate.run` returns a summary; `match.play_chunk` exposes per-game records for a future logging wrapper. Do not assume the CLI already saves a complete experiment log. A custom driver needs the hash-seed setup and a `__main__` guard because the harness starts agent processes using spawn.

Reproducibility also needs the kit's maritime-trade ordering patch and protection against feature-order initialization reseeding randomness. Import the kit before constructing games; do not rewrite or bypass its patches.

No numerical performance claims are available from this task. We have not measured F locally, beaten F/O, trained anything, or tested an implementation.

## 11. Decisions, open questions and handoff

### Decisions for this stage

| Decision | Reason |
|---|---|
| Stop after source review and this Markdown document | User requested one task at a time |
| Use the user-supplied repository and exact engine pin | Prevent silent interface drift |
| Keep SSH and remote operations out of this work | Teammate already owns that responsibility |
| Make local setup the next bounded execution task | It is required before trustworthy experiments |
| Treat fast heuristics plus bounded search as an initial candidate | Tight clock and available F baseline justify testing it first |
| Keep strategy choices provisional until research and measurement | Source analysis is not performance evidence |
| Defer four-person allocation and GitHub creation | User placed those after research and planning |

### Open items to resolve in later tasks

- Can the exact dependency pins be installed on local Python 3.11, and does the full self-check pass?
- What are local baseline timing, memory, throughput and repeatability under this harness?
- Which action sequences and opening features produce measurable improvements under budget?
- What features are actually present in the runtime vector, with what dimensionality and cost?
- What are the exact engine edge cases for setup resources, development timing, road bonuses and terminal wins?
- What are O's behavior and weaknesses? Its implementation is not in the supplied repository; do not invent them.
- Does the observed benefit of extra world sampling justify its CPU cost for our chosen policy?
- How will the team coordinate the report deadline and limited uploads with the remote-machine owner?
- After research, what interfaces and ownership boundaries let four people work independently and integrate safely?

### Intended sequence, not an assigned implementation plan

1. **Completed:** understand the supplied problem, PDF and environment source; write this document.
2. **Next bounded task:** install and validate the local environment, recording actual commands and results in a separate Markdown setup log.
3. Research Catan strategy and relevant agent techniques against these exact constraints; produce a sourced research note.
4. Choose an approach and make the four-person plan with interfaces, dependencies and acceptance checks.
5. Create the private team repository with environment/credential exclusions and shared context.
6. Implement, benchmark, iterate, and prepare evidence for the report; the teammate handles remote access/submission.

**Stop point:** only Task 1 is complete. This document is the durable deliverable. The temporary source checkouts under `/tmp` are review aids, not a persistent installed environment; the pinned URLs above are the reproducible references.
