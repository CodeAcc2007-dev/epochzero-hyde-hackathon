# Common team context

Status: local environment setup **complete and validated**; source/dataset collection complete; **Phase 1 research assignments are ready**. This planning task has not executed the assigned research.

## What we are building

A Python agent for the Hyde two-player Catan hackathon. Games use the supplied patched engine, 10 victory points, no player-to-player trades, and normal bank/port trades. The deliverable is an agent ZIP with `agent.py` at its root, at most 100 MB. This folder is working context, not a submission package.

Organizer repository: https://github.com/lyric-hyde/catan-hackathon-agent

Reviewed/installed kit commit: `04fffac90e00610f60e0b06d919f262f4b3ed9db`.

Engine commit: `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816` from the organizer requirements. Do not replace it with the PyPI engine or independently upgrade dependencies.

## Read first

- [Problem and environment analysis](../../01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md): source findings and provisional strategy hypotheses.
- [Local setup and validation](../../02-LOCAL-SETUP-AND-VALIDATION.md): exact commands, versions, results, limitations and shared paths.
- [Team workspace instructions](../README.md): how all members reuse one environment.
- [Research and dataset catalogue](../../03-RESEARCH-AND-DATASET-CATALOGUE.md): downloaded resources, source claims and rule mismatches.
- [Phase-wise roadmap](../../04-PHASE-WISE-PLAN.md): research through repeated bot clashes and eight local finalists.
- [Phase 1 common research brief](../PHASE-1-COMMON-BRIEF.md): scope, dataset access and evidence standards.
- [Your member-specific context](02-MEMBER-CONTEXT.md), [detailed research brief](03-PHASE-1-RESEARCH-BRIEF.md) and [findings worksheet](04-PHASE-1-FINDINGS.md).
- [Pinned official problem statement](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/PROBLEM_STATEMENT.md).

The four numbered project-wide Markdown documents live outside the member folder. Include them and source metadata in a standalone handoff. Downloaded datasets/papers stay shared locally; their URLs, hashes and terms are in the catalogue.

## Interface and constraints

Implement `Agent.__init__()` and `Agent.decide(obs, playable_actions) -> int`. Return an index in the current legal-action list. Do not return an Action, float or boolean. Forced single-action moves bypass our code.

CPU allowance per game: `min(0.300 + 0.0125 * decisions, 1.500)` seconds. `obs.cpu_left` is current remaining CPU, including this decision's increment. Exceeding the allowance causes random moves for the rest of the game. One call may take at most three wall-clock seconds; model loading has a separate 60-second limit. The scorer uses Python 3.11, one CPU core per game and 2 GB per agent.

No agent network calls, LLM calls, worker subprocesses or bundled executables. Load data relative to `__file__`; temporary writes use `tempfile.gettempdir()`. One Agent instance spans multiple games, so distinguish game state from intentional opponent adaptation.

We see the exact opponent resource hand and bank, board, own hand/cards, own actual points, opponent public points and unplayed-card count. Opponent unplayed development-card identities and future draws are hidden. `sample_world` supplies hypothetical consistent worlds, not hidden truth.

## Important source findings

- A city is worth two points total, but upgrading a settlement adds one point.
- Monopoly exists although the introductory PDF omits it.
- F evaluates one action ahead using a fixed heuristic. It is a useful baseline, not our final chosen strategy.
- `get_value_fn("base_fn", custom_weights)` ignores custom weights in this pinned engine. A tuning experiment must verify that its parameters change scores.
- Default vector extraction omits explicit production/reachability features and opponent resource counts by type. Do not assume the vector contains all observation information.
- Exact kit patches and Python/hash settings matter for reproducibility.

These findings suggest experiments; none establishes that we have improved on F or O. No competition agent or trained model has been created in this setup task.

## Shared environment: reuse it

All four member folders on this computer use the SAME interpreter and organizer checkout. There is no environment, dependency clone, or credentials file in any member folder.

From this member directory:

```bash
../run-python.sh --version
../run-python.sh -c "import catan_kit, catanatron; print('Shared imports OK')"
```

Later, in the implementation/testing phases, when a real `agent.py` exists in your folder, evaluate it using the shared harness. This is a future command, not a Phase 1 task:

```bash
../run-python.sh -m catan_kit.evaluate --a agent.py --b ../../shared-local/organizer-kit/examples/f_agent.py --games 20
```

The launcher preserves your current directory and uses one thread per numeric-library process. It never installs, clones or upgrades packages. Keep shared dependencies stable while others work. Do not run large evaluations concurrently without coordinating CPU and RAM.

On another computer with an already installed environment, set `CATAN_PYTHON` to its absolute Python executable and `CATAN_KIT_DIR` to its absolute organizer-kit directory, then use the same launcher. The values are local shell settings, not committed credentials/configuration. The filesystem environment on this laptop cannot be used directly by a different computer; that computer must already have or separately install the compatible runtime.

## Collaboration boundaries

- Use your own member folder for assigned research and derived outputs. Do not modify another member's files without coordination.
- Phase 1 research roles are assigned in the member briefs. Names are assigned: Aroosh (1), Avadooth (2), Pranesh (3), Anni (4). Later bot-building ownership and integration interfaces remain to be decided after research.
- Do not modify the organizer kit/harness to make an agent appear stronger or faster.
- SSH, organizer-machine credentials, remote uploads and the portal belong to the teammate already handling them.
- Keep environments, API keys, passwords, caches and credentials outside shareable folders and future Git history.
- Keep every design decision, run configuration, result and limitation in Markdown with links to raw evidence.
- Smoke tests prove setup only. Later comparisons need adequate games, held-out seeds, faults/CPU metrics and diverse opponents.
- The official scoring includes private F/O strength and worst-matchup group robustness; do not optimize only the public leaderboard.

## Verified setup results

Python 3.11.17, the exact engine commit, all supplied package pins and CPU-only Torch were verified. The organizer self-check passed. F won 20/20 games against random with zero errors, timeouts, crashes and budget overruns. Two 12-game F-versus-F runs matched per-game outcomes, lengths and decision counts. All four member directories were tested against the same interpreter and kit. These are setup checks, not proof of competitive agent strength. See the setup report for commands and raw-evidence links.

## Current Phase 1 assignment and stop point

The four research tracks are: Member 1 (Aroosh) statistical evidence/economy; Member 2 (Avadooth) opening/expansion/ports; Member 3 (Pranesh) tactics/threats/VP races; Member 4 (Anni) methods/text-data audit/tournament design. Read your detailed brief and complete your findings report. Offline research analysis is now part of those instructions; no research has been performed merely by creating the briefs.

The later workflow is multiple candidate bots, repeated eligibility/clash/selection/improvement rounds, and eight validated local finalists. The current event permits **7 scored submissions and 10 total uploads**, so eight local finalists are not eight scored submissions. The portal teammate must track remaining slots.

Phase 1 stops with reviewed findings, alternatives and proposed experiments. Bot implementation, training, new game simulations, later bot/test task assignment, GitHub creation and submissions wait for the relevant later phase. Do not modify the environment or raw downloads to carry out this planning task.
