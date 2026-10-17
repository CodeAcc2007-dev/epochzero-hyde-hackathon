"""Pranesh's standalone tactics policies for the pinned Hyde Catan kit.

No network, learning, workers, seed prediction, or opponent hidden-card reads.
A sampled copy supplies the public engine interface; sampled opponent VP/dev
identities and sampled deck order are deliberately never evaluated.
"""
import math
import random
import time

from catanatron.models.enums import ActionType as AT, ActionPrompt as AP
from catanatron.models.board import STATIC_GRAPH
from race_math import can_afford, deficit, hidden_vp_cap
from terminal_math import terminal_action
from round2_math import one_trade_build

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

    def threat_categories(self, g, h):
        """Conditional public-hand completions, not a forecast through a roll."""
        ps=g.state.player_state
        goals=[]
        if g.state.buildings_by_color[self.enemy]['SETTLEMENT'] and ps[self.ekey+'_CITIES_AVAILABLE']>0:
            goals.append(('city',CITY))
        if ps[self.ekey+'_SETTLEMENTS_AVAILABLE']>0 and self.board_features(g)[4]:
            goals.append(('settlement',SETTLE))
        ports=g.state.board.get_player_port_resources(self.enemy)
        ratios=tuple(2 if r in ports else 3 if None in ports else 4 for r in RES)
        bank=tuple(g.state.resource_freqdeck)
        direct=tuple(name for name,cost in goals if can_afford(h,cost))
        converted=[]
        for name,cost in goals:
            if not can_afford(h,cost):
                trades=one_trade_build(h,cost,ratios,bank)
                if trades:converted.append((name,trades))
        converted=tuple(converted)
        public=ps[self.ekey+'_VICTORY_POINTS']
        return {'affordable_now':direct,'one_trade_if_hand_persists':converted,
                'roll_boundary_pending':not ps[self.ekey+'_HAS_ROLLED'],
                'hidden_dev_conditional':public==8 and self.opp_count>0}

    def threat(self, g, h):
        if not self.threats:return 0.0
        public=g.state.player_state[self.ekey+'_VICTORY_POINTS']
        confidence=1.0 if public>=9 else .35 if public==8 and self.opp_count else 0.0
        if not confidence:return 0.0
        categories=self.threat_categories(g,h)
        # Preserve the parent's immediate-risk weight; lower weight for a
        # one-trade opportunity conditional on surviving the next roll/discard.
        risk=16.0 if categories['affordable_now'] else 12.0 if categories['one_trade_if_hand_persists'] else 0.0
        return confidence*risk

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


def state_key(g):
    st = g.state
    # Per-decision search, one fixed public context. No chance branches/deck draws are expanded.
    return (tuple(sorted(st.player_state.items())),tuple(sorted(st.board.buildings.items())),
            tuple(sorted(st.board.roads.items())),tuple(st.resource_freqdeck),st.current_prompt,
            st.current_player_index,st.current_turn_index,st.is_road_building,st.free_roads_available)


class Policy:
    def __init__(self, mode):
        self.mode = mode
        self.search_nodes = 0
        self.cutoffs = 0
        self.decisions = 0
        self.enabler_slots = 0
        self.roots_examined = 0

    def decide(self, obs, actions):
        if not actions:
            raise ValueError('Official contract requires a nonempty legal-action list')
        if len(actions) == 1:
            return 0
        self.decisions += 1
        started = time.process_time()
        allowance = obs.cpu_left
        cap = .022 if self.mode == 'beam' else .016
        budget = cap if allowance is None else max(0.0,min(cap,.22*allowance))
        deadline = started+budget
        terminal=terminal_action(obs,actions)
        if terminal is not None:
            return terminal
        fallback = next((i for i,a in enumerate(actions) if a.action_type in (AT.ROLL,AT.END_TURN)),0)
        if budget < .001:
            return int(fallback)
        world = obs.sample_world(random.Random(0))
        ctx = Context(world,obs.me,self.mode == 'threat')
        ps = world.state.player_state
        for i,a in enumerate(actions):
            if a.action_type == AT.PLAY_KNIGHT_CARD and obs.my_actual_vps >= 8:
                k,e = ctx.key,ctx.ekey
                count = ps[k+'_PLAYED_KNIGHT']+1
                if not ps[k+'_HAS_ARMY'] and count>=3 and (not ps[e+'_HAS_ARMY'] or count>ps[e+'_PLAYED_KNIGHT']):
                    return i
        # Cheap fallback established before any search. Timing cutoff never returns a fabricated action.
        if world.state.current_prompt == AP.BUILD_INITIAL_SETTLEMENT:
            current = ctx.board_features(world)[0]
            return max(range(len(actions)),key=lambda i: self._opening(ctx,current,actions[i].value))
        baseline = ctx.value(world)
        ranked = []
        best, best_value = fallback, -float('inf')
        # Stable cheap priorities reduce damage if a large root list reaches its cap.
        priority = {AT.BUILD_CITY:0,AT.BUILD_SETTLEMENT:1,AT.PLAY_KNIGHT_CARD:2,
                    AT.END_TURN:3,AT.ROLL:3,AT.MARITIME_TRADE:4,AT.PLAY_YEAR_OF_PLENTY:5}
        order = sorted(range(len(actions)),key=lambda i:(priority.get(actions[i].action_type,6),i))
        for i in order:
            if ranked and time.process_time() > deadline:
                self.cutoffs += 1
                break
            a = actions[i]
            # Before roll: save non-Knight devs for known post-roll needs. Do not simulate a lucky roll.
            if AT.ROLL in {x.action_type for x in actions} and a.action_type not in (AT.ROLL,AT.PLAY_KNIGHT_CARD):
                continue
            value,child = ctx.action_value(world,a)
            self.search_nodes += 1
            self.roots_examined += 1
            # Cover all short terminal enablers before pruning a beam shortlist.
            if (self.mode == 'beam' and obs.my_actual_vps >= 8 and child is not None
                    and a.action_type in DETERMINISTIC and child.state.current_color() == obs.me
                    and child.state.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS'] < child.vps_to_win):
                for completion in child.playable_actions:
                    if time.process_time()>deadline:break
                    if completion.action_type in (AT.BUILD_CITY,AT.BUILD_SETTLEMENT,AT.BUILD_ROAD,AT.PLAY_KNIGHT_CARD):
                        terminal = child.copy()
                        terminal.execute(completion)
                        self.search_nodes += 1
                        if ctx.value(terminal) >= WIN:
                            return int(i)
            ranked.append((value,i,child))
            if value > best_value:
                best,best_value=i,value
            if value >= WIN:
                return i
        if self.mode != 'beam' or world.state.current_prompt != AP.PLAY_TURN or time.process_time()>deadline:
            return int(best)
        # Root shortlist includes enabling actions even if their immediate score is lower.
        candidates = sorted((r for r in ranked if r[2] is not None and actions[r[1]].action_type in DETERMINISTIC),
                            key=lambda r:(-r[0],r[1]))
        frontier = self.reserve_enablers(world,ctx,actions,candidates)
        self.enabler_slots += sum(r[1] not in {x[1] for x in candidates[:5]} for r in frontier)
        seen = {state_key(world)}
        expanded = 0
        for depth in range(2,5):
            new = []
            for _,root,g in frontier:
                if time.process_time()>deadline or expanded>=80:
                    self.cutoffs += 1
                    return int(best)
                st = g.state
                if st.current_color()!=obs.me or st.current_prompt!=AP.PLAY_TURN or st.num_turns!=world.state.num_turns or st.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS'] >= g.vps_to_win:
                    continue
                local = []
                for a in sorted(g.playable_actions,key=lambda a:(priority.get(a.action_type,6),repr(a.value))):
                    if a.action_type not in DETERMINISTIC:
                        continue
                    if expanded>=80 or time.process_time()>deadline:
                        break
                    value,child = ctx.action_value(g,a)
                    expanded += 1
                    self.search_nodes += 1
                    if value>=WIN:
                        return int(root)
                    value -= .025*(depth-1)
                    if value > best_value:
                        best,best_value=root,value
                    if child is not None and child.state.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS'] < child.vps_to_win:
                        fingerprint=state_key(child)
                        if fingerprint not in seen:
                            seen.add(fingerprint)
                            local.append((value,root,child))
                new.extend(sorted(local,key=lambda r:-r[0])[:5])
            frontier=sorted(new,key=lambda r:(-r[0],r[1]))[:5]
            if not frontier:
                break
        return int(best)

    @staticmethod
    def reserve_enablers(world,ctx,actions,candidates):
        """Keep three greedy roots plus at most two distinct useful enablers."""
        if len(candidates)<=5:return candidates
        ps=world.state.player_state
        before=hand(world.state,ctx.key)
        goals=[]
        if world.state.buildings_by_color[ctx.me]['SETTLEMENT'] and ps[ctx.key+'_CITIES_AVAILABLE']>0:
            goals.append(CITY)
        if ps[ctx.key+'_SETTLEMENTS_AVAILABLE']>0 and world.state.board.buildable_node_ids(ctx.me):
            goals.append(SETTLE)
        initial_sites=len(world.state.board.buildable_node_ids(ctx.me))
        def progress(row):
            child=row[2];a=actions[row[1]]
            if child is None or child.state.current_color()!=ctx.me:return 0
            h=hand(child.state,ctx.key)
            if a.action_type in (AT.MARITIME_TRADE,AT.PLAY_YEAR_OF_PLENTY,AT.PLAY_MONOPOLY):
                return max((deficit(before,cost)-deficit(h,cost) for cost in goals),default=0)
            if a.action_type==AT.BUILD_ROAD and ps[ctx.key+'_SETTLEMENTS_AVAILABLE']>0:
                return int(len(child.state.board.buildable_node_ids(ctx.me))>initial_sites)
            return 0
        chosen=candidates[:3]
        used={r[1] for r in chosen}
        enablers=sorted(((progress(r),r) for r in candidates if r[1] not in used),key=lambda x:(-x[0],-x[1][0],x[1][1]))
        for gain,row in enablers:
            if gain>0 and len(chosen)<5:
                chosen.append(row);used.add(row[1])
        for row in candidates:
            if len(chosen)>=5:break
            if row[1] not in used:chosen.append(row);used.add(row[1])
        return chosen

    @staticmethod
    def _opening(ctx,owned,node):
        rates = ctx.rates.get(node,(0.0,)*5)
        combined = tuple(a+b for a,b in zip(owned,rates))
        return sum(x*w for x,w in zip(combined,(.95,.95,.9,1.15,1.15))) + .10*sum(min(x/.08,1) for x in combined)
