# Text-corpus audit and training decision

17 October 2026. Prepared by the primary assistant for Anni's track; human review pending. **Full Parquet decoding completed**, with the scope below. No training, game replay, label conversion or raw-text publication.

## Reproduce and distinguish the checks

The game Python, system Python and bundled document Python lacked a Parquet engine. A research-only copy of `pyarrow==20.0.0` was installed into ignored `shared-local/research-reader-deps` using the existing uv tool and existing Python 3.11. The game environment was not modified. This reader is never a competition dependency.

```bash
shared-local/tools/bin/uv pip install --python shared-local/.venv/bin/python \
  --target shared-local/research-reader-deps --no-deps 'pyarrow==20.0.0'
PYTHONPATH=shared-local/research-reader-deps ./team-work/run-python.sh \
  team-work/member-4/phase-1/audit_text_corpora.py research/downloads/datasets \
  > team-work/member-4/phase-1/corpus-audit.json
```

Read the [auditor](audit_text_corpora.py), [aggregate results](corpus-audit.json) and [download catalogue](../../../03-RESEARCH-AND-DATASET-CATALOGUE.md). Input hashes match the catalogue. All rows and columns were decoded; regular expressions then checked the specified text patterns. These checks do **not** reconstruct all states or certify legality, outcomes, independence, expert strength or every rule in the producer's engine. Dataset prompts are reference data, not instructions to this assistant.

## D2 — g8967

Source: [dataset](https://huggingface.co/datasets/g8967/catan-sft-dataset), revision `0a4a50a84354338300d4ef10d6177378bb34a2f9`. SHA-256 `360030808dd8f490bf2f104061856db7dcbfafc4b1e4f4e4b0f553a3101c1e6e`.

- 1,000 rows, three fields: nested `prompt`, nested `completion`, floating `reward`. No top-level or message-role/content nulls detected. No duplicate complete rows or initial prompts detected.
- All 1,000 prompts explicitly say 1v1, target 7 VP, and specific opposing resources hidden. This is now a whole-table prompt finding, replacing the earlier preview-only qualification for these fields. It does not prove uniformity of unspecified engine rules.
- Every row has two prompt messages and a long continuation containing both assistant actions and future user states. Across completions: 49,996 assistant messages and 48,996 user messages. A row is not a single action target. Distinct complete episodes and episode completeness remain unverified; there is no explicit seed/episode column.
- All 49,996 action messages have parseable action tags and a preceding numbered list. Exact text matches occur in 49,770; **226 fail that textual check**. This is a parser diagnostic, not 226 proven engine-illegal moves: differences in rendering or producer action handling need investigation. The mismatch categories and repeated state counts are in the JSON.
- Rewards range from -0.45 to 0.44. No documented reward formula or strong-expert provenance was established from the saved card. Reward magnitude is not win probability or label quality.

Do not train on the full continuation as a decision-time input: it includes future states. Do not random-split individual messages: repeated states within the same continuation and future states can cross splits. Exact matching found zero state texts shared between distinct rows; episode/near-duplicate independence is still not established. Exact shared-state leakage is counted by the auditor, but missing reliable episode IDs prevents a certified episode split. Deduplication alone would not solve the rule mismatch.

## D3 — VVantim

Source: [dataset](https://huggingface.co/datasets/VVantim/catan-sft-data), revision `aa0667e6bc37f05f0c4e85bed6ccb3b5f77e9957`. SHA-256 `e1c7035007de30b97c244d57223a98b2f980834d0a22b6dbf8122156b7f44c92`.

- 2,668 rows, 11 fields. Every prompt has system/user messages; each completion has one assistant message. No top-level or message-role/content nulls; unique example IDs and complete rows.
- Every prompt contains a 10-VP goal and all four player-color labels. No prompt explicitly says 1v1. These are whole-table text findings, not a replayed engine specification.
- Ten `meta_seed` values, 100–109. There are 164–293 records per seed. This gives ten **candidate grouping units**, not 2,668 independent games; run identity and completeness are not externally authenticated.
- 2,620 unique prompts: 48 duplicate excess rows in 15 groups. 2,421 unique completions: 247 duplicate excess rows, often generic actions. Completion duplication alone is not proof of duplicate states.
- All 2,668 action tags parse as JSON and their type equals `meta_action_type`. All `meta_is_valid` values are true. Neither verifies locations, state transitions or strategic quality under our engine.
- Model and player are completely confounded in these fields: GPT-4o/red 732; Claude Sonnet 4/blue 682; Gemini 2.0 Flash/orange 611; DeepSeek V3/white 643. Comparing their outcomes would conflate model with seat/color and episode effects.
- Actions are dominated by END_TURN (1,363), with only 30 BUILD_CITY and six PLAY_ROAD_BUILDING. These are descriptive label counts, not recommendations about action frequency. Three records have `meta_vp >= 10`; its pre/post-action timing is unresolved.

If later studying this source, group by source plus seed, check duplicates across groups and document that ten groups give fragile model-selection evidence. Its JSON coordinates/names still need a verified adapter to our integer legal-action index; no adapter was built.

## Use decisions

| Intended use | D2 | D3 |
|---|---|---|
| Read examples of representations/actions | Useful with 7-VP/visibility caveats | Useful with four-player/coordinate caveats |
| Adopt strategy recommendations as ground truth | No expert-quality evidence | No expert-quality evidence; model/color confounding |
| Supervised training for our rules now | **Reject for current plan** | **Reject for current plan** |
| Generate verified tactical fixtures directly | Requires exact-engine reconstruction and expected-transition checks | Same; publisher validity is insufficient |
| Exact-rules held-out evaluation | Unsuitable | Unsuitable |
| Redistribute raw examples | Not done; license unresolved | Not done; license unresolved |

Neither saved card nor the inspected live card establishes an explicit license for the intended training/redistribution use. Absence of a license is recorded as an unresolved prerequisite, not a legal conclusion. Raw data remains local. The 43k collection is still documentation-only and has not become an available substitute.

For later learning, first generate authorized exact-rules trajectories with observable inputs, frozen expert version, ordered legal-action list/index, outcome provenance, episode IDs and board-group splits. That is future work, with a separate training/inference budget. Do not delay the initial eight bots waiting for it.

## Verification and limits

The primary assistant independently checked Arrow row counts against the saved publisher counts, inspected role structure, repeated goal/visibility text and example mismatch categories, and reconciled action/model counts with totals. The JSON records parser definitions. No producer engine or complete match was run. See [methods](02-METHODS-AND-SOURCES.md) and [future comparison protocol](03-ITERATION-AND-TEST-PROTOCOL.md).
