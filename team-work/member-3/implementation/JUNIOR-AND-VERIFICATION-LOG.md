# Junior tasks and primary acceptance

17 October 2026. Hyde is a development assistant only; runtime bots make no model calls. No credentials, environment, full repository, raw dataset or unrelated member material was sent. Raw jobs/reasoning/events stay local, outside Git. Primary owns the strategy/core, experiments, acceptance and publication.

| Job | Actual output / time | Primary review and disposition |
|---|---|---|
| `20261017T072048Z-40e44b43` | `race_math.py`,26.703s, exit0, no tool errors. Raw SHA-256 `e9b43a4610714cd1b79954d6b070782e0c53e36f4efb1b0d8c8d8602c51a3b98` | Inspected every function against specified tuple costs, random-card probability and nonterminal10VP bound. **Accepted** without logic changes. can_afford/deficit/hidden_vp_cap are used by the bots; the extra expectation/break helpers are tested utilities. |
| `20261017T072449Z-6889fe8a` | `test_race_math.py`,63.983s, exit0, no tool errors. Raw SHA-256 `ce51e2b4df015ea378df0650ed6bcb0dfc9f73e01cb63efbfe201fefcc612f78` | **Accepted with edits**: primary made the enumeration oracle use its own explicit affordability comparison rather than the helper under test. Four unittest methods passed; enumeration covers243 hands ×2 costs. |

Both jobs pinned `hyde-inference/hyde/glm-5.3-flash`, three steps, timeout150/120s respectively. Numeric reported token counts are provider metadata; no monetary saving is inferred. No junior output was applied, executed or published automatically.

Primary validation: inspected engine/API and preserved exact pins; authored and ran semantic tests; checked full clocked game records and source fingerprints; retained failed/interrupted evidence honestly; checked standalone packaging and publication exclusions before upload. The report records actual final results after the experiment finishes; no model-authored claim substitutes for harness evidence.

One reporting-only command initially used system Python and could not import catanatron. It was rerun through the existing shared launcher; partial-run summary creation then succeeded. This was an administrative interpreter-selection error, not a bot/harness fault. No environment was installed or changed.
