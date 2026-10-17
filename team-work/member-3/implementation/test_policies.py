"""Constructed engine-state semantic fixtures, not claimed full reachable traces.

Setup actions are genuine engine actions. Resource/dev allocations and added
buildings are explicit counterfactual fixtures, with deck/piece/VP invariants.
"""
import hashlib
from pathlib import Path
import random
import sys
import unittest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'bots/B05/v003'))
import catan_kit
from catan_kit.obs import Obs
from catanatron.game import Game
from catanatron.models.actions import generate_playable_actions
from catanatron.models.enums import Action,ActionRecord,ActionType as AT,ActionPrompt as AP
from catanatron.models.player import Color,RandomPlayer
import catanatron.state_functions as sf
from member3_core import Policy,Context,RES,DEVS,DECK,CITY,WIN


def fresh(seed=603):
    g=Game([RandomPlayer(Color.RED),RandomPlayer(Color.BLUE)],seed=seed)
    while g.state.is_initial_build_phase:
        actions=g.playable_actions
        if g.state.current_prompt==AP.BUILD_INITIAL_SETTLEMENT:
            ports=set().union(*g.state.board.map.port_nodes.values())
            a=next((a for a in actions if a.value not in ports),actions[0])
        else:a=sorted(actions,key=lambda a:a.value)[0]
        g.execute(a)
    me=g.state.current_color()
    for color in g.state.colors:set_hand(g,color,(0,0,0,0,0))
    phase(g,me,True)
    return g,me


def key(g,c):return 'P'+str(g.state.color_to_index[c])


def set_hand(g,color,h):
    k=key(g,color)
    for i,r in enumerate(RES):
        g.state.player_state[k+'_'+r+'_IN_HAND']=h[i]
        g.state.resource_freqdeck[i]=19-sum(g.state.player_state[key(g,c)+'_'+r+'_IN_HAND'] for c in g.state.colors)
    assert min(g.state.resource_freqdeck)>=0
    g.playable_actions=generate_playable_actions(g.state)


def phase(g,c,rolled):
    st=g.state;k=key(g,c)
    st.current_player_index=st.current_turn_index=st.color_to_index[c]
    st.current_prompt=AP.PLAY_TURN
    st.player_state[k+'_HAS_ROLLED']=rolled
    g.playable_actions=generate_playable_actions(st)


def add_settlement(g,c):
    b=g.state.board;ports=set().union(*b.map.port_nodes.values())
    n=next(n for n in b.buildable_node_ids(c,True) if n not in ports)
    b.build_settlement(c,n,True);sf.build_settlement(g.state,c,n,True)
    g.playable_actions=generate_playable_actions(g.state)
    return n


def upgrade(g,c):
    phase(g,c,True);set_hand(g,c,CITY)
    a=next(a for a in g.playable_actions if a.action_type==AT.BUILD_CITY)
    g.execute(a);set_hand(g,c,(0,0,0,0,0))


def dev(g,c,d,count=1,old=False):
    k=key(g,c)
    for _ in range(count):g.state.development_listdeck.remove(d)
    g.state.player_state[k+'_'+d+'_IN_HAND']+=count
    if d=='VICTORY_POINT':g.state.player_state[k+'_ACTUAL_VICTORY_POINTS']+=count
    else:g.state.player_state[k+'_'+d+'_OWNED_AT_START']=old
    g.playable_actions=generate_playable_actions(g.state)


def near_win():
    g,c=fresh();add_settlement(g,c);upgrade(g,c);dev(g,c,'VICTORY_POINT',5)
    assert g.state.player_state[key(g,c)+'_ACTUAL_VICTORY_POINTS']==9
    return g,c


def invariant(g):
    st=g.state
    for i,r in enumerate(RES):
        assert st.resource_freqdeck[i]+sum(st.player_state[key(g,c)+'_'+r+'_IN_HAND'] for c in st.colors)==19
    for d,total in zip(DEVS,DECK):
        assert st.development_listdeck.count(d)+sum(st.player_state[key(g,c)+'_'+d+'_IN_HAND']+st.player_state[key(g,c)+'_PLAYED_'+d] for c in st.colors)==total
    for c in st.colors:
        k=key(g,c);ps=st.player_state;build=st.buildings_by_color[c]
        assert ps[k+'_SETTLEMENTS_AVAILABLE']+len(build['SETTLEMENT'])==5
        assert ps[k+'_CITIES_AVAILABLE']+len(build['CITY'])==4
        assert ps[k+'_ROADS_AVAILABLE']+len(build['ROAD'])==15
        public=len(build['SETTLEMENT'])+2*len(build['CITY'])+2*ps[k+'_HAS_ROAD']+2*ps[k+'_HAS_ARMY']
        assert ps[k+'_VICTORY_POINTS']==public
        assert ps[k+'_ACTUAL_VICTORY_POINTS']==public+ps[k+'_VICTORY_POINT_IN_HAND']


def choose(g,c,mode):
    invariant(g)
    obs=Obs(g,c);obs.cpu_left=1.0
    before=(repr(g.state.player_state),repr(g.state.board.buildings),repr(g.state.board.roads),list(g.state.resource_freqdeck),list(g.state.development_listdeck),list(g.state.action_records))
    i=Policy(mode).decide(obs,g.playable_actions)
    assert type(i) is int and 0<=i<len(g.playable_actions)
    after=(repr(g.state.player_state),repr(g.state.board.buildings),repr(g.state.board.roads),list(g.state.resource_freqdeck),list(g.state.development_listdeck),list(g.state.action_records))
    assert before==after,'Observation was mutated'
    return g.playable_actions[i]


class PolicyTests(unittest.TestCase):
    def test_runtime_modules_identical(self):
        for name in ['race_math.py','member3_core.py']:
            self.assertEqual((BASE/'bots/B05/v003'/name).read_bytes(),(BASE/'bots/B06/v003'/name).read_bytes())

    def test_own_city_win_over_ghost_opponent(self):
        for mode in ['beam','threat']:
            g,c=near_win();set_hand(g,c,CITY)
            # Masked hidden scores are ignored; malformed hypothetical sample cannot defeat exact own win.
            obs=Obs(g,c);obs.cpu_left=1
            obs.sample_world=lambda rng: ghost(g,c)
            idx=Policy(mode).decide(obs,g.playable_actions)
            self.assertEqual(g.playable_actions[idx].action_type,AT.BUILD_CITY)
            g.execute(g.playable_actions[idx]);invariant(g)
            self.assertEqual(g.winning_color(),c)

    def test_trade_then_city_terminal(self):
        g,c=near_win();set_hand(g,c,(0,4,0,1,3))
        self.assertFalse(any(a.action_type==AT.BUILD_CITY for a in g.playable_actions))
        a=choose(g,c,'beam');self.assertEqual(a.action_type,AT.MARITIME_TRADE)
        g.execute(a);a=choose(g,c,'beam');self.assertEqual(a.action_type,AT.BUILD_CITY)
        g.execute(a);invariant(g);self.assertEqual(g.winning_color(),c)

    def test_road_then_settlement_terminal(self):
        g,c=near_win();g=road_settlement_fixture(g,c);set_hand(g,c,(2,2,1,1,0))
        self.assertFalse(any(a.action_type==AT.BUILD_SETTLEMENT for a in g.playable_actions))
        a=choose(g,c,'beam');self.assertEqual(a.action_type,AT.BUILD_ROAD)
        g.execute(a);a=choose(g,c,'beam');self.assertEqual(a.action_type,AT.BUILD_SETTLEMENT)
        g.execute(a);invariant(g);self.assertEqual(g.winning_color(),c)

    def test_yop_then_city_terminal(self):
        g,c=near_win();set_hand(g,c,(0,0,0,0,3));dev(g,c,'YEAR_OF_PLENTY',old=True)
        a=choose(g,c,'beam');self.assertEqual(a.action_type,AT.PLAY_YEAR_OF_PLENTY)
        self.assertEqual(a.value,('WHEAT','WHEAT'))
        g.execute(a);a=choose(g,c,'beam');g.execute(a);invariant(g)
        self.assertEqual(g.winning_color(),c)

    def test_knight_wins_before_robber_and_roll(self):
        for mode in ['beam','threat']:
            g,c=fresh();add_settlement(g,c);dev(g,c,'VICTORY_POINT',5)
            k=key(g,c)
            for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
            g.state.player_state[k+'_PLAYED_KNIGHT']=2
            dev(g,c,'KNIGHT',old=True);phase(g,c,False)
            a=choose(g,c,mode);self.assertEqual(a.action_type,AT.PLAY_KNIGHT_CARD)
            g.execute(a);invariant(g)
            self.assertEqual(g.state.current_prompt,AP.MOVE_ROBBER)
            self.assertEqual(g.winning_color(),c)

    def test_new_knight_ineligible_until_next_turn(self):
        g,c=fresh();set_hand(g,c,(0,0,1,1,1))
        a=next(a for a in g.playable_actions if a.action_type==AT.BUY_DEVELOPMENT_CARD)
        g.execute(a,action_record=ActionRecord(a,'KNIGHT'))
        self.assertFalse(any(a.action_type==AT.PLAY_KNIGHT_CARD for a in g.playable_actions))
        g.execute(next(a for a in g.playable_actions if a.action_type==AT.END_TURN))
        a=next(a for a in g.playable_actions if a.action_type==AT.ROLL)
        g.execute(a,action_record=ActionRecord(a,(1,1)))
        g.execute(next(a for a in g.playable_actions if a.action_type==AT.END_TURN))
        self.assertEqual(g.state.current_color(),c)
        self.assertTrue(any(a.action_type==AT.PLAY_KNIGHT_CARD for a in g.playable_actions));invariant(g)

    def test_vp_draw_scores_immediately(self):
        g,c=fresh();set_hand(g,c,(0,0,1,1,1));before=g.state.player_state[key(g,c)+'_ACTUAL_VICTORY_POINTS']
        a=next(a for a in g.playable_actions if a.action_type==AT.BUY_DEVELOPMENT_CARD)
        g.execute(a,action_record=ActionRecord(a,'VICTORY_POINT'));invariant(g)
        self.assertEqual(g.state.player_state[key(g,c)+'_ACTUAL_VICTORY_POINTS'],before+1)

    def test_no_build_before_roll(self):
        g,c=near_win();set_hand(g,c,CITY);phase(g,c,False)
        self.assertEqual({a.action_type for a in g.playable_actions},{AT.ROLL})
        self.assertEqual(choose(g,c,'beam').action_type,AT.ROLL)

    def test_road_building_forced_second_road(self):
        g,c=fresh();dev(g,c,'ROAD_BUILDING',old=True)
        a=next(a for a in g.playable_actions if a.action_type==AT.PLAY_ROAD_BUILDING);g.execute(a)
        g.execute(choose(g,c,'beam'))
        self.assertTrue(g.state.is_road_building)
        self.assertTrue(all(a.action_type==AT.BUILD_ROAD for a in g.playable_actions))
        g.execute(choose(g,c,'beam'));invariant(g);self.assertFalse(g.state.is_road_building)

    def test_out_of_turn_discard_fixed_quota(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c);set_hand(g,e,(4,4,0,0,0));phase(g,c,False)
        a=next(a for a in g.playable_actions if a.action_type==AT.ROLL)
        g.execute(a,action_record=ActionRecord(a,(1,6)))
        self.assertEqual(g.state.current_color(),e)
        for left in range(4,0,-1):
            self.assertEqual(g.state.discard_counts[g.state.color_to_index[e]],left)
            a=choose(g,e,'threat');self.assertEqual(a.action_type,AT.DISCARD_RESOURCE);g.execute(a)
        self.assertEqual(g.state.current_color(),c);self.assertEqual(g.state.current_prompt,AP.MOVE_ROBBER);invariant(g)

    def test_robber_expectation_matches_forced_outcomes(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c);set_hand(g,e,(1,0,0,2,0))
        g.state.current_prompt=AP.MOVE_ROBBER;g.playable_actions=generate_playable_actions(g.state)
        ctx=Context(g,c,True)
        a=next(a for a in g.playable_actions if a.value[1]==e)
        expected=0
        for resource,n in [('WOOD',1),('WHEAT',2)]:
            copy=g.copy();copy.execute(a,action_record=ActionRecord(a,resource))
            expected+=n/3*ctx.value(copy)
        self.assertAlmostEqual(ctx.robber_value(g,a),expected)
        choose(g,c,'threat');invariant(g)

    def test_dev_value_independent_of_sample_order_and_hidden_allocation(self):
        g,c=fresh();set_hand(g,c,(0,0,1,1,1));ctx=Context(g,c,False)
        other=g.copy();other.state.development_listdeck.reverse()
        self.assertEqual(ctx.buy_value(g),ctx.buy_value(other))
        self.assertAlmostEqual(sum(ctx.draw_probs),1.0)
        self.assertTrue(all(p>=0 for p in ctx.draw_probs))

    def test_monopoly_exact_transfer_and_bank_unchanged(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c)
        set_hand(g,e,(0,0,0,4,0));dev(g,c,'MONOPOLY',old=True)
        before=list(g.state.resource_freqdeck)
        a=next(a for a in g.playable_actions if a.action_type==AT.PLAY_MONOPOLY and a.value=='WHEAT')
        g.execute(a);invariant(g)
        self.assertEqual(g.state.player_state[key(g,c)+'_WHEAT_IN_HAND'],4)
        self.assertEqual(g.state.player_state[key(g,e)+'_WHEAT_IN_HAND'],0)
        self.assertEqual(g.state.resource_freqdeck,before)

    def test_yop_respects_single_card_bank(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c);dev(g,c,'YEAR_OF_PLENTY',old=True)
        set_hand(g,e,(19,19,19,18,19))
        options=[a for a in g.playable_actions if a.action_type==AT.PLAY_YEAR_OF_PLENTY]
        self.assertEqual({a.value for a in options},{('WHEAT',)})
        g.execute(options[0]);invariant(g)
        self.assertEqual(g.state.resource_freqdeck,[0,0,0,0,0])

    def test_army_tie_does_not_transfer(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c)
        for player in [c,e]:
            for _ in range(3):g.state.development_listdeck.remove('KNIGHT')
            g.state.player_state[key(g,player)+'_PLAYED_KNIGHT']=3
        ep=key(g,e);cp=key(g,c)
        g.state.player_state[ep+'_HAS_ARMY']=True
        g.state.player_state[ep+'_VICTORY_POINTS']+=2;g.state.player_state[ep+'_ACTUAL_VICTORY_POINTS']+=2
        before=(g.state.player_state[cp+'_ACTUAL_VICTORY_POINTS'],g.state.player_state[ep+'_ACTUAL_VICTORY_POINTS'])
        sf.maintain_largest_army(g.state,c,e,3)
        self.assertEqual((g.state.player_state[cp+'_ACTUAL_VICTORY_POINTS'],g.state.player_state[ep+'_ACTUAL_VICTORY_POINTS']),before)
        dev(g,c,'KNIGHT',old=True);a=next(a for a in g.playable_actions if a.action_type==AT.PLAY_KNIGHT_CARD)
        g.execute(a);invariant(g)
        self.assertEqual(g.state.player_state[cp+'_ACTUAL_VICTORY_POINTS'],before[0]+2)
        self.assertEqual(g.state.player_state[ep+'_ACTUAL_VICTORY_POINTS'],before[1]-2)

    def test_road_tie_then_strict_takeover(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c)
        extend_road(g,e,6);extend_road(g,c,6)
        invariant(g);self.assertEqual(g.state.board.road_color,e)
        cp,ep=key(g,c),key(g,e)
        before=(g.state.player_state[cp+'_ACTUAL_VICTORY_POINTS'],g.state.player_state[ep+'_ACTUAL_VICTORY_POINTS'])
        extend_road(g,c,7);invariant(g)
        self.assertEqual(g.state.board.road_color,c)
        self.assertEqual(g.state.player_state[cp+'_ACTUAL_VICTORY_POINTS'],before[0]+2)
        self.assertEqual(g.state.player_state[ep+'_ACTUAL_VICTORY_POINTS'],before[1]-2)

    def test_visible_city_threat_and_hidden_risk_weight(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c)
        add_settlement(g,e);add_settlement(g,e)
        for _ in range(3):upgrade(g,e)
        extend_road(g,e,5);phase(g,c,True);set_hand(g,e,CITY)
        invariant(g);self.assertEqual(g.state.player_state[key(g,e)+'_VICTORY_POINTS'],9)
        ctx=Context(g,c,True)
        self.assertEqual(ctx.threat(g,CITY),16.0)
        self.assertEqual(ctx.threat(g,(0,0,0,1,3)),0.0)
        self.assertEqual(ctx.draw_probs[1],5/25)  # no unplayed opposing devs in this fixture
        # A different constructed eight-public-point board; one hidden dev makes a conditional risk, not certainty.
        h,c=fresh();e=next(x for x in h.state.colors if x!=c)
        add_settlement(h,e)
        for _ in range(2):upgrade(h,e)
        dev(h,e,'KNIGHT',old=True)
        # Add an ordinary settlement and one Army award to reach eight public points.
        add_settlement(h,e)
        ek=key(h,e)
        for _ in range(3):h.state.development_listdeck.remove('KNIGHT')
        h.state.player_state[ek+'_PLAYED_KNIGHT']=3
        h.state.player_state[ek+'_HAS_ARMY']=True
        h.state.player_state[ek+'_VICTORY_POINTS']+=2;h.state.player_state[ek+'_ACTUAL_VICTORY_POINTS']+=2
        phase(h,c,True);set_hand(h,e,CITY);invariant(h)
        self.assertEqual(h.state.player_state[ek+'_VICTORY_POINTS'],8)
        self.assertAlmostEqual(Context(h,c,True).threat(h,CITY),5.6)

    def test_sampled_hidden_allocation_does_not_change_evaluator(self):
        g,c=fresh();e=next(x for x in g.state.colors if x!=c)
        dev(g,e,'KNIGHT');set_hand(g,c,(0,0,1,1,1));obs=Obs(g,c)
        worlds=[obs.sample_world(random.Random(seed)) for seed in [1,2,3,4]]
        values=[Context(w,c,True).value(w) for w in worlds]
        probs=[Context(w,c,True).draw_probs for w in worlds]
        self.assertTrue(all(v==values[0] for v in values))
        self.assertTrue(all(v==probs[0] for v in probs))

    def test_public_simultaneous_terminal_guard(self):
        g,c=near_win();ctx=Context(g,c,False);e=ctx.enemy
        # Directly probe the scoring guard only; not represented as a reachable Road-cut trace.
        g.state.colors=(c,e)
        g.state.player_state[ctx.key+'_ACTUAL_VICTORY_POINTS']=10
        g.state.player_state[ctx.ekey+'_VICTORY_POINTS']=10
        self.assertEqual(ctx.value(g),-WIN)

    def test_known_opposing_terminal_is_loss(self):
        g,c=fresh();ctx=Context(g,c,True)
        g.state.player_state[ctx.ekey+'_VICTORY_POINTS']=10
        self.assertEqual(ctx.value(g),-WIN)

    def test_low_clock_fallback_is_legal(self):
        g,c=fresh();set_hand(g,c,(4,4,2,2,3));obs=Obs(g,c);obs.cpu_left=0
        obs.sample_world=lambda rng: (_ for _ in ()).throw(AssertionError('Low-clock path copied a world'))
        for mode in ['beam','threat']:
            i=Policy(mode).decide(obs,g.playable_actions)
            self.assertEqual(g.playable_actions[i].action_type,AT.END_TURN)




def extend_road(g,c,target):
    while g.state.player_state[key(g,c)+'_LONGEST_ROAD_LENGTH']<target:
        if g.state.player_state[key(g,c)+'_ROADS_AVAILABLE']<=0:raise AssertionError('No road pieces')
        trials=[]
        for edge in sorted(g.state.board.buildable_edges(c)):
            b=g.state.board.copy()
            try:result=b.build_road(c,edge)
            except (ValueError,TypeError):continue
            trials.append((result[2][c],edge))
        if not trials:raise AssertionError('No road extension')
        _,edge=max(trials,key=lambda t:(t[0],t[1]))
        result=g.state.board.build_road(c,edge)
        sf.build_road(g.state,c,edge,True)
        sf.maintain_longest_road(g.state,*result)
    g.playable_actions=generate_playable_actions(g.state)


def road_settlement_fixture(g,c):
    # Find a real legal road prefix rather than assuming a one-road site exists.
    frontier=[g]
    for depth in range(3):
        next_layer=[]
        for parent in frontier:
            set_hand(parent,c,(2,2,1,1,0))
            for a in parent.playable_actions:
                if a.action_type!=AT.BUILD_ROAD:continue
                child=parent.copy();child.execute(a)
                if child.winning_color() is not None:continue
                if any(x.action_type==AT.BUILD_SETTLEMENT for x in child.playable_actions):return parent
                next_layer.append(child)
        frontier=next_layer
    raise AssertionError('Could not construct a legal road-to-settlement fixture')


def ghost(g,c):
    result=g.copy();e=next(x for x in g.state.colors if x!=c)
    result.state.player_state[key(g,e)+'_ACTUAL_VICTORY_POINTS']=10
    return result


if __name__=='__main__':unittest.main(verbosity=2)
