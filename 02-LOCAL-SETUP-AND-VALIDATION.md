# Local environment setup and team workspace

Date: **17 October 2026 (IST)**.

Status: **COMPLETE — local environment installed and validated; all four member folders verified against the same shared installation.**

## Scope and decisions

The user authorized local setup from the supplied repository, testing, a Markdown record, and a separate folder with four member subfolders. Each member receives common context and a separate member-specific document; task allocation is deferred. No SSH, remote portal, upload, training, strategy implementation, external Catan research or new GitHub repository is part of this task.

One installation lives in `shared-local/`, outside the shareable `team-work/` tree. All four members on this computer reuse the same Python executable and organizer checkout. The shared environment is never copied into a member folder. A teammate on another machine can reuse that machine's existing compatible installation through launcher overrides; they cannot directly use this laptop's filesystem environment.

The earlier [problem analysis](01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md) is retained as the historical source review. Its statements that setup was not yet performed describe the previous task. This document is the current setup record.

## Files and folders created

```text
shared-local/                         local only, ignored for future Git
  organizer-kit/                      single organizer repository clone
  python/                             managed Python 3.11 runtime
  .venv/                              shared installed packages
  tools/                              uv bootstrap tooling
  cache/                              uv installation cache
  logs/                               raw install/test evidence
  verify_environment.py               version/provenance/import checks
  verify_games.py                     bounded F-vs-F repeatability check
  verify_member_access.py             checks all four member working directories
team-work/                            shareable; contains no environment
  README.md
  run-python.sh                       selects existing shared installation
  member-1/
    01-COMMON-CONTEXT.md
    02-MEMBER-CONTEXT.md
  member-2/                           same two context documents
  member-3/                           same two context documents
  member-4/                           same two context documents
```

Both workspace and team `.gitignore` files exclude virtual environments, secrets and caches; the workspace ignore excludes the entire `shared-local/` directory. No new Git repository was initialized. The organizer clone retains its existing `.git` directory as expected.

## Initial checks

- Current system `python3` was Python 3.14.8. Python 3.11 and uv were absent from the shell PATH; the inspected system Python paths did not provide 3.11.
- The Codex bundled runtime was Python 3.12.14, so it was not used as the scoring-compatible interpreter.
- Git 2.56.0 was available.
- Initial resources: 24 logical CPU units, about 15 GiB RAM total / 4.5 GiB available, and about 74 GiB free on the workspace filesystem. These are observations at setup time, not guaranteed future capacity.
- No applicable `AGENTS.md` was found in the project or organizer checkout. Parent instructions were checked in the preceding review.

Decision: install a local managed Python 3.11 runtime and one virtual environment without replacing system Python or editing shell startup files. Use CPU-only Torch, as instructed by the organizer, to avoid installing CUDA dependencies.

## Executed installation steps

All paths below are relative to the project root unless stated otherwise. Run one command at a time. Shell pipeline commands use `set -o pipefail` so installation/test failures are not hidden by `tee`.

### 1. Create shared and member directories

```bash
mkdir -p shared-local/logs shared-local/tools team-work/member-1 team-work/member-2 team-work/member-3 team-work/member-4
```

### 2. Clone the supplied repository once over HTTPS

```bash
git clone https://github.com/lyric-hyde/catan-hackathon-agent.git shared-local/organizer-kit
git -C shared-local/organizer-kit rev-parse HEAD
sha256sum shared-local/organizer-kit/requirements.txt
```

Result: commit `04fffac90e00610f60e0b06d919f262f4b3ed9db`, identical to the previous review. Requirements SHA-256: `e6419ef5507a3487694b6c8b95241884046a9353edaf326f2691ef7ad55fbaf8`.

The README names a different example clone URL; the user's supplied URL was used. No source changes or alternative engine versions were introduced.

### 3. Install uv locally as bootstrap tooling

```bash
set -o pipefail
python3 -m pip install --target shared-local/tools uv 2>&1 | tee shared-local/logs/01-install-uv.log
```

Result: uv 0.13.1 installed under `shared-local/tools`. Pip encountered one transient TLS `WRONG_VERSION_NUMBER` warning and retried successfully. Certificate verification was not disabled. This did not change system-installed Python packages.

### 4. Install Python 3.11 into the shared directory

```bash
UV_PYTHON_INSTALL_DIR="$PWD/shared-local/python" UV_CACHE_DIR="$PWD/shared-local/cache" shared-local/tools/bin/uv python install 3.11 --no-bin 2>&1 | tee shared-local/logs/02-install-python.log
```

Result: managed CPython 3.11.17 installed. `--no-bin` avoided adding a user-level executable link. The system Python remains unchanged.

### 5. Create the single shared virtual environment

```bash
UV_PYTHON_INSTALL_DIR="$PWD/shared-local/python" UV_CACHE_DIR="$PWD/shared-local/cache" shared-local/tools/bin/uv venv --python 3.11 --seed shared-local/.venv 2>&1 | tee shared-local/logs/03-create-venv.log
```

Result: Python 3.11 environment created with pip 26.2.1 and seed packaging tools.

### 6. Install CPU Torch, then exact organizer requirements

```bash
shared-local/.venv/bin/python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu 2>&1 | tee shared-local/logs/04-install-torch.log
shared-local/.venv/bin/python -m pip install -r shared-local/organizer-kit/requirements.txt 2>&1 | tee shared-local/logs/05-install-requirements.log
```

Installation succeeded with all supplied version pins unchanged. Torch remains `2.8.0+cpu`. NumPy and SciPy downloads were temporarily slow but completed without a version workaround; remaining packages then installed successfully. The pinned catanatron source built as a Python wheel. Dependency resolution and actual imported versions were checked separately below.

### 7. Create common launcher and member context

Created `team-work/run-python.sh`, made it executable with `chmod +x`, and validated Bash syntax with `bash -n`.

The launcher resolves the sibling shared directory, checks that its interpreter and kit exist, adds the kit to `PYTHONPATH`, and sets `PYTHONHASHSEED=0` plus `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, and `NUMEXPR_NUM_THREADS` to 1. It preserves the caller's current directory. It does not clone, install, upgrade or activate another environment.

Each of the four member folders has the same common-context document and a separate document explicitly marked unassigned. No person, role, module ownership or strategy was chosen.

## Validation commands and results

All checks below were actually executed. Game runs were sequential. No organizer source or example agent was modified.

### 8. Dependency, provenance and numeric-library checks

```bash
./team-work/run-python.sh shared-local/verify_environment.py 2>&1 | tee shared-local/logs/06-environment-audit.log
./team-work/run-python.sh -m pip check 2>&1 | tee shared-local/logs/07-pip-check.log
./team-work/run-python.sh -m pip freeze > shared-local/logs/installed-packages.txt
```

Result: **PASS**. `pip check` reported `No broken requirements found.`

| Component | Actual installed value | Verification |
|---|---|---|
| Python | 3.11.17 | Correct scoring minor version |
| catanatron | 3.3.0 | Installed Git provenance matches exact pinned commit |
| networkx | 3.6.1 | Matches requirements |
| psutil | 7.2.2 | Matches requirements |
| numpy | 2.4.6 | Matches requirements; array operations used |
| scipy | 1.17.1 | Matches requirements; linear solve passed |
| scikit-learn | 1.9.1 | Matches requirements; fit/predict regression passed |
| torch | 2.8.0+cpu | Matches CPU build requirement; tensor operation passed |

The audit asserted the versions rather than merely printing them. Torch reports no CUDA build and one compute thread. The catanatron install's `direct_url.json` records engine commit `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. The kit's worktree is clean. `PYTHONHASHSEED` is `0`, the determinism patch is active, and a real two-player game produces a **614-value feature vector**.

The complete transitive-package snapshot is in [installed-packages.txt](shared-local/logs/installed-packages.txt). The organizer pins its listed packages, not every transitive dependency; this snapshot records what this local installation resolved. Bootstrap packaging tools are not additional permitted agent dependencies.

### 9. Organizer self-check

```bash
set -euo pipefail
./team-work/run-python.sh -m catan_kit.selfcheck 2>&1 | tee shared-local/logs/08-selfcheck.log
```

Result: **all checks passed**, exit code 0.

| Check | Actual result |
|---|---|
| Interpreter, engine version, networkx, patch and hash settings | Passed |
| Legal action enum set | Matches pinned engine |
| Repeated reference game, seed 4256 | `Color.RED`, 111 turns, identical across four runs |
| F vs random | 20/20 F wins |
| F errors | 0 |
| F CPU in self-check | 149 ms mean/game; 0 games over budget |
| Random vs F | 0/20 random wins |
| Repeated self-check evaluation | 976 then 976 decisions |

This self-check includes 70 harness games (20 + 20 + 15 + 15) plus four direct reference games.

### 10. Explicit evaluator smoke run

```bash
./team-work/run-python.sh -m catan_kit.evaluate --a shared-local/organizer-kit/examples/f_agent.py --b shared-local/organizer-kit/examples/random_agent.py --games 20 --seed0 990000 2>&1 | tee shared-local/logs/09-f-vs-random.log
```

Result: **PASS**, exit code 0.

| Metric for F | Measured value |
|---|---|
| Wins | 20 / 20 |
| Mean CPU per game | 149.5 ms |
| Worst CPU per game | 300.0 ms |
| Decisions | 1,227 |
| Games over budget / random fallback moves | 0 / 0 |
| Errors | 0 |
| Timeouts / crashes | 0 / 0 |
| Reported load time | 0.00 s, rounded by evaluator |
| Wall time | 4.7 s |

The CLI printed `1.0000 +-0.0000`; its normal-approximation interval degenerates at 20/20. This does not mean certainty about the true win rate. This is an environment smoke test, not a strength claim for our future agent.

### 11. Per-game repeatability with both seats running F

```bash
./team-work/run-python.sh shared-local/verify_games.py 2>&1 | tee shared-local/logs/10-repeatability.log
```

Result: **PASS**, exit code 0. Two independent harness runs each played 12 F-versus-F games on six seat-paired boards starting at seed `771000`.

For every game, both runs matched on winner, turn count, both agents' decision counts, seed and seat metadata. Each run had six A wins and six B wins, with no unfinished games. A made 617 decisions and B made 636 in each run. Both seats in both runs had **zero errors, timeouts, crashes, clock-exhausted games and fallback moves**.

| Run | A mean / worst CPU | B mean / worst CPU |
|---|---|---|
| repeat-a | 116.7 / 190.0 ms | 122.5 / 180.0 ms |
| repeat-b | 122.5 / 180.0 ms | 126.7 / 190.0 ms |

CPU and wall durations were deliberately excluded from equality comparison because they vary with scheduling. Full per-game records are retained in [repeat-a.json](shared-local/logs/repeat-a.json) and [repeat-b.json](shared-local/logs/repeat-b.json); the comparison outcome is in [repeatability.json](shared-local/logs/repeatability.json).

Total game checks in this task: **114 harness games plus four direct reference games**. These establish local operation and bounded repeatability; they are not a large competitive benchmark.

### 12. All four member directories reuse the same installation

```bash
./team-work/run-python.sh shared-local/verify_member_access.py 2>&1 | tee shared-local/logs/11-member-access.log
git -C shared-local/organizer-kit status --porcelain
python3 --version
```

Result: **PASS**. The script actually invoked the launcher from each member directory and imported the kit and engine. All four resolved exactly the same interpreter and kit paths:

```text
Python: shared-local/.venv/bin/python
Kit:    shared-local/organizer-kit/catan_kit/__init__.py
```

The member-access JSON stores their full absolute paths. It also verified byte-identical common-context files and absence of `.venv`, `venv`, `env`, `.env` and `organizer-kit` entries anywhere under `team-work`.

Final source status was clean. System Python remained **3.14.8**. Approximate disk usage was **1.3 GiB** for the shared installation/tooling and **80 KiB** for the team workspace. All members have two context documents; none has a duplicate checkout or environment.

## Evidence index

| File | Contents |
|---|---|
| [01-install-uv.log](shared-local/logs/01-install-uv.log) | uv install and transient retry |
| [02-install-python.log](shared-local/logs/02-install-python.log) | Managed Python install |
| [03-create-venv.log](shared-local/logs/03-create-venv.log) | Shared venv creation |
| [04-install-torch.log](shared-local/logs/04-install-torch.log) | CPU-only Torch installation |
| [05-install-requirements.log](shared-local/logs/05-install-requirements.log) | Exact source resolution and package installation |
| [environment.json](shared-local/logs/environment.json) | Asserted versions, source commit, CPU build and feature count |
| [06-environment-audit.log](shared-local/logs/06-environment-audit.log) | Full environment audit output |
| [07-pip-check.log](shared-local/logs/07-pip-check.log) | Dependency compatibility result |
| [08-selfcheck.log](shared-local/logs/08-selfcheck.log) | Organizer checks |
| [09-f-vs-random.log](shared-local/logs/09-f-vs-random.log) | Explicit CLI smoke run |
| [10-repeatability.log](shared-local/logs/10-repeatability.log) | Per-seat repeated-game summaries |
| [11-member-access.log](shared-local/logs/11-member-access.log) | Four-member shared-import checks |
| [member-access.json](shared-local/logs/member-access.json) | Shared paths confirmed for every member |

The three verification scripts are local setup aids, not competition agent files. Their checks are documented above and they remain available under `shared-local/` for rerunning on this machine.

## Daily use: no repeated cloning or installation

From any member directory:

```bash
../run-python.sh --version
../run-python.sh -c "import catan_kit, catanatron; print('Shared imports OK')"
```

From the project root:

```bash
./team-work/run-python.sh --version
./team-work/run-python.sh -m catan_kit.selfcheck
```

Use the launcher rather than bare system `python`. If an existing environment is located elsewhere, set `CATAN_PYTHON` and `CATAN_KIT_DIR` to absolute paths in that terminal before using the launcher. No `.env` file or credentials are needed.

Changes to the shared packages affect every member, so coordinate dependency changes and preserve the supplied pins. Member code and outputs should remain in the member's own folder. Initially run evaluations sequentially to avoid distorted timings and excess memory usage.

## Evidence and limitations

Installation logs are in [shared-local/logs](shared-local/logs/). Raw evidence stays local with the environment; this report embeds key results for sharing. Do not share `shared-local/`. Share `team-work/` and both project-wide Markdown documents for complete context.

A passing local setup test does not certify organizer-machine timing, official ranking, robustness against teams or performance against O. No organizer credentials or remote machine were used. There is no agent implementation or training in this task.

## Completion and stop point

**Completed:** one local Python 3.11 environment using the supplied repository and pins, actual game validation, a reusable launcher, four member context folders, and this command/result record.

**Deferred:** deeper Catan research, selecting the final agent strategy, dividing work among four people, writing a competition agent, training, GitHub creation, remote access and submissions. No SSH was used. Stop after this task, as requested.
