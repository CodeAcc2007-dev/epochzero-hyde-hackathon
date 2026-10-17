# B07 v001 — Sampled-opponent planning

Owner: Anni (Member 4). Built by the primary assistant at the user's explicit request.

**Use this folder's `agent.py` directly.** All helpers are included; only stdlib and the existing pinned organizer engine are required. No environment, credentials, weights, network calls or runtime LLM.

B07 starts with a visible incumbent, then may compare three roots across three accepted hypothetical hidden-dev worlds (at most twelve rejection attempts). It rejects already-terminal opponent samples, forecasts one deterministic own follow-up and voluntary end, then examines capped pre-roll dev replies. All currently held opposing cards are eligible only in that forecasted NEW turn. It stops before dice, buy draws and random steals; selected steals use exact conditional expectations. Incomplete common-world comparisons return the incumbent. This is a bounded risk model, not exhaustive minimax or a calibrated posterior.

`manifest.json` records exact source/entrypoint hashes and executable-AST assembly verification. Preserve this frozen version. Package: `../../../artifacts/B07-v001.zip` contains only `agent.py`; the archive was CRC-checked and byte-compared to this entrypoint.

Main evaluation: 500 games against unchanged F on paired boards, original clock, 20-game process resets. Results and limitations are in [build report](../../../implementation/BUILD-AND-RESULTS.md); no private scorer or tournament guarantee. No SSH or portal submission.
