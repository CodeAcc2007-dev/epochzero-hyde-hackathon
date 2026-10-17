# Member 3: exact-source semantic audit

Date: **17 October 2026 (IST)**. Research owner: **Pranesh**. Primary-assistant source review; Hyde performed bounded extraction, not final interpretation. Status: **source-verified findings, awaiting user and Avadooth review**.

No game was constructed or played, no benchmark run, and no bot implemented. **SOURCE** means inspected branch/call-path behavior; **DERIVATION** means reasoning from it; **RISK** means a source-level issue whose reachable runtime manifestation has not been demonstrated. Source review does not establish tactical win-rate improvement.

## Revisions and source map

Engine: `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`. Kit: `04fffac90e00610f60e0b06d919f262f4b3ed9db`. The installation's `direct_url.json` identifies this engine revision. File hashes and remote-comparison outcomes are in [source-verification.json](source-verification.json). Source line numbers below refer to those files, not Hyde's generated prose.

| ID | Pinned source | Functions inspected |
|---|---|---|
| G | [game.py](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/game.py) | `play`, `execute`, `winning_color`, constructor defaults |
| A | [models/actions.py](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/models/actions.py) | Action generation, build/dev/trade/robber/discard possibilities |
| X | [apply_action.py](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/apply_action.py) | Dispatch and state transitions; purchases, rolls, discards, card effects, payouts |
| S | [state_functions.py](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/state_functions.py) | Resource/VP mutations, dev eligibility/cleanup, Army/Road scoring |
| B | [models/board.py](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/models/board.py) | Build legality, route traversal, extension/interruption ownership |
| V | [players/value.py](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/players/value.py) | F heuristic and factory |
| O | [kit obs.py](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/obs.py) | Visible fields, `sample_world`, `masked_copy` |
| M | [kit match.py](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/match.py) | Masked view, action-index validation, clock, `play_game` |
| P | [kit patches](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/_patch.py) | Deterministic maritime offers and protected feature-order RNG |

The inspected kit patches do not repair the Road or masking issues discussed below. Do not change the installed engine to resolve them during research.

## Semantic findings

| ID / topic | SOURCE finding and exact call path | Observable inputs / caveat | Counterexample to a naive rule |
|---|---|---|---|
| S01: actual win | G `winning_color` L197–212 compares every player's actual VP with the target; G `play` L132–151 checks for a winner between ticks. It does not restrict the winner to the turn owner. M L337–352 uses that loop. | Our actual VP is visible; sampled opponent actual VP is hypothetical. Multiple simultaneous qualifying players are resolved by the last qualifying color in iteration, not a separately specified tie rule. | “Public VP alone determines every win” ignores our known VP cards. |
| S02: VP purchase | X L236–257 buys a shuffled-deck card; S `buy_dev_card` L259–272 immediately adds one actual VP for a VP card. No explicit VP-card play action exists in A L56–89. | The draw is uncertain beforehand unless public card-count constraints determine it. Own actual VP updates when it happens. | “A bought VP must wait until next turn” is false. “Buying a card certainly wins at 9 VP” is also false. |
| S03: city | S `build_city` L196–208 adds **one** public and actual VP, spends 2 wheat/3 ore, returns a settlement piece. A `city_possibilities` L191–205 requires an owned settlement, resources and an available city. | Resource affordability alone is insufficient. | Four deployed cities leave no city piece even with the full resource cost. |
| S04: old dev / limit | S `player_can_play_dev` L232–238 requires a held card, type's owned-at-start flag and no dev already played this turn. S `play_dev_card` L327–335 consumes the card, sets the turn flag and increments its cumulative played count. | Current legal list is the final authority for our eligibility. | Knight → Year of Plenty on the same turn violates the shared dev-play limit. |
| S05: reset timing | X `apply_end_turn` L128–132 calls S `player_clean_turn` L338–354, then advances. Cleanup resets rolled/dev-play flags and marks held playable-dev types available for the owner's next turn. Cumulative played counts are **not** reset. | Newly bought action devs cannot be used immediately when no old card of that type was owned. | A new Knight cannot immediately complete Army; an existing old Knight remains a separate opportunity. |
| S06: pre-roll | A `generate_playable_actions` L56–89 offers eligible action devs before and after rolling. Before roll, ordinary buys/builds/trades/end-turn are absent; after roll those actions are considered. | Prompt, rolled flag, dev timing and current legal actions matter. | Pre-roll YOP → immediate city is illegal: a roll must intervene. |
| S07: Knight/Army | X L363–371 calls S `play_dev_card`; Army is updated inside S L47–69/L327–335 **before** the robber follow-up. First Army needs 3 played Knights; a different holder loses it only to a strictly larger played count. Transfer is +2/−2 VP. | Played Knights are public. An unplayed opponent Knight remains uncertain. | Three cards in hand are not three played Knights; tying a holder does not take Army. |
| S08: seven/discard | X `apply_roll` L268–290 fixes each discard quota as `floor(cards/2)` only above the configured limit (default 7 in G). X L306–341 removes one selected resource per action, processes discarders in color-index order, then returns control to the roller for robber movement. | Being asked to discard does not mean it is our turn. Quota is fixed for the phase, not recalculated after each card. | Holding eight cards requires four discards, not repeatedly halving the shrinking hand. |
| S09: robber | A L222–249 excludes the current robber tile and self-steal; a victim must have a neighboring building and resources. If an eligible victim exists, the generated action steals from it. X L344–360 steals one uniformly selected **card**, moves the robber, returns to PLAY_TURN. S L322–324 implements the random selection. | Exact opposing hand gives the steal distribution. It is deterministic in type if all victim cards are the same resource. Own adjacent production may also be blocked. | A high-pip tile occupied by both players may hurt us; the stolen type is not generally our choice. |
| S10: YOP | A L124–144 permits bank-supported pairs and, when a pair cannot be supplied, available single-card options. X L374–386 validates bank stock, transfers cards and consumes the dev. | Never manufacture missing bank resources; selected action tuple may have one card. | “YOP always gives exactly two cards” is unsafe under shortages. |
| S11: Monopoly | X L389–407 transfers every opposing card of the selected resource, consumes the dev and leaves bank stock unchanged. A L120–121 offers the resource choices. | In 1v1 the immediate amount is the exact visible opposing count; later rolls/interventions can still matter. | Maximizing stolen quantity need not enable the winning purchase; zero available cards can make a legal choice worthless. |
| S12: Road Building | X L410–420 activates up to two free road placements. A L57–58 then offers only free roads. X L197–211 leaves that subphase after two roads or no legal road remains. Each road can change VP before the next loop check. | Cannot voluntarily interleave a settlement between its first and second roads while the second remains legal. | Activation → first road → settlement is not generally the legal action sequence. |
| S13: maritime | A L314–340 uses 4:1, generic port 3:1, matching resource port 2:1; requested resource must be in bank. X L423–438 transfers offered cards back to bank and the requested card to hand. | Post-roll only in ordinary PLAY_TURN. Engine tuples are padded; select a legal index later. | A supposed winning trade is unavailable if the bank has no requested card. |
| S14: route calculation | B L192–236 takes Road on normal extension only at length ≥5 and strictly above the incumbent record. B L355–385 traverses friendly roads without reusing an edge and blocks entry through an enemy node. Road is not total edge count. | Vertex revisits are not expressly forbidden; branching/loop/cut cases need exact-engine validation later. B stores both edge directions. | Counting the road dictionary doubles physical edges and ignores continuity. |
| S15: bank payout | X `yield_resources` L550–585 skips the robber tile, awards 1/2 per settlement/city, and suppresses an entire resource payout if total demand exceeds bank stock. | This engine branch is authoritative for forward resource forecasts. | Standard-rule assumptions about partial payment to a sole claimant may not match this branch. |

## Two high-priority source-level risks

### R1 — Longest Road after a settlement cut

B `build_settlement` L113–145 recomputes a cut opponent component and chooses the maximum road-length entry. Unlike normal road extension, that branch does **not** enforce the five-road threshold and does not explicitly preserve an incumbent on equal lengths. S `maintain_longest_road` L26–44 awards/transfers the two points whenever the returned color changes; it returns without removing points if the returned color is `None`.

**Verified:** those guards are absent in the inspected paths. **Not demonstrated:** a legally reached game history producing a specific wrong award, every tie/cycle topology, or an exploitable sequence. Later fixtures should cover a cut dropping both players below five, a cut producing a tie, and consistency of board owner/length versus VP flags. Until then, no strategy should promise a textbook cut-and-transfer outcome. This is a compatibility risk to hand to Avadooth/Anni, not an instruction to modify the engine.

### R2 — A masked world can contradict the ongoing-game evidence

O `masked_copy` L96–113 uniformly redistributes unseen dev cards and sets opposing actual VP to public VP plus the sampled VP cards. It does not reject a sample that already gives the opponent 10 VP. G `play` checks for a winner before the next actual decision. Therefore, in a real ongoing 10-VP game, opposing hidden VP must satisfy `hidden ≤ 9 − opposing_public`, while a sample can violate it.

This is a **source-derived consistency issue**, not hidden truth exposed by the sampler. A sampled winning opponent can distort a terminal check on that sampled world. A later design should distinguish our exact current actual VP and the current legal list from a sampled opponent's fictional actual VP. Probability assumptions and a toy calculation appear in [the threat analysis](03-THREATS-VP-RACES-AND-HYPOTHESES.md). No sampler or bot was changed.

O also fills opponent owned-at-start fields from sampled hand counts. Treat those as hypothetical eligibility metadata, especially for within-turn reasoning; do not reconstruct real opponent purchase identities from them.

## F-specific observations

The [kit F adapter](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/examples/f_agent.py) scores one executed action in one sampled world. V `base_fn` L57–119 rewards public VP and other visible features, but does not explicitly check actual VP or a terminal winner. This does **not** establish that F misses every immediate win: many winning actions also receive large public-VP rewards. V `get_value_fn` L186–192 ignores passed custom weights for `base_fn`; a later tuning comparison must verify actual parameter use.

## Literature source cards: supporting ideas, not rules authority

- **Guhe & Lascarides (2014), §III**, [primary paper](https://www.pure.ed.ac.uk/ws/portalfiles/portal/19351482/CIG2014_GS.pdf), physical PDF p4 visually checked: describes build plans and estimated build/win times rather than isolated road purchases. Its experiments use four agents and player trading. **Transfer:** motivates competing sequence hypotheses; supplies no result against our F/O or clock. No human raw corpus was acquired here.
- **Driss & Cazenave, Deep Catan, §2.3**, [primary paper](https://www.lamsade.dauphine.fr/~cazenave/papers/DeepCatanEvo.pdf), physical PDF p3 visually checked: four-player imperfect-information setting, refusing peer trades. Its displayed city recipe uses one grain, which disagrees with our pinned two-wheat cost; we did not inspect their implementation to explain it. **Transfer:** method reference only, not a recipe/rule authority or 1v1 timing validation.

Only the relevant planning/rules passages were reviewed for these cards, not every paper result. No published win rate was recomputed. The [earlier catalogue](../../../03-RESEARCH-AND-DATASET-CATALOGUE.md) retains the broader bibliography and dataset limits.
