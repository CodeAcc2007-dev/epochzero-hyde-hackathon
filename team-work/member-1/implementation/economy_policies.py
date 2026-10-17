"""B01 purchase bottlenecks and B02 conditional city/dev investment.

No runtime I/O, provider, seed prediction, learning or worker process. Hidden
opponent dev identities/deck order are never used as known information.
"""
import random
import time

from catanatron.models.enums import ActionType as AT, ActionPrompt as AP
from public_context import Context, RES, DEVS, CITY, SETTLE, DEV_COST, WIN, hand, resource_hand_value
from spatial_context import SpatialContext
from goal_math import conversion_gap, goal_priority, improves_goal

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

    def decide(self,obs,actions):
        if not actions:
            raise ValueError('Expected nonempty original legal-action list')
        if len(actions)==1:
            return 0
        self.decisions+=1
        start=time.process_time()
        budget=.022 if obs.cpu_left is None else max(0.0,min(.022,.22*obs.cpu_left))
        fallback=next((i for i,a in enumerate(actions) if a.action_type in (AT.ROLL,AT.END_TURN)),0)
        if obs.my_actual_vps>=9:
            city=next((i for i,a in enumerate(actions) if a.action_type==AT.BUILD_CITY),None)
            if city is not None:return city
        if budget<.001:
            return fallback
        deadline=start+budget
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
