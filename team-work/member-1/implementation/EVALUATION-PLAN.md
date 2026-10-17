# B01/B02 frozen verification plan

Per the user's standing preference, main evaluation is **500 games per bot against unchanged F**. Both use fresh seeds 911000–911249, swapped seats, original 10-VP rules and cumulative clock. Preserve all outcomes. Both agent processes reload every 20 games, original global indices retained, using the existing comparison driver and shared environment. Run sequentially; no extra tournament or component-ablation matches.

Pre-freeze evidence: 19 semantic test methods, including an independent exhaustive reachable-trade oracle over 18,225 two-resource cases embedded in five-resource vectors. Separate 12-game development load/play checks per bot, seeds 901000–901005, excluded from main win rates. Do not infer strength or tune weights from those tiny checks.

Freeze standalone v001 after correctness/loading verification, record source and assembly hashes, then run main tests without edits. Any later fix needs a new version and fresh confirmation boards. No component benefit, direct B01/B02 head-to-head, old-bot ranking, private O or scorer-machine timing may be inferred from F results alone. Matched component tests are deferred under the reduced budget. No SSH, training, environment copy, publishing or portal action.

The official public local dice key is used. Pair-bootstrap ranges are descriptive because time cutoffs and process-persistent F RNG can affect replay/dependence. Keep original metadata, every game, faults and no-winner losses. Preserve earlier Member 1 sources/research unchanged.
