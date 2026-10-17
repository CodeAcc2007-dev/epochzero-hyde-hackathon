# B08 v001 — Adaptive VP-route planning

Owner: Anni (Member 4). Built by the primary assistant at the user's explicit request.

**Use this folder's `agent.py` directly.** All helpers are included; only stdlib and the existing pinned organizer engine are required. No environment, credentials, weights, network calls or runtime LLM.

B08 adds a menu of city, short legal expansion, development, Army and verified short Road routes to a public-state evaluator. It reserves ingredients, trades only integer port/bank bundles and projects capped mean production. It uses own actual VP gap and excludes owned/unattainable bonuses and unavailable pieces. A bounded same-turn search can complete enabling trades. Resource timing is a heuristic, not a true expected hitting time or future-income guarantee; hidden draw risk and distant spatial plans remain approximate.

`manifest.json` records exact source/entrypoint hashes and executable-AST assembly verification. Preserve this frozen version. Package: `../../../artifacts/B08-v001.zip` contains only `agent.py`; the archive was CRC-checked and byte-compared to this entrypoint.

Main evaluation: 500 games against unchanged F on paired boards, original clock, 20-game process resets. Results and limitations are in [build report](../../../implementation/BUILD-AND-RESULTS.md); no private scorer or tournament guarantee. No SSH or portal submission.
