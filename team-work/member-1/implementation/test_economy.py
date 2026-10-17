"""Economic semantics: pure independent oracles and constructed engine fixtures."""
import importlib.util
import itertools
import math
from pathlib import Path
import sys
import unittest

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(BASE.parents[1]/'member-3/implementation'))
import test_policies as f
from catan_kit.obs import Obs
from catanatron.game import Game
from catanatron.models.player import Color,RandomPlayer
from catanatron.models.enums import ActionType as AT,ActionPrompt as AP,ActionRecord
from public_context import Context,CITY,SETTLE,DEV_COST,WIN,hand
from economy_policies import EconomyContext,EconomyPolicy
from goal_math import conversion_gap,goal_priority,improves_goal

def choose(g,c,engine=False):
    f.invariant(g)
    before=repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.action_records))
    obs=Obs(g,c);obs.cpu_left=1
    i=EconomyPolicy(engine).decide(obs,g.playable_actions)
    assert type(i) is int and 0<=i<len(g.playable_actions)
    assert before==repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.action_records))
    return g.playable_actions[i]

def settlement_ready():
    g,c=f.fresh();parent=f.road_settlement_fixture(g,c)
    for a in parent.playable_actions:
        if a.action_type==AT.BUILD_ROAD:
            child=parent.copy();child.execute(a)
            if any(b.action_type==AT.BUILD_SETTLEMENT for b in child.playable_actions):return child,c
    raise AssertionError('No legal settlement fixture')

class GoalMathTests(unittest.TestCase):
    def test_gap_against_exhaustive_trade_oracle(self):
        def oracle(h,c,r,b):
            queue=[(h,b)];seen=set(queue);best=sum(max(c[i]-h[i],0) for i in (0,1))
            for x,bank in queue:
                best=min(best,sum(max(c[i]-x[i],0) for i in (0,1)))
                for i,j in ((0,1),(1,0)):
                    if x[i]>=r[i] and bank[j]:
                        nxt=list(x);nb=list(bank);nxt[i]-=r[i];nxt[j]+=1;nb[i]+=r[i];nb[j]-=1
                        state=tuple(nxt),tuple(nb)
                        if state not in seen:seen.add(state);queue.append(state)
            return best
        count=0
        for h in itertools.product(range(5),repeat=2):
            for c in itertools.product(range(3),repeat=2):
                for b in itertools.product(range(3),repeat=2):
                    for r in itertools.product((2,3,4),repeat=2):
                        self.assertEqual(conversion_gap(h+(0,)*3,c+(0,)*3,r+(4,)*3,b+(0,)*3),oracle(h,c,r,b));count+=1
        self.assertEqual(count,18225)

    def test_nine_cards_without_wheat_and_reserved_last_wood(self):
        bank=(19,)*5;ratios=(4,)*5
        self.assertEqual(conversion_gap((3,3,3,0,0),SETTLE,ratios,bank),1)
        self.assertGreater(goal_priority(SETTLE,SETTLE,ratios,bank,12),goal_priority((3,3,3,0,0),SETTLE,ratios,bank,12))
        self.assertFalse(improves_goal((4,1,1,0,0),(0,1,1,1,0),SETTLE,ratios,bank,bank))
        self.assertTrue(improves_goal((4,1,1,0,0),(2,1,1,1,0),SETTLE,(2,4,4,4,4),bank,bank))
        self.assertEqual(conversion_gap((4,1,1,0,0),SETTLE,(2,4,4,4,4),(19,19,19,0,19)),1)

class EconomicEngineTests(unittest.TestCase):
    def test_known_city_and_trade_wins(self):
        for engine in (False,True):
            g,c=f.near_win();f.set_hand(g,c,CITY)
            self.assertEqual(choose(g,c,engine).action_type,AT.BUILD_CITY)
            g,c=f.near_win();f.set_hand(g,c,(4,0,0,2,2))
            self.assertEqual(choose(g,c,engine).action_type,AT.MARITIME_TRADE)

    def test_policy_rejects_last_wood_trade(self):
        g,c=settlement_ready();f.set_hand(g,c,(4,1,1,0,0))
        ctx=EconomyContext(g,c)
        goal=ctx.goal(g,hand(g.state,ctx.key))
        self.assertEqual(goal[0],'expand');self.assertEqual(goal[1],SETTLE)
        trade=next(a for a in g.playable_actions if a.action_type==AT.MARITIME_TRADE and a.value[0]=='WOOD' and a.value[-1]=='WHEAT')
        self.assertEqual(ctx.action_value(g,trade),(-math.inf,None))
        self.assertNotEqual(choose(g,c),trade)

    def test_owned_port_only_not_map_presence(self):
        g=Game([RandomPlayer(Color.RED),RandomPlayer(Color.BLUE)],seed=603);c=g.state.current_color()
        self.assertTrue(g.state.board.map.port_nodes['WOOD'])
        self.assertEqual(EconomyContext(g,c).board_features(g)[3][0],4)
        nodes=g.state.board.map.port_nodes['WOOD']
        a=next(a for a in g.playable_actions if a.value in nodes)
        g.execute(a)
        self.assertEqual(EconomyContext(g,c).board_features(g)[3][0],2)
        f.invariant(g)

    def test_discard_preserves_selected_bundle(self):
        g,c=f.fresh();f.set_hand(g,c,(0,0,1,2,6))
        st=g.state;st.current_prompt=AP.DISCARD;st.is_discarding=True
        st.discard_counts=[0,0];st.discard_counts[st.color_to_index[c]]=4
        g.playable_actions=f.generate_playable_actions(st)
        for engine in (False,True):
            a=choose(g,c,engine)
            self.assertEqual(a.value,'ORE')

    def test_no_legal_settlement_or_city_piece(self):
        g,c=f.fresh();k=f.key(g,c)
        g.state.board.board_buildable_ids=set();g.state.player_state[k+'_CITIES_AVAILABLE']=0
        ctx=EconomyContext(g,c)
        self.assertFalse({'city','expand'}.intersection(p[0] for p in ctx.specs(g)))

    def test_citydev_escapes_when_ore_supply_blocked(self):
        g,c=settlement_ready();f.set_hand(g,c,SETTLE)
        ore=[(coord,t) for coord,t in g.state.board.map.land_tiles.items() if t.resource=='ORE']
        owned=set(g.state.buildings_by_color[c]['SETTLEMENT'])
        tile=next(((coord,t) for coord,t in ore if owned.intersection(t.nodes.values())),ore[0])
        g.state.board.robber_coordinate=tile[0]
        before=g.state.player_state[f.key(g,c)+'_ACTUAL_VICTORY_POINTS']
        a=choose(g,c,True)
        self.assertIn(a.action_type,(AT.BUILD_SETTLEMENT,AT.BUILD_ROAD))
        g.execute(a)
        # This fixture also permits a Road award: two points is a valid escape,
        # and better immediate progress than the initially assumed settlement.
        self.assertGreater(g.state.player_state[f.key(g,c)+'_ACTUAL_VICTORY_POINTS'],before)

    def test_depleted_bank_prevents_wheat_trade(self):
        g,c=f.fresh();e=next(x for x in g.state.colors if x!=c)
        f.set_hand(g,c,(8,0,0,0,0));f.set_hand(g,e,(0,0,0,19,0));f.invariant(g)
        self.assertFalse(any(a.action_type==AT.MARITIME_TRADE and a.value[-1]=='WHEAT' for a in g.playable_actions))
        choose(g,c)

    def test_nearly_empty_deck_probabilities_not_actual_order(self):
        g,c=f.fresh();e=next(x for x in g.state.colors if x!=c)
        while len(g.state.development_listdeck)>1:
            f.dev(g,e,g.state.development_listdeck[0])
        f.set_hand(g,c,DEV_COST);f.invariant(g)
        ctx=EconomyContext(g,c,True)
        self.assertEqual(len(g.state.development_listdeck),1)
        self.assertAlmostEqual(sum(ctx.draw_probs),1)
        self.assertLess(max(ctx.draw_probs),1)
        self.assertTrue(math.isfinite(ctx.buy_value(g)))
        choose(g,c,True)

    def test_old_new_knight_and_army_terminal(self):
        for engine in (False,True):
            g,c=f.fresh();f.add_settlement(g,c);f.dev(g,c,'VICTORY_POINT',5)
            k=f.key(g,c)
            for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
            g.state.player_state[k+'_PLAYED_KNIGHT']=2
            f.dev(g,c,'KNIGHT',old=True);f.phase(g,c,False)
            self.assertEqual(choose(g,c,engine).action_type,AT.PLAY_KNIGHT_CARD)
        g,c=f.fresh();f.set_hand(g,c,DEV_COST)
        buy=next(a for a in g.playable_actions if a.action_type==AT.BUY_DEVELOPMENT_CARD)
        g.execute(buy,action_record=ActionRecord(buy,'KNIGHT'))
        self.assertFalse(any(a.action_type==AT.PLAY_KNIGHT_CARD for a in g.playable_actions))
        choose(g,c,True)
        g.execute(next(a for a in g.playable_actions if a.action_type==AT.END_TURN))
        roll=next(a for a in g.playable_actions if a.action_type==AT.ROLL)
        g.execute(roll,action_record=ActionRecord(roll,(1,1)))
        g.execute(next(a for a in g.playable_actions if a.action_type==AT.END_TURN))
        self.assertTrue(any(a.action_type==AT.PLAY_KNIGHT_CARD for a in g.playable_actions));f.invariant(g)

    def test_no_extra_army_bonus_when_already_owned(self):
        g,c=f.fresh();k=f.key(g,c)
        for _ in range(3):g.state.development_listdeck.remove('KNIGHT')
        g.state.player_state[k+'_PLAYED_KNIGHT']=3;g.state.player_state[k+'_HAS_ARMY']=True
        g.state.player_state[k+'_VICTORY_POINTS']+=2;g.state.player_state[k+'_ACTUAL_VICTORY_POINTS']+=2
        f.set_hand(g,c,DEV_COST);f.invariant(g)
        ctx=EconomyContext(g,c,True)
        self.assertAlmostEqual(ctx.buy_value(g),Context.buy_value(ctx,g))

    def test_strict_army_takeover_requires_more_than_tie(self):
        g,c=f.fresh();e=next(x for x in g.state.colors if x!=c)
        for player,n in ((c,2),(e,3)):
            for _ in range(n):g.state.development_listdeck.remove('KNIGHT')
            g.state.player_state[f.key(g,player)+'_PLAYED_KNIGHT']=n
        ek=f.key(g,e)
        g.state.player_state[ek+'_HAS_ARMY']=True
        g.state.player_state[ek+'_VICTORY_POINTS']+=2;g.state.player_state[ek+'_ACTUAL_VICTORY_POINTS']+=2
        f.set_hand(g,c,DEV_COST);f.invariant(g)
        ctx=EconomyContext(g,c,True)
        self.assertAlmostEqual(ctx.buy_value(g)-Context.buy_value(ctx,g),2*ctx.draw_probs[0])

    def test_free_road_subphases_do_not_spend_cards(self):
        for engine in (False,True):
            g,c=f.fresh();f.dev(g,c,'ROAD_BUILDING',old=True)
            g.execute(next(a for a in g.playable_actions if a.action_type==AT.PLAY_ROAD_BUILDING))
            before=hand(g.state,f.key(g,c))
            for _ in range(2):
                a=choose(g,c,engine);self.assertEqual(a.action_type,AT.BUILD_ROAD)
                g.execute(a);self.assertEqual(hand(g.state,f.key(g,c)),before);f.invariant(g)
            self.assertFalse(g.state.is_road_building)

    def test_unused_dev_stock_limit_and_deck_order(self):
        g,c=f.fresh();f.set_hand(g,c,DEV_COST)
        for d in ('KNIGHT','MONOPOLY','ROAD_BUILDING'):f.dev(g,c,d)
        ctx=EconomyContext(g,c,True)
        self.assertLess(ctx.buy_value(g),ctx.value(g))
        g,c=f.fresh();f.set_hand(g,c,DEV_COST);ctx=EconomyContext(g,c,True)
        a=ctx.buy_value(g);g.state.development_listdeck.reverse()
        self.assertEqual(ctx.buy_value(g),a);self.assertAlmostEqual(sum(ctx.draw_probs),1)

    def test_distinct_economic_goal_choice(self):
        found=False
        for seed in range(4):
            g,c=f.fresh(seed);f.set_hand(g,c,(1,1,1,2,1))
            balanced=EconomyContext(g,c,False);engine=EconomyContext(g,c,True)
            if balanced.family!=engine.family:found=True;break
        self.assertTrue(found,'City commitment must differ from balanced goal choice in a supported fixture')

    def test_low_clock_before_sampling(self):
        g,c=f.fresh();obs=Obs(g,c);obs.cpu_left=0
        obs.sample_world=lambda rng:(_ for _ in ()).throw(AssertionError('sample with no clock'))
        for engine in (False,True):
            i=EconomyPolicy(engine).decide(obs,g.playable_actions)
            self.assertEqual(g.playable_actions[i].action_type,AT.END_TURN)

    def test_no_unmodeled_chance_execution(self):
        g,c=f.fresh();f.set_hand(g,c,(4,4,2,2,3))
        original=type(g).execute
        def guard(game,action,*args,**kwargs):
            self.assertNotIn(action.action_type,(AT.ROLL,AT.BUY_DEVELOPMENT_CARD,AT.MOVE_ROBBER))
            return original(game,action,*args,**kwargs)
        type(g).execute=guard
        try:
            for engine in (False,True):choose(g,c,engine)
        finally:type(g).execute=original

    def test_standalone_legal_entrypoints(self):
        for bot in ('B01','B02'):
            p=BASE/'development'/bot/'agent.py'
            spec=importlib.util.spec_from_file_location('standalone_'+bot,p)
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            g,c=f.fresh();obs=Obs(g,c);obs.cpu_left=.3
            i=m.Agent().decide(obs,g.playable_actions)
            self.assertIs(type(i),int);self.assertTrue(0<=i<len(g.playable_actions))
            self.assertNotIn('from goal_math import',p.read_text())

if __name__=='__main__':unittest.main(verbosity=2)
