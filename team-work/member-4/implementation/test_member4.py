"""Meaningful contract checks and explicit constructed engine fixtures, not full histories."""
import importlib.util
import itertools
import math
from pathlib import Path
import random
import sys
import time
import unittest

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(BASE.parents[1]/'member-3/implementation'))
import test_policies as fixture
from catan_kit.obs import Obs
from catanatron.models.enums import ActionType as AT, ActionPrompt as AP
from member4_policies import Member4Policy, RouteContext
from public_context import Context, WIN, hand
from route_math import bank_convertible, estimate_rolls

def choose(g,c,mode):
    fixture.invariant(g)
    before=repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.action_records))
    obs=Obs(g,c);obs.cpu_left=1
    i=Member4Policy(mode).decide(obs,g.playable_actions)
    assert type(i) is int and 0<=i<len(g.playable_actions)
    assert before==repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.action_records))
    return g.playable_actions[i]

class RouteMathTests(unittest.TestCase):
    def test_integer_conversion_against_exhaustive_trade_search(self):
        def oracle(h,c,r,b):
            queue=[(h,b)];seen=set(queue)
            for x,bank in queue:
                if all(x[i]>=c[i] for i in (0,1)):return True
                for i,j in ((0,1),(1,0)):
                    if x[i]>=r[i] and bank[j]:
                        nxt=list(x);nb=list(bank)
                        nxt[i]-=r[i];nxt[j]+=1;nb[i]+=r[i];nb[j]-=1
                        state=tuple(nxt),tuple(nb)
                        if state not in seen:seen.add(state);queue.append(state)
            return False
        count=0
        for h in itertools.product(range(5),repeat=2):
            for c in itertools.product(range(3),repeat=2):
                for b in itertools.product(range(3),repeat=2):
                    for r in itertools.product((2,3,4),repeat=2):
                        self.assertEqual(bank_convertible(h+(0,)*3,c+(0,)*3,r+(4,)*3,b+(0,)*3),oracle(h,c,r,b))
                        count+=1
        self.assertEqual(count,18225)

    def test_projection_and_absent_bank(self):
        zero=(0,)*5;cost=(0,1,0,0,0);ratios=(4,)*5
        t=estimate_rolls(zero,cost,(1,0,0,0,0),ratios,(10,1,0,0,0))
        self.assertGreaterEqual(t,4-1e-8);self.assertLess(t,4.00031)
        self.assertEqual(estimate_rolls(zero,cost,(1,1,0,0,0),ratios,(10,0,0,0,0)),math.inf)
        self.assertEqual(estimate_rolls(cost,cost,zero,ratios,zero),0)

class EngineTests(unittest.TestCase):
    def test_immediate_win_and_one_trade_win(self):
        for mode in ('route','belief'):
            g,c=fixture.near_win();fixture.set_hand(g,c,fixture.CITY)
            self.assertEqual(choose(g,c,mode).action_type,AT.BUILD_CITY)
            g,c=fixture.near_win();fixture.set_hand(g,c,(4,0,0,2,2))
            self.assertEqual(choose(g,c,mode).action_type,AT.MARITIME_TRADE)

    def test_low_clock_never_samples(self):
        g,c=fixture.fresh();obs=Obs(g,c);obs.cpu_left=0
        obs.sample_world=lambda rng: (_ for _ in ()).throw(AssertionError('sampled with no clock'))
        for mode in ('route','belief'):
            i=Member4Policy(mode).decide(obs,g.playable_actions)
            self.assertEqual(g.playable_actions[i].action_type,AT.END_TURN)

    def test_beliefs_reject_impossible_terminal_and_cap_nine(self):
        g,c=fixture.fresh();e=next(x for x in g.state.colors if x!=c);ek=fixture.key(g,e)
        g.state.player_state[ek+'_VICTORY_POINTS']=9
        g.state.player_state[ek+'_ACTUAL_VICTORY_POINTS']=10
        self.assertFalse(Member4Policy.valid_belief(g,c))
        obs=Obs(g,c)
        obs.sample_world=lambda rng:g.copy()
        agent=Member4Policy('belief')
        self.assertEqual(agent.sample_beliefs(obs,time.process_time()+1),[])
        self.assertEqual(agent.sample_attempts,12)
        g.state.player_state[ek+'_ACTUAL_VICTORY_POINTS']=9
        worlds=agent.sample_beliefs(obs,time.process_time()+1)
        self.assertEqual(len(worlds),3)

    def test_new_knight_only_eligible_in_forecast_next_turn(self):
        g,c=fixture.fresh();e=next(x for x in g.state.colors if x!=c)
        fixture.dev(g,e,'KNIGHT',old=False)
        k=fixture.key(g,e)
        self.assertFalse(g.state.player_state[k+'_KNIGHT_OWNED_AT_START'])
        ctx=Context(g,c,True);agent=Member4Policy('belief')
        end=next(a for a in g.playable_actions if a.action_type==AT.END_TURN)
        out=agent.forecast_end(g,end,ctx,time.process_time()+1)
        self.assertTrue(out.state.player_state[k+'_KNIGHT_OWNED_AT_START'])
        self.assertTrue(any(a.action_type==AT.PLAY_KNIGHT_CARD for a in out.playable_actions))
        self.assertFalse(g.state.player_state[k+'_KNIGHT_OWNED_AT_START'])

    def test_opponent_roll_is_a_boundary(self):
        g,c=fixture.fresh();ctx=Context(g,c,True);agent=Member4Policy('belief')
        end=next(a for a in g.playable_actions if a.action_type==AT.END_TURN)
        out=agent.forecast_end(g,end,ctx,time.process_time()+1)
        before=len(out.state.action_records)
        self.assertEqual(agent.opponent_reply(out,ctx,time.process_time()+1),ctx.value(out))
        self.assertEqual(len(out.state.action_records),before)
        self.assertEqual(agent.reply_nodes,0)

    def test_hidden_monopoly_reply_has_observable_model_effect(self):
        g,c=fixture.fresh();e=next(x for x in g.state.colors if x!=c)
        fixture.set_hand(g,c,(0,0,0,4,3));fixture.dev(g,e,'MONOPOLY',old=False)
        ctx=Context(g,c,True);agent=Member4Policy('belief')
        end=next(a for a in g.playable_actions if a.action_type==AT.END_TURN)
        out=agent.forecast_end(g,end,ctx,time.process_time()+1)
        before=ctx.value(out)
        self.assertLess(agent.opponent_reply(out,ctx,time.process_time()+1),before)
        self.assertEqual(agent.reply_nodes,5)
        self.assertEqual(fixture.hand(out.state,ctx.key) if hasattr(fixture,'hand') else hand(out.state,ctx.key),(0,0,0,4,3))

    def test_sampled_knight_win_is_bounded_conditional_risk(self):
        g,c=fixture.fresh();e=next(x for x in g.state.colors if x!=c)
        fixture.add_settlement(g,e);fixture.add_settlement(g,e)
        fixture.upgrade(g,e);fixture.upgrade(g,e);fixture.extend_road(g,e,5)
        ek=fixture.key(g,e)
        for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
        g.state.player_state[ek+'_PLAYED_KNIGHT']=2
        fixture.dev(g,e,'KNIGHT',old=False);fixture.dev(g,e,'VICTORY_POINT')
        fixture.phase(g,c,True)
        # The setup's artificial enemy upgrades left HAS_ROLLED set; a real
        # completed prior turn would have cleaned it before our current turn.
        g.state.player_state[ek+'_HAS_ROLLED']=False
        fixture.invariant(g)
        self.assertEqual(g.state.player_state[ek+'_ACTUAL_VICTORY_POINTS'],9)
        ctx=Context(g,c,True);agent=Member4Policy('belief')
        end=next(a for a in g.playable_actions if a.action_type==AT.END_TURN)
        out=agent.forecast_end(g,end,ctx,time.process_time()+1)
        base=ctx.value(out)
        self.assertAlmostEqual(agent.opponent_reply(out,ctx,time.process_time()+1),base-126)

    def test_enemy_robber_expectation(self):
        g,c=fixture.fresh();e=next(x for x in g.state.colors if x!=c)
        fixture.set_hand(g,c,(2,1,0,0,0));fixture.dev(g,e,'KNIGHT',old=True)
        fixture.phase(g,e,False)
        knight=next(a for a in g.playable_actions if a.action_type==AT.PLAY_KNIGHT_CARD);g.execute(knight)
        move=next(a for a in g.playable_actions if a.value[1]==c)
        ctx=Context(g,c,True);expected=0
        own=hand(g.state,ctx.key);enemy=hand(g.state,ctx.ekey)
        for i,n in enumerate(own):
            if n:
                child=g.copy();child.state.board.robber_coordinate=move.value[0]
                a,b=list(own),list(enemy);a[i]-=1;b[i]+=1
                expected+=n/sum(own)*ctx.value(child,tuple(a),tuple(b))
        self.assertAlmostEqual(Member4Policy.enemy_robber_value(g,move,ctx),expected)

    def test_plans_respect_pieces_and_owned_bonuses(self):
        g,c=fixture.fresh();k=fixture.key(g,c)
        g.state.player_state[k+'_CITIES_AVAILABLE']=0
        g.state.player_state[k+'_SETTLEMENTS_AVAILABLE']=0
        g.state.player_state[k+'_HAS_ARMY']=True
        g.state.player_state[k+'_HAS_ROAD']=True
        ctx=RouteContext(g,c)
        names={p[0] for p in ctx.plans(g,hand(g.state,k))}
        self.assertFalse(names.intersection({'city','expand','army','road'}))

    def test_blocked_targets_and_far_road(self):
        g,c=fixture.fresh();ctx=RouteContext(g,c)
        self.assertIsNone(ctx.road_steps(g))
        g.state.board.board_buildable_ids=set()
        self.assertNotIn('expand',{p[0] for p in RouteContext(g,c).spatial_plans(g)})

    def test_buy_ignores_sampled_deck_order(self):
        g,c=fixture.fresh();fixture.set_hand(g,c,fixture.DEV_COST if hasattr(fixture,'DEV_COST') else (0,0,1,1,1))
        ctx=RouteContext(g,c);v=ctx.buy_value(g)
        h=g.copy();h.state.development_listdeck.reverse()
        self.assertEqual(v,ctx.buy_value(h))

    def test_no_mutation_legal_indices_and_no_chance_execution(self):
        g,c=fixture.fresh();fixture.set_hand(g,c,(4,4,2,2,3))
        enemy=next(x for x in g.state.colors if x!=c)
        fixture.dev(g,enemy,'MONOPOLY',old=False)
        original=type(g).execute
        def guarded(game,action,*args,**kwargs):
            self.assertNotIn(action.action_type,(AT.ROLL,AT.BUY_DEVELOPMENT_CARD,AT.MOVE_ROBBER))
            return original(game,action,*args,**kwargs)
        type(g).execute=guarded
        try:
            for mode in ('route','belief'):choose(g,c,mode)
        finally:type(g).execute=original

    def test_standalone_modules_load_without_helper_imports(self):
        for bot in ('B07','B08'):
            path=BASE/'development'/bot/'agent.py'
            spec=importlib.util.spec_from_file_location('standalone_'+bot,path)
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            g,c=fixture.fresh();obs=Obs(g,c);obs.cpu_left=.3
            index=m.Agent().decide(obs,g.playable_actions)
            self.assertIs(type(index),int)
            self.assertTrue(0<=index<len(g.playable_actions))
            text=path.read_text()
            self.assertNotIn('from route_math import',text)
            self.assertNotIn('from public_context import',text)

if __name__=='__main__':unittest.main(verbosity=2)
