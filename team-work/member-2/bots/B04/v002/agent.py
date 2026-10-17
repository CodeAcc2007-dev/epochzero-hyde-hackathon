"""B04 v002 - Port specialization.

Owner: Avadooth (Member 2). Assignment: team-work/member-2/07-TWO-BOT-BUILD-ASSIGNMENT.md.
Supersedes v001 (bots/B04/v001), which lost to unchanged F on screen batches
(18/80, see bots/REPORT.md). Same root cause and fix as B03 v002: F's own
ValueFunctionPlayer (catanatron.players.value) scores every legal action by actually
executing a copy of the game and evaluating the RESULTING state with base_fn (lexicographic
VP, then production, then enemy-denied production, then reachable production/buildable
nodes/hand synergy/dev cards/army size). v001 approximated this with static current-state
heuristics and a hand-rolled "surplus justifies the port" rule that never saw the real
resultant state (e.g. a trade's effect on hand_synergy, or a port settlement's effect on
reachable_production). v002 runs the same real one-ply simulation F uses, and keeps B04's
port-specialization hypothesis as an ADDITIVE bonus on top, so it cannot score worse than
"the same mechanism F uses" at the margin where no port opportunity exists.

Port bonus: scaled well below base_fn's production weight (1e8) so it only breaks
near-ties base_fn already found close, never overrides a real VP/production difference.
A port node is only worth the bonus when my own production of that resource (read from the
real resultant state, not a static map lookup) actually justifies the rate, and the bonus is
withdrawn once the opponent reaches PORT_URGENCY_CUTOFF public VP (savings can no longer
repay the detour).

Contract: unchanged from v001 (decide(obs, playable_actions) -> int; no hidden info; no
network/threads; fallback to a cheap legal index on any internal error).
"""
import random

from catanatron.models.enums import ActionType
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn
from catanatron.features import build_production_features

PORT_BONUS_STRONG = 3.0e6   # justified 2:1/3:1 port, scaled below base_fn's production (1e8)
PORT_BONUS_ROUTE = 1.0e6    # road heading toward such a port
PORT_URGENCY_CUTOFF = 9     # stop port-chasing once the opponent is about to win
PROBA_6 = 0.1389            # 5/36, dice probability of rolling a 6 or 8 (per DICE_PROBAS)


class Agent:
    def __init__(self):
        self.rng = random.Random(0)
        self._value_fn = base_fn(DEFAULT_WEIGHTS)

    # ------------------------------------------------------------- entry
    def decide(self, obs, playable_actions):
        try:
            idx = self._decide(obs, playable_actions)
        except Exception:
            idx = self._fallback(playable_actions)
        if isinstance(idx, bool) or not isinstance(idx, int):
            idx = 0
        if not 0 <= idx < len(playable_actions):
            idx = self._fallback(playable_actions)
        return idx

    @staticmethod
    def _fallback(actions):
        for i, a in enumerate(actions):
            if a.action_type == ActionType.ROLL:
                return i
        for i, a in enumerate(actions):
            if a.action_type == ActionType.END_TURN:
                return i
        return 0

    def _decide(self, obs, actions):
        if len(actions) == 1:
            return 0
        kinds = {a.action_type for a in actions}
        if ActionType.ROLL in kinds and len(kinds) == 1:
            return 0
        if ActionType.REJECT_TRADE in kinds or ActionType.CANCEL_TRADE in kinds:
            return 0  # no peer trades in this ruleset; always decline/cancel
        me = obs.me
        port_live = obs.opp_public_vps < PORT_URGENCY_CUTOFF
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            v = self._score(obs, me, act, port_live)
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i

    # ------------------------------------------------------------ scoring
    def _score(self, obs, me, act, port_live):
        game_copy = obs._game.copy()
        game_copy.execute(act)
        v = self._value_fn(game_copy, me)
        if port_live:
            v += self._port_bonus(obs, me, act, game_copy)
        return v

    def _port_bonus(self, obs, me, act, game_copy):
        at = act.action_type
        if at == ActionType.BUILD_SETTLEMENT:
            node = act.value
            return self._justified_port_value(obs, me, node, game_copy, PORT_BONUS_STRONG)
        if at == ActionType.BUILD_ROAD:
            _, far = act.value
            return self._justified_port_value(obs, me, far, game_copy, PORT_BONUS_ROUTE)
        return 0.0

    def _justified_port_value(self, obs, me, node, game_copy, scale):
        for resource, nodes in obs.board.map.port_nodes.items():
            if node not in nodes:
                continue
            my_production = self._my_production(game_copy, me)
            if resource is None:
                # generic 3:1 port: needs real surplus across at least two resources
                return scale if sum(1 for p in my_production.values() if p > 0) >= 2 else 0.0
            return scale if my_production.get(resource, 0.0) >= PROBA_6 else scale * 0.1
        return 0.0

    def _my_production(self, game_copy, me):
        production_features = build_production_features(True)
        sample = production_features(game_copy, me)
        out = {}
        for resource in ("WOOD", "BRICK", "SHEEP", "WHEAT", "ORE"):
            out[resource] = sample.get(f"EFFECTIVE_P0_{resource}_PRODUCTION", 0.0)
        return out
