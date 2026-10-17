"""New bounded-certificate regressions on constructed engine states."""
import sys,time,random,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE))
import test_terminal_regressions as r
from catan_kit.obs import Obs,masked_copy
from catanatron.models.enums import ActionType as AT
M=r.load('two_roads_candidate',BASE/'candidates/tactical/agent.py')
OLD=r.load('two_roads_parent',ROOT/'team-work/member-1/bots/B01/v003/agent.py')
BASELINE=r.load('two_roads_baseline',ROOT/'team-work/member-1/bots/B01/v002/agent.py')

def fixture(seat=0):
 g,c=r.near(seat,8);r.f.extend_road(g,c,3);r.f.phase(g,c,True);r.f.set_hand(g,c,(1,2,0,2,6));r.f.invariant(g);return g,c

class TwoRoadTests(unittest.TestCase):
 def test_old_misses_and_new_completes_win_in_both_seats(self):
  for seat in (0,1):
   g,c=fixture(seat)
   for previous in (BASELINE,OLD):
    old=g.copy()
    a=r.pick(previous,old,c);self.assertEqual(a.action_type,AT.BUILD_CITY);old.execute(a)
    for _ in range(6):
     a=r.pick(previous,old,c)
     if a.action_type==AT.END_TURN:break
     old.execute(a)
    self.assertIsNone(old.winning_color())
   for step in range(3):
    a=r.pick(M,g,c)
    if step==0:self.assertEqual(a.action_type,AT.MARITIME_TRADE)
    else:self.assertEqual(a.action_type,AT.BUILD_ROAD)
    g.execute(a);r.f.invariant(g)
   self.assertEqual(g.winning_color(),c)
 def test_deadline_and_phase_guards(self):
  g,c=fixture();obs=Obs(g,c)
  self.assertEqual(M.terminal_two_roads(obs,g.playable_actions,time.process_time()-1),(None,0,True))
  early,c=r.f.fresh();self.assertEqual(M.terminal_two_roads(Obs(early,c),early.playable_actions,time.process_time()+1),(None,0,False))
  r.f.phase(g,c,False)
  self.assertEqual(M.terminal_two_roads(Obs(g,c),g.playable_actions,time.process_time()+1),(None,0,False))
 def test_strict_opponent_road_target(self):
  for length in (5,6):
   g,c=fixture();e=next(x for x in g.state.colors if x!=c)
   r.f.extend_road(g,e,length);r.f.phase(g,c,True);r.f.set_hand(g,c,(1,2,0,2,6));r.f.invariant(g)
   self.assertEqual(M.terminal_two_roads(Obs(g,c),g.playable_actions,time.process_time()+1),(None,0,False))
 def test_original_indices_copy_bound_immutability_and_chance_boundary(self):
  original=r.f.Game.execute
  def guarded(g,a,*args,**kwargs):
   self.assertNotIn(a.action_type,(AT.ROLL,AT.BUY_DEVELOPMENT_CARD,AT.MOVE_ROBBER));return original(g,a,*args,**kwargs)
  for seat in (0,1):
   g,c=fixture(seat);actions=list(reversed(g.playable_actions));obs=Obs(masked_copy(g,c,random.Random(27)),c)
   before=repr((obs._game.state.player_state,obs._game.state.board.roads,obs._game.state.resource_freqdeck,obs._game.state.action_records))
   r.f.Game.execute=guarded
   try:index,copies,cut=M.terminal_two_roads(obs,actions,time.process_time()+1)
   finally:r.f.Game.execute=original
   self.assertIsNotNone(index);self.assertLessEqual(copies,80)
   self.assertEqual(actions[index].action_type,AT.MARITIME_TRADE)
   self.assertEqual(before,repr((obs._game.state.player_state,obs._game.state.board.roads,obs._game.state.resource_freqdeck,obs._game.state.action_records)))
 def test_road_building_card_can_complete_without_resource_cost(self):
  for seat in (0,1):
   g,c=fixture(seat);r.f.set_hand(g,c,(0,0,0,0,0));r.f.dev(g,c,'ROAD_BUILDING',old=True);r.f.invariant(g)
   obs=Obs(g,c);index,copies,cut=M.terminal_two_roads(obs,g.playable_actions,time.process_time()+1)
   self.assertIsNotNone(index);self.assertEqual(g.playable_actions[index].action_type,AT.PLAY_ROAD_BUILDING)
   resources=M.hand(g.state,r.f.key(g,c))
   for _ in range(3):
    a=r.pick(M,g,c);g.execute(a);r.f.invariant(g)
    if g.winning_color()==c:break
   self.assertEqual(g.winning_color(),c);self.assertEqual(M.hand(g.state,r.f.key(g,c)),resources)
 def test_bank_and_card_eligibility_follow_legal_roots(self):
  g,c=fixture();r.f.set_hand(g,c,(0,0,0,0,0));r.f.dev(g,c,'ROAD_BUILDING',old=False)
  self.assertFalse(any(a.action_type==AT.PLAY_ROAD_BUILDING for a in g.playable_actions))
  self.assertIsNone(M.terminal_two_roads(Obs(g,c),g.playable_actions,time.process_time()+1)[0])
  g,c=fixture();e=next(x for x in g.state.colors if x!=c);r.f.set_hand(g,e,(18,0,0,0,0));r.f.invariant(g)
  self.assertFalse(any(a.action_type==AT.MARITIME_TRADE and a.value[-1]=='WOOD' for a in g.playable_actions))
  self.assertIsNone(M.terminal_two_roads(Obs(g,c),g.playable_actions,time.process_time()+1)[0])

if __name__=='__main__':unittest.main(verbosity=2)
