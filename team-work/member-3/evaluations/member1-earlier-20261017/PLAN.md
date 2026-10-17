# Member 1 earlier bots: independent evaluation plan

User request: evaluate the seven newly added earlier Member 1 bots. Primary owns evaluation and verification; no bot fixes, strategy tuning, SSH, or submission. All originals stay unchanged. Evaluation artifacts live in Member 3's folder.

## Frozen inputs and method

`source-inventory.json` records exact SHA-256 hashes and syntax checks. The entrants are the seven Python files under `team-work/member-1/earlier bots/`; their names are retained rather than assigning them B01/B02 identities. Default configuration only: unset `W` and `OPP` for greedy v3, meaning DEFAULT_WEIGHTS and opponent weight zero.

1. Run each entrant for 12 load/play diagnostic games, seeds 870000–870005.
2. Run each loadable entrant for 400 main games against unchanged organizer F, seeds 871000–871199, alternating starting seat on each board. Keep all losses and faults.
3. Run frozen B05/v003 and B06/v003 over the same 400 main games to provide contemporaneous reference results.
4. Use the existing official `match.play_chunk` through the existing comparison driver. Both agents reload every 20 games. Ten VP; original cumulative clock (300 ms + 12.5 ms/decision, maximum 1.5 s). Public local dice key; no scorer/private-key claim. Matches run sequentially in the existing shared environment.
5. Verify source hashes again after testing, preserve per-game records, and report all counters. No claim that 400 games proves a unique strongest bot. Pair bootstrap ranges are descriptive; process lifecycle and time-based search affect replay and independence.

This is comparison against F, not a round robin or private tournament evaluation. No bot is changed after inspecting these test boards. Further improvement/confirmation needs new versions and fresh boards.

## Source review notes to verify against outcomes

- Every supplied bot catches top-level exceptions and can return a legal random index. Harness zero-error/random-fallback counts therefore do not prove there were no internally caught exceptions or internal random choices. Report that limitation explicitly.
- `agent.py` and `agent_claude.py` use truncated-rollout UCT/MCTS, with actual configured rollout depths 1 and 6 respectively. Their running time controls the work completed, so seeded RNG alone does not guarantee identical decisions across hardware/runs.
- `agent_claude_greedy_v3.py` uses a one-world one-ply value scan without its own CPU deadline. Optional environmental configuration is fixed to defaults for these tests.
- `agent_sab.py` implements same-turn maximizing depth-two refinement; it stops at opponent turns rather than performing a conventional alternating alpha-beta search. Its predicted-root-cost guard can skip evaluation entirely at high branching. Claims in source comments that every root move is always evaluated are not guarantees.
- `agent_claude_greedy_v4.py` uses relative one-ply scoring and a bounded follow-up/opponent-reply stage. Root and continuation scan caps mean neither every root nor every opponent reply is guaranteed examined, and a continuation step cap can stop before turn end.
- `agent_modifiedf.py` is a hand-written feature-based heuristic, not a trained model. Its original performance/comment claims were not accepted as evidence.

## Hyde junior review

A bounded job supplies only the seven bot source files and asks for a mechanical inventory. It cannot run matches or change originals. Its output, status and primary review will be recorded separately; actual harness records remain the result evidence.
