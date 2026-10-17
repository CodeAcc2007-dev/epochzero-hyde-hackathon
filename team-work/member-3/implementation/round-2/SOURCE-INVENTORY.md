# Round-2 Source Inventory: `ACTUAL_VICTORY_POINTS` access, chance boundaries, explicit limits

Mechanical extraction for senior review only. Comments/docstrings are treated as claims, not proof; no correctness, tuning, or design claims are made. No environment, config, or credentials supplied or requested. Inputs read: `terminal_math.py` (50 lines), `member3_core.py` (413), `member4_policies.py` (448).

## A. Functions accessing an `ACTUAL_VICTORY_POINTS` field

Binding legend — **own**: deciding agent's own field on `obs._game`, a copy, or its sampled world; **model-sampled**: opposing player's field on an `obs.sample_world` copy, not treated here as real hidden information; **implicit**: whole-state dump that contains the field.

| # | File : function (line) | Exact key expression | Use | Binding (visible path) |
|---|---|---|---|---|
| 1 | `terminal_math.py` : `public_terminal` (L11) | `ps[k+'_ACTUAL_VICTORY_POINTS'] < g.vps_to_win`, `k='P'+str(g.state.color_to_index[me])` (L8) | terminal win guard on a copied child | own — sole caller `terminal_action` passes `child, obs.me` (L46) |
| 2 | `member3_core.py` : `Context.value` (L161) | `actual = ps[self.key+'_ACTUAL_VICTORY_POINTS']`; `self.key = 'P' + str(st.color_to_index[me])` (`__init__` L45) | win guard (L162) and score term `40.0*actual` (L185) | own — constructed as `Context(world, obs.me, …)` (L287) |
| 3 | `member3_core.py` : `Context.buy_value` (L232) | `ps[self.key+'_ACTUAL_VICTORY_POINTS'] == g.vps_to_win-1` | selects VP-card value `vp = WIN-self.value(g) … else 40.0` | own — reached via `action_value` (L240) |
| 4 | `member3_core.py` : `Policy.decide` (L320) | `child.state.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS'] < child.vps_to_win` | gate for beam enabler scan | own — `ctx.key` from `Context(world, obs.me, …)` |
| 5 | `member3_core.py` : `Policy.decide` (L350) | `st.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS'] >= g.vps_to_win` | beam-node skip guard | own |
| 6 | `member3_core.py` : `Policy.decide` (L366) | `child.state.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS'] < child.vps_to_win` | frontier admission/dedup gate | own |
| 7 | `member3_core.py` : `state_key` (L255) | `tuple(sorted(st.player_state.items()))` | search fingerprint | implicit — contains every player's `…_ACTUAL_VICTORY_POINTS` item, including the sampled opponent's |
| 8 | `member4_policies.py` : `RouteContext.potential` (L142) | `g.vps_to_win-g.state.player_state[self.key+'_ACTUAL_VICTORY_POINTS']` | gap term in plan scoring | own — `RouteContext(world, obs.me, …)` (L195) |
| 9 | `member4_policies.py` : `Member4Policy.valid_belief` (L270) | `g.state.player_state[k+'_ACTUAL_VICTORY_POINTS'] < g.vps_to_win`, `k='P'+str(g.state.color_to_index[enemy])` | filters sampled worlds | model-sampled — worlds from `obs.sample_world(rng)` (L278) |
| 10 | `member4_policies.py` : `Member4Policy.opponent_reply` (L378) | `child.state.player_state[ctx.ekey+'_ACTUAL_VICTORY_POINTS'] >= child.vps_to_win` | sampled-reply loss penalty `baseline-180.0` | model-sampled — belief world from `sample_beliefs` |
| 11 | `member4_policies.py` : `Member4Policy.opponent_reply` (L410) | `child.state.player_state[ctx.ekey+'_ACTUAL_VICTORY_POINTS']>=child.vps_to_win` (road-building branch) | same penalty path | model-sampled |

- Indirect own reads via `obs.my_actual_vps`: `terminal_action` (terminal_math L28), `Policy.decide` (member3 L290, L318), `Member4Policy.decide` (member4 L217). Underlying key not visible (obs wrapper unsupplied).
- Distinct public field `_VICTORY_POINTS` (e.g. `ps[ek+'_VICTORY_POINTS']` terminal_math L13; `ps[self.ekey+'_VICTORY_POINTS']` member3 L173) is outside Table A.
- Adjacent claims, quoted not verified: member3 L164-166 "Use only public increases plus a real-nonterminal hidden-VP bound, / never the sampled opponent ACTUAL_VICTORY_POINTS field."; member3 L4-5 "sampled opponent VP/dev identities … deliberately never evaluated"; member4 L3 "All hidden identities below are conditional model samples."

## B. Chance-execution boundaries in `action_value` / search

`member3_core.Context.action_value` (L236-249); module docstring of `terminal_math.py` L1 claims "no sampled identities or chance execution" (claim only):
- `AT.ROLL` → `return self.value(g), None`: pre-roll value; no roll outcomes expanded.
- `AT.BUY_DEVELOPMENT_CARD` → `buy_value(g)`; comment L225 "Do not inspect/execute the sampled deck order. Value all publicly feasible draw types." Draw valued via `self.draw_probs` (L233) from `_draw_probabilities`.
- `AT.MOVE_ROBBER` → `robber_value`: expectation weighted by `hand(g.state,self.ekey)` counts; steal identity not executed.
- Default → `child = g.copy(); child.execute(action)` (L243-244); if `child.state.current_prompt == AP.MOVE_ROBBER` on own turn, value is `max((self.robber_value(child,a) …))` — comment L248 "Exact one-steal expectation; no sampled continuation."
- Search guards: `Policy.decide` skips non-ROLL/non-Knight actions when a ROLL is present (L311-313, "Do not simulate a lucky roll."); beam loop expands only `DETERMINISTIC` actions (L354-355) at own-turn `AP.PLAY_TURN` nodes with unchanged `num_turns` (L350); comment L254 "No chance branches/deck draws are expanded."
- `terminal_action` executes only BUILD_SETTLEMENT/BUILD_ROAD children (L42-48).

`member4_policies.py`:
- Root loop skips non-ROLL/non-Knight when `has_roll` (L211-212).
- `forecast_end` (L285-322): copies world, executes root action, at most one greedy `SAFE` follow-up, then `g.execute(stop)` (END_TURN); then prepares an opponent turn by overwriting `ctx.ekey+'_'+d+'_OWNED_AT_START'` from sampled `_IN_HAND` (L319), clearing `_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN` (L320), `generate_playable_actions(g.state)` (L321). Boundary: stops before any opponent roll/draw executes.
- `opponent_reply`: only KNIGHT/MONOPOLY/ROAD_BUILDING/YEAR_OF_PLENTY replies (L372-373); MOVE_ROBBER → `min` over ≤6 moves via `enemy_robber_value` (L389-393); road-building → 2-step greedy loop (L395-409). No dice/deck execution.
- `sample_beliefs`: `obs.sample_world(rng)` with fixed `random.Random(17)` (L274-278) — belief-world sampling boundary.
- Gap: member4's `ctx.action_value`/`ctx.value` resolve to `public_context.Context` (unsupplied); boundaries above are from `member3_core` only.

## C. Explicit limits

| Kind | Location | Exact expression |
|---|---|---|
| terminal copy | `terminal_action` | `if copies>=12:break` (L49); plus `if gap>3: return None` (L29-30); `BUILD_ROAD and gap>2:continue` (L44) |
| terminal copy | member3 enabler loop | `terminal = child.copy(); terminal.execute(completion)` (L324-325) — deadline-checked (L322), no copy-count cap |
| terminal copy | member4 completion loop | `end = child.copy();end.execute(completion)` (L220) — no deadline or count cap inside |
| root | member3 beam | frontier `[:5]` (L372); `reserve_enablers` `chosen=candidates[:3]`, `len(chosen)<5` (L398-406) |
| node | member3 beam | `for depth in range(2,5)` (L343); `expanded>=80` (L346, L356); per-node children `[:5]` (L371) |
| root | member4 `route_search` | depths `(2,3)` (L238); frontier `[:3]` (L235, L263) |
| node | member4 `route_search` | `count >= 42` (L244, L256) |
| root | member4 `belief_search` | eligible `[:3]` (L422) |
| reply/world | member4 `sample_beliefs` | `for _ in range(12)` (L275); `if len(worlds)==3: return` (L281) |
| reply | member4 `reply_shortlist` | `if len(selected)==8:return selected` (L366) |
| reply | member4 `opponent_reply` | robber moves `[:6]` (L389); road moves `[:6]` (L397); `for _ in range(2)` (L395) |
| follow-up | member4 `forecast_end` | `sorted(g.playable_actions,key=action_order)[:12]` (L298) |
| node | member4 `road_steps` | `examined >= 28` (L95-104); beam `[:4]` (L108); depth `min(2, …)+1` (L90) |
| time | member3 budget | `cap = .022 if self.mode == 'beam' else .016`; `budget = … max(0.0,min(cap,.22*allowance))` (L277-278); `budget < .001` bail (L284); root deadline break (L307) |
| time | member4 budget | `cap = .024 if self.mode == 'belief' else .022` (L186); `root_deadline = min(deadline,start+.011)` (L205); `budget < .001` bail (L191) |
| cache | member4 `potential_cache` | `if len(self.potential_cache)>=128:self.potential_cache.clear()` (L157) — 128 entries, clear-on-full |
| cache | member3 `Context.features` (L118); member4 `RouteContext.geometry` (L72, L109) | signature-keyed; no size cap or eviction (per-decision lifetime) |
| dedup | `seen` sets (member3 L341; member4 L237) | unbounded within a decision; bounded in practice only by node caps above |

Loops without an explicit node bound:
- member3 `Policy.decide` L289-294 knight shortcut: iterates all `actions`; no deadline or count cap inside.
- member4 `Member4Policy.decide` L218-222 win-completion loop over `child.playable_actions`: no deadline or count cap inside (outer loop has `root_deadline` only).
- `Context.board_features` frontier expansion (member3 L102-113) and `RouteContext.spatial_plans` (member4 L58-71): iterate `STATIC_GRAPH.neighbors` over a growing frontier; bounded only by board size, no numeric cap.

Counters are instrumentation, not limits: member3 `search_nodes`, `roots_examined`, `cutoffs`; member4 `nodes`, `reply_nodes`, `sample_attempts`, `valid_samples`, `reply_comparisons`, `reply_changes`, `cache_hits`/`cache_misses`, `estimate_calls`.

## Gaps (not supplied, so not inventoried)
- `race_math.py` (`hidden_vp_cap`, `can_afford`, `deficit`), `round2_math.py` (`one_trade_build`, `knight_wait_rolls`), `public_context.py`, obs wrapper (`sample_world`, `my_actual_vps`, `cpu_left`, `opp_public_vps`, `opp_dev_count`, `my_devs`), engine (`Game.copy`/`execute`, `vps_to_win`, `state.*` semantics, `development_listdeck`).
- `public_context.Context` vs `member3_core.Context` identity assumed from imports only (member4 L13-16); not verifiable from supplied files.
- Whether any unsupplied helper reads `ACTUAL_VICTORY_POINTS` (e.g. inside `hidden_vp_cap` inputs) cannot be checked from these sources.

## Senior verification and corrections

Primary checked the inventory against actual sources and the installed organizer/engine. The statement that gaps were unsupplied is a limitation of this junior task, not a missing primary verification: Obs and masked_copy, race/round2 helpers, public_context, Game.execute/winning_color and manifests were independently inspected and exercised by tests. Member4's imported public_context is the preserved original utility (SHA-2563de5bd723eb36988f347399b9a50ed5680c6e5e12effad5ddddfe741145dc3c3), not Member3's newly extended conversion-threat Context.

One table-A omission is corrected: Member4Policy.route_search also fingerprints tuple(sorted(child.state.player_state.items())), which includes the masked opponent's hypothetical actual VP. Like Member3's state_key, it is a per-search deduplication key; it is not a known-truth opponent score. Explicit opposing actual-VP comparisons occur only in valid sampled-belief/reply paths, where they are conditional model outcomes. Own terminal certification uses public opponent VP/nonterminal bounds, not that sampled score.

The retained Member4 short-completion loop has no inner time check; its finite building-action list and outer root deadline are soft rather than a hard deadline. The broader copied geometry loops are bounded by the finite board. This is documented as a retained limit; do not claim every inner operation has a hard CPU bound. No source change was made during the frozen comparison. This inventory supplies code-navigation evidence, not a passed test, proof of exhaustive coverage or strength result.
