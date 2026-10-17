"""Actual standalone regressions on explicit constructed/counterfactual states."""
import hashlib,importlib.util,itertools,json,random,sys,time,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(ROOT/'team-work/member-3/implementation'))
import test_policies as f
from catan_kit.obs import Obs,masked_copy
from catanatron.models.enums import ActionType as AT,ActionPrompt as AP,Action,ActionRecord
from catanatron.models.actions import generate_playable_actions


def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def path(bot):
 p=ROOT/f'team-work/member-1/bots/{bot}/v002/agent.py'
 return p if p.exists() else BASE/'development'/bot/'agent.py'

NEW={b:load('new_'+b,path(b)) for b in ('B01',)}
OLD={b:load('old_'+b,ROOT/f'team-work/member-1/bots/{b}/v001/agent.py') for b in NEW}

def near(seat=0,vp=9):
 g,_=f.fresh();c=g.state.colors[seat];f.phase(g,c,True)
 f.add_settlement(g,c);f.upgrade(g,c);f.dev(g,c,'VICTORY_POINT',vp-4)
 f.invariant(g);return g,c

def road_trade(seat=0):
 g,c=near(seat,8);f.extend_road(g,c,4);f.phase(g,c,True);f.set_hand(g,c,(0,1,0,2,4));f.invariant(g);return g,c

def settle_win(seat=0):
 g,c=near(seat);g=f.road_settlement_fixture(g,c)
 for a in g.playable_actions:
  if a.action_type!=AT.BUILD_ROAD:continue
  h=g.copy();h.execute(a)
  if any(x.action_type==AT.BUILD_SETTLEMENT for x in h.playable_actions):g=h;break
 f.set_hand(g,c,(1,1,1,1,0));f.invariant(g);return g,c

def pick(module,g,c,credit=1):
 before=repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.development_listdeck,g.state.action_records))
 obs=Obs(masked_copy(g,c,random.Random(33)),c);obs.cpu_left=credit
 masked_before=repr((obs._game.state.player_state,obs._game.state.board.buildings,obs._game.state.board.roads,obs._game.state.resource_freqdeck,obs._game.state.development_listdeck,obs._game.state.action_records))
 if credit<=.0009:obs.sample_world=lambda rng:(_ for _ in ()).throw(AssertionError('Emergency path sampled'))
 index=module.Agent().decide(obs,obs._game.playable_actions)
 assert type(index) is int and 0<=index<len(g.playable_actions)
 assert masked_before==repr((obs._game.state.player_state,obs._game.state.board.buildings,obs._game.state.board.roads,obs._game.state.resource_freqdeck,obs._game.state.development_listdeck,obs._game.state.action_records))
 assert before==repr((g.state.player_state,g.state.board.buildings,g.state.board.roads,g.state.resource_freqdeck,g.state.development_listdeck,g.state.action_records))
 return g.playable_actions[index]

class Round2Tests(unittest.TestCase):
 def test_parent_goal_filter_failure_and_new_trade_road_win_both_seats(self):
  for seat in (0,1):
   for bot,m in NEW.items():
    g,c=road_trade(seat);self.assertEqual(pick(OLD[bot],g,c).action_type,AT.BUILD_CITY)
    a=pick(m,g,c);self.assertEqual(a.action_type,AT.MARITIME_TRADE);self.assertEqual(a.value[-1],'WOOD')
    g.execute(a);f.invariant(g);a=pick(m,g,c);self.assertEqual(a.action_type,AT.BUILD_ROAD)
    g.execute(a);f.invariant(g);self.assertEqual(g.winning_color(),c)
 def test_parent_low_clock_failure_and_new_settlement_win(self):
  for seat in (0,1):
   for bot,m in NEW.items():
    g,c=settle_win(seat);self.assertEqual(pick(OLD[bot],g,c,.0009).action_type,AT.END_TURN)
    g.execute(pick(m,g,c,.0009));f.invariant(g);self.assertEqual(g.winning_color(),c)
 def test_low_clock_city_and_road_bonus_both_seats(self):
  for seat in (0,1):
   for m in NEW.values():
    for road in (False,True):
     g,c=near(seat,8 if road else 9)
     if road:f.extend_road(g,c,4)
     f.set_hand(g,c,(1,1,0,0,0) if road else f.CITY)
     g.execute(pick(m,g,c,.0009));f.invariant(g);self.assertEqual(g.winning_color(),c)
 def test_low_clock_old_knight_before_roll_both_seats(self):
  for seat in (0,1):
   for m in NEW.values():
    g,_=f.fresh();c=g.state.colors[seat];f.phase(g,c,True);f.add_settlement(g,c);f.dev(g,c,'VICTORY_POINT',5);k=f.key(g,c)
    for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
    g.state.player_state[k+'_PLAYED_KNIGHT']=2;f.dev(g,c,'KNIGHT',old=True);f.phase(g,c,False);f.invariant(g)
    a=pick(m,g,c,.0009);self.assertEqual(a.action_type,AT.PLAY_KNIGHT_CARD);g.execute(a);f.invariant(g);self.assertEqual(g.winning_color(),c)
 def test_immediate_win_precedes_trade_search(self):
  for m in NEW.values():
   g,c=near();f.extend_road(g,c,4);f.set_hand(g,c,(0,1,0,2,4))
   a=pick(m,g,c);self.assertEqual(a.action_type,AT.BUILD_CITY);g.execute(a);self.assertEqual(g.winning_color(),c)
 def test_no_terminal_fallback_and_expired_trade_deadline(self):
  for m in NEW.values():
   for seat in (0,1):
    g,_=f.fresh();c=g.state.colors[seat];f.phase(g,c,True)
    self.assertEqual(pick(m,g,c,0).action_type,AT.END_TURN)
    f.phase(g,c,False);self.assertEqual(pick(m,g,c,0).action_type,AT.ROLL)
   g,c=road_trade();self.assertEqual(m.terminal_trade(Obs(g,c),g.playable_actions,time.process_time()-1),(None,0,True))
 def test_trade_certificate_honors_reordered_original_roots(self):
  for m in NEW.values():
   g,c=road_trade();obs=Obs(masked_copy(g,c,random.Random(9)),c);obs.cpu_left=1
   actions=list(reversed(obs._game.playable_actions));i=m.Agent().decide(obs,actions)
   self.assertIs(type(i),int);a=actions[i];self.assertEqual(a.action_type,AT.MARITIME_TRADE)
   h=g.copy();h.execute(a);h.execute(pick(m,h,c));f.invariant(h);self.assertEqual(h.winning_color(),c)
 def test_nonterminal_road_and_opponent_road_tie_or_longer(self):
  for m in NEW.values():
   for length in (5,6):
    g,c=road_trade();e=next(x for x in g.state.colors if x!=c)
    f.extend_road(g,e,length);f.phase(g,c,True);f.set_hand(g,c,(0,1,0,2,4));f.invariant(g)
    result,n,cut=m.terminal_trade(Obs(g,c),g.playable_actions,time.process_time()+1)
    self.assertIsNone(result);self.assertLessEqual(n,48);self.assertFalse(cut)
   g,c=near(vp=8);f.set_hand(g,c,(0,1,0,2,4))
   self.assertIsNone(m.terminal_trade(Obs(g,c),g.playable_actions,time.process_time()+1)[0])
 def test_depleted_bank_and_no_road_piece_legal_menus(self):
  for m in NEW.values():
   g,c=road_trade();e=next(x for x in g.state.colors if x!=c);f.set_hand(g,e,(19,0,0,0,0));f.invariant(g)
   self.assertFalse(any(a.action_type==AT.MARITIME_TRADE and a.value[-1]=='WOOD' for a in g.playable_actions))
   self.assertIsNone(m.terminal_trade(Obs(g,c),g.playable_actions,time.process_time()+1)[0])
   # Explicit counterfactual exhausted piece menu, not a reached fifteen-road board.
   g,c=road_trade();g.state.player_state[f.key(g,c)+'_ROADS_AVAILABLE']=0;g.playable_actions=generate_playable_actions(g.state)
   self.assertIsNone(m.terminal_trade(Obs(g,c),g.playable_actions,time.process_time()+1)[0])
 def test_blocked_road_extension_uses_engine_geometry(self):
  for m in NEW.values():
   g,c=road_trade();e=next(x for x in g.state.colors if x!=c);f.set_hand(g,c,(1,1,0,0,0))
   before={a.value for a in g.playable_actions if a.action_type==AT.BUILD_ROAD}
   owned=set().union(*g.state.board.connected_components[c])
   candidates=owned.intersection(g.state.board.buildable_node_ids(e,True));blocked=None
   for n in candidates:
    h=g.copy()
    # Connect the enemy's counterfactual isolated component to n, then run
    # ordinary placement so engine endpoint/cut maintenance is exercised.
    h.state.board.connected_components[e].append({n})
    result=h.state.board.build_settlement(e,n,False);f.sf.build_settlement(h.state,e,n,True);f.sf.maintain_longest_road(h.state,*result)
    f.set_hand(h,c,(1,1,0,0,0));after={a.value for a in h.playable_actions if a.action_type==AT.BUILD_ROAD}
    if before-after:blocked=h;break
   self.assertIsNotNone(blocked);f.invariant(blocked)
   f.set_hand(blocked,c,(0,1,0,2,4));f.invariant(blocked)
   result,n,_=m.terminal_trade(Obs(blocked,c),blocked.playable_actions,time.process_time()+1)
   if result is not None:
    blocked.execute(blocked.playable_actions[result]);j=m.terminal_action(Obs(blocked,c),blocked.playable_actions)
    self.assertIsNotNone(j);blocked.execute(blocked.playable_actions[j]);f.invariant(blocked);self.assertEqual(blocked.winning_color(),c)
 def test_trade_certificates_against_independent_engine_oracle(self):
  cases=0
  for seat in (0,1):
   for enemy_length in (0,5,6):
    template,c=road_trade(seat);e=next(x for x in template.state.colors if x!=c)
    if enemy_length:f.extend_road(template,e,enemy_length)
    f.phase(template,c,True)
    for brick,wheat,ore in itertools.product((0,1),(0,2),(0,3,4,8)):
     g=template.copy();f.set_hand(g,c,(0,brick,0,wheat,ore));f.invariant(g)
     expected=[]
     for root,a in enumerate(g.playable_actions):
      if a.action_type!=AT.MARITIME_TRADE:continue
      child=g.copy();child.execute(a)
      for b in child.playable_actions:
       if b.action_type not in (AT.BUILD_CITY,AT.BUILD_SETTLEMENT,AT.BUILD_ROAD):continue
       end=child.copy();end.execute(b);f.invariant(end)
       if end.winning_color()==c:expected.append(root);break
     for m in NEW.values():
      index,n,cut=m.terminal_trade(Obs(g,c),g.playable_actions,time.process_time()+1)
      self.assertLessEqual(n,48)
      if index is not None:self.assertIn(index,expected)
      elif not cut:self.assertFalse(expected)
     cases+=1
  self.assertEqual(cases,96)
 def test_full_discard_sequences_record_retained_goal_and_oracle(self):
  records=[]
  for bot,m in NEW.items():
   for out_of_turn in (False,True):
    for original in ((0,0,1,2,6),(5,2,1,1,0),(4,4,2,2,3)):
     g,c=f.fresh();e=next(x for x in g.state.colors if x!=c);roller=e if out_of_turn else c
     f.set_hand(g,c,original);f.phase(g,roller,False)
     roll=next(a for a in g.playable_actions if a.action_type==AT.ROLL)
     g.execute(roll,action_record=ActionRecord(roll,(1,6)));st=g.state
     self.assertEqual(st.current_color(),c);initial=m.EconomyContext(g,c,bot=='B02');goal=initial.goal(g,original);families=[]
     quota=sum(original)//2
     for left in range(quota,0,-1):
      self.assertEqual(st.discard_counts[st.color_to_index[c]],left)
      ctx=m.EconomyContext(g,c,bot=='B02');families.append(ctx.family);a=pick(m,g,c);self.assertEqual(a.action_type,AT.DISCARD_RESOURCE)
      g.execute(a);f.invariant(g)
     self.assertEqual(st.current_color(),roller);self.assertEqual(st.current_prompt,AP.MOVE_ROBBER)
     self.assertEqual(sum(m.hand(st,f.key(g,c))),sum(original)-quota);self.assertFalse(st.is_discarding)
     h=m.hand(st,f.key(g,c));ratios=initial.board_features(g)[3];outcomes=[]
     for kept in itertools.product(*(range(x+1) for x in original)):
      if sum(kept)!=sum(original)-quota:continue
      bank=tuple(19-x for x in kept);outcomes.append((m.goal_priority(kept,goal[1],ratios,bank,goal[2]),kept))
     got=m.goal_priority(h,goal[1],ratios,tuple(st.resource_freqdeck),goal[2]);best=max(outcomes)
     if original==(0,0,1,2,6):self.assertAlmostEqual(got,best[0])
     records.append({'bot':bot,'out_of_turn':out_of_turn,'initial_hand':original,'families':families,'retained_hand':h,'fixed_initial_goal_oracle':best,'chosen_score':got,'score_regret':best[0]-got})
  self.discard_records = records

if __name__=='__main__':unittest.main(verbosity=2)
