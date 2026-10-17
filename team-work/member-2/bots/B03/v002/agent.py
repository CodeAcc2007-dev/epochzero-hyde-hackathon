"""B03 v002 - Frontier expansion and space denial.

Owner: Avadooth (Member 2). Assignment: team-work/member-2/07-TWO-BOT-BUILD-ASSIGNMENT.md.
Supersedes v001 (bots/B03/v001), which lost to unchanged F on screen batches
(29/80, see bots/REPORT.md). Root cause identified by reviewing F's own implementation
(catanatron.players.value.ValueFunctionPlayer / base_fn): F does not score the CURRENT
state with hand-rolled pip heuristics. For every legal action it executes a real copy of
the game (game.copy().execute(action)) and scores the RESULTING state with base_fn, which
is dominated lexicographically by public VP (weight 3e14), then production (1e8), then
enemy-denied production (-1e8), then reachable production / buildable nodes / hand
synergy / dev cards / army size. v001 approximated this with static current-state pip
counts and never looked at the actual resulting state, so it undervalued second-order
effects (new reachable production, buildable-node count, hand synergy after a trade) that
F's real simulation sees directly.

v002 keeps B03's identity as this member's frontier/denial hypothesis bot, but keeps it as
an ADDITIVE bonus on top of a real one-ply simulation using F's own base_fn, so it cannot
regress below running "the same mechanism F uses" at the margin where no denial opportunity
exists. The bonus: when the chosen action puts me on a node the opponent could plausibly
reach within two hops (computed on the state BEFORE the action, from each candidate's own
legal board graph, not a snake-order or Manhattan-coordinate assumption), add a contest
premium scaled well below the production term (1e8) so it only breaks near-ties toward
denial and never overrides an actual VP/production difference base_fn already found.

Contract: unchanged from v001 (decide(obs, playable_actions) -> int; no hidden info; no
network/threads; fallback to a cheap legal index on any internal error).
"""
import random

from catanatron.models.board import STATIC_GRAPH
from catanatron.models.enums import ActionType, CITY, SETTLEMENT
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn
from catanatron.state_functions import get_player_buildings

# Scaled well below base_fn's production weight (1e8) so this only breaks near-ties
# between options base_fn already considers close, never overrides a real VP/production
# difference the simulated resultant state found.
CONTEST_BONUS = 3.0e6
STEAL_BONUS = 1.0e6
REACH_HOPS = 2


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
        opp_reach = self._opp_reach(obs, me)
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            v = self._score(obs, me, act, opp_reach)
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i

    # ------------------------------------------------------------ scoring
    def _score(self, obs, me, act, opp_reach):
        game_copy = obs._game.copy()
        game_copy.execute(act)
        v = self._value_fn(game_copy, me)
        v += self._contest_bonus(obs, me, act, opp_reach)
        return v

    def _contest_bonus(self, obs, me, act, opp_reach):
        at = act.action_type
        if at == ActionType.BUILD_SETTLEMENT:
            node = act.value
            if node in opp_reach:
                return CONTEST_BONUS
        elif at == ActionType.BUILD_ROAD:
            a, b = act.value
            far = self._far_end(obs, me, a, b)
            if far in opp_reach:
                return 0.5 * CONTEST_BONUS
        elif at == ActionType.MOVE_ROBBER:
            _, victim = act.value
            if victim is not None:
                return STEAL_BONUS
        return 0.0

    def _far_end(self, obs, me, a, b):
        st = obs._game.state
        comp = set()
        for c in st.board.connected_components.get(me, ()):
            comp |= c
        return b if a in comp else a

    def _opp_reach(self, obs, me):
        """Nodes the opponent's own legal board graph can plausibly reach within
        REACH_HOPS edges, computed from the actual graph (STATIC_GRAPH), never a
        snake-order or Manhattan-coordinate assumption."""
        st = obs._game.state
        opp = next((c for c in st.colors if c != me), None)
        if opp is None:
            return set()
        seeds = set(get_player_buildings(st, opp, SETTLEMENT)) | set(
            get_player_buildings(st, opp, CITY))
        if not seeds:
            return set()
        frontier = set(seeds)
        seen = set(seeds)
        for _ in range(REACH_HOPS):
            nxt = set()
            for n in frontier:
                for w in STATIC_GRAPH.neighbors(n):
                    if w in seen or st.board.buildings.get(w) is not None:
                        continue
                    if st.board.get_edge_color((n, w)) == me:
                        continue
                    nxt.add(w)
            frontier = nxt
            seen |= frontier
        return seen
