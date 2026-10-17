# Hyde contribution and verification record

The user explicitly authorized building Anni's B07/B08. Primary designed both strategies, bounded their work, implemented policy code and owns acceptance.

## Accepted bounded junior task

- Runner: existing `team-work/run-hyde-junior.py`; model `hyde-inference/hyde/glm-5.3-flash`.
- Job ID `20261017T090102Z-6a8f4a7b`; 3 steps, 120-second wall limit. Process exited normally in 83.573 s, no tool errors.
- Supplied only the pure-function contract, no repository contents, environment or credentials.
- Output `route_math.py`, SHA-256 `d9d31dde395ec2ec4a424d811b1c1094b3fabc4a5e54fb867263ea6b7fae05d6`, 2,171 bytes. Copied unchanged after primary review. Raw provider logs stay outside Git.
- Primary verified the exact integer reservation/trade/bank rules and capped mean-income projection; independently compared bank conversion with exhaustive reachable-trade search over 18,225 two-resource cases spanning 2:1/3:1/4:1 rates. All passed. Projection threshold and absent-bank checks also passed. Model-reported success alone was not acceptance.

## Semantic checks

`test_member4.py` currently passes 15 test methods, including the exhaustive helper oracle, constructed terminal/eligibility/conditional-Knight cases, chance-execution guard, sampled Monopoly effect, blocked/piece-limited plans, no-clock fallback and standalone entrypoint loading. Engine fixtures are explicit counterfactual states with conservation/piece/VP checks where applicable; they are not all complete reached game histories.

A newly added conditional-Knight fixture initially failed because its artificial enemy upgrades left the opposing HAS_ROLLED flag set. The forecast correctly refused that inconsistent turn boundary. The fixture was corrected to represent a completed prior enemy turn; no bot code was changed to bypass that guard. All 15 methods then passed.

The first B08 20-game development smoke completed 17 wins, zero recorded faults/fallback/exhaustion. This is loading/profile evidence, not a statistical strength claim. Its comparison was started while a fixture issue was still being diagnosed; semantic verification was resolved before source freezing or confirmation runs. B07 smoke and final frozen evidence are recorded separately in the build report.
