"""B03 v003 - Frontier expansion and space denial.

Owner: Avadooth (Member 2). Assignment: team-work/member-2/07-TWO-BOT-BUILD-ASSIGNMENT.md.
Parent: v002 (bots/B03/v002/agent.py, sha256 1a4a304932718ba2b76af1ff966bb08c55c5c00c7a0ef5c0f9cf788bdcc66e30,
commit 791e6705d09f62ceba691777e041980d673f1c69). Addresses verified findings from the
8 October-17 2026 independent review (team-work/reviews/2026-10-17-B03-B08/):

B03-01 (P1, verified): `_opp_reach` seeded its BFS only from the opponent's settlement/city
nodes and then spent its hop budget walking back out along the opponent's OWN existing
roads, so an opponent six-road network's legal frontier node (the review's constructed
node 39) never appeared in the contest set even though it costs zero additional roads.
Fixed by seeding the search from the opponent's full existing connected-component node set
(catanatron's own `board.connected_components`, which already accounts for every road they
own), then hopping out REACH_HOPS *new* edges from there, and filtering the result to
`board.board_buildable_ids` so distance-rule-illegal nodes are never reported as contestable.

M2-C01 (P1): the old `decide` wrapped the *entire* per-turn decision in one try/except, so a
single bad candidate discarded every already-scored action and fell back to ROLL/END_TURN
even when far better legal actions had already been evaluated. Fixed by moving exception
handling inside the per-candidate loop: a failing candidate is skipped and counted, the best
already-scored action (if any) is kept as the running incumbent. Internal diagnostic
counters (self.diagnostics) track evaluated/skipped/exception/low_clock/guaranteed_win
decisions for inspection in tests; nothing is printed or written at runtime.

M2-C02 (P1): base_fn's public-VP weight (3e14) should already dominate everything else, but
the review correctly notes an additive bonus is not provably incapable of overriding a real
difference. Rather than argue about bonus scale, `decide` now checks explicitly: if executing
a candidate action produces a state where I have already won (`game_copy.winning_color() ==
me`), that action is returned immediately, bypassing heuristic scoring and any bonus term
entirely. ROLL/BUY_DEVELOPMENT_CARD/MOVE_ROBBER cross real chance boundaries in the engine;
this agent does not claim to resolve or search over them, only to never let a bonus term
out-rank an already-confirmed win.

Clock budgeting: when `obs.cpu_left` is supplied and below CPU_SAFETY_FLOOR, skip the
expensive simulate-and-score loop (which still runs a `game.copy()` per candidate) and use a
cheap winning-action-only check, falling back to a type-preferred legal action.

Contract: unchanged (decide(obs, playable_actions) -> int; no hidden info; no
network/threads; never raises to the harness).
"""
import random

from catanatron.models.board import STATIC_GRAPH
from catanatron.models.enums import ActionType
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn

# Scaled well below base_fn's production weight (1e8) so this only breaks near-ties
# base_fn already found close, never overrides a real VP/production difference. Calibrated
# in v002 after a first cut at 2.5e7 (same order as base_fn's production term) made B03
# *worse* than v001 by overriding genuine production differences; see v002's manifest.
CONTEST_BONUS = 3.0e6
STEAL_BONUS = 1.0e6
REACH_HOPS = 2
CPU_SAFETY_FLOOR = 0.05  # seconds; below this, skip the simulate-and-score loop entirely


class Agent:
    def __init__(self):
        self.rng = random.Random(0)
        self._value_fn = base_fn(DEFAULT_WEIGHTS)
        self.diagnostics = {
            "evaluated": 0, "exceptions": 0, "low_clock_decisions": 0,
            "guaranteed_wins": 0, "all_candidates_failed": 0,
        }

    # ------------------------------------------------------------- entry
    def decide(self, obs, playable_actions):
        try:
            idx = self._decide(obs, playable_actions)
        except Exception:
            self.diagnostics["exceptions"] += 1
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
        cpu_left = getattr(obs, "cpu_left", None)
        if cpu_left is not None and cpu_left < CPU_SAFETY_FLOOR:
            self.diagnostics["low_clock_decisions"] += 1
            return self._cheap_safe_index(obs, me, actions)
        opp_reach = self._opp_reach(obs, me)
        best_i, best_v, any_scored = 0, None, False
        for i, act in enumerate(actions):
            try:
                game_copy = obs._game.copy()
                game_copy.execute(act)
            except Exception:
                self.diagnostics["exceptions"] += 1
                continue
            if game_copy.winning_color() == me:
                self.diagnostics["guaranteed_wins"] += 1
                return i
            try:
                v = self._value_fn(game_copy, me)
                v += self._contest_bonus(obs, me, act, opp_reach)
            except Exception:
                self.diagnostics["exceptions"] += 1
                continue
            any_scored = True
            self.diagnostics["evaluated"] += 1
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        if not any_scored:
            self.diagnostics["all_candidates_failed"] += 1
            return self._fallback(actions)
        return best_i

    def _cheap_safe_index(self, obs, me, actions):
        """Low-clock path: check only for an immediate win, skip heuristic scoring."""
        for i, act in enumerate(actions):
            try:
                game_copy = obs._game.copy()
                game_copy.execute(act)
            except Exception:
                self.diagnostics["exceptions"] += 1
                continue
            if game_copy.winning_color() == me:
                self.diagnostics["guaranteed_wins"] += 1
                return i
        for i, a in enumerate(actions):
            if a.action_type in (ActionType.BUILD_CITY, ActionType.BUILD_SETTLEMENT):
                return i
        return self._fallback(actions)

    # ------------------------------------------------------------ bonus
    def _contest_bonus(self, obs, me, act, opp_reach):
        at = act.action_type
        if at == ActionType.BUILD_SETTLEMENT:
            if act.value in opp_reach:
                return CONTEST_BONUS
        elif at == ActionType.BUILD_ROAD:
            far = self._far_end(obs, me, *act.value)
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
        """Legal contestable settlement nodes within REACH_HOPS new roads of the opponent's
        EXISTING road network (not just their building sites -- see B03-01 above), filtered
        to distance-rule-legal spots. Uses the real board graph (STATIC_GRAPH) and the
        engine's own connected-components, never a snake-order or coordinate assumption."""
        st = obs._game.state
        opp = next((c for c in st.colors if c != me), None)
        if opp is None:
            return set()
        comp_nodes = set()
        for comp in st.board.connected_components.get(opp, ()):
            comp_nodes |= comp
        if not comp_nodes:
            return set()
        frontier = set(comp_nodes)
        seen = set(comp_nodes)
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
        return seen & st.board.board_buildable_ids
