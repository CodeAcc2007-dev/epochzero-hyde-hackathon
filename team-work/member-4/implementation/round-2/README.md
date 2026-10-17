# Anni — round 2 complete

Locally verified candidates; human review and publication pending. [Full results](BUILD-AND-RESULTS.md), [plan](PLAN-AND-DECISIONS.md), [verification and remaining scope](VERIFICATION-AND-SCOPE.md), [Hyde review](HYDE-REVIEW.md).

| Bot | New / 500 vs F | Parent / 500 vs F |
| --- | ---: | ---: |
| B07 v002 | 369 | 369 |
| B08 v002 | 359 | 355 |

All runs recorded zero errors, timeouts, crashes, clock overruns and harness random moves. Win-rate improvement remains unestablished. Each candidate and parent played 500 games on the same fresh boards. B08 mean CPU fell about 12.3% for the whole revision; no isolated cache-only causal claim.

New-version regressions and adapted contracts: 54 methods passed across both members, with exhaustive helper cases embedded. All packages are verified single-file agents. Original parents remain preserved. No further bots, games or publication were performed after this round.
