"""External constructed-call timing and partial legal-history profiles, not strength."""
import hashlib,json,random,statistics,time
from pathlib import Path
import test_round2 as r
from catan_kit.obs import Obs,masked_copy
from catanatron.game import Game
from catanatron.models.player import Color,RandomPlayer
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]

def main():
 profile={};histories={};anchor_module=r.load('diagnostic_f',ROOT/'shared-local/organizer-kit/examples/f_agent.py')
 for num,(bot,m) in enumerate(r.NEW.items()):
  g,c=r.settle_win();obs=Obs(masked_copy(g,c,random.Random(30)),c);obs.cpu_left=.0009;obs.sample_world=lambda rng:(_ for _ in ()).throw(AssertionError('Emergency sample'))
  agent=m.Agent();times=[]
  for _ in range(200):
   start=time.process_time();i=agent.decide(obs,obs._game.playable_actions);times.append(time.process_time()-start)
   end=g.copy();end.execute(g.playable_actions[i]);assert end.winning_color()==c
  profile[bot]={'calls':200,'source_sha256':hashlib.sha256(r.path(bot).read_bytes()).hexdigest(),'median_cpu_s':statistics.median(times),'p95_cpu_s':sorted(times)[189],'max_cpu_s':max(times),'scope':'Constructed low-clock settlement-win calls; excludes serialization and does not certify zero-credit/scorer timing'}
  random.seed(935600+num);game=Game([RandomPlayer(Color.RED),RandomPlayer(Color.BLUE)],seed=935600+num)
  me=game.state.colors[0];agent=m.Agent();anchor=anchor_module.Agent();contexts=[]
  Original=m.EconomyContext
  class Capture(Original):
   def __init__(self,g,*args,**kwargs):
    super().__init__(g,*args,**kwargs);self.root=g;self.root_calls=0;contexts.append(self)
   def action_value(self,g,a):
    if g is self.root:self.root_calls+=1
    return super().action_value(g,a)
  m.EconomyContext=Capture
  history=[];decisions=[];changes=0
  try:
   for step in range(100):
    if game.winning_color() is not None:break
    color=game.state.current_color();actions=game.playable_actions;obs=Obs(masked_copy(game,color,random.Random(step+17)),color);obs.cpu_left=1
    if len(actions)==1:i=0
    elif color==me:
     before={k:v for k,v in vars(agent).items() if isinstance(v,(int,float))};prior=len(contexts);start=time.process_time()
     i=agent.decide(obs,actions);elapsed=time.process_time()-start
     parent=r.OLD[bot].Agent().decide(obs,actions);changes+=parent!=i
     decisions.append({'step':step,'prompt':str(game.state.current_prompt),'legal_roots':len(actions),'root_evaluated':sum(ctx.root_calls for ctx in contexts[prior:]),'cpu_s':elapsed,'chosen':repr(actions[i]),'parent_chosen':repr(actions[parent]),'differs_from_parent':parent!=i,'counters':{k:v-before.get(k,0) for k,v in vars(agent).items() if isinstance(v,(int,float))}})
    else:i=anchor.decide(obs,actions)
    assert type(i) is int and 0<=i<len(actions)
    action=actions[i];result=game.execute(action);r.f.invariant(game)
    history.append({'step':step,'color':str(color),'action':repr(action),'engine_record':repr(result)})
  finally:m.EconomyContext=Original
  histories[bot]={'seed':935600+num,'source_sha256':hashlib.sha256(r.path(bot).read_bytes()).hexdigest(),'scope':'At most 100 actions against F with generous fixed decision credit, ordinary engine dice; parent choices are external controls. Not original-clock match evidence or a causal strength test. Time-cutoff differences may change choices.','actions':len(history),'completed_game':game.winning_color() is not None,'winner':str(game.winning_color()),'different_decisions':changes,'decisions':decisions,'history':history}
  print(json.dumps({'bot':bot,'profile':profile[bot],'partial_actions':len(history),'changed_decisions':changes}),flush=True)
 (BASE/'terminal-profile.json').write_text(json.dumps(profile,indent=2)+'\n');(BASE/'diagnostics.json').write_text(json.dumps(histories,indent=2)+'\n')
if __name__=='__main__':main()
