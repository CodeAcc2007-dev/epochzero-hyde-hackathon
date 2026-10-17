"""B07 v002: reviewed corrections; standalone organizer-engine agent."""

ResourceTuple = tuple  # length-5 int sequence in WOOD, BRICK, SHEEP, WHEAT, ORE order


def deficit(hand: ResourceTuple, cost: ResourceTuple) -> int:
    """Total missing cards: sum(max(cost[i] - hand[i], 0)) over paired slots.

    Returns an exact int (0 when the cost is already met).
    """
    return sum(max(c - h, 0) for h, c in zip(hand, cost))


def can_afford(hand: ResourceTuple, cost: ResourceTuple) -> bool:
    """True iff hand[i] >= cost[i] for every paired slot."""
    return all(h >= c for h, c in zip(hand, cost))


def steal_break_probability(hand: ResourceTuple, cost: ResourceTuple) -> float:
    """Probability that one uniformly random resource card, if stolen, makes `cost` unaffordable.

    Assumes the hand currently affords the cost; returns 0.0 if it does not, or if
    the hand is empty. Numerator counts cards of types where cost[i] > 0 and the
    hand holds exactly cost[i] of them (losing any one card of such a type breaks
    affordability). Does NOT certify a legal building location or a future win.
    """
    if not can_afford(hand, cost) or sum(hand) == 0:
        return 0.0
    total = sum(hand)
    fragile = sum(h for h, c in zip(hand, cost) if c > 0 and h == c)
    return fragile / total


def expected_stolen_value(hand: ResourceTuple, values: ResourceTuple) -> float:
    """Expected value of one uniformly random card from the hand: sum(hand[i]*values[i])/sum(hand).

    Returns 0.0 for an empty hand. Closed form; no random sampling.
    """
    total = sum(hand)
    if total == 0:
        return 0.0
    return sum(h * v for h, v in zip(hand, values)) / total


def hidden_vp_cap(public_vp: int, dev_count: int, unseen_vps: int) -> int:
    """Upper bound on an opponent's hidden victory points: max(0, min(dev_count, unseen_vps, 9 - public_vp)).

    A necessary bound for a real, nonterminal 10-VP game only (an opponent at or
    past 10 would have already won, hence the 9 - public_vp term); it is not a
    posterior estimate of hidden VP.
    """
    return max(0, min(dev_count, unseen_vps, 9 - public_vp))

def one_trade_build(hand, cost, ratios, bank):
    """Enumerate every distinct legal single maritime trade after which hand meets cost.

    Args:
        hand, cost, bank: length-five nonnegative integer sequences (resources 0..4);
            no argument is mutated.
        ratios: length-five give-ratios, each 2, 3 or 4; one trade gives ratios[i]
            copies of resource i to the bank for 1 copy of another resource j != i.

    Returns a tuple of (source_index, destination_index) pairs in numeric sorted
    order: exactly those i != j with hand[i] >= ratios[i] and bank[j] >= 1 such
    that, after applying the exact trade, every cost ingredient is covered
    (hand[k] >= cost[k] for all k). Nothing is reserved artificially. If the hand
    already meets cost, the result is still only the actual one-trade completions
    (trades of surplus included); the caller handles the already-affordable case.
    bank is only read: the give-side return to the bank cannot affect the
    hand-versus-cost check, so no bank copy is modeled.
    """
    completions = []
    for i in range(5):
        if hand[i] < ratios[i]:
            continue
        for j in range(5):
            if j == i or bank[j] < 1:
                continue
            traded = list(hand)
            traded[i] -= ratios[i]
            traded[j] += 1
            if all(t >= c for t, c in zip(traded, cost)):
                completions.append((i, j))
    return tuple(sorted(completions))


def knight_wait_rolls(plays_needed, held, old_eligible, played_this_turn):
    """Lower bound, in two-player roll units, until the last needed Knight is played.

    An own-turn wait is scored in units of two roll opportunities. This is
    a route-scoring conversion, not the exact number of rolls before a pre-roll
    Knight (which may play before our next roll). Assumptions:
      * plays_needed >= 0 Knights must still be played; held >= 0 Knights are
        already in hand. old_eligible means held Knights were bought on an
        earlier turn; played_this_turn means an action development card was
        already played this turn (blocking a Knight play now).
      * Optimistic acquisition: every Knight still needed is assumed buyable
        this current turn, so acquisition itself adds no wait; only the
        same-turn-play ban matters.
      * Hence a Knight can be played this turn only if one is already held
        (held > 0), it is old/eligible, and no action dev was played yet this
        turn. Exactly one Knight is played per own turn; each later play lands
        one own turn after the previous one.

    Returns 0 when plays_needed == 0; else 2 * (plays_needed - 1 + first_turn_wait)
    where first_turn_wait is 0 exactly when held > 0 and old_eligible and not
    played_this_turn, else 1. This scales an optimistic own-turn eligibility bound by two; it is not an
    expected completion time or a bound on actual elapsed dice rolls.
    """
    if plays_needed == 0:
        return 0
    first_turn_wait = 0 if (held > 0 and old_eligible and not played_this_turn) else 1
    return 2 * (plays_needed - 1 + first_turn_wait)

from catanatron.models.enums import ActionType as AT


def public_terminal(g, me, initial_enemy_public, opp_count, unseen_vps):
    ps=g.state.player_state
    k='P'+str(g.state.color_to_index[me])
    enemy=next(c for c in g.state.colors if c!=me)
    ek='P'+str(g.state.color_to_index[enemy])
    if ps[k+'_ACTUAL_VICTORY_POINTS'] < g.vps_to_win:
        return False
    public=ps[ek+'_VICTORY_POINTS']
    # The engine's last qualifying color wins. Real input was nonterminal;
    # unchanged opponent public VP cannot suddenly create a real opponent win.
    return (g.state.colors[-1]==me or public<=initial_enemy_public or
            public+hidden_vp_cap(initial_enemy_public,opp_count,unseen_vps)<g.vps_to_win)


def terminal_action(obs, actions):
    """Certify an immediate legal own win before expensive context/sampling.

    At most 12 road/settlement copies; the fast city/Knight cases need none.
    An incomplete bounded scan returns None, not a claim no win exists.
    The harness's masked game supplies public geometry/own exact cards only.
    """
    g=obs._game
    gap=g.vps_to_win-obs.my_actual_vps
    if gap>3:
        return None
    ps=g.state.player_state;k='P'+str(g.state.color_to_index[obs.me])
    enemy=next(c for c in g.state.colors if c!=obs.me)
    ek='P'+str(g.state.color_to_index[enemy])
    for i,a in enumerate(actions):
        if a.action_type==AT.BUILD_CITY and gap<=1:
            return i
        if a.action_type==AT.PLAY_KNIGHT_CARD and gap<=2:
            count=ps[k+'_PLAYED_KNIGHT']+1
            if not ps[k+'_HAS_ARMY'] and count>=3 and (not ps[ek+'_HAS_ARMY'] or count>ps[ek+'_PLAYED_KNIGHT']):
                return i
    copies=0
    for i,a in enumerate(actions):
        if a.action_type not in (AT.BUILD_SETTLEMENT,AT.BUILD_ROAD):continue
        if a.action_type==AT.BUILD_ROAD and gap>2:continue
        child=g.copy();child.execute(a);copies+=1
        if public_terminal(child,obs.me,obs.opp_public_vps,obs.opp_dev_count,
                           max(0,5-obs.my_devs['VICTORY_POINT'])):
            return i
        if copies>=12:break
    return None

import math
import random
import time

from catanatron.models.enums import ActionType as AT, ActionPrompt as AP
from catanatron.models.board import STATIC_GRAPH

RES = ('WOOD', 'BRICK', 'SHEEP', 'WHEAT', 'ORE')
DEVS = ('KNIGHT', 'VICTORY_POINT', 'ROAD_BUILDING', 'YEAR_OF_PLENTY', 'MONOPOLY')
DECK = (14, 5, 2, 2, 2)
SETTLE = (1, 1, 1, 1, 0)
CITY = (0, 0, 0, 2, 3)
DEV_COST = (0, 0, 1, 1, 1)
WIN = 1_000_000_000.0
DETERMINISTIC = frozenset((AT.BUILD_CITY, AT.BUILD_SETTLEMENT, AT.BUILD_ROAD,
    AT.MARITIME_TRADE, AT.PLAY_YEAR_OF_PLENTY, AT.PLAY_MONOPOLY,
    AT.PLAY_KNIGHT_CARD, AT.PLAY_ROAD_BUILDING))


def hand(state, key):
    return tuple(state.player_state[key + '_' + r + '_IN_HAND'] for r in RES)


def resource_hand_value(h, city_possible=True, settlement_possible=True):
    # Marginal ingredient retention; surplus is worth less, not zero.
    return (0.22 * sum(h) + (3.0 * (5 - deficit(h, CITY)) if city_possible else 0)
            + (2.0 * (4 - deficit(h, SETTLE)) if settlement_possible else 0)
            - 0.35 * max(sum(h) - 7, 0))


class Context:
    def __init__(self, game, me, threats):
        st = game.state
        self.me = me
        self.enemy = next(c for c in st.colors if c != me)
        self.key = 'P' + str(st.color_to_index[me])
        self.ekey = 'P' + str(st.color_to_index[self.enemy])
        self.threats = threats
        self.initial_enemy_public = st.player_state[self.ekey+'_VICTORY_POINTS']
        self.features = {}
        self.rates = {}
        self.by_tile = {}
        for coord, tile in st.board.map.land_tiles.items():
            if tile.resource is None:
                continue
            p = (6 - abs(7 - tile.number)) / 36.0
            r = RES.index(tile.resource)
            for node in tile.nodes.values():
                self.rates.setdefault(node, [0.0] * 5)[r] += p
                self.by_tile.setdefault(coord, []).append((node, r, p))
        self.pool = tuple(max(0, n - st.player_state[self.key+'_'+d+'_IN_HAND']
                         - sum(st.player_state.get('P'+str(i)+'_PLAYED_'+d, 0)
                               for i in range(len(st.colors)))) for d,n in zip(DEVS, DECK))
        self.opp_count = sum(st.player_state[self.ekey+'_'+d+'_IN_HAND'] for d in DEVS)
        self.draw_probs = self._draw_probabilities(st.player_state[self.ekey+'_VICTORY_POINTS'])

    def _draw_probabilities(self, public):
        # Exchangeable allocation conditioned on the necessary real nonterminal VP bound.
        n, v, k = sum(self.pool), self.pool[1], self.opp_count
        if n <= k:
            return (0.0,) * 5
        weights = []
        for h in range(hidden_vp_cap(public, k, v) + 1):
            if 0 <= k-h <= n-v:
                weights.append((h, math.comb(v,h)*math.comb(n-v,k-h)))
        z = sum(w for _,w in weights)
        if not z:
            return tuple(c/n for c in self.pool)  # Conservative model fallback, not truth.
        expected_h = sum(h*w for h,w in weights)/z
        expected_other = k-expected_h
        return tuple((c-expected_h)/(n-k) if j == 1 else
                     (c - expected_other*c/(n-v))/(n-k) if n > v else 0.0
                     for j,c in enumerate(self.pool))

    def board_features(self, g):
        b = g.state.board
        signature = (tuple(sorted(b.buildings.items())), tuple(sorted(b.roads.items())), b.robber_coordinate)
        if signature in self.features:
            return self.features[signature]
        own, enemy = [0.0]*5, [0.0]*5
        for node,(color,kind) in b.buildings.items():
            target = own if color == self.me else enemy
            for i,x in enumerate(self.rates.get(node, (0.0,)*5)):
                target[i] += x * (2 if kind == 'CITY' else 1)
        for node,r,p in self.by_tile.get(b.robber_coordinate, ()):
            if node in b.buildings:
                color,kind = b.buildings[node]
                (own if color == self.me else enemy)[r] -= p*(2 if kind == 'CITY' else 1)
        # At most two additional roads. Potential only; legal actions remain authoritative.
        frontier = set().union(*b.connected_components[self.me]) if b.connected_components[self.me] else set()
        seen = set(frontier)
        best = []
        for depth in range(3):
            sites = frontier.intersection(b.board_buildable_ids)
            best.append(max((self.site_quality(n, own) for n in sites), default=0.0))
            new = set()
            for n in sorted(frontier):
                if b.is_enemy_node(n, self.me):
                    continue
                for other in STATIC_GRAPH.neighbors(n):
                    if other in b.map.land_nodes and not b.is_enemy_road((n,other),self.me) and other not in seen:
                        new.add(other)
            seen.update(new)
            frontier = new
        ports = b.get_player_port_resources(self.me)
        rates = tuple(2 if r in ports else 3 if None in ports else 4 for r in RES)
        result = (tuple(own), tuple(enemy), tuple(best), rates,
                  bool(b.buildable_node_ids(self.enemy)))
        self.features[signature] = result
        return result

    def site_quality(self, node, owned):
        production = self.rates.get(node, (0.0,)*5)
        return sum(x*w for x,w in zip(production,(.95,.95,.9,1.15,1.15))) + .08*sum(x>0 and owned[i]<.055 for i,x in enumerate(production))

    def threat(self, g, h):
        if not self.threats:
            return 0.0
        st, ps = g.state, g.state.player_state
        public = ps[self.ekey+'_VICTORY_POINTS']
        confidence = 1.0 if public >= 9 else .35 if public == 8 and self.opp_count else 0.0
        if not confidence:
            return 0.0
        can_city = bool(st.buildings_by_color[self.enemy]['SETTLEMENT']) and ps[self.ekey+'_CITIES_AVAILABLE'] > 0
        can_settle = ps[self.ekey+'_SETTLEMENTS_AVAILABLE'] > 0 and self.board_features(g)[4]
        affordable = (can_city and can_afford(h,CITY)) or (can_settle and can_afford(h,SETTLE))
        # Current affordability only; a future roll may restore it. .35 is a design risk weight, not a probability.
        return 16.0 * confidence * affordable

    def value(self, g, own_hand=None, enemy_hand=None):
        st, ps = g.state, g.state.player_state
        actual = ps[self.key+'_ACTUAL_VICTORY_POINTS']
        if actual >= g.vps_to_win:
            enemy_public = ps[self.ekey+'_VICTORY_POINTS']
            # Game.winning_color resolves simultaneous qualifiers by color iteration.
            # Use only public increases plus a real-nonterminal hidden-VP bound,
            # never the sampled opponent ACTUAL_VICTORY_POINTS field.
            if st.colors[-1] == self.me or enemy_public <= self.initial_enemy_public:
                return WIN
            cap = hidden_vp_cap(self.initial_enemy_public,self.opp_count,self.pool[1])
            if enemy_public + cap < g.vps_to_win:
                return WIN
            return -WIN if enemy_public >= g.vps_to_win else 0.0
        if ps[self.ekey+'_VICTORY_POINTS'] >= g.vps_to_win:
            return -WIN
        own, enemy, sites, rates, _ = self.board_features(g)
        h = hand(st,self.key) if own_hand is None else own_hand
        eh = hand(st,self.ekey) if enemy_hand is None else enemy_hand
        city_possible = bool(st.buildings_by_color[self.me]['SETTLEMENT']) and ps[self.key+'_CITIES_AVAILABLE'] > 0
        settle_possible = ps[self.key+'_SETTLEMENTS_AVAILABLE'] > 0 and max(sites) > 0
        hand_score = resource_hand_value(h,city_possible,settle_possible)
        # Small surplus/port credit, after reserving useful ingredients.
        hand_score += .45*sum(max(h[i]-2,0)/rates[i] for i in range(5))
        production = sum(x*w for x,w in zip(own,(.95,.95,.9,1.15,1.15)))
        diversity = .10*sum(min(max(x,0)/.08,1) for x in own)
        value = 40.0*actual - 30.0*ps[self.ekey+'_VICTORY_POINTS']
        value += 30.0*(production+diversity) - 22.0*sum(enemy)
        if settle_possible:
            value += 24.0*sites[0] + 12.0*sites[1] + 4.0*sites[2]
        value += hand_score
        played = ps[self.key+'_PLAYED_KNIGHT']
        target = max(3, ps[self.ekey+'_PLAYED_KNIGHT']+1) if ps[self.ekey+'_HAS_ARMY'] else 3
        value += 2.0*min(played,target)
        for d,w in [('KNIGHT',1.6),('ROAD_BUILDING',2.2),('YEAR_OF_PLENTY',2.0),('MONOPOLY',2.2)]:
            value += w*ps[self.key+'_'+d+'_IN_HAND']
        if st.is_road_building and st.current_color() == self.me:
            value += 2.0*st.free_roads_available
        if self.threats:
            length = ps[self.key+'_LONGEST_ROAD_LENGTH']
            opposing = ps[self.ekey+'_LONGEST_ROAD_LENGTH']
            road_target = max(5,opposing+1) if ps[self.ekey+'_HAS_ROAD'] else 5
            if not ps[self.key+'_HAS_ROAD'] and 0 < road_target-length <= 3:
                value += 1.2*(4-(road_target-length))
            elif ps[self.key+'_HAS_ROAD'] and opposing >= length-2:
                value += .4*min(max(length-opposing,0),3)
            value -= self.threat(g,eh)
        return value

    def robber_value(self, g, action):
        moved = g.copy()
        moved.state.board.robber_coordinate = action.value[0]
        own, opp = hand(g.state,self.key), hand(g.state,self.ekey)
        total = sum(opp) if action.value[1] is not None else 0
        if not total:
            return self.value(moved)
        expected = 0.0
        for i,n in enumerate(opp):
            if n:
                a,b = list(own),list(opp)
                a[i] += 1
                b[i] -= 1
                expected += n/total*self.value(moved,tuple(a),tuple(b))
        return expected

    def buy_value(self, g):
        # Do not inspect/execute the sampled deck order. Value all publicly feasible draw types.
        st, ps = g.state, g.state.player_state
        own = hand(st,self.key)
        after = tuple(h-c for h,c in zip(own,DEV_COST))
        delta = self.value(g, own_hand=after)-self.value(g)
        played = ps[self.key+'_PLAYED_KNIGHT']
        knight = 1.6 + (1.5 if played >= 1 and not ps[self.key+'_HAS_ARMY'] else 0)
        vp = WIN-self.value(g) if ps[self.key+'_ACTUAL_VICTORY_POINTS'] == g.vps_to_win-1 else 40.0
        expected = sum(p*v for p,v in zip(self.draw_probs,(knight,vp,2.2,2.0,2.2)))
        return self.value(g)+delta+expected

    def action_value(self, g, action):
        if action.action_type == AT.ROLL:
            return self.value(g), None
        if action.action_type == AT.BUY_DEVELOPMENT_CARD:
            return self.buy_value(g), None
        if action.action_type == AT.MOVE_ROBBER:
            return self.robber_value(g,action), None
        child = g.copy()
        child.execute(action)
        value = self.value(child)
        if value < WIN and child.state.current_prompt == AP.MOVE_ROBBER and child.state.current_color() == self.me:
            value = max((self.robber_value(child,a) for a in child.playable_actions), default=value)
            return value, None  # Exact one-steal expectation; no sampled continuation.
        return value,child

import math


def bank_convertible(hand, cost, ratios, bank):
    """Return True if `cost` is reachable from `hand` plus the ingredient `bank`.

    Cost ingredients already held are reserved first. Each deficit
    max(cost[i] - hand[i], 0) must fit within bank[i]. Remaining surplus
    units past the reserved cost convert to integer trade credits at
    max(hand[i] - cost[i], 0) // ratios[i]; fractional bundles are never
    spent and reserved ingredients are never consumed.
    """
    deficits = [max(c - h, 0) for h, c in zip(hand, cost)]
    if any(d > b for d, b in zip(deficits, bank)):
        return False
    credits = sum(max(h - c, 0) // r for h, c, r in zip(hand, cost, ratios))
    return credits >= sum(deficits)


def estimate_rolls(hand, cost, rates, ratios, bank, horizon=80.0):
    """Estimate the earliest t in [0, horizon] where projected inventory is convertible.

    At time t: collected[i] = min(bank[i], floor(max(rates[i], 0) * t + 1e-9));
    the projected hand is hand + collected and the remaining bank is
    bank - collected. This is a conservative capped mean-production projection,
    not a true expected completion time or probability. Returns 0.0 if
    initially convertible, math.inf if not convertible at the horizon,
    otherwise the smallest verified-feasible t after 18 bisection iterations.
    """

    def convertible_at(t):
        collected = [
            min(b, math.floor(max(r, 0.0) * t + 1e-9))
            for r, b in zip(rates, bank)
        ]
        projected_hand = [h + c for h, c in zip(hand, collected)]
        remaining_bank = [b - c for b, c in zip(bank, collected)]
        return bank_convertible(projected_hand, cost, ratios, remaining_bank)

    if convertible_at(0.0):
        return 0.0
    if not convertible_at(horizon):
        return math.inf
    lo, hi = 0.0, float(horizon)
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        if convertible_at(mid):
            hi = mid
        else:
            lo = mid
    return hi

import math
import random
import time

from catanatron.models.actions import generate_playable_actions
from catanatron.models.enums import ActionType as AT, ActionPrompt as AP
from catanatron.models.board import STATIC_GRAPH

SAFE = frozenset((AT.BUILD_CITY, AT.BUILD_SETTLEMENT, AT.BUILD_ROAD,
                 AT.MARITIME_TRADE, AT.PLAY_YEAR_OF_PLENTY, AT.PLAY_MONOPOLY,
                 AT.PLAY_KNIGHT_CARD, AT.PLAY_ROAD_BUILDING))
PRIORITY = {AT.BUILD_CITY:0, AT.BUILD_SETTLEMENT:1, AT.PLAY_KNIGHT_CARD:2,
            AT.END_TURN:3, AT.ROLL:3, AT.MARITIME_TRADE:4,
            AT.PLAY_YEAR_OF_PLENTY:5, AT.PLAY_MONOPOLY:5, AT.BUILD_ROAD:6}


def action_order(action):
    return PRIORITY.get(action.action_type, 7), repr(action.value)


class RouteContext(Context):
    """A small feasible-plan menu, scored on a capped mean-income projection."""
    def __init__(self, game, me, adaptive=True, cache=True):
        super().__init__(game, me, True)
        self.adaptive = adaptive
        self.geometry = {}
        self.cache_enabled=cache
        self.potential_cache={}
        self.cache_hits=self.cache_misses=self.estimate_calls=0

    def spatial_plans(self, g):
        st, b, ps = g.state, g.state.board, g.state.player_state
        signature = (tuple(sorted(b.buildings.items())), tuple(sorted(b.roads.items())),
                     b.robber_coordinate, ps[self.key+'_CITIES_AVAILABLE'],
                     ps[self.key+'_SETTLEMENTS_AVAILABLE'], ps[self.key+'_ROADS_AVAILABLE'])
        if signature in self.geometry:
            return self.geometry[signature]
        blocked = self.by_tile.get(b.robber_coordinate, ())
        def gain(node):
            return max(0.0, sum(self.rates.get(node, ()))
                       - sum(p for n,_,p in blocked if n == node))
        plans = []
        cities = st.buildings_by_color[self.me]['SETTLEMENT']
        if cities and ps[self.key+'_CITIES_AVAILABLE'] > 0:
            plans.append(('city', CITY, 1, max(gain(n) for n in cities), 0))
        if ps[self.key+'_SETTLEMENTS_AVAILABLE'] > 0:
            frontier = set().union(*b.connected_components[self.me]) if b.connected_components[self.me] else set()
            seen = set(frontier)
            for depth in range(min(2, ps[self.key+'_ROADS_AVAILABLE']) + 1):
                sites = frontier.intersection(b.board_buildable_ids)
                if sites:
                    cost = (1+depth, 1+depth, 1, 1, 0)
                    plans.append(('expand', cost, 1, max(gain(n) for n in sites), 0))
                new = set()
                for n in sorted(frontier):
                    if b.is_enemy_node(n, self.me):
                        continue
                    for m in STATIC_GRAPH.neighbors(n):
                        if m in b.map.land_nodes and m not in seen and not b.is_enemy_road((n,m),self.me):
                            new.add(m)
                seen.update(new)
                frontier = new
        self.geometry[signature] = tuple(plans)
        return self.geometry[signature]

    def road_steps(self, g):
        """Only credit a bonus reachable by an examined legal one/two-road path."""
        ps, b = g.state.player_state, g.state.board
        if ps[self.key+'_HAS_ROAD'] or ps[self.key+'_ROADS_AVAILABLE'] <= 0:
            return None
        target = max(5, ps[self.ekey+'_LONGEST_ROAD_LENGTH']+1) if ps[self.ekey+'_HAS_ROAD'] else 5
        if target-ps[self.key+'_LONGEST_ROAD_LENGTH'] > 2:
            return None
        signature = ('road', tuple(sorted(b.buildings.items())), tuple(sorted(b.roads.items())), target,
                     ps[self.key+'_ROADS_AVAILABLE'])
        if signature in self.geometry:
            return self.geometry[signature]
        frontier = [b]
        examined = 0
        result = None
        for depth in range(1, min(2, ps[self.key+'_ROADS_AVAILABLE'])+1):
            following = []
            for board in frontier:
                for edge in sorted(board.buildable_edges(self.me)):
                    if examined >= 28:
                        break
                    child = board.copy()
                    _,_,lengths = child.build_road(self.me,edge)
                    examined += 1
                    length = lengths[self.me]
                    if length >= target:
                        result = depth
                        break
                    following.append((length, edge, child))
                if result is not None or examined >= 28:
                    break
            if result is not None or examined >= 28:
                break
            frontier = [r[2] for r in sorted(following,key=lambda r:(-r[0],r[1]))[:4]]
        self.geometry[signature] = result
        return result

    def plans(self, g, h):
        ps = g.state.player_state
        plans = list(self.spatial_plans(g))
        if not self.adaptive:
            return [p for p in plans if p[0] == 'city']  # fixed-city ablation
        if not ps[self.key+'_HAS_ARMY']:
            target = max(3, ps[self.ekey+'_PLAYED_KNIGHT']+1) if ps[self.ekey+'_HAS_ARMY'] else 3
            to_play = max(0, target-ps[self.key+'_PLAYED_KNIGHT'])
            to_buy = max(0, to_play-ps[self.key+'_KNIGHT_IN_HAND'])
            probability = self.draw_probs[0]
            buys = math.ceil(to_buy/probability) if probability > 0 else (0 if to_buy == 0 else 100)
            if to_play and to_buy<=self.pool[0] and buys <= min(5, len(g.state.development_listdeck)):
                delay=knight_wait_rolls(to_play,ps[self.key+'_KNIGHT_IN_HAND'],
                    ps[self.key+'_KNIGHT_OWNED_AT_START'],ps[self.key+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN'])
                plans.append(('army', tuple(buys*c for c in DEV_COST), 2, 0.0, delay))
        probability = self.draw_probs[1]
        if probability > 0:
            buys = math.ceil(1/probability)
            if buys <= min(6, len(g.state.development_listdeck)):
                plans.append(('dev', tuple(buys*c for c in DEV_COST), 1, 0.0, 4))
        roads = self.road_steps(g)
        if roads is not None:
            plans.append(('road', (roads,roads,0,0,0), 2, 0.0, 0))
        return plans

    def potential(self, g, h):
        own,_,_,ratios,_ = self.board_features(g)
        # A safety discount for burst/robber risk; not a fitted distribution.
        rates = tuple(max(0.0,r)*.85 for r in own)
        bank = tuple(g.state.resource_freqdeck)
        gap = max(1, g.vps_to_win-g.state.player_state[self.key+'_ACTUAL_VICTORY_POINTS'])
        menu=tuple(self.plans(g,h))
        signature=(tuple(h),rates,ratios,bank,gap,menu)
        if self.cache_enabled and signature in self.potential_cache:
            self.cache_hits+=1
            return self.potential_cache[signature]
        self.cache_misses+=1
        best = 0.0
        for _,cost,points,gain,delay in menu:
            self.estimate_calls+=1
            rolls = estimate_rolls(h,cost,rates,ratios,bank)
            if math.isfinite(rolls):
                value = (8*min(points,gap)+8*gain*min(gap,6)/6)/(1+(rolls+delay)/8)
                best = max(best,value)
        if self.cache_enabled:
            if len(self.potential_cache)>=128:self.potential_cache.clear()
            self.potential_cache[signature]=best
        return best

    def value(self, g, own_hand=None, enemy_hand=None):
        base = super().value(g,own_hand,enemy_hand)
        if abs(base) >= WIN:
            return base
        h = hand(g.state,self.key) if own_hand is None else own_hand
        return base + self.potential(g,h)


class Member4Policy:
    def __init__(self, mode, sampled_replies=True, adaptive=True, forecast_mode="full"):
        self.mode = mode
        self.sampled_replies = sampled_replies
        self.adaptive = adaptive
        self.forecast_mode=forecast_mode
        self.decisions = self.nodes = self.cutoffs = 0
        self.sample_attempts = self.valid_samples = self.reply_nodes = 0
        self.reply_comparisons = self.reply_changes = 0

    def decide(self, obs, actions):
        if not actions:
            raise ValueError('Expected nonempty original legal-action list')
        if len(actions) == 1:
            return 0
        self.decisions += 1
        start = time.process_time()
        cap = .024 if self.mode == 'belief' else .022
        budget = cap if obs.cpu_left is None else max(0.0,min(cap,.22*obs.cpu_left))
        fallback = next((i for i,a in enumerate(actions) if a.action_type in (AT.ROLL,AT.END_TURN)),0)
        terminal=terminal_action(obs,actions)
        if terminal is not None:return terminal
        if budget < .001:
            return fallback
        deadline = start+budget
        world = obs.sample_world(random.Random(0))
        ctx = RouteContext(world,obs.me,self.adaptive) if self.mode == 'route' else Context(world,obs.me,True)
        if world.state.current_prompt == AP.BUILD_INITIAL_SETTLEMENT:
            own = ctx.board_features(world)[0]
            def opening(i):
                rates = ctx.rates.get(actions[i].value,(0.0,)*5)
                combined = tuple(a+b for a,b in zip(own,rates))
                return sum(x*w for x,w in zip(combined,(.95,.95,.9,1.15,1.15))) + .10*sum(min(x/.08,1) for x in combined)
            return max(range(len(actions)),key=opening)
        ranked = []
        has_roll = any(a.action_type == AT.ROLL for a in actions)
        root_deadline = min(deadline,start+.011)
        for i in sorted(range(len(actions)),key=lambda i:(PRIORITY.get(actions[i].action_type,7),i)):
            if ranked and time.process_time() >= root_deadline:
                self.cutoffs += 1
                break
            a = actions[i]
            if has_roll and a.action_type not in (AT.ROLL,AT.PLAY_KNIGHT_CARD):
                continue
            value, child = ctx.action_value(world,a)
            self.nodes += 1
            if value >= WIN:
                return i
            if obs.my_actual_vps >= 9 and child is not None and child.state.current_color()==obs.me:
                for completion in child.playable_actions:
                    if completion.action_type in (AT.BUILD_CITY,AT.BUILD_SETTLEMENT):
                        end = child.copy();end.execute(completion);self.nodes += 1
                        if ctx.value(end) >= WIN:
                            return i
            ranked.append((value,i,child))
        if not ranked:
            return fallback
        best = max(ranked,key=lambda r:(r[0],-r[1]))
        if world.state.current_prompt != AP.PLAY_TURN or has_roll or world.state.is_road_building:
            return int(best[1])
        if self.mode == 'route':
            return self.route_search(world,ctx,ranked,best,deadline)
        return self.belief_search(obs,actions,world,ctx,ranked,best,deadline)

    def route_search(self, world, ctx, ranked, best, deadline):
        incumbent, best_value = best[1], best[0]
        frontier = sorted((r for r in ranked if r[2] is not None and r[2].state.current_color()==ctx.me),key=lambda r:(-r[0],r[1]))[:3]
        seen = set()
        count = 0
        for depth in (2,3):
            following = []
            for _,root,g in frontier:
                if g.state.num_turns != world.state.num_turns or g.state.current_prompt != AP.PLAY_TURN:
                    continue
                for a in sorted(g.playable_actions,key=action_order):
                    if time.process_time() >= deadline or count >= 42:
                        self.cutoffs += 1
                        return int(incumbent)
                    if a.action_type not in SAFE:
                        continue
                    value, child = ctx.action_value(g,a)
                    count += 1;self.nodes += 1
                    if value >= WIN:
                        return int(root)
                    value -= .04*(depth-1)
                    if value > best_value:
                        incumbent,best_value = root,value
                    if child is not None and child.state.current_color()==ctx.me:
                        signature = (tuple(sorted(child.state.player_state.items())),
                                     tuple(sorted(child.state.board.roads.items())),
                                     tuple(sorted(child.state.board.buildings.items())),
                                     child.state.current_prompt,child.state.free_roads_available)
                        if signature not in seen:
                            seen.add(signature);following.append((value,root,child))
            frontier = sorted(following,key=lambda r:(-r[0],r[1]))[:3]
        return int(incumbent)

    @staticmethod
    def valid_belief(g, me):
        enemy = next(c for c in g.state.colors if c != me)
        k = 'P'+str(g.state.color_to_index[enemy])
        return g.state.player_state[k+'_ACTUAL_VICTORY_POINTS'] < g.vps_to_win

    def sample_beliefs(self, obs, deadline):
        worlds = []
        rng = random.Random(17)
        for _ in range(12):
            if time.process_time() >= deadline:
                return []
            g = obs.sample_world(rng);self.sample_attempts += 1
            if self.valid_belief(g,obs.me):
                worlds.append(g);self.valid_samples += 1
                if len(worlds)==3:
                    return worlds
        return []

    def forecast_end(self, world, action, ctx, deadline):
        if action.action_type not in SAFE and action.action_type != AT.END_TURN:
            return None
        g = world.copy();g.execute(action);self.nodes += 1
        if ctx.value(g) >= WIN:
            return g
        if g.state.current_prompt != AP.PLAY_TURN:
            return None
        if g.state.current_color() == ctx.me:
            if g.state.is_road_building:
                return None
            # One greedy deterministic follow-up, then voluntarily stop our forecasted turn.
            base = ctx.value(g);chosen = None
            for a in sorted(g.playable_actions,key=action_order)[:12]:
                if time.process_time() >= deadline:
                    return None
                if a.action_type not in SAFE:
                    continue
                value, child = ctx.action_value(g,a);self.nodes += 1
                if child is not None and child.state.current_prompt==AP.PLAY_TURN and not child.state.is_road_building and value>base:
                    base,chosen = value,child
            if chosen is not None:
                g = chosen
            if ctx.value(g) >= WIN:
                return g
            stop = next((a for a in g.playable_actions if a.action_type==AT.END_TURN),None)
            if stop is None:
                return None
            g.execute(stop)
        if g.state.current_color()!=ctx.enemy or g.state.player_state[ctx.ekey+'_HAS_ROLLED']:
            return None
        # This is a NEW opponent turn, so all currently held sampled cards are old.
        for d in DEVS:
            if d != 'VICTORY_POINT':
                g.state.player_state[ctx.ekey+'_'+d+'_OWNED_AT_START'] = g.state.player_state[ctx.ekey+'_'+d+'_IN_HAND'] > 0
        g.state.player_state[ctx.ekey+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN'] = False
        g.playable_actions = generate_playable_actions(g.state)
        return g

    @staticmethod
    def enemy_robber_value(g, action, ctx):
        moved = g.copy();moved.state.board.robber_coordinate = action.value[0]
        own,enemy = hand(g.state,ctx.key),hand(g.state,ctx.ekey)
        if action.value[1] != ctx.me or not sum(own):
            return ctx.value(moved)
        result = 0.0
        for i,n in enumerate(own):
            if n:
                a,b = list(own),list(enemy);a[i]-=1;b[i]+=1
                result += n/sum(own)*ctx.value(moved,tuple(a),tuple(b))
        return result

    @staticmethod
    def reply_shortlist(g,ctx,replies):
        """Round-robin families: relevant resources before numeric action order."""
        enemy=hand(g.state,ctx.ekey);own=hand(g.state,ctx.key);ps=g.state.player_state
        goals=[]
        if g.state.buildings_by_color[ctx.enemy]['SETTLEMENT'] and ps[ctx.ekey+'_CITIES_AVAILABLE']>0:goals.append(CITY)
        if ps[ctx.ekey+'_SETTLEMENTS_AVAILABLE']>0 and g.state.board.buildable_node_ids(ctx.enemy):goals.append(SETTLE)
        def readiness(h):
            return max((sum(min(x,c) for x,c in zip(h,cost))+4*all(x>=c for x,c in zip(h,cost)) for cost in goals),default=0)
        groups={}
        for a in replies:
            score=0.0
            if a.action_type==AT.PLAY_MONOPOLY:
                j=RES.index(a.value)
                if own[j]==0:continue
                h=list(enemy);h[j]+=own[j]
                score=readiness(h)-readiness(enemy)+.2*own[j]
            elif a.action_type==AT.PLAY_YEAR_OF_PLENTY:
                h=list(enemy)
                for resource in a.value:h[RES.index(resource)]+=1
                score=readiness(h)-readiness(enemy)
            groups.setdefault(a.action_type,[]).append((score,a))
        order=(AT.PLAY_KNIGHT_CARD,AT.PLAY_MONOPOLY,AT.PLAY_YEAR_OF_PLENTY,AT.PLAY_ROAD_BUILDING)
        for family in groups:groups[family].sort(key=lambda x:(-x[0],repr(x[1].value)))
        selected=[]
        for rank in range(8):
            for family in order:
                options=groups.get(family,())
                if rank<len(options):selected.append(options[rank][1])
                if len(selected)==8:return selected
        return selected

    def opponent_reply(self, g, ctx, deadline):
        baseline = ctx.value(g)
        worst = baseline
        replies = [a for a in g.playable_actions if a.action_type in
                   (AT.PLAY_KNIGHT_CARD,AT.PLAY_MONOPOLY,AT.PLAY_ROAD_BUILDING,AT.PLAY_YEAR_OF_PLENTY)]
        for a in self.reply_shortlist(g,ctx,replies):
            if time.process_time() >= deadline:
                return None
            child = g.copy();child.execute(a);self.reply_nodes += 1
            if child.state.player_state[ctx.ekey+'_ACTUAL_VICTORY_POINTS'] >= child.vps_to_win:
                value = baseline-180.0  # conditional sampled victory, bounded risk cost
            elif child.state.current_prompt == AP.MOVE_ROBBER:
                values = []
                def robber_priority(move):
                    damage = 0.0
                    for node,_,p in ctx.by_tile.get(move.value[0],()):
                        building = child.state.board.buildings.get(node)
                        if building:
                            damage += p*(2 if building[1]=='CITY' else 1)*(1 if building[0]==ctx.me else -1)
                    return -damage, repr(move.value)
                for move in sorted(child.playable_actions,key=robber_priority)[:6]:
                    if time.process_time() >= deadline:
                        return None
                    values.append(self.enemy_robber_value(child,move,ctx));self.reply_nodes += 1
                value = min(values,default=baseline)
            elif child.state.is_road_building:
                for _ in range(2):
                    options=[]
                    for move in sorted(child.playable_actions,key=action_order)[:6]:
                        if time.process_time() >= deadline:
                            return None
                        if move.action_type != AT.BUILD_ROAD:
                            continue
                        c = child.copy();c.execute(move);self.reply_nodes += 1
                        score = ctx.value(c)
                        options.append((score,-c.state.player_state[ctx.ekey+'_LONGEST_ROAD_LENGTH'],c))
                    if not options:
                        break
                    child = min(options,key=lambda r:(r[0],r[1]))[2]
                    if not child.state.is_road_building:
                        break
                value = baseline-180.0 if child.state.player_state[ctx.ekey+'_ACTUAL_VICTORY_POINTS']>=child.vps_to_win else ctx.value(child)
            else:
                value = ctx.value(child)
            worst = min(worst,max(baseline-180.0,value))
        return baseline-.7*(baseline-worst)

    def belief_search(self, obs, actions, world, ctx, ranked, best, deadline):
        if self.forecast_mode=="root" or not obs.opp_dev_count or world.state.current_color()!=obs.me:
            return int(best[1])
        eligible = [r for r in ranked if r[2] is not None and
                    (actions[r[1]].action_type in SAFE or actions[r[1]].action_type==AT.END_TURN)
                    and r[0] >= best[0]-8.0]
        eligible = sorted(eligible,key=lambda r:(-r[0],r[1]))[:3]
        if len(eligible)<2 or best[1] not in [r[1] for r in eligible] or deadline-time.process_time()<.003:
            return int(best[1])
        full=self.sampled_replies and self.forecast_mode=="full"
        worlds = self.sample_beliefs(obs,deadline) if full else [world]
        if not worlds:
            return int(best[1])
        totals = {r[1]:0.0 for r in eligible}
        for sample in worlds:
            for _,index,_ in eligible:
                end = self.forecast_end(sample,actions[index],ctx,deadline)
                if end is None or time.process_time() >= deadline:
                    self.cutoffs += 1
                    return int(best[1])
                value = ctx.value(end)
                if value >= WIN:
                    return int(index)
                if full:
                    value = self.opponent_reply(end,ctx,deadline)
                    if value is None:
                        self.cutoffs += 1
                        return int(best[1])
                totals[index] += value/len(worlds)
        self.reply_comparisons += 1
        chosen = max(totals,key=lambda i:(totals[i],-i))
        self.reply_changes += chosen != best[1]
        return int(chosen)

class Agent(Member4Policy):
    def __init__(self):
        super().__init__('belief')
