# Aroosh — Member 1

The user explicitly authorized the primary assistant to build B01 and B02 after the original human implementation assignment. Both initial candidates are complete locally; human review and GitHub upload remain pending.

| Bot | Strategy | Standalone file | ZIP | Wins against F |
| --- | --- | --- | --- | --- |
| B01 v001 | Bottleneck economy | [agent.py](bots/B01/v001/agent.py) | [ZIP](artifacts/B01-v001.zip) | 381/500 (76.2%) |
| B02 v001 | City/dev engine | [agent.py](bots/B02/v001/agent.py) | [ZIP](artifacts/B02-v001.zip) | 359/500 (71.8%) |

Each completed 500 paired-seat games against unchanged organizer F with zero recorded errors, timeouts, crashes, clock overruns or harness random moves. B01 has the higher observed F score here; a direct B01/B02 clash has not been run. These results do not establish performance against other bots or private event scoring.

Read the [build and results report](implementation/BUILD-AND-RESULTS.md) for evidence, strategy decisions, exact sources, reproduction and limitations. [Design](implementation/DESIGN-AND-DECISIONS.md) and [Hyde review and verification](implementation/HYDE-AND-VERIFICATION.md) record the development decisions. Both ZIPs contain only the exact standalone frozen agent.py; use the existing supplied environment rather than copying it.

The seven user-supplied files in `earlier bots/` and the Phase 1 research were preserved. Their earlier evaluation remains separate. Preserve these frozen v001 versions; later changes need a new version and fresh confirmation boards. No SSH, portal submission or GitHub upload was performed during this build.

Original context: [research findings](04-PHASE-1-FINDINGS.md), [two-bot assignment](07-TWO-BOT-BUILD-ASSIGNMENT.md), [shared iteration plan](../../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md).
