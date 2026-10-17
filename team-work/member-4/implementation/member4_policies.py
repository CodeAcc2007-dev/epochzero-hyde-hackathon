"""Anni's bounded belief-reply and adaptive VP-route policies.

All hidden identities below are conditional model samples. No global game RNG,
board seed prediction, external I/O, learning or worker processes are used.
"""
import math
import random
import time

from catanatron.models.actions import generate_playable_actions
from catanatron.models.enums import ActionType as AT, ActionPrompt as AP
from catanatron.models.board import STATIC_GRAPH
from public_context import Context, RES, DEVS, CITY, SETTLE, DEV_COST, WIN, hand
from route_math import estimate_rolls

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
    def __init__(self, game, me, adaptive=True):
        super().__init__(game, me, True)
        self.adaptive = adaptive
        self.geometry = {}

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
            if to_play and buys <= min(5, len(g.state.development_listdeck)):
                delay = 2*max(0,to_play-1)
                if not ps[self.key+'_KNIGHT_OWNED_AT_START'] and ps[self.key+'_KNIGHT_IN_HAND']:
                    delay += 2
                elif ps[self.key+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN']:
                    delay += 2
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
        best = 0.0
        for _,cost,points,gain,delay in self.plans(g,h):
            rolls = estimate_rolls(h,cost,rates,ratios,bank)
            if math.isfinite(rolls):
                value = (8*min(points,gap)+8*gain*min(gap,6)/6)/(1+(rolls+delay)/8)
                best = max(best,value)
        return best

    def value(self, g, own_hand=None, enemy_hand=None):
        base = super().value(g,own_hand,enemy_hand)
        if abs(base) >= WIN:
            return base
        h = hand(g.state,self.key) if own_hand is None else own_hand
        return base + self.potential(g,h)


class Member4Policy:
    def __init__(self, mode, sampled_replies=True, adaptive=True):
        self.mode = mode
        self.sampled_replies = sampled_replies
        self.adaptive = adaptive
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
        if obs.my_actual_vps >= 9:
            city = next((i for i,a in enumerate(actions) if a.action_type == AT.BUILD_CITY),None)
            if city is not None:
                return city
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

    def opponent_reply(self, g, ctx, deadline):
        baseline = ctx.value(g)
        worst = baseline
        replies = [a for a in g.playable_actions if a.action_type in
                   (AT.PLAY_KNIGHT_CARD,AT.PLAY_MONOPOLY,AT.PLAY_ROAD_BUILDING,AT.PLAY_YEAR_OF_PLENTY)]
        order = {AT.PLAY_KNIGHT_CARD:0,AT.PLAY_MONOPOLY:1,AT.PLAY_ROAD_BUILDING:2,AT.PLAY_YEAR_OF_PLENTY:3}
        for a in sorted(replies,key=lambda a:(order[a.action_type],repr(a.value)))[:8]:
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
        if not obs.opp_dev_count or world.state.current_color()!=obs.me:
            return int(best[1])
        eligible = [r for r in ranked if r[2] is not None and
                    (actions[r[1]].action_type in SAFE or actions[r[1]].action_type==AT.END_TURN)
                    and r[0] >= best[0]-8.0]
        eligible = sorted(eligible,key=lambda r:(-r[0],r[1]))[:3]
        if len(eligible)<2 or best[1] not in [r[1] for r in eligible] or deadline-time.process_time()<.003:
            return int(best[1])
        worlds = self.sample_beliefs(obs,deadline) if self.sampled_replies else [world]*3
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
                if self.sampled_replies:
                    value = self.opponent_reply(end,ctx,deadline)
                    if value is None:
                        self.cutoffs += 1
                        return int(best[1])
                totals[index] += value/len(worlds)
        self.reply_comparisons += 1
        chosen = max(totals,key=lambda i:(totals[i],-i))
        self.reply_changes += chosen != best[1]
        return int(chosen)
