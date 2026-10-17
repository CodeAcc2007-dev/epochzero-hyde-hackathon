"""B03 v001 — Frontier expansion and space denial.

Owner: Avadooth (Member 2). Assignment: team-work/member-2/07-TWO-BOT-BUILD-ASSIGNMENT.md.

Hypothesis: complementary openings and timely occupation of valuable legal sites can
outpace concentrated city investment. Distinct decision logic versus B04 (port
conversion): expansion targets are ranked by production/ingredient value minus legal
road delay, with a contest premium for occupying sites the opponent can also reach
(denial priced as opportunity cost, never as guaranteed victory).

Contract:
- decide(obs, playable_actions) -> a genuine int index into playable_actions.
- The observation is never mutated; hidden information and seeds are never used.
- No network, threads, workers or runtime LLM calls.
- Any unexpected state falls back to a cheap legal index; nothing raises to the harness.
- Opening choices come from the actual legal node/edge lists each prompt supplies; no
  seating or snake-order assumptions are made.
"""
import random

from catanatron.models.board import STATIC_GRAPH
from catanatron.models.enums import (
    ActionType,
    BRICK,
    CITY,
    ORE,
    SETTLEMENT,
    SHEEP,
    WHEAT,
    WOOD,
)
from catanatron.models.map import DICE_PROBAS
from catanatron.state_functions import (
    get_player_buildings,
    player_key,
)

COST_ROAD = {WOOD: 1, BRICK: 1}
COST_SETTLEMENT = {WOOD: 1, BRICK: 1, SHEEP: 1, WHEAT: 1}
COST_CITY = {WHEAT: 2, ORE: 3}
COST_DEV = {SHEEP: 1, WHEAT: 1, ORE: 1}
ALL_RES = (WOOD, BRICK, SHEEP, WHEAT, ORE)

W_PROD = 42.0        # cards of value per unit of expected production
W_CITY_EXTRA = 5.0
W_DEV = 2.0
W_STEAL = 0.9
W_DRY = 7.0
CONTEST_PREMIUM = 0.45


def _afford(hand, cost):
    return all(hand.get(r, 0) >= n for r, n in cost.items())


class Agent:
    def __init__(self):
        self.rng = random.Random(0)

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
        st = obs._game.state
        kinds = {a.action_type for a in actions}
        if st.is_initial_build_phase:
            if ActionType.BUILD_SETTLEMENT in kinds:
                return self._opening_settlement(obs, actions)
            if ActionType.BUILD_ROAD in kinds:
                return self._opening_road(obs, actions)
        if ActionType.MOVE_ROBBER in kinds:
            return self._robber_prompt(obs, actions)
        if ActionType.DISCARD_RESOURCE in kinds:
            return self._discard_prompt(obs, actions)
        if ActionType.REJECT_TRADE in kinds or ActionType.CANCEL_TRADE in kinds:
            return 0  # reject/cancel is always the first listed action
        return self._regular(obs, actions)

    # ------------------------------------------------------------ helpers
    def _my_nodes(self, obs, me):
        st = obs._game.state
        return set(get_player_buildings(st, me, SETTLEMENT)) | set(
            get_player_buildings(st, me, CITY))

    def _comp_nodes(self, obs, me):
        st = obs._game.state
        nodes = set()
        for comp in st.board.connected_components.get(me, ()):
            nodes |= comp
        return nodes

    def _pips(self, st, node):
        total = 0.0
        for t in st.board.map.adjacent_tiles.get(node, ()):
            if t.resource is not None:
                total += DICE_PROBAS[t.number]
        return total

    def _res_map(self, st, nodes):
        out = {}
        for n in nodes:
            for t in st.board.map.adjacent_tiles.get(n, ()):
                if t.resource is not None:
                    out[t.resource] = out.get(t.resource, 0.0) + DICE_PROBAS[t.number]
        return out

    def _nums(self, st, nodes):
        out = set()
        for n in nodes:
            for t in st.board.map.adjacent_tiles.get(n, ()):
                if t.resource is not None:
                    out.add(t.number)
        return out

    def _opp_reach(self, obs, me):
        """Nodes the opponent can plausibly settle soon (their roads + 2 hops)."""
        st = obs._game.state
        opp = next((c for c in st.colors if c != me), None)
        if opp is None:
            return set()
        seeds = set(get_player_buildings(st, opp, SETTLEMENT)) | set(
            get_player_buildings(st, opp, CITY))
        frontier = set(seeds)
        seen = set(seeds)
        for _ in range(2):
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

    # ------------------------------------------------------------ opening
    def _opening_settlement(self, obs, actions):
        st = obs._game.state
        me = obs.me
        my_setts = list(get_player_buildings(st, me, SETTLEMENT))
        opp_setts = []
        for c in st.colors:
            if c != me:
                opp_setts = set(get_player_buildings(st, c, SETTLEMENT)) | set(
                    get_player_buildings(st, c, CITY))
        opp_reach = self._opp_reach(obs, me) if opp_setts else set()
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            v = self._opening_score(obs, act.value, my_setts, opp_setts, opp_reach)
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i

    def _opening_score(self, obs, cand, my_setts, opp_setts, opp_reach):
        st = obs._game.state
        pair_nodes = [cand] + list(my_setts)
        pair_res = self._res_map(st, pair_nodes)
        nums = self._nums(st, pair_nodes)
        pips = sum(pair_res.values())
        v = W_PROD * pips
        v += 2.2 * sum(1 for r in ALL_RES if pair_res.get(r, 0.0) > 0)
        if pair_res.get(WHEAT, 0.0) > 0:
            v += 4.0
        if pair_res.get(ORE, 0.0) > 0:
            v += 4.0
        if all(pair_res.get(r, 0.0) > 0 for r in (WOOD, BRICK, SHEEP, WHEAT)):
            v += 2.6
        dry = 1.0
        for n in nums:
            dry *= 1.0 - DICE_PROBAS[n]
        v -= W_DRY * dry
        if my_setts:
            shared = nums & self._nums(st, [my_setts[0]])
            v -= 5.5 * len(shared)
        if my_setts:
            hand = dict(obs.my_resources)
            for t in st.board.map.adjacent_tiles.get(cand, ()):
                if t.resource is not None:
                    hand[t.resource] = hand.get(t.resource, 0) + 1
            if _afford(hand, COST_ROAD):
                v += 1.5
            if _afford(hand, COST_DEV):
                v += 1.2
            if _afford(hand, COST_SETTLEMENT):
                v += 2.6
        if opp_setts and cand in opp_reach:
            v += CONTEST_PREMIUM * max(self._pips(st, cand), 1.0) * 8.0
        v += 0.5 * self._port_term(obs, cand, pair_res)
        return v

    def _opening_road(self, obs, actions):
        st = obs._game.state
        me = obs.me
        comp = self._comp_nodes(obs, me)
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            a, b = act.value
            far = b if a in comp else a
            if far in comp:
                far = a
            v = 25.0 * self._pips(st, far)
            beyond = 0.0
            for w in STATIC_GRAPH.neighbors(far):
                if w == a or st.board.buildings.get(w) is not None:
                    continue
                bp = self._pips(st, w)
                if bp > beyond:
                    beyond = bp
            v += 0.3 * beyond * 6.0
            for w in STATIC_GRAPH.neighbors(far):
                if st.board.get_node_color(w) is not None and \
                        st.board.get_node_color(w) != me:
                    v += 0.3 * 6.0 * self._pips(st, far)
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i

    # ------------------------------------------------------------ regular
    def _regular(self, obs, actions):
        me = obs.me
        st = obs._game.state
        opp_reach = self._opp_reach(obs, me)
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            at = act.action_type
            if at == ActionType.ROLL:
                v = 0.5
            elif at == ActionType.END_TURN:
                v = 0.0
            elif at == ActionType.BUILD_SETTLEMENT:
                v = self._site_value(obs, act.value, opp_reach)
            elif at == ActionType.BUILD_CITY:
                v = W_PROD * self._pips(st, act.value) + W_CITY_EXTRA
            elif at == ActionType.BUILD_ROAD:
                v = self._road_score(obs, act.value, opp_reach)
            elif at == ActionType.BUY_DEVELOPMENT_CARD:
                v = self._dev_value(obs, me, st)
            elif at == ActionType.MARITIME_TRADE:
                v = self._trade_value(obs, act.value)
            elif at == ActionType.PLAY_KNIGHT_CARD:
                v = self._knight_value(obs, me, st)
            elif at == ActionType.PLAY_MONOPOLY:
                n = obs.opp_resources.get(act.value, 0)
                v = 0.9 * n if n >= 2 else 0.0
            elif at == ActionType.PLAY_YEAR_OF_PLENTY:
                v = self._yop_value(obs, act.value)
            elif at == ActionType.PLAY_ROAD_BUILDING:
                v = self._road_building_value(obs, me, opp_reach)
            else:
                v = 0.0
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i

    # ----- site / road evaluation
    def _site_value(self, obs, node, opp_reach):
        st = obs._game.state
        rm = self._res_map(st, [node])
        pips = sum(rm.values())
        v = W_PROD * pips
        v += 2.2 * sum(1 for r in ALL_RES if rm.get(r, 0.0) > 0)
        if rm.get(WHEAT, 0.0) > 0:
            v += 4.0
        if rm.get(ORE, 0.0) > 0:
            v += 4.0
        if opp_reach and node in opp_reach:
            v += 6.0 + CONTEST_PREMIUM * W_PROD * pips
        v += 0.5 * self._port_term(obs, node)
        return v

    def _port_term(self, obs, node, res_map=None):
        for resource, nodes in obs.board.map.port_nodes.items():
            if node in nodes:
                if resource is None:
                    return 0.8
                own = (res_map or {}).get(resource, 0.0)
                return 1.5 if own >= DICE_PROBAS[6] else 0.2
        return 0.0

    def _road_site(self, obs, me, edge):
        st = obs._game.state
        comp = self._comp_nodes(obs, me)
        a, b = edge
        near = a if a in comp else b
        far = b if near == a else a
        if far in st.board.board_buildable_ids:
            return far, 1
        for w in STATIC_GRAPH.neighbors(far):
            if w == near:
                continue
            if st.board.get_edge_color((w, far)) is None and \
                    w in st.board.board_buildable_ids:
                return w, 2
        return None, 3

    def _road_score(self, obs, edge, opp_reach):
        st = obs._game.state
        me = obs.me
        node, depth = self._road_site(obs, me, edge)
        v = 0.0
        if node is not None:
            v += 0.8 * self._site_value(obs, node, opp_reach) / depth
        my_len = st.board.road_lengths.get(me, 0)
        opp_len = max((st.board.road_lengths.get(c, 0) for c in st.colors if c != me),
                      default=0)
        if my_len == 4:
            v += 5.0
        if opp_len >= 5 and my_len + 1 > opp_len:
            v += 2.0
        a, b = edge
        for n in (a, b):
            c = st.board.get_node_color(n)
            if c is not None and c != me:
                v += 3.0 + 0.2 * W_PROD * self._pips(st, n)
        if v <= 0.5:
            v = -1.0  # never a road to nowhere
        return v

    # ----- other action scores
    def _trade_value(self, obs, offer):
        """B03 trades only to unlock a purchase this turn, at the best offered rate."""
        out = None
        rate = 0
        for x in offer[:4]:
            if x is not None:
                out = x
                rate += 1
        ask = offer[4]
        hand = dict(obs.my_resources)
        if hand.get(out, 0) < rate:
            return 0.0
        after = dict(hand)
        after[out] = after.get(out, 0) - rate
        after[ask] = after.get(ask, 0) + 1
        best = 0.0
        for cost, val in ((COST_SETTLEMENT, 5.0), (COST_CITY, 5.5),
                          (COST_ROAD, 1.8), (COST_DEV, W_DEV - 0.3)):
            if _afford(after, cost) and not _afford(hand, cost):
                best = max(best, val)
        return (best - 0.4 * rate) if best > 0 else 0.0

    def _dev_value(self, obs, me, st):
        v = W_DEV
        for c in st.colors:
            if c != me:
                opp_vp = st.player_state[f"P{st.color_to_index[c]}_VICTORY_POINTS"]
                if opp_vp >= 8:
                    v += 0.6
        key = player_key(st, me)
        if st.player_state[f"{key}_CITIES_AVAILABLE"] > 0 and \
                obs.my_resources.get(WHEAT, 0) + obs.my_resources.get(ORE, 0) >= 3:
            v -= 0.9
        return v

    def _knight_value(self, obs, me, st):
        coord = st.board.robber_coordinate
        me_hit = False
        for n in self._my_nodes(obs, me):
            for t in st.board.map.adjacent_tiles.get(n, ()):
                if t is st.board.map.land_tiles.get(coord):
                    me_hit = True
        opp_vp = 0
        for c in st.colors:
            if c != me:
                opp_vp = st.player_state[f"P{st.color_to_index[c]}_VICTORY_POINTS"]
        if me_hit or opp_vp >= 9:
            return 2.0
        return 0.25

    def _monopoly_value(self, obs, resource):
        n = obs.opp_resources.get(resource, 0)
        return 1.4 * n if n >= 2 else 0.0

    def _yop_value(self, obs, cards):
        hand = dict(obs.my_resources)
        for c in cards:
            hand[c] = hand.get(c, 0) + 1
        if _afford(hand, COST_SETTLEMENT):
            return 4.5
        if _afford(hand, COST_CITY):
            return 4.5
        if _afford(hand, COST_ROAD):
            return 1.4
        if _afford(hand, COST_DEV):
            return 1.3
        return 0.0

    def _road_building_value(self, obs, me, opp_reach):
        try:
            edges = obs.board.buildable_edges(me)
        except Exception:
            return 0.0
        vals = sorted((self._road_score(obs, e, opp_reach) for e in edges),
                      reverse=True)
        if not vals or vals[0] <= 0.5:
            return 0.0
        return sum(vals[:2]) + 1.5

    # ----- robber / discard prompts
    def _robber_prompt(self, obs, actions):
        st = obs._game.state
        me = obs.me
        my_nodes = self._my_nodes(obs, me)
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            coord, victim = act.value
            tile = st.board.map.land_tiles[coord]
            tile_nodes = set(tile.nodes.values())
            opp_gain = own_loss = 0.0
            for node_id in tile_nodes:
                building = st.board.buildings.get(node_id)
                if building is None:
                    continue
                color, btype = building
                mult = 2 if btype == CITY else 1
                if color == me:
                    own_loss += mult * self._pips(st, node_id)
                else:
                    opp_gain += mult * self._pips(st, node_id)
            v = W_PROD * opp_gain - 0.8 * W_PROD * own_loss
            if victim is not None:
                v += W_STEAL
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i

    def _discard_prompt(self, obs, actions):
        st = obs._game.state
        me = obs.me
        prod = {}
        for n in self._my_nodes(obs, me):
            mult = 2 if n in set(get_player_buildings(st, me, CITY)) else 1
            for t in st.board.map.adjacent_tiles.get(n, ()):
                if t.resource is not None:
                    prod[t.resource] = prod.get(t.resource, 0.0) + mult * DICE_PROBAS[t.number]
        best_i, best_v = 0, None
        for i, act in enumerate(actions):
            r = act.value
            keep = 3.0 * prod.get(r, 0.0) + (0.6 if r in (WHEAT, ORE) else 0.0)
            v = obs.my_resources.get(r, 0) - 2.0 * keep
            if best_v is None or v > best_v:
                best_i, best_v = i, v
        return best_i
