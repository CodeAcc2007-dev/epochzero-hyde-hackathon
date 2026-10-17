# Contract for the next GLM improvement round

17 October 2026. User: Pranesh, Member 3. This review now covers **B01–B08** after the user supplied B01/B02 during the review. It writes implementation handoffs and verification evidence; it does not replace any frozen bot. The owners' research findings and earlier superseded Member1 bots remain outside scope.

## What the receiving GLM should do

Read the owner's `08-GLM-IMPROVEMENT-CONTEXT.md`, this contract, the pinned parent source and its manifest, then implement the highest-priority correctness tickets first in a **new version**. B03/B04 next version is v003; B05/B06 next is v004; B01/B02 and B07/B08 next is v002, provided those directories do not already exist when you start. If they exist, inspect them and choose the next unused version. Preserve the parent and all original evidence. A hypothesis is an experiment, not an established improvement.

Work only in the assigned member folder. A shared defect may be fixed in independent owner copies; do not rewrite another member's frozen helper. Pranesh's B05/B06 share a core but remain distinct beam/threat policies; Anni's B07/B08 share utilities but remain belief/route policies. Member2 should preserve frontier versus port objectives rather than deliver two F copies with different names. The owner can consume a review without merging unrelated branches.

Use `./team-work/run-python.sh` and the existing `shared-local/` environment. The exact kit is `04fffac90e00610f60e0b06d919f262f4b3ed9db`; engine is `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Do not install another engine, patch F, duplicate the environment, run a runtime LLM, add network/process calls to the agent, or take SSH/event-portal actions.

Follow `AGENTS.md` and `team-work/JUNIOR-ENGINEER-WORKFLOW.md`: use the existing pinned Hyde GLM-5.3 Flash junior for bounded boilerplate/test drafting, with selected input copies and primary review. The Member2 remote branch also changes the shared junior runner for a different machine. That runner change was **not merged** here; do not replace the working local runner/provider as part of a bot improvement.

## Exact runtime semantics

- `Agent.decide(obs, playable_actions)` returns a genuine in-range integer referring to the **current** list. Never return a simulated action/index from a child state.
- Two players, ten VP, no peer trading. Own actual VP is known. The opponent's resources are public; opponent unplayed development identities/actual VP and future draws are not.
- The official harness masks the game **before** passing it to the worker (`catan_kit/match.py`, `Seat.decide`). Thus Member2's use of `obs._game` is not evidence of cheating or access to real hidden identities. It is still a hypothetical masked state and its deck order is not a forecast. Plain `Obs(real_game, color)` in a local test does not reproduce that masking; use `masked_copy` or an explicit counterfactual fixture when testing information use.
- `sample_world` is a consistent allocation mechanism, not a history-calibrated posterior. Reject already-terminal opposing worlds when using a nonterminal belief model. Do not let sampled opposing VP defeat a known own win.
- ROLL, BUY_DEVELOPMENT_CARD and robber theft cross chance boundaries. Either stop at the boundary with an explicit expectation/heuristic or enumerate feasible outcomes with weights. Never call a sampled favorable draw a guaranteed terminal line. Reordering candidate actions must not accidentally allocate different favorable random draws to them.
- Newly bought action cards cannot be played this turn; at most one action dev per turn. A Knight can win through Army before rolling/moving the robber. Strict Road/Army transfers and settlement-cut cases need the real engine's rules.
- Clock allowance is `min(0.300 + 0.0125 * decisions, 1.500)` seconds, with `obs.cpu_left` supplied. Budget incumbent selection, world construction, feature extraction and search together. Keep a cheap legal incumbent; check deadlines inside expensive loops. Internal fallback counters and harness counters measure different failures.

## Evidence and acceptance sequence

1. **Freeze input identity.** Record parent path, commit if available, SHA-256 of every runtime file, configuration and packaging. The review's `source-and-result-audit.json` supplies these eight parents. Verify hashes before using old results.
2. **Turn a verified finding into a new-version regression.** `verify_findings.py` deliberately asserts the old defects to reproduce them. A successful run means the findings were reproduced, **not** that new code is correct. Keep it untouched as parent evidence. Write new tests that load the new version and assert the desired corrected behavior; prove they expose the parent defect first.
3. **Run relevant existing tests and new semantic cases.** Existing 19 Member1 tests, 26 Member3 tests and 15 Member4 tests passed during review. They were insufficient to catch the new cases. New tests must target the actual frozen or packaged artifact, not only development helpers. Verify state/deck/piece/VP invariants, immutability, legal indices, both seats, low-clock behavior and chance/turn boundaries.
4. **Small correctness/profile checks.** Four to twenty clocked games per bot are for loading and fault diagnosis. Include at least one peer style. Diagnostic instrumentation belongs outside the competition artifact; record internal fallback, root coverage, cutoffs, nodes and useful changed decisions. Do not interpret a handful of wins as strength evidence.
5. **Main evaluation: 500 games per bot.** Use 250 paired boards versus unchanged F. For a proposed improvement, compare the new version and the frozen parent on the **same fresh development board group**, same global indices, same opponent bytes and same process lifecycle; report paired differences. A direct peer comparison or additional ablation is a separately labelled batch, not a substitute for the 500-game main run. Do not automatically start a giant tournament for every coefficient change.
6. **Freeze the revision before confirmation.** Used review boards (932000–932249), all historical published boards and all tuning boards are development evidence now. Proposed next namespaces: 933000–933249 for development and 934000–934249 reserved for confirmation. Check the team's latest ledger for collisions before starting; these are proposed, not executed/reserved globally by a scheduler. If confirmation changes the policy/selection, disclose it and allocate another fresh group.
7. **Deliver code, manifest, ZIP verification, tests, full per-game records, summary, CPU/fault counts and change log.** Record rejected variants and explain any cost/strength tradeoff. Human review and event scorer/private O validation remain separate.

Use board-pair clustered intervals and paired differences on matched boards. No-winner outcomes count as zero wins for both; do not discard them or faults. A small-sample or 0/100% bootstrap is not certainty. Local timings do not certify scorer hardware. Different board groups, machine load and process lifecycles mean historical F percentages do not form an eight-bot ranking.

## Reusable commands

From repository root, the main comparison driver is already available:

```bash
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py \
  --a team-work/member-2/bots/B03/v003/agent.py \
  --b shared-local/organizer-kit/examples/f_agent.py \
  --games 500 --seed0 933000 --chunk-size 20 \
  --out team-work/member-2/implementation/results/B03-v003-vs-F-dev-500
```

Adapt owner/bot/version and output directory. This is a **future example**, not evidence that v003 exists or passed. Re-run the parent with the same seeds, global indices and 20-game chunks into a different new directory. The driver refuses to overwrite existing output. A later-chunk single-game replay must retain the original global game index and preceding chunk lifecycle; setting only `--seed0` does not reproduce F's persistent RNG or the pair-key index.

## Required improvement ticket fields

Every change record must name: ticket ID, parent/new hashes, verified defect versus hypothesis, exact reproducer or reached decision, expected correction, tests actually executed, main batch IDs, internal/harness fault counts, CPU impact, remaining uncertainty, and owner review status. Keep credentials, raw provider sessions, environments and datasets out of Git. Never mark a strategy successful merely because its code executed or its heuristic score rose.
