"""Targeted new-policy contracts, constructed states rather than match evidence."""
import sys,unittest,random,importlib.util,itertools,math
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE.parent/'round-2'))
import test_terminal_regressions as r
from catan_kit.obs import Obs,masked_copy
from catanatron.models.enums import ActionType as AT,ActionPrompt as AP
from catanatron.game import Game
from catanatron.models.player import RandomPlayer,Color
mods={n:r.load('specific_'+n,BASE/'candidates'/n/'agent.py') for n in ('menu','opening','combined','search')}
parent=r.load('specific_parent',ROOT/'team-work/member-1/bots/B01/v002/agent.py')

class SprintTests(unittest.TestCase):
 def test_goal_reconsiders_changed_hand_instead_of_stale_family(self):
  # Geometry is genuine engine-generated; alternate hands are counterfactual.
  g,c=r.f.fresh();g=r.f.road_settlement_fixture(g,c)
  for a in g.playable_actions:
   if a.action_type==AT.BUILD_ROAD:
    h=g.copy();h.execute(a)
    if any(x.action_type==AT.BUILD_SETTLEMENT for x in h.playable_actions):g=h;break
  r.f.set_hand(g,c,(0,0,0,2,3));old=parent.EconomyContext(g,c)
  self.assertEqual(old.family,'city')
  after=(1,1,1,1,0)
  self.assertEqual(old.goal(g,after)[0],'city')
  for name in ('menu','combined','search'):
   ctx=mods[name].EconomyContext(g,c)
   self.assertEqual(ctx.goal(g,after)[0],'expand')
   self.assertEqual(ctx.goal(g,after)[1],mods[name].SETTLE)
 def test_opening_monotone_and_balanced_equal_total(self):
  for name in ('opening','combined'):
   score=mods[name].opening_score
   self.assertEqual(score((0,0,0,0,0)),0)
   self.assertGreater(score((.08,)*5),score((.4,0,0,0,0)))
   for h in itertools.product((0,.03,.1),repeat=5):
    for i in range(5):
     after=list(h);after[i]+=.01
     self.assertGreater(score(after),score(h))
 def test_reordered_opening_indices_and_observation_immutability(self):
  for m in mods.values():
   g=Game([RandomPlayer(Color.RED),RandomPlayer(Color.BLUE)],seed=938999)
   c=g.state.current_color();obs=Obs(masked_copy(g,c,random.Random(2)),c);obs.cpu_left=1
   before=repr((obs._game.state.player_state,obs._game.state.board.buildings,obs._game.state.action_records))
   actions=list(g.playable_actions);rev=list(reversed(actions))
   a=m.Agent().decide(obs,actions);b=m.Agent().decide(obs,rev)
   # Ties may use original order; compare selected opening score, not node identity.
   ctx=m.EconomyContext(obs.sample_world(random.Random(0)),c)
   def val(action):
    p=ctx.rates.get(action.value,(0,)*5)
    return m.opening_score(p) if hasattr(m,'opening_score') else sum(x*w for x,w in zip(p,(1,1,1,1.15,1.1)))+.11*sum(min(x/.08,1) for x in p)
   self.assertEqual(val(actions[a]),val(rev[b]))
   self.assertEqual(before,repr((obs._game.state.player_state,obs._game.state.board.buildings,obs._game.state.action_records)))
 def test_trade_retains_monotone_certificate_and_no_reexport(self):
  for name in ('menu','combined','search'):
   m=mods[name];accepted=0
   for h in ((4,4,1,1,0),(5,1,1,0,0),(0,1,0,2,4),(0,0,4,2,3),(0,0,0,1,7)):
    g,c=r.f.fresh();r.f.set_hand(g,c,h);ctx=m.EconomyContext(g,c)
    for a in g.playable_actions:
     if a.action_type!=AT.MARITIME_TRADE:continue
     child=g.copy();child.execute(a)
     if not ctx.trade_allowed(g,child,a):continue
     accepted+=1
     self.assertTrue(any(m.improves_goal(h,m.hand(child.state,ctx.key),p[1],ctx.board_features(g)[3],tuple(g.state.resource_freqdeck),tuple(child.state.resource_freqdeck)) for p in ctx.specs(g)))
     # Add cards as a constructed follow-on state so an imported good CAN be
     # exported legally; policy must still refuse it this turn.
     imported=a.value[-1];hh=list(m.hand(child.state,ctx.key));hh[m.RES.index(imported)]=8;r.f.set_hand(child,c,hh)
     for b in child.playable_actions:
      if b.action_type==AT.MARITIME_TRADE and b.value[0]==imported:
       end=child.copy();end.execute(b)
       self.assertFalse(ctx.trade_allowed(child,end,b))
   self.assertGreater(accepted,0)
 def test_reordered_rich_turn_roots_legal_and_nonmutating(self):
  for m in mods.values():
   g,c=r.f.fresh();r.f.set_hand(g,c,(4,4,2,2,3))
   obs=Obs(masked_copy(g,c,random.Random(33)),c);obs.cpu_left=.4
   before=repr((obs._game.state.player_state,obs._game.state.board.buildings,obs._game.state.board.roads,obs._game.state.action_records))
   actions=list(reversed(obs._game.playable_actions))
   chosen=m.Agent().decide(obs,actions)
   self.assertIs(type(chosen),int);self.assertTrue(0<=chosen<len(actions))
   self.assertEqual(before,repr((obs._game.state.player_state,obs._game.state.board.buildings,obs._game.state.board.roads,obs._game.state.action_records)))
   copy=g.copy();copy.execute(actions[chosen]);r.f.invariant(copy)

if __name__=='__main__':unittest.main(verbosity=2)
