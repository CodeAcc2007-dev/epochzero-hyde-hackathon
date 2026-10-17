"""B04 v003 - Port specialization.

Owner: Avadooth (Member 2). Assignment: team-work/member-2/07-TWO-BOT-BUILD-ASSIGNMENT.md.
Parent: v002 (bots/B04/v002/agent.py, sha256 763c88df0a815aeb97bf6cc1bb02865f8bb148c58bed6965ffb54911907d0b45,
commit 791e6705d09f62ceba691777e041980d673f1c69). Addresses verified findings from the
17 October 2026 independent review (team-work/reviews/2026-10-17-B03-B08/):

B04-01 (P1, verified): `_port_bonus` read `_, far = act.value` on BUILD_ROAD, assuming the
engine's edge tuple is given in (near, far) order. `Board.buildable_edges` actually returns
edges as `(n1, n2)` with `n1 < n2` -- an arbitrary sort order, not direction. The review's
constructed road prefix reaches a new port at the LOWER-numbered endpoint while the
HIGHER-numbered endpoint was already connected; v002 scored the already-owned node instead
of the new port. Fixed by determining the newly-reached endpoint from pre-action
connectivity (the same `connected_components`-based check B03 already uses correctly in
`_far_end`), not tuple position.

B04-02 (P1, verified): `_justified_port_value` granted `scale*0.1` even at exactly zero
specialized production, and a generic 3:1 port earned full credit for "at least two resource
types with any positive production," regardless of how small. Fixed: zero production now
earns zero bonus (not 10%); the generic-port case now requires real two-resource-equivalent
surplus (`>= 2 * PROBA_6`), not merely two nonzero entries. `PROBA_6` is now the exact
fraction `5/36` (v002 used the rounded decimal `0.1389`, slightly larger than 5/36, which
made the review's exact-5/36 probe fail the intended threshold).

M2-C01/M2-C02 (P1): same operational hardening as B03 v003 -- per-candidate exception
handling that preserves the best already-scored incumbent instead of discarding all
progress, internal diagnostic counters (self.diagnostics, never printed/written), a cheap
low-clock path gated on `obs.cpu_left`, and an explicit immediate-win check that bypasses
heuristic scoring and the port bonus entirely rather than relying on bonus-scale arguments.

B04-03 (P2 hypothesis, deferred): the review also proposes a bounded port-to-purchase trade
chain so MARITIME_TRADE itself is priced toward a named purchase rather than left entirely to
base_fn. Deferred from this round -- it is a separate experiment from the two verified P1
defects above and the contract asks for one interpretable change at a time; see
implementation/BUILD-AND-RESULTS.md for the explicit rejection rationale.

Contract: unchanged (decide(obs, playable_actions) -> int; no hidden info; no
network/threads; never raises to the harness).
"""
import random

from catanatron.models.enums import ActionType
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn
from catanatron.features import build_production_features

PORT_BONUS_STRONG = 3.0e6   # justified 2:1/3:1 port, scaled below base_fn's production (1e8)
PORT_BONUS_ROUTE = 1.0e6    # road heading toward such a port
PORT_URGENCY_CUTOFF = 9     # stop port-chasing once the opponent is about to win
PROBA_6 = 5.0 / 36.0        # exact dice probability of rolling a 6 or 8
CPU_SAFETY_FLOOR = 0.05     # seconds; below this, skip the simulate-and-score loop entirely


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
        port_live = obs.opp_public_vps < PORT_URGENCY_CUTOFF
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
                if port_live:
                    v += self._port_bonus(obs, me, act, game_copy)
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
    def _port_bonus(self, obs, me, act, game_copy):
        at = act.action_type
        if at == ActionType.BUILD_SETTLEMENT:
            return self._justified_port_value(obs, me, act.value, game_copy, PORT_BONUS_STRONG)
        if at == ActionType.BUILD_ROAD:
            far = self._far_end(obs, me, *act.value)
            return self._justified_port_value(obs, me, far, game_copy, PORT_BONUS_ROUTE)
        return 0.0

    def _far_end(self, obs, me, a, b):
        """The endpoint NOT already in my connected component (B04-01 fix: edge tuples are
        (n1, n2) with n1 < n2, an arbitrary sort order, not a near/far direction)."""
        st = obs._game.state
        comp = set()
        for c in st.board.connected_components.get(me, ()):
            comp |= c
        return b if a in comp else a

    def _justified_port_value(self, obs, me, node, game_copy, scale):
        for resource, nodes in obs.board.map.port_nodes.items():
            if node not in nodes:
                continue
            my_production = self._my_production(game_copy, me)
            if resource is None:
                total = sum(my_production.values())
                if total <= 0.0:
                    return 0.0
                return scale if total >= 2 * PROBA_6 else 0.0
            own = my_production.get(resource, 0.0)
            if own <= 0.0:
                return 0.0
            return scale if own >= PROBA_6 - 1e-9 else scale * 0.1
        return 0.0

    def _my_production(self, game_copy, me):
        production_features = build_production_features(True)
        sample = production_features(game_copy, me)
        out = {}
        for resource in ("WOOD", "BRICK", "SHEEP", "WHEAT", "ORE"):
            out[resource] = sample.get(f"EFFECTIVE_P0_{resource}_PRODUCTION", 0.0)
        return out
