"""B01: Aroosh Member 1, standalone v002 correctness revision. Pinned organizer engine required."""

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

from catanatron.models.board import STATIC_GRAPH

class SpatialContext(Context):
    def __init__(self,game,me):
        super().__init__(game,me,True)
        self.geometry={}

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

def conversion_gap(hand, cost, ratios, bank):
    """Target cards still unavailable after optimal direct trades.

    Uses only surplus beyond reserved cost. Returns the integer
    max(blocked, sum(missing) - credits), where missing[i] is the
    shortfall per resource, blocked counts shortfalls the bank cannot
    cover, and credits are tradeable surplus units.
    """
    missing = [max(c - h, 0) for c, h in zip(cost, hand)]
    blocked = sum(max(m - b, 0) for m, b in zip(missing, bank))
    credits = sum(max(h - c, 0) // r for h, c, r in zip(hand, cost, ratios))
    return max(blocked, sum(missing) - credits)


def goal_priority(hand, cost, ratios, bank, reward):
    """Heuristic priority score for a goal with the given reward.

    Explicitly chosen heuristic, not a probability or learned
    coefficient: reward / (1 + conversion_gap + 0.35*sum(missing)
    + blocked).
    """
    missing = [max(c - h, 0) for c, h in zip(cost, hand)]
    blocked = sum(max(m - b, 0) for m, b in zip(missing, bank))
    return reward / (1.0 + conversion_gap(hand, cost, ratios, bank)
                     + 0.35 * sum(missing) + blocked)


def improves_goal(before, after, cost, ratios, bank_before, bank_after):
    """True only if total missing strictly decreases and gap does not rise.

    Requires sum(max(cost - after, 0)) < sum(max(cost - before, 0))
    and conversion_gap(after, ...) <= conversion_gap(before, ...).
    This forbids a trade consuming one missing ingredient just to
    replace it with another.
    """
    before_missing = sum(max(c - h, 0) for c, h in zip(cost, before))
    after_missing = sum(max(c - h, 0) for c, h in zip(cost, after))
    if after_missing >= before_missing:
        return False
    return conversion_gap(after, cost, ratios, bank_after) <= \
        conversion_gap(before, cost, ratios, bank_before)

import time
from catanatron.models.enums import ActionType as AT


def public_terminal(g, me, initial_enemy_public, opp_count, unseen_vps):
    ps=g.state.player_state
    k='P'+str(g.state.color_to_index[me])
    enemy=next(c for c in g.state.colors if c!=me)
    ek='P'+str(g.state.color_to_index[enemy])
    if ps[k+'_ACTUAL_VICTORY_POINTS'] < g.vps_to_win:
        return False
    public=ps[ek+'_VICTORY_POINTS']
    return (g.state.colors[-1]==me or public<=initial_enemy_public or
            public+hidden_vp_cap(initial_enemy_public,opp_count,unseen_vps)<g.vps_to_win)


def immediate_terminal(g, me, actual, public, count, unseen, actions, limit=12, deadline=None):
    gap=g.vps_to_win-actual
    if gap>3:return None,0,False
    ps=g.state.player_state;k='P'+str(g.state.color_to_index[me])
    enemy=next(c for c in g.state.colors if c!=me);ek='P'+str(g.state.color_to_index[enemy])
    for i,a in enumerate(actions):
        if a.action_type==AT.BUILD_CITY and gap<=1:return i,0,False
        if a.action_type==AT.PLAY_KNIGHT_CARD and gap<=2:
            played=ps[k+'_PLAYED_KNIGHT']+1
            if not ps[k+'_HAS_ARMY'] and played>=3 and (not ps[ek+'_HAS_ARMY'] or played>ps[ek+'_PLAYED_KNIGHT']):
                return i,0,False
    copies=0
    for i,a in enumerate(actions):
        if a.action_type not in (AT.BUILD_SETTLEMENT,AT.BUILD_ROAD):continue
        if a.action_type==AT.BUILD_ROAD and gap>2:continue
        if copies>=limit or (deadline is not None and time.process_time()>=deadline):return None,copies,True
        child=g.copy();child.execute(a);copies+=1
        if public_terminal(child,me,public,count,unseen):return i,copies,False
    return None,copies,False


def terminal_action(obs,actions):
    return immediate_terminal(obs._game,obs.me,obs.my_actual_vps,obs.opp_public_vps,
                              obs.opp_dev_count,max(0,5-obs.my_devs['VICTORY_POINT']),actions)[0]


def terminal_trade(obs,actions,deadline):
    """Only one maritime trade then legal build; <=12 trades, <=48 executions.

    No heuristic trade permission or sampled hidden score participates. Original
    root index is retained. A timeout/cap means unsearched, never impossible.
    """
    g=obs._game;gap=g.vps_to_win-obs.my_actual_vps
    if gap>2:return None,0,False
    k='P'+str(g.state.color_to_index[obs.me]);ps=g.state.player_state
    costs=[]
    if gap<=1:costs.append((0,0,0,2,3))
    # Settlement may transfer Road as well as add its ordinary VP.
    costs.append((1,1,1,1,0))
    if gap<=2 and not ps[k+'_HAS_ROAD'] and ps[k+'_LONGEST_ROAD_LENGTH']>=4:
        costs.append((1,1,0,0,0))
    res=('WOOD','BRICK','SHEEP','WHEAT','ORE')
    h=tuple(ps[k+'_'+r+'_IN_HAND'] for r in res)
    copies=trades=0
    for i,a in enumerate(actions):
        if a.action_type!=AT.MARITIME_TRADE:continue
        after=list(h)
        for r in a.value[:-1]:
            if r is not None:after[res.index(r)]-=1
        after[res.index(a.value[-1])]+=1
        if not any(all(x>=n for x,n in zip(after,cost)) for cost in costs):continue
        if trades>=12 or copies>=48 or time.process_time()>=deadline:return None,copies,True
        child=g.copy();child.execute(a);copies+=1;trades+=1
        completion,n,cut=immediate_terminal(child,obs.me,obs.my_actual_vps,obs.opp_public_vps,
            obs.opp_dev_count,max(0,5-obs.my_devs['VICTORY_POINT']),child.playable_actions,
            limit=min(12,48-copies),deadline=deadline)
        copies+=n
        if completion is not None:return i,copies,cut
        if cut:return None,copies,True
    return None,copies,False

import random
import time

from catanatron.models.enums import ActionType as AT, ActionPrompt as AP

SAFE=frozenset((AT.BUILD_CITY,AT.BUILD_SETTLEMENT,AT.BUILD_ROAD,AT.MARITIME_TRADE,
                AT.PLAY_YEAR_OF_PLENTY,AT.PLAY_MONOPOLY,AT.PLAY_KNIGHT_CARD,AT.PLAY_ROAD_BUILDING))
PRIORITY={AT.BUILD_CITY:0,AT.BUILD_SETTLEMENT:1,AT.PLAY_KNIGHT_CARD:2,
          AT.END_TURN:3,AT.ROLL:3,AT.MARITIME_TRADE:4,
          AT.PLAY_YEAR_OF_PLENTY:5,AT.PLAY_MONOPOLY:5,AT.BUILD_ROAD:6}


class EconomyContext(SpatialContext):
    def __init__(self,game,me,engine=False):
        super().__init__(game,me)
        self.engine=engine
        self.family=None
        h=hand(game.state,self.key)
        plans=self.specs(game)
        if plans:
            best=max(plans,key=lambda p:self.priority(game,h,p))
            if engine and self.investment_window(game):
                cities=[p for p in plans if p[0]=='city']
                if cities:
                    city=max(cities,key=lambda p:self.priority(game,h,p))
                    ratios=self.board_features(game)[3]
                    if conversion_gap(h,city[1],ratios,tuple(game.state.resource_freqdeck))<=2:
                        best=city
            self.family=best[0]

    def investment_window(self,g):
        own=self.board_features(g)[0]
        ps=g.state.player_state
        return ps[self.key+'_ACTUAL_VICTORY_POINTS']<=7 and own[3]+own[4]>=.09

    def specs(self,g):
        ps=g.state.player_state
        plans=[]
        for name,cost,_,gain,_ in self.spatial_plans(g):
            reward=12.0+8.0*gain
            plans.append((name,cost,reward))
        nonvp=sum(ps[self.key+'_'+d+'_IN_HAND'] for d in DEVS if d!='VICTORY_POINT')
        if len(g.state.development_listdeck) and nonvp<3:
            # A readiness heuristic; actual draw expectation is evaluated separately.
            reward=2+5*self.draw_probs[1]+(1.5*self.draw_probs[0] if not ps[self.key+'_HAS_ARMY'] else 0)
            plans.append(('dev',DEV_COST,reward))
        return plans

    def priority(self,g,h,plan):
        ratios=self.board_features(g)[3]
        return goal_priority(h,plan[1],ratios,tuple(g.state.resource_freqdeck),plan[2])

    def goal(self,g,h):
        plans=self.specs(g)
        retained=[p for p in plans if p[0]==self.family]
        return max(retained or plans,key=lambda p:self.priority(g,h,p),default=None)

    def value(self,g,own_hand=None,enemy_hand=None):
        base=Context.value(self,g,own_hand,enemy_hand)
        if abs(base)>=WIN:
            return base
        ps=g.state.player_state
        h=hand(g.state,self.key) if own_hand is None else own_hand
        own,_,sites,ratios,_=self.board_features(g)
        city=bool(g.state.buildings_by_color[self.me]['SETTLEMENT']) and ps[self.key+'_CITIES_AVAILABLE']>0
        settle=ps[self.key+'_SETTLEMENTS_AVAILABLE']>0 and max(sites)>0
        # Replace the generic simultaneous-city/settlement hand formula with a
        # feasible retained-goal formula; all other public position terms stay.
        generic=resource_hand_value(h,city,settle)+.45*sum(max(h[i]-2,0)/ratios[i] for i in range(5))
        goal=self.goal(g,h)
        readiness=self.priority(g,h,goal) if goal is not None else 0.0
        useful=.15*sum(min(h[i],(goal[1][i] if goal else 0)+ratios[i]) for i in range(5))
        value=base-generic+readiness+useful-.5*max(sum(h)-7,0)
        if self.engine:
            gap=max(1,g.vps_to_win-ps[self.key+'_ACTUAL_VICTORY_POINTS'])
            value+=8*min(gap/4,1)*(1.2*own[3]+1.4*own[4]+.35*own[2])
        return value

    def buy_value(self,g):
        ps=g.state.player_state
        nonvp=sum(ps[self.key+'_'+d+'_IN_HAND'] for d in DEVS if d!='VICTORY_POINT')
        if nonvp>=3 and not (ps[self.key+'_ACTUAL_VICTORY_POINTS']>=9 and self.draw_probs[1]>0):
            return self.value(g)-1  # END_TURN is preferable to unused-card accumulation.
        base=Context.buy_value(self,g)
        if not self.engine:
            return base
        # Probability-weighted Army investment, not an assumed Knight draw.
        bonus=0.0
        if not ps[self.key+'_HAS_ARMY']:
            target=max(3,ps[self.ekey+'_PLAYED_KNIGHT']+1) if ps[self.ekey+'_HAS_ARMY'] else 3
            need=max(0,target-ps[self.key+'_PLAYED_KNIGHT']-ps[self.key+'_KNIGHT_IN_HAND'])
            if need>0:
                bonus=self.draw_probs[0]*(4.0 if need==1 else 2.0)
        if ps[self.key+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN']:
            bonus*=.5
        return base+bonus

    def trade_allowed(self,g,child,action):
        h=hand(g.state,self.key)
        goal=self.goal(g,h)
        if goal is None:
            return False
        # Never export a resource imported earlier this turn. This prevents a
        # circular/intermediate conversion plan; it can omit some later trades.
        imported=set()
        for record in reversed(g.state.action_records):
            a=record.action
            if a.action_type==AT.ROLL or a.color!=self.me:
                break
            if a.action_type==AT.MARITIME_TRADE:
                imported.add(a.value[-1])
        given=next(r for r in action.value[:-1] if r is not None)
        if given in imported:
            return False
        return improves_goal(h,hand(child.state,self.key),goal[1],self.board_features(g)[3],
                             tuple(g.state.resource_freqdeck),tuple(child.state.resource_freqdeck))

    def action_value(self,g,action):
        value,child=Context.action_value(self,g,action)
        if action.action_type==AT.MARITIME_TRADE and not self.trade_allowed(g,child,action):
            return -float('inf'),None
        return value,child


class EconomyPolicy:
    def __init__(self,engine=False):
        self.engine=engine
        self.decisions=self.nodes=self.cutoffs=0
        self.city_commitments=self.discard_goals=0
        self.terminal_checks=self.terminal_nodes=self.terminal_cutoffs=self.terminal_trades=0

    def decide(self,obs,actions):
        if not actions:
            raise ValueError('Expected nonempty original legal-action list')
        if len(actions)==1:
            return 0
        self.decisions+=1
        start=time.process_time()
        budget=.022 if obs.cpu_left is None else max(0.0,min(.022,.22*obs.cpu_left))
        fallback=next((i for i,a in enumerate(actions) if a.action_type in (AT.ROLL,AT.END_TURN)),0)
        self.terminal_checks+=1
        terminal=terminal_action(obs,actions)
        if terminal is not None:return int(terminal)
        if budget<.001:
            return fallback
        deadline=start+budget
        terminal,nodes,cut=terminal_trade(obs,actions,min(deadline,start+.004))
        self.terminal_nodes+=nodes;self.terminal_cutoffs+=cut
        if terminal is not None:
            self.terminal_trades+=1
            return int(terminal)
        world=obs.sample_world(random.Random(0))
        ctx=EconomyContext(world,obs.me,self.engine)
        if world.state.current_prompt==AP.BUILD_INITIAL_SETTLEMENT:
            own=ctx.board_features(world)[0]
            def opening(i):
                combined=tuple(a+b for a,b in zip(own,ctx.rates.get(actions[i].value,(0.0,)*5)))
                if self.engine:
                    return sum(x*w for x,w in zip(combined,(.8,.8,1.1,1.6,1.7)))+.075*sum(min(x/.08,1) for x in combined)
                return sum(x*w for x,w in zip(combined,(1,1,1,1.15,1.1)))+.11*sum(min(x/.08,1) for x in combined)
            return max(range(len(actions)),key=opening)
        if world.state.current_prompt==AP.DISCARD:
            h=hand(world.state,ctx.key);goal=ctx.goal(world,h)
            if goal is not None:
                self.discard_goals+=1
                ratios=ctx.board_features(world)[3]
                def retained(i):
                    index=RES.index(actions[i].value)
                    after=list(h);after[index]-=1
                    bank=list(world.state.resource_freqdeck);bank[index]+=1
                    return goal_priority(tuple(after),goal[1],ratios,tuple(bank),goal[2]),h[index]-goal[1][index],-i
                return max(range(len(actions)),key=retained)
        ranked=[]
        has_roll=any(a.action_type==AT.ROLL for a in actions)
        for i in sorted(range(len(actions)),key=lambda i:(PRIORITY.get(actions[i].action_type,7),i)):
            if ranked and time.process_time()>=min(deadline,start+.011):
                self.cutoffs+=1;break
            a=actions[i]
            if has_roll and a.action_type not in (AT.ROLL,AT.PLAY_KNIGHT_CARD):continue
            value,child=ctx.action_value(world,a);self.nodes+=1
            if value>=WIN:return i
            # Check short certain endgame completions before chance-valued BUY.
            if obs.my_actual_vps>=9 and child is not None and child.state.current_color()==obs.me:
                for completion in child.playable_actions:
                    if completion.action_type in (AT.BUILD_CITY,AT.BUILD_SETTLEMENT):
                        end=child.copy();end.execute(completion);self.nodes+=1
                        if ctx.value(end)>=WIN:return i
            ranked.append((value,i,child))
        if not ranked:return fallback
        best=max(ranked,key=lambda r:(r[0],-r[1]))
        if self.engine and ctx.investment_window(world):
            cities=[r for r in ranked if actions[r[1]].action_type==AT.BUILD_CITY and r[0]>=best[0]-5]
            if cities:
                # Explicit investment commitment among near-equivalent choices.
                best=max(cities,key=lambda r:(r[0],-r[1]));self.city_commitments+=1
        if world.state.current_prompt!=AP.PLAY_TURN or has_roll:
            return int(best[1])
        return self.complete_purchases(world,ctx,ranked,best,deadline)

    def complete_purchases(self,world,ctx,ranked,best,deadline):
        incumbent,best_value=best[1],best[0]
        frontier=sorted((r for r in ranked if r[2] is not None and r[2].state.current_color()==ctx.me),key=lambda r:(-r[0],r[1]))[:4]
        seen=set();count=0
        for depth in (2,3):
            following=[]
            for _,root,g in frontier:
                if g.state.num_turns!=world.state.num_turns or g.state.current_prompt!=AP.PLAY_TURN:continue
                for a in sorted(g.playable_actions,key=lambda a:(PRIORITY.get(a.action_type,7),repr(a.value))):
                    if time.process_time()>=deadline or count>=52:
                        self.cutoffs+=1;return int(incumbent)
                    if a.action_type not in SAFE:continue
                    value,child=ctx.action_value(g,a);count+=1;self.nodes+=1
                    if value>=WIN:return int(root)
                    value-=.04*(depth-1)
                    if value>best_value:incumbent,best_value=root,value
                    if child is not None and child.state.current_color()==ctx.me:
                        signature=(tuple(sorted(child.state.player_state.items())),tuple(sorted(child.state.board.roads.items())),
                                   tuple(sorted(child.state.board.buildings.items())),child.state.current_prompt,child.state.free_roads_available)
                        if signature not in seen:seen.add(signature);following.append((value,root,child))
            frontier=sorted(following,key=lambda r:(-r[0],r[1]))[:4]
        return int(incumbent)

class Agent(EconomyPolicy):
    def __init__(self):
        super().__init__(engine=False)
