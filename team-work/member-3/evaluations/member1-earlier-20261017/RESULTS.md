# Member 1 earlier bots: independent evaluation results

Completed 2026-10-17T08:57:40.010193+00:00. Primary ran and verified all games. Originals preserved unchanged; no bot fixes, strategy tuning, SSH, event submission or GitHub upload performed in this evaluation.

## Results against organizer F

Each row is 400 main games on the same 200 boards (871000–871199), once from each seat. Member 1 rows are sorted by observed wins. B05/B06 were rerun on this exact set as references; these are not their previous 1,000-game results.

| Bot | Wins / 400 | Win rate | Descriptive paired bootstrap 95% range | Mean CPU/game | Worst CPU/game | Clock overruns | Errors / timeouts / crashes | Harness random moves |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: |
| [agent_claude_greedy_v4](main/agent_claude_greedy_v4/summary.json) | 208 | 52.00% | 47.25%–56.50% | 496.3 ms | 1230 ms | 0 | 0 / 0 / 0 | 0 |
| [agent_claude_greedy_v3](main/agent_claude_greedy_v3/summary.json) | 201 | 50.25% | 47.75%–52.75% | 131.6 ms | 280 ms | 0 | 0 / 0 / 0 | 0 |
| [agent_sab](main/agent_sab/summary.json) | 200 | 50.00% | 45.25%–54.75% | 171.3 ms | 430 ms | 0 | 0 / 0 / 0 | 0 |
| [agent_claude_greedy_v2](main/agent_claude_greedy_v2/summary.json) | 187 | 46.75% | 42.50%–51.00% | 205.4 ms | 490 ms | 0 | 0 / 0 / 0 | 0 |
| [agent](main/agent/summary.json) | 162 | 40.50% | 35.75%–45.25% | 321.9 ms | 660 ms | 0 | 0 / 0 / 0 | 0 |
| [agent_claude](main/agent_claude/summary.json) | 142 | 35.50% | 31.00%–39.75% | 310.6 ms | 790 ms | 0 | 0 / 0 / 0 | 0 |
| [agent_modifiedf](main/agent_modifiedf/summary.json) | 119 | 29.75% | 25.50%–33.75% | 85.1 ms | 190 ms | 0 | 0 / 0 / 0 | 0 |
| [B05](main/B05/summary.json) | 297 | 74.25% | 69.75%–78.50% | 158.4 ms | 500 ms | 0 | 0 / 0 / 0 | 0 |
| [B06](main/B06/summary.json) | 283 | 70.75% | 65.75%–75.00% | 97.3 ms | 250 ms | 0 | 0 / 0 / 0 | 0 |

F health: zero clock overruns, harness random fallback moves, errors, timeouts and crashes in all nine main comparisons.

Ranges are descriptive board-pair bootstrap intervals from 2,000 resamples. Timing and process-persistent RNG/adaptive estimates affect repeatability and independence; these are not a private-score guarantee or multiple-comparison-adjusted winner test. No-winner counts: agent=0, agent_claude=0, agent_claude_greedy_v2=0, agent_claude_greedy_v3=0, agent_claude_greedy_v4=0, agent_modifiedf=0, agent_sab=0, B05=0, B06=0.

## Interpretation and next review

Best observed Member 1 version on this set: **agent_claude_greedy_v4**, 208/400 (52.0%). This is selection on the evaluated boards, not independent confirmation. Preserve this exact source hash as an anchor; a revised candidate needs a new version and fresh confirmation boards.

The leading earlier versions' descriptive ranges include 50%; none establishes an advantage over F here. Retain greedy v3 as a cheap F-level control, and greedy v4 as an unconfirmed search candidate. Its observed gain over v3 is 1.75 percentage points for about 3.77 times the CPU. See [review for Aroosh](REVIEW-FOR-AROOSH.md) for evidence-linked follow-up points; no fixes were implemented.

F-relative results do not establish direct head-to-head results between candidates. No cross-bot round robin, private O test, event scoring or scorer-hardware timing was run. Use this table to choose which frozen versions merit the next independent round; no claim of final submission readiness.

All seven candidates swallow some exceptions and can return random legal moves. Thus zero harness errors/random moves does not prove every strategy decision succeeded. The separate diagnostic below measures some such events without contaminating the original-code main benchmark.

## Internal fallback diagnostics

Separate instrumented four-game checks per bot, boards 870500–870501. The original source is imported unchanged; an RNG proxy records calls from source-verified exception-return lines. These checks alter execution overhead and are not used for strength or timing ranking. Zero observed occurrences is limited to these checks. Raw stderr logs and wrappers remain under shared-local/.

| Bot | Diagnostic decisions | Observed caught-exception random fallbacks | Exception details |
| --- | ---: | ---: | --- |
| agent | 190 | 0 | None observed |
| agent_claude | 207 | 0 | None observed |
| agent_claude_greedy_v2 | 210 | 0 | None observed |
| agent_claude_greedy_v3 | 229 | 0 | None observed |
| agent_claude_greedy_v4 | 212 | 0 | None observed |
| agent_modifiedf | 164 | 0 | None observed |
| agent_sab | 165 | 0 | None observed |

All seven fallback detectors also passed an intentional positive control: a synthetic observation raises a known diagnostic RuntimeError and each detector records exactly one fallback. These injected probe exceptions are not actual game faults. Evidence: [fallback-detector-positive-control.json](fallback-detector-positive-control.json). No such fallbacks were observed in the separate four-game checks (1,377 decisions total); this does not prove absence across the main benchmark.

## Seat balance

| Bot | Wins when first / 200 | Wins when second / 200 |
| --- | ---: | ---: |
| agent_claude_greedy_v4 | 103 | 105 |
| agent_claude_greedy_v3 | 97 | 104 |
| agent_sab | 98 | 102 |
| agent_claude_greedy_v2 | 89 | 98 |
| agent | 78 | 84 |
| agent_claude | 74 | 68 |
| agent_modifiedf | 61 | 58 |
| B05 | 150 | 147 |
| B06 | 140 | 143 |

## Method, provenance and reproduction

- Existing shared Python environment; pinned organizer kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`, engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`.
- Unchanged `match.play_chunk`, `evaluate.summarise`, F and observation masking. Byte verification: [harness-verification.json](harness-verification.json). Ten VP, both clocks active: 300 ms + 12.5 ms per decision, maximum 1.5 s per game.
- Public local dice key. Agents receive masked observations. Both processes reload every 20 games with global indices retained; this differs from one uninterrupted official CLI run.
- Default candidate configuration: `W` and `OPP` unset. No optional CONTENDER/OPP sweep. No parallel matches. CPU is measured by the official harness; peak memory and event scorer hardware were not measured.
- Original filenames retained; no unsupported assignment of these earlier files to B01/B02. All source hashes rechecked after the batch and diagnostics. Every game's loss/fault/outcome retained.
- Seven 12-game smoke checks, nine 400-game main comparisons including B05/B06, and seven separate four-game diagnostics. Total retained games: 3,712.
- [Source inventory](source-inventory.json), [source review](SOURCE-REVIEW.md), [evaluation plan](PLAN.md), [batch status](batch-status.json), [internal fallback diagnostic records](internal-fallback-diagnostics.json), [Hyde junior review](HYDE-REVIEW.md). Hyde timed out with no accepted output; primary completed the review and verification.
- Main records: `main/<name>/games.json`, `summary.json`, `metadata.json`; smoke records: `smoke/<name>/`; diagnostic records: `diagnostics/<name>/`. Metadata includes commands, code hashes and lifecycle. Local process stdout/stderr logs are not publication artifacts.

Reproduction uses `python3 team-work/member-3/evaluations/member1-earlier-20261017/run_batch.py`. Existing output directories intentionally cannot be overwritten: copy the driver and source inventory into a new sibling evaluation directory before a repeat. Use fresh seeds for new confirmation; these boards are now seen. `run_diagnostics.py` runs the separate fallback check after batch completion.

No implementation changes were made to any supplied bot.
