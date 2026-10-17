# Complete project context — start here

Updated 17 October 2026. This is the entry point for all four members and any assisting model. The user authorized publication of all remaining project context across members: plans, research, frozen bots, handoffs, reviews, saved evaluations and verification evidence. This publication does not run games, alter bot logic, submit to the event or change the recommendation.

**Current recommendation: [B01 v004 agent.py](team-work/member-1/bots/B01/v004/agent.py), [submission ZIP](team-work/member-1/artifacts/B01-v004.zip).** v005 is an experiment, not the recommended replacement. On fresh matched boards v005 won 383/500 against F versus v004's 381/500, with an inconclusive difference and about 10% higher mean CPU. Read the [latest experiment](team-work/member-1/implementation/tempo-sprint/RESULTS.md) and the [earlier B01 final sprint](team-work/member-1/implementation/final-sprint/RESULTS.md). This is the current practical recommendation, not proof of superiority over every bot.

## Read in this order

1. [Working agreement and latest authorizations](AGENTS.md), [exact problem/rules](01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md), [local setup](02-LOCAL-SETUP-AND-VALIDATION.md).
2. [Research and dataset source catalogue](03-RESEARCH-AND-DATASET-CATALOGUE.md), [phase-wise plan](04-PHASE-WISE-PLAN.md), [Phase 1 verification](team-work/PHASE-1-COMPLETION-AND-VERIFICATION.md).
3. [Eight strategies and iteration plan](07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md), [team entry](team-work/README.md), [GLM startup instructions](team-work/GLM-START-PROMPT.md).
4. [Independent review and improvements](team-work/reviews/2026-10-17-B03-B08/README.md), then each round's plan, results, verification scope and Hyde review below.
5. [Current B01 recommendation evidence](team-work/member-1/implementation/tempo-sprint/RESULTS.md). Respect exact versions, opponent, board seeds and original run status when comparing any figures.

## All members and current source locations

| Owner | Bots and frozen sources | Research / improvement context |
|---|---|---|
| Aroosh, Member 1 | [B01 v004](team-work/member-1/bots/B01/v004/agent.py), [experimental v005](team-work/member-1/bots/B01/v005/agent.py), [B02 v002](team-work/member-1/bots/B02/v002/agent.py) | [Research](team-work/member-1/04-PHASE-1-FINDINGS.md), [round 2](team-work/member-1/implementation/round-2/BUILD-AND-RESULTS.md), [B01 upgrade handoff](team-work/member-1/B01-UPGRADE-HANDOFF.md) |
| Avadooth, Member 2 | [B03/B04 pinned branch snapshot](https://github.com/CodeAcc2007-dev/epochzero-hyde-hackathon/tree/954d2da93ded80bd98b7456aaa89968a6c7621f5/team-work/member-2) | [Assignment](team-work/member-2/03-PHASE-1-RESEARCH-BRIEF.md), [uploaded evidence audit](team-work/member-3/evaluations/common-F-20261017/member2-upload-audit.json) |
| Pranesh, Member 3 | [B05 v004](team-work/member-3/bots/B05/v004/agent.py), [B06 v004](team-work/member-3/bots/B06/v004/agent.py) | [Research](team-work/member-3/04-PHASE-1-FINDINGS.md), [round 2](team-work/member-3/implementation/round-2/BUILD-AND-RESULTS.md), [B05 handoff](team-work/member-3/B05-UPGRADE-HANDOFF.md) |
| Anni, Member 4 | [B07 v002](team-work/member-4/bots/B07/v002/agent.py), [B08 v002](team-work/member-4/bots/B08/v002/agent.py) | [Research](team-work/member-4/04-PHASE-1-FINDINGS.md), [round 2](team-work/member-4/implementation/round-2/BUILD-AND-RESULTS.md) |

Avadooth's existing work is already on GitHub in `member-2/avadooth-bots`; this publication links the audited commit and does not merge or rewrite that branch. His research has not been declared complete by the assistant. Frozen versions and manifests retain their identities.

## Additional evidence and historical status

- [Common-F evaluation stop record](team-work/member-3/evaluations/common-F-20261017/STOPPED-AND-RECOMMENDATION.md): preserves the user's stop instruction and distinguishes complete evidence from the interrupted B02 run. A target of 500 in metadata does not mean 500 games finished.
- [Uploaded agent versus B05](team-work/member-3/evaluations/upload-vs-B05-20261017/RESULTS.md): 280–220 in that direct matchup; [exact source snapshot and provenance](team-work/member-3/evaluations/upload-vs-B05-20261017/sources/README.md). It is a distinct upload, despite its internal B01 label, and this result does not compare it with B01 v004.
- [Earlier Member 1 upgrade context](team-work/member-1/09-ROUND-2-LOCAL-UPGRADES.md) and all round-2 directories contain plans, scripts, preserved development/source snapshots, raw game records and verification reports. They are included as historical evidence, not newly rerun checks.
- [Teammate upgrade prompts](team-work/member-1/implementation/final-sprint/TEAMMATE-PROMPTS.md) and [shared GLM instructions](team-work/GLM-START-PROMPT.md) remain available. Check the latest versions here before using an older handoff.

Older reports saying “local only,” “nothing published” or “publication pending” describe their original task state. This full-context publication supersedes those publication-status statements. It does not turn pending human review into approval, partial evaluations into completed runs, or historical hypotheses into established gains. No new simulations were run for this upload.

## Environment, datasets and next work

The [README environment section](README.md#reuse-an-existing-environment) explains reuse through `CATAN_PYTHON`, `CATAN_KIT_DIR` and `team-work/run-python.sh`; the repository does not ship an environment. Dataset source links, pinned revisions, checksums and limitations remain in the [catalogue](03-RESEARCH-AND-DATASET-CATALOGUE.md). Raw datasets, downloaded papers and row previews remain local, as requested.

Credentials, PATs, `.env`, installed dependencies, the organizer checkout, raw provider/session logs and local authentication helpers are excluded. No SSH or event portal action was performed. Later work must preserve frozen sources, use a new version for edits, and distinguish measured results from hypotheses. Default main evaluations are 500 games per bot when separately authorized; this upload is not authorization to launch more games.

[Publication audit and junior review](team-work/publications/2026-10-17-all-context/README.md).
