"""Primary-authored chance/public-bound/turn eligibility contract cases."""
import random,time,unittest
import test_terminal_regressions as r
from catan_kit.obs import Obs,masked_copy
from catanatron.models.enums import ActionType as AT
from catanatron.models.actions import generate_playable_actions

class TerminalGuards(unittest.TestCase):
 def test_new_knight_tie_owned_army_and_already_played_are_not_wins(self):
  for m in r.NEW.values():
   for seat in (0,1):
    for mode in ('new','tie','owned','played'):
     g,_=r.f.fresh();c=g.state.colors[seat];r.f.phase(g,c,True);e=next(x for x in g.state.colors if x!=c)
     r.f.add_settlement(g,c);r.f.dev(g,c,'VICTORY_POINT',5);k=r.f.key(g,c);ek=r.f.key(g,e)
     for _ in range(2):g.state.development_listdeck.remove('KNIGHT')
     ps=g.state.player_state;ps[k+'_PLAYED_KNIGHT']=2;r.f.dev(g,c,'KNIGHT',old=mode!='new')
     if mode=='tie':
      for _ in range(3):g.state.development_listdeck.remove('KNIGHT')
      ps[ek+'_PLAYED_KNIGHT']=3;ps[ek+'_HAS_ARMY']=True;ps[ek+'_VICTORY_POINTS']+=2;ps[ek+'_ACTUAL_VICTORY_POINTS']+=2
     if mode=='owned':
      # Already-owned Army, eight actual VP with no incremental two-point gain.
      ps[k+'_HAS_ARMY']=True;ps[k+'_VICTORY_POINTS']+=2;ps[k+'_ACTUAL_VICTORY_POINTS']+=2
      ps[k+'_VICTORY_POINT_IN_HAND']-=2;ps[k+'_ACTUAL_VICTORY_POINTS']-=2;g.state.development_listdeck.extend(['VICTORY_POINT']*2)
      ps[k+'_PLAYED_KNIGHT']=3;g.state.development_listdeck.remove('KNIGHT')
     if mode=='played':ps[k+'_HAS_PLAYED_DEVELOPMENT_CARD_IN_TURN']=True
     r.f.phase(g,c,False);r.f.invariant(g)
     self.assertIsNone(m.terminal_action(Obs(g,c),g.playable_actions))
 def test_public_guard_ignores_hidden_ghost_and_checks_new_public_vp(self):
  for m in r.NEW.values():
   g,c=r.near();e=next(x for x in g.state.colors if x!=c);k=r.f.key(g,c);ek=r.f.key(g,e)
   g.state.colors=(c,e);ps=g.state.player_state;ps[k+'_ACTUAL_VICTORY_POINTS']=10;ps[ek+'_ACTUAL_VICTORY_POINTS']=99
   self.assertTrue(m.public_terminal(g,c,2,3,5))
   ps[ek+'_VICTORY_POINTS']=8;self.assertFalse(m.public_terminal(g,c,7,3,5));self.assertTrue(m.public_terminal(g,c,7,1,5))
   ps[ek+'_VICTORY_POINTS']=10;self.assertFalse(m.public_terminal(g,c,7,0,0))
   g.state.colors=(e,c);self.assertTrue(m.public_terminal(g,c,7,3,5))
 def test_no_chance_execution_or_identity_dependence_in_certificates(self):
  original=r.f.Game.execute
  def guard(g,a,*args,**kwargs):
   self.assertNotIn(a.action_type,(AT.ROLL,AT.BUY_DEVELOPMENT_CARD,AT.MOVE_ROBBER));return original(g,a,*args,**kwargs)
  r.f.Game.execute=guard
  try:
   for m in r.NEW.values():
    g,c=r.road_trade();e=next(x for x in g.state.colors if x!=c);r.f.dev(g,e,'MONOPOLY')
    choices=[]
    for seed in (1,2,3):
     obs=Obs(masked_copy(g,c,random.Random(seed)),c);obs.cpu_left=1
     i=m.Agent().decide(obs,obs._game.playable_actions);choices.append(obs._game.playable_actions[i])
    self.assertTrue(all(a==choices[0] for a in choices));self.assertEqual(choices[0].action_type,AT.MARITIME_TRADE)
    g,c=r.f.fresh();r.f.set_hand(g,c,(4,4,2,2,3));r.pick(m,g,c)
  finally:r.f.Game.execute=original

if __name__=='__main__':unittest.main(verbosity=2)
