# Aroosh B01/B02 v002: local upgrades and matched results

Completed 2026-10-17T16:11:10.054820+05:30 (India time). **Human verification pending; nothing published or submitted.** Frozen v001, earlier Member1 agents and research are preserved. Other members' frozen bot sources were not modified by this task.

Both bots now recognize the reproduced winning trade→Road sequence before strategic city-goal filtering and recognize immediate legal wins before the low-clock fallback. B01 retains its bottleneck economy policy and B02 its city/dev investment policy; no strategic coefficients, opening weights or search widths/depths were changed.

## Fresh frozen comparison

| Candidate | New vs unchanged F | Matched v001 vs F | Change [paired descriptive 95%] | Mean CPU new / parent | New p95 / max CPU |
| --- | --- | --- | --- | --- | --- |
| B01 v002 | 371/500 (74.2%) | 371/500 (74.2%) | +0.0 pp [+0.0, +0.0] | 215.3 / 215.0 ms | 390 / 710 ms |
| B02 v002 | 357/500 (71.4%) | 357/500 (71.4%) | +0.0 pp [-0.6, +0.6] | 193.6 / 194.9 ms | 340 / 450 ms |

All four 500-game runs recorded **zero errors, timeouts, crashes, clock overruns and harness random moves for both agents**. Every outcome was retained and the report independently recomputed wins, seats, CPU and fault counts from the individual records.

- **B01:** new win-rate descriptive range 70.8%–77.8%; first-seat wins 188/250, second 183/250. New-only wins 0; parent-only wins 0. No-winner counts new/parent 0/0. Difference reset-chunk sensitivity range [+0.0, +0.0] pp. [New records](main/B01-v002-new-vs-F-500/games.json), [matched parent records](main/B01-v001-parent-vs-F-500/games.json).
- **B02:** new win-rate descriptive range 67.2%–75.4%; first-seat wins 185/250, second 172/250. New-only wins 1; parent-only wins 1. No-winner counts new/parent 0/0. Difference reset-chunk sensitivity range [-0.6, +0.6] pp. [New records](main/B02-v002-new-vs-F-500/games.json), [matched parent records](main/B02-v001-parent-vs-F-500/games.json).

Both versions used the same 250 fresh boards **935000–935249**, swapped seats/global indices 0–499, ten VP and original cumulative clock: 300 ms + 12.5 ms/decision, maximum 1.5 s/game. Processes reload every twenty games, matching parent/candidate lifecycle; this differs from one uninterrupted official CLI run. F hash `72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613`. Kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`; engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Exact commands, source hashes, platform and lifecycle are in each metadata.json. [Hardware/harness audit](harness-and-hardware.json).

Two thousand main games = 500 per candidate + 500 per matched parent. Twelve ZIP/F/peer smoke games are separate. Two 100-action partial diagnostic histories did not finish games and are not pooled. No extra tournament, strategic ablation or event/private-O test. Source bytes were frozen before the first main game; this untouched first evaluation also serves as confirmation, and no tuning followed it.

Ranges resample the 250 board-pair win differences 2,000 times; the reset-chunk sensitivity range resamples 25 ten-pair process chunks. Both are descriptive and unadjusted across two candidates. If every observed paired difference is zero, the bootstrap collapses to [0, 0]; that does not prove equivalence or exclude unobserved rare differences. Time cutoffs, F persistent process RNG and a shared host affect replay/dependence. The preexisting Member3/4 evaluation was already running during early batches and was left untouched; timing is not an isolated hardware benchmark. Local F results on other groups are not an eight-bot ranking.

## Verification and accepted scope

- Fifteen new regression methods passed on frozen standalone files and again on exact ZIP-extracted modules. Nineteen original economic contracts passed against the new standalone classes, including the independent 18,225-case conversion oracle. The original parent nineteen also passed before repair; new regressions explicitly reproduce parent failures. [Semantic evidence](semantic-verification.json).
- New coverage includes both seats, reordered original action indices, immutable original and masked observations, low-clock city/settlement/Road/old-Knight wins, new-card eligibility, strict/owned Army, already-played dev, Road ties/longer rivals, bank/piece/blocking constraints, chance boundaries and an independent 96-fixture trade certificate oracle. These are constructed/counterfactual engine states, not claims of full reached histories. Full reached Road-cut/simultaneous-terminal acceptance remains open.
- Twelve complete forced-seven discard sequences had zero fixed-initial-goal oracle regret and no observed family switches, covering three hands and own/out-of-turn discards per bot. This bounded diagnostic does not establish globally optimal discards or justify new persistent memory. [Discard evidence](discard-diagnostics.json).
- The immediate selector copies at most twelve legal settlement/Road transitions, with cheap city/eligible Knight checks. Trade completion examines at most twelve relevant trades and forty-eight simulated actions, with a four millisecond deadline inside the existing budget. These caps leave cases unsearched; this is not exhaustive tactical search. Emergency timing excludes serialization/scorer hardware: [terminal profile](terminal-profile.json).
- Short external histories record internal counters/root coverage, but reached neither repair and observed no changed parent decisions. Main harness records do not expose per-decision internal cutoffs. Zero harness random moves is not a claim of zero internal fallback/cutoff decisions. [Diagnostics](diagnostics.json).
- Hyde GLM-5.3 Flash job `20261017T102336Z-a90a4d35` timed out after a read-permission/session error, produced no files and contributed no accepted revision. Primary completed and independently verified the tests. No provider switch or runtime LLM. [Exact job/review record](HYDE-REVIEW.md).

[Precommitted plan](PLAN-AND-DECISIONS.md), [ticket decisions and explicitly deferred hypotheses](VERIFICATION-AND-SCOPE.md), [source review](source-review.json). Broader multi-goal/re-export, city-payback and dev-stock tuning remain separate experiments; no gain is claimed for deferred work.

## Files and interpretation

- [B01 v002 agent](../../bots/B01/v002/agent.py), [manifest](../../bots/B01/v002/manifest.json), [ZIP](../../artifacts/B01-v002.zip).
- [B02 v002 agent](../../bots/B02/v002/agent.py), [manifest](../../bots/B02/v002/manifest.json), [ZIP](../../artifacts/B02-v002.zip).

Each ZIP contains only the exact standalone agent.py. CRC, hashes, development/frozen/extracted equality, clean loading, executable-AST assembly and actual extracted F smoke games passed. [Package checks](package-verification.json). Stdlib plus the pinned engine only; no key, data, environment, sibling module, network, worker or runtime logging.

- **B01:** A win-rate gain is not established by both descriptive ranges. v002 is a correctness-repaired review candidate; do not call it stronger.
- **B02:** A win-rate gain is not established by both descriptive ranges. v002 is a correctness-repaired review candidate; do not call it stronger.

Human acceptance remains pending. Do not overwrite either v001 or v002; future changes need a new version and fresh boards. No SSH, event portal action, automatic GitHub upload or publication occurred. [Preservation audit](preservation-verification.json) verifies original Member1 files and frozen runtime/research files while separately recording concurrent Member3/4 evidence/status and review-documentation updates by their existing work.

Reproduce through `./team-work/run-python.sh`; the main driver is `team-work/member-1/implementation/round-2/run_round.py --phase main`, which refuses existing outputs. New runs require new evidence paths/namespaces. `verify_semantics.py` checks both frozen and extracted forms; `audit_artifacts.py` and `write_results.py` recompute preservation/provenance and saved result validity. Keep raw provider sessions, dependencies and local logs out of Git.
