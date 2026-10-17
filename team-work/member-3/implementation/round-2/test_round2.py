"""New standalone-artifact regressions; constructed engine fixtures, not reached games."""
import hashlib, importlib.util, itertools, json, math, random, sys, time, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'team-work/member-3/implementation'))
import test_policies as f
from catan_kit.obs import Obs, masked_copy
from catanatron.models.enums import Action, ActionRecord, ActionType as AT, ActionPrompt as AP
from catanatron.models.actions import generate_playable_actions


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def candidate(bot):
    member=3 if bot in ('B05','B06') else 4
    version='v004' if member==3 else 'v002'
    frozen=ROOT/f'team-work/member-{member}/bots/{bot}/{version}/agent.py'
    return frozen if frozen.exists() else ROOT/f'team-work/member-{member}/implementation/round-2/development/{bot}/agent.py'

NEW={b:load('new_'+b,candidate(b)) for b in ('B05','B06','B07','B08')}
OLD={b:load('old_'+b,ROOT/f'team-work/member-{3 if b in ("B05","B06") else 4}'/(f'direct-agents/{b}/agent.py' if b in ('B05','B06') else f'bots/{b}/v001/agent.py')) for b in NEW}


def near(seat=0,vp=9):
    g,_=f.fresh();c=g.state.colors[seat];f.phase(g,c,True)
    f.add_settlement(g,c);f.upgrade(g,c);f.dev(g,c,'VICTORY_POINT',vp-4)
    f.invariant(g);assert g.state.player_state[f.key(g,c)+'_ACTUAL_VICTORY_POINTS']==vp
    return g,c


def settle_win(seat=0):
    g,c=near(seat);g=f.road_settlement_fixture(g,c)
    for a in g.playable_actions:
        if a.action_type!=AT.BUILD_ROAD:continue
        h=g.copy();h.execute(a)
        if any(x.action_type==AT.BUILD_SETTLEMENT for x in h.playable_actions):g=h;break
    f.set_hand(g,c,(1,1,1,1,0));f.invariant(g)
    assert any(a.action_type==AT.BUILD_SETTLEMENT for a in g.playable_actions)
    return g,c


def pick(module,g,c,credit=1):
    before=repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.development_listdeck,g.state.action_records))
    obs=Obs(masked_copy(g,c,random.Random(33)),c);obs.cpu_left=credit
    if credit<=.0009:obs.sample_world=lambda rng:(_ for _ in ()).throw(AssertionError('Emergency path sampled'))
    index=module.Agent().decide(obs,obs._game.playable_actions)
    assert type(index) is int and 0<=index<len(g.playable_actions)
    assert before==repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.development_listdeck,g.state.action_records))
    return g.playable_actions[index]


def enemy_nine():
    g,c=f.fresh();e=next(x for x in g.state.colors if x!=c)
    for _ in range(2):f.add_settlement(g,e)
    for _ in range(3):f.upgrade(g,e)
    ek=f.key(g,e)
    for _ in range(3):g.state.development_listdeck.remove('KNIGHT')
    ps=g.state.player_state;ps[ek+'_PLAYED_KNIGHT']=3;ps[ek+'_HAS_ARMY']=True
    ps[ek+'_VICTORY_POINTS']+=2;ps[ek+'_ACTUAL_VICTORY_POINTS']+=2
    f.set_hand(g,e,(4,0,0,2,2));f.phase(g,e,True);f.invariant(g)
    return g,c,e


class Round2Tests(unittest.TestCase):
    def test_parents_miss_low_clock_settlement_new_artifacts_win_both_seats(self):
        for seat in (0,1):
            for bot in NEW:
                g,c=settle_win(seat)
                self.assertEqual(pick(OLD[bot],g,c,.0009).action_type,AT.END_TURN)
                a=pick(NEW[bot],g,c,.0009);self.assertIn(a.action_type,(AT.BUILD_SETTLEMENT,AT.BUILD_ROAD))
                g.execute(a);f.invariant(g);self.assertEqual(g.winning_color(),c)

    def test_low_clock_road_bonus_from_eight(self):
        for seat in (0,1):
            for bot in NEW:
                g,c=near(seat,8);f.extend_road(g,c,4);f.set_hand(g,c,(1,1,0,0,0));f.invariant(g)
                a=pick(NEW[bot],g,c,.0009);self.assertEqual(a.action_type,AT.BUILD_ROAD)
                g.execute(a);f.invariant(g);self.assertEqual(g.winning_color(),c)

    def test_low_clock_old_knight_wins_before_roll(self):
        for seat in (0,1):
            for bot,m in NEW.items():
                g,_=f.fresh();c=g.state.colors[seat];f.phase(g,c,True);f.add_settlement(g,c);f.dev(g,c,'VICTORY_POINT',5)
                k=f.key(g,c)
                for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
                g.state.player_state[k+'_PLAYED_KNIGHT']=2;f.dev(g,c,'KNIGHT',old=True);f.phase(g,c,False);f.invariant(g)
                a=pick(m,g,c,.0009);self.assertEqual(a.action_type,AT.PLAY_KNIGHT_CARD)
                g.execute(a);f.invariant(g);self.assertEqual(g.winning_color(),c)

    def test_new_knight_and_army_incumbent_tie_are_not_certified(self):
        m=NEW['B06'];g,c=f.fresh();k=f.key(g,c);e=next(x for x in g.state.colors if x!=c);ek=f.key(g,e)
        f.add_settlement(g,c);f.dev(g,c,'VICTORY_POINT',5)
        for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
        g.state.player_state[k+'_PLAYED_KNIGHT']=2;f.dev(g,c,'KNIGHT',old=False);f.phase(g,c,False)
        obs=Obs(g,c);self.assertIsNone(m.terminal_action(obs,g.playable_actions))
        g.state.player_state[k+'_KNIGHT_OWNED_AT_START']=True
        for _ in range(3):g.state.development_listdeck.remove('KNIGHT')
        ps=g.state.player_state;ps[ek+'_PLAYED_KNIGHT']=3;ps[ek+'_HAS_ARMY']=True;ps[ek+'_VICTORY_POINTS']+=2;ps[ek+'_ACTUAL_VICTORY_POINTS']+=2
        g.playable_actions=generate_playable_actions(g.state);f.invariant(g)
        self.assertIsNone(m.terminal_action(Obs(g,c),g.playable_actions))

    def test_public_terminal_guard_ignores_ghost_but_handles_public_increase(self):
        for m in NEW.values():
            g,c=near();e=next(x for x in g.state.colors if x!=c);k=f.key(g,c);ek=f.key(g,e)
            g.state.colors=(c,e);g.state.player_state[k+'_ACTUAL_VICTORY_POINTS']=10
            g.state.player_state[ek+'_ACTUAL_VICTORY_POINTS']=99
            self.assertTrue(m.public_terminal(g,c,2,3,5))
            g.state.player_state[ek+'_VICTORY_POINTS']=8
            self.assertFalse(m.public_terminal(g,c,7,3,5))
            self.assertTrue(m.public_terminal(g,c,7,1,5))
            g.state.player_state[ek+'_VICTORY_POINTS']=10
            self.assertFalse(m.public_terminal(g,c,7,0,0))
            g.state.colors=(e,c);self.assertTrue(m.public_terminal(g,c,7,3,5))

    def test_zero_clock_no_terminal_never_samples(self):
        for m in NEW.values():
            g,c=f.fresh();f.set_hand(g,c,(4,4,2,2,3))
            self.assertEqual(pick(m,g,c,0).action_type,AT.END_TURN)

    def test_no_roll_buy_or_random_steal_execution(self):
        g,c=f.fresh();f.set_hand(g,c,(4,4,2,2,3));e=next(x for x in g.state.colors if x!=c);f.dev(g,e,'MONOPOLY')
        original=type(g).execute
        def guarded(game,a,*args,**kwargs):
            self.assertNotIn(a.action_type,(AT.ROLL,AT.BUY_DEVELOPMENT_CARD,AT.MOVE_ROBBER));return original(game,a,*args,**kwargs)
        type(g).execute=guarded
        try:
            for m in NEW.values():pick(m,g,c)
        finally:type(g).execute=original

    def test_one_trade_oracle_and_reservations(self):
        helper=NEW['B06'].one_trade_build;count=0
        # Independent actual-state update oracle, exhaustively embedded two-resource cases.
        for h in itertools.product(range(5),repeat=2):
            for cost in itertools.product(range(3),repeat=2):
                for bank in itertools.product(range(3),repeat=2):
                    for ratios in itertools.product((2,3,4),repeat=2):
                        expected=[]
                        for i,j in ((0,1),(1,0)):
                            after=list(h)
                            if after[i]>=ratios[i] and bank[j]>0:
                                after[i]-=ratios[i];after[j]+=1
                                if all(x>=c for x,c in zip(after,cost)):expected.append((i,j))
                        self.assertEqual(helper(h+(0,)*3,cost+(0,)*3,ratios+(4,)*3,bank+(0,)*3),tuple(sorted(expected)));count+=1
        self.assertEqual(count,18225)
        self.assertEqual(helper((4,1,1,0,0),(1,1,1,1,0),(4,)*5,(15,18,18,19,19)),())
        self.assertIn((0,3),helper((5,1,1,0,0),(1,1,1,1,0),(4,)*5,(14,18,18,19,19)))

    def test_b06_parent_misses_trade_city_new_recognizes_and_denial_breaks(self):
        g,c,e=enemy_nine();old=OLD['B06'].Context(g,c,True);new=NEW['B06'].Context(g,c,True);h=(4,0,0,2,2)
        self.assertEqual(old.threat(g,h),0);self.assertEqual(new.threat(g,h),12)
        categories=new.threat_categories(g,h)
        self.assertIn(('city',((0,4),)),categories['one_trade_if_hand_persists']);self.assertFalse(categories['roll_boundary_pending'])
        self.assertEqual(new.threat(g,(3,0,0,2,2)),0)
        f.phase(g,c,True);g.state.player_state[f.key(g,e)+'_HAS_ROLLED']=False
        self.assertTrue(new.threat_categories(g,h)['roll_boundary_pending'])

    def test_b06_bank_piece_and_owned_port_constraints(self):
        g,c,e=enemy_nine();m=NEW['B06'];k=f.key(g,e)
        f.set_hand(g,c,(0,0,0,0,17));ctx=m.Context(g,c,True)
        self.assertEqual(ctx.threat(g,(4,0,0,2,2)),0)
        g,c,e=enemy_nine();g.state.player_state[f.key(g,e)+'_CITIES_AVAILABLE']=0
        self.assertEqual(m.Context(g,c,True).threat(g,(4,0,0,2,2)),0)
        g,c,e=enemy_nine();h=(2,0,0,2,2);ctx=m.Context(g,c,True)
        original=g.state.board.get_player_port_resources
        g.state.board.get_player_port_resources=lambda who:{'WOOD'} if who==e else original(who)
        self.assertEqual(ctx.threat(g,h),12)
        g.state.board.get_player_port_resources=lambda who:set()
        self.assertEqual(m.Context(g,c,True).threat(g,h),0)

    def test_b07_reply_family_and_useful_yop_survive_ordering(self):
        m=NEW['B07'];g,c=f.fresh();e=next(x for x in g.state.colors if x!=c)
        f.set_hand(g,e,(0,0,0,1,2));f.set_hand(g,c,(0,0,0,2,0))
        for d in ('KNIGHT','MONOPOLY','ROAD_BUILDING','YEAR_OF_PLENTY'):f.dev(g,e,d,old=True)
        f.phase(g,e,False);f.invariant(g);ctx=m.Context(g,c,True)
        families=(AT.PLAY_KNIGHT_CARD,AT.PLAY_MONOPOLY,AT.PLAY_ROAD_BUILDING,AT.PLAY_YEAR_OF_PLENTY)
        replies=[a for a in g.playable_actions if a.action_type in families]
        chosen=m.Member4Policy.reply_shortlist(g,ctx,replies)
        self.assertLessEqual(len(chosen),8);self.assertEqual({a.action_type for a in chosen},set(families))
        self.assertIn(('WHEAT','ORE'),[a.value for a in chosen if a.action_type==AT.PLAY_YEAR_OF_PLENTY])
        self.assertEqual(chosen,m.Member4Policy.reply_shortlist(g,ctx,list(reversed(replies))))
        self.assertEqual([a.value for a in chosen if a.action_type==AT.PLAY_MONOPOLY],['WHEAT'])
        # Engine-generated bank shortage removes the impossible two-card YOP.
        f.set_hand(g,c,(19,19,19,18,17));f.set_hand(g,e,(0,0,0,0,0))
        remaining=[a for a in g.playable_actions if a.action_type in families]
        chosen=m.Member4Policy.reply_shortlist(g,ctx,remaining)
        self.assertTrue(all(a in g.playable_actions for a in chosen))

    def test_b07_three_explicit_forecast_controls(self):
        m=NEW['B07'];g,c=f.fresh();f.set_hand(g,c,(4,4,2,2,3));e=next(x for x in g.state.colors if x!=c);f.dev(g,e,'MONOPOLY')
        for mode in ('root','own','full'):
            agent=m.Member4Policy('belief',forecast_mode=mode);obs=Obs(g,c);obs.cpu_left=1
            idx=agent.decide(obs,g.playable_actions);self.assertTrue(0<=idx<len(g.playable_actions))
            if mode=='root':self.assertEqual(agent.sample_attempts,0);self.assertEqual(agent.reply_nodes,0)
            if mode=='own':self.assertEqual(agent.sample_attempts,0);self.assertEqual(agent.reply_nodes,0)

    def test_knight_wait_helper_against_turn_scheduling(self):
        helper=NEW['B08'].knight_wait_rolls
        for needed,held,old,played in itertools.product(range(5),range(5),(False,True),(False,True)):
            pending=needed;turn=0
            while pending:
                if turn>0 or (held and old and not played):pending-=1
                if pending:turn+=1
            self.assertEqual(helper(needed,held,old,played),2*turn)

    def test_b08_parent_zero_wait_corrected(self):
        g,c=f.fresh();k=f.key(g,c)
        for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
        g.state.player_state[k+'_PLAYED_KNIGHT']=2;f.set_hand(g,c,(0,0,2,2,2));f.invariant(g)
        old=next(p for p in OLD['B08'].RouteContext(g,c).plans(g,(0,0,2,2,2)) if p[0]=='army')
        new=next(p for p in NEW['B08'].RouteContext(g,c).plans(g,(0,0,2,2,2)) if p[0]=='army')
        self.assertEqual(old[-1],0);self.assertEqual(new[-1],2)
        a=next(a for a in g.playable_actions if a.action_type==AT.BUY_DEVELOPMENT_CARD)
        g.execute(a,action_record=ActionRecord(a,'KNIGHT'));f.invariant(g)
        self.assertFalse(any(a.action_type==AT.PLAY_KNIGHT_CARD for a in g.playable_actions))

    def test_b08_cache_exact_equivalence_and_invalidation(self):
        m=NEW['B08'];g,c=f.fresh();f.set_hand(g,c,(4,4,2,2,3));h=(4,4,2,2,3)
        cache=m.RouteContext(g,c);plain=m.RouteContext(g,c,cache=False)
        self.assertEqual(cache.value(g),plain.value(g));calls=cache.estimate_calls
        self.assertEqual(cache.value(g),plain.value(g));self.assertEqual(cache.estimate_calls,calls);self.assertGreater(cache.cache_hits,0)
        variants=[]
        for label in ('bank','robber','army','devflag','hand'):
            v=g.copy();ps=v.state.player_state;k=f.key(v,c)
            if label=='bank':v.state.resource_freqdeck[4]-=1
            elif label=='robber':v.state.board.robber_coordinate=next(x for x in v.state.board.map.land_tiles if x!=v.state.board.robber_coordinate)
            elif label=='army':ps[k+'_HAS_ARMY']=True
            elif label=='devflag':ps[k+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN']=True
            elif label=='hand':ps[k+'_WHEAT_IN_HAND']-=1
            variants.append(v)
        for v in variants:self.assertEqual(cache.value(v),m.RouteContext(v,c,cache=False).value(v))
        for n in range(180):cache.potential(g,(n,0,0,0,0))
        self.assertLessEqual(len(cache.potential_cache),128)

    def test_b08_held_old_new_played_and_no_supply(self):
        m=NEW['B08']
        for old,played,expected in ((True,False,0),(False,False,2),(True,True,2)):
            g,c=f.fresh();k=f.key(g,c)
            for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
            g.state.player_state[k+'_PLAYED_KNIGHT']=2;f.dev(g,c,'KNIGHT',old=old)
            g.state.player_state[k+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN']=played
            ctx=m.RouteContext(g,c);army=next(p for p in ctx.plans(g,(0,)*5) if p[0]=='army');self.assertEqual(army[-1],expected)
        g,c=f.fresh();ctx=m.RouteContext(g,c);ctx.pool=(0,)+ctx.pool[1:];ctx.draw_probs=(0,)+ctx.draw_probs[1:]
        self.assertNotIn('army',{p[0] for p in ctx.plans(g,(0,)*5)})

    def test_b05_reserves_lower_scoring_exact_purchase_enabler(self):
        m=NEW['B05'];g,c=near();f.set_hand(g,c,(4,4,0,1,3));ctx=m.Context(g,c,False)
        trade=next(a for a in g.playable_actions if a.action_type==AT.MARITIME_TRADE and a.value[-1]=='WHEAT')
        child=g.copy();child.execute(trade)
        actions=[Action(c,AT.BUILD_ROAD,(0,1))]*5+[trade]
        # Synthetic ranking isolates shortlist policy; trade and child are real/legal.
        rows=[(100-i,i,g.copy()) for i in range(5)]+[(0,5,child)]
        selected=m.Policy.reserve_enablers(g,ctx,actions,rows)
        self.assertEqual(len(selected),5);self.assertIn(5,[r[1] for r in selected]);self.assertEqual([r[1] for r in selected[:3]],[0,1,2])
        self.assertNotIn(5,[r[1] for r in rows[:5]])

    def test_b05_actual_trade_chain_and_unavailable_bank(self):
        m=NEW['B05'];g,c=near();f.set_hand(g,c,(8,0,0,0,3))
        # Actual city completion needs two trades; legality/cost checked each step.
        for _ in range(3):
            a=pick(m,g,c);g.execute(a)
            if g.winning_color()==c:break
        self.assertEqual(g.winning_color(),c);f.invariant(g)
        g,c=near();e=next(x for x in g.state.colors if x!=c)
        f.set_hand(g,e,(0,0,0,19,0));f.set_hand(g,c,(8,0,0,0,3))
        self.assertFalse(any(a.action_type==AT.MARITIME_TRADE and a.value[-1]=='WHEAT' for a in g.playable_actions))
        pick(m,g,c)

if __name__=='__main__':unittest.main(verbosity=2)
