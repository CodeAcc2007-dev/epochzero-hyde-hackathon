# Frozen evaluation plan and replay conventions

17 October 2026. Runtime code is frozen as B05/v003 and B06/v003. Actual per-file SHA-256 values are in each manifest and every run's metadata. All experiment arguments were written to metadata before that run's first game; this explanatory document was assembled while the frozen runs executed. No formal third-party preregistration is claimed.

## Batches and scope

| Batch | Boards | Games | Role |
|---|---|---:|---|
| v001 smoke, each bot | 711000–711005 | 12 each | Development diagnostics |
| B05/v002 interrupted run | Started821000; completed first240 games/120 boards | 240 retained | Preliminary only; stopped for source-review guard correction, next incomplete chunk excluded |
| B05/v003 vs F | 841000–841499 | 1,000 | New fixed held-out comparison, no weight tuning afterward |
| B06/v003 vs F | Same841000–841499 | 1,000 | Comparable paired boards/seats and lifecycle |
| Common greedy control vs F | 841000–841199 | 400 | Ablation on first200 matching board pairs; not a third strategy entrant |
| B05/v003 vs B06/v003 | 855000–855099 | 200 | Separate direct matchup; still only one peer style |
| Clean-package smoke | 873000–873001 per bot | 4 each | Standalone load/legality check, not extra strength evidence |

Final code is not modified based on these results. These board ranges are now used evaluation evidence; future owner improvements must not pretend they remain untouched confirmation data. Internal versions and all unsuccessful/interrupted evidence are retained.

## Exact commands

From project root, using the existing launcher/environment:

```bash
./team-work/run-python.sh team-work/member-3/implementation/test_policies.py
PYTHONPATH=team-work/member-3/bots/B05/v003 ./team-work/run-python.sh \
  team-work/member-3/implementation/test_race_math.py -v
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-3/bots/B05/v003/agent.py \
  --b shared-local/organizer-kit/examples/f_agent.py \
  --games 1000 --seed0 841000 \
  --out team-work/member-3/implementation/results/B05-v003-vs-F
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-3/bots/B06/v003/agent.py \
  --b shared-local/organizer-kit/examples/f_agent.py \
  --games 1000 --seed0 841000 \
  --out team-work/member-3/implementation/results/B06-v003-vs-F
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-3/implementation/controls/greedy/agent.py \
  --b shared-local/organizer-kit/examples/f_agent.py \
  --games 400 --seed0 841000 \
  --out team-work/member-3/implementation/results/greedy-control-vs-F
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-3/bots/B05/v003/agent.py \
  --b team-work/member-3/bots/B06/v003/agent.py \
  --games 200 --seed0 855000 \
  --out team-work/member-3/implementation/results/B05-vs-B06
```

Use a **new output directory** for replay; the driver refuses to overwrite evidence. Teammates with another supplied environment set `CATAN_PYTHON`/`CATAN_KIT_DIR` using the shared instructions. The shown F path refers to this machine's existing kit; choose the corresponding unchanged pinned F on another machine. Never copy or commit the environment.

## Harness and statistics

The driver calls the unchanged official `match.play_chunk`, with the default secret-key mechanism's **public local key**, ten VP and both clocks enabled. It records each game's original index/board/seat, outcome and both seats' official CPU/wall/decision/over/fallback/error/timeout/crash fields. Both agent processes reset every20 games; all indices remain global and adjacent board/seat pairs stay together. This exact lifecycle differs from the CLI's one uninterrupted process pair over1,000 games, and results are not advertised as a canonical CLI/private-score prediction. A frozen rerun should use the same lifecycle and order.

No parallel matches run on this laptop. Load times are separate from game CPU. Local Intel i7-14650HX measurements are not the AMD scorer's measurements. No peak-RSS profile is claimed; unchanged host limits remain in place. The code uses one Python execution thread and no spawned workers; launcher numeric-thread settings are1.

Retain no-winner games as losses for both bots. The stock normal interval is preserved in JSON as an official summary field; interpretation uses board-pair descriptive bootstrap intervals plus the conservative bounded-score interval under independent-pair assumptions. Matched candidate/control comparisons resample board-pair score differences together and are descriptive, without a multiple-comparison superiority claim. Never describe an extra layer as responsible for all wins merely because the full bot beats F.

Check all source hashes at run end, not only before starting. A fault/exhaustion or source mismatch requires investigation; do not silently drop the affected game. A 4-game package test confirms portability/loading only. No O bot, private boards, other members' bots or event submission is available in this task.
