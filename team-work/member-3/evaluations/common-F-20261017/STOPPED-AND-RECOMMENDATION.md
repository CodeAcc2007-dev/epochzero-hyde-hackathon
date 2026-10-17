# Stopped by user: current F recommendation

17 October 2026. User explicitly stopped further tests due to time limits. The evaluation driver and its worker descendants were terminated. No more tests, tournament, implementation or publication in this task.

B01 completed its common-board run before cancellation: **390/500 (78.0%)**, mean CPU 211.94 ms/game, with zero recorded candidate/F errors, timeouts, crashes, clock overruns or harness random moves. B02 had only 20 checkpointed games when stopped; the partial run and interrupted in-flight chunk are excluded from performance recommendations. Its earlier complete result is used instead.

Member 3/4 results were **reused unchanged**, never rerun here.

## Completed common-board results against unchanged F

| Candidate | Wins /500 | F win rate | Evidence |
| --- | ---: | ---: | --- |
| B01 v002 | 390 | 78.0% | Completed before stop |
| B05 v004 | 375 | 75.0% | Existing result reused |
| B07 v002 | 369 | 73.8% | Existing result reused |
| B08 v002 | 359 | 71.8% | Existing result reused |
| B06 v004 | 356 | 71.2% | Existing result reused |

These five use boards 934000–934249, swapped seats, unchanged F hash 72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613, ten VP, original cumulative clock and 20-game resets. This is observed F-score order, not proof of true strength or a direct peer result. No new significance or tournament testing after cancellation.

## Other completed evidence

- **B02 v002: 357/500 (71.4%)**, prior local run on 935000–935249. Different boards from the table; the interrupted run does not replace it.
- **B03 v003: 260/500 (52.0%)**, Avadooth's newer upload at 954d2da, boards 933000–933249, WSL machine. Audited source hashes/records; not replayed locally. This replaces the stale 42.8% v002 headline when discussing his latest version.
- **B04 v003: 216/500 (43.2%)**, same uploaded commit, boards 933500–933749; audited uploaded evidence, not replayed locally.

## Recommendation

**Prioritize B01, B05 and B07.** B01 has the highest observed F score; B05 is next; B07 is a fast alternative (about 125 ms/game in its saved run). Preserve B02/B06/B08 as alternative styles. Deprioritize B04. B03 improved to roughly F-level in the upload but remains less promising than the leading cohort; an interval including 50% does not prove equivalence with F.

This is a practical F-based shortlist, not final selection after peer clashes/private O. Different groups/machines and selection after viewing results limit inference. No extra tests will be run without a new instruction.

[Source index](source-index.json), [Member2 upload audit](member2-upload-audit.json), [stopped batch status](status.json), [completed B01 summary](results/B01-v002-vs-F-500/summary.json), [original plan](PLAN.md). The planned all-six common-board report was not completed because B02 was stopped. Its script is not a completed result. Partial records remain preserved without extrapolation.
