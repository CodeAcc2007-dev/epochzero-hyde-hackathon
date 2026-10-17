# Uploaded agent versus B05 v004

17 October 2026. **Uploaded `agent (2).py` won 280–220 (56.0%) against B05 v004.** Prefer the uploaded agent for this tested matchup; B05 was faster. All 500 planned games completed, plus a separate four-game loading check, within the user's ten-minute limit. Main-match wall time: 202.4 seconds.

| Bot | Wins / games | Win rate | Mean CPU/game | Worst CPU/game | Recorded errors / timeouts / crashes | Clock overruns |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Uploaded agent | 280/500 | 56.0% | 183.56 ms | 790 ms | 0 / 0 / 0 | 0 |
| B05 v004 | 220/500 | 44.0% | 139.08 ms | 570 ms | 0 / 0 / 0 | 0 |

Uploaded agent wins by seat: **147/250 first (58.8%), 133/250 second (53.2%)**. B05: 103/250 first (41.2%), 117/250 second (46.8%). No draws/no-winner games and no harness random fallback moves. Uploaded mean CPU was 32.0% higher; timing is measured over the actual games and differing decision counts, not an isolated equal-decision microbenchmark.

Descriptive board-pair bootstrap 95% range for uploaded win rate: **51.8%–60.2%**. Resampling the 25 process-reset chunks gives **51.4%–60.4%**. These are local sample estimates, not a guarantee across opponents or event hardware. The more conservative independent-pair Hoeffding range is 47.4%–64.6%, including 50%. This result supports a practical preference here; it does not establish a new overall leaderboard.

## Exact tested sources

- Original uploaded file: `/home/CodeAcc2007/Downloads/agent (2).py`; unchanged snapshot under `shared-local/jobs/upload-vs-B05-20261017/source/agent.py`. SHA-256 `504f11305e1e9a7d1d3db456563a8ec32315fc84a2a675c190e2db7f7da8a868`.
- B05 frozen version: `team-work/member-3/bots/B05/v004/agent.py`. SHA-256 `8226e2c978cd6ec48fee2939dd4ccf021acb64e131b87bc71ddfcd29e0d05cbf`; matches its manifest. B05 was the second-ranked bot in the prior common-F evidence, so this interprets the user's wording as B05's current frozen v004, not an older B05 revision.
- The upload self-labels B01 v002, but neither bytes nor executable AST match any saved B01 version. No old B01 score is assigned to this upload.

## Method and evidence

500 direct games on 250 previously unused local boards **951000–951249**, each swapped across seats, global indices 0–499, ten VP, organizer public dice key and original cumulative CPU clock (300 ms + 12.5 ms per decision, max 1.5 seconds/game). Unchanged `match.play_chunk` and observation masking; existing shared environment through `team-work/run-python.sh`; sequential games with both agent processes reset every 20 games. This lifecycle differs from a single uninterrupted official CLI run. Kit commit `04fffac90e00610f60e0b06d919f262f4b3ed9db`; installed engine commit `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. No source tuning, implementation, external submissions or publication. No F-anchor rerun or extra tournament.

Separate loading check: four games on 950900–950901, 2–2, no faults/overruns. Excluded from main strength statistics. Primary independently recalculated counts and CPU, checked all board/seat pairs, verified source hashes after the run and byte-checked organizer harness files against the pinned checkout. Recorded zero harness faults does not certify every internal strategic choice.

[500 game records](main/games.json) · [summary and intervals](main/summary.json) · [exact commands and lifecycle](main/metadata.json) · [source inventory](source-inventory.json) · [source/harness audit](source-and-harness-audit.json) · [final verification](final-verification.json) · [Hyde job and primary review](HYDE-REVIEW.md). Local raw process/provider logs and source snapshots remain outside Git.
