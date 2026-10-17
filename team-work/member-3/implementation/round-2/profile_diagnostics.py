"""External partial legal-history diagnostics; not official match/strength evidence."""
import collections, hashlib, json, random, sys, time
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE))
import test_round2 as r
from catan_kit.obs import Obs, masked_copy
from catanatron.game import Game
from catanatron.models.player import Color, RandomPlayer
from catanatron.models.enums import ActionType as AT


def main():
    fmodule=r.load('diagnostic_f',ROOT/'shared-local/organizer-kit/examples/f_agent.py')
    records={}
    for num,(bot,module) in enumerate(r.NEW.items()):
        random.seed(933600+num)
        game=Game([RandomPlayer(Color.RED),RandomPlayer(Color.BLUE)],seed=933600+num)
        me=game.state.colors[0];agent=module.Agent();anchor=fmodule.Agent()
        contexts=[]
        context_name='RouteContext' if bot=='B08' else 'Context'
        Original=getattr(module,context_name)
        class Capture(Original):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs);contexts.append(self)
        setattr(module,context_name,Capture)
        history=[];decisions=[];control_changes=collections.Counter();control_calls=0
        for step in range(100):
            if game.winning_color() is not None:break
            color=game.state.current_color();actions=game.playable_actions
            obs=Obs(masked_copy(game,color,random.Random(step+17)),color);obs.cpu_left=1.0
            if len(actions)==1:index=0
            elif color==me:
                copies=[0];execute_count=[0];old_copy=Game.copy;old_execute=Game.execute
                def copied(g):copies[0]+=1;return old_copy(g)
                def executed(g,a,*args,**kwargs):execute_count[0]+=1;return old_execute(g,a,*args,**kwargs)
                Game.copy=copied;Game.execute=executed
                before={k:v for k,v in vars(agent).items() if isinstance(v,(int,float))}
                started=time.process_time();prior_contexts=len(contexts)
                try:index=agent.decide(obs,actions)
                finally:Game.copy=old_copy;Game.execute=old_execute
                elapsed=time.process_time()-started
                after={k:v-before.get(k,0) for k,v in vars(agent).items() if isinstance(v,(int,float))}
                row={'step':step,'prompt':str(game.state.current_prompt),'legal_roots':len(actions),'chosen':repr(actions[index]),'cpu_s':elapsed,'copies':copies[0],'simulated_actions':execute_count[0],'counters':after}
                if bot=='B08':
                    new_contexts=contexts[prior_contexts:]
                    row['route_cache']={key:sum(getattr(c,key,0) for c in new_contexts) for key in ('cache_hits','cache_misses','estimate_calls')}
                if bot=='B07' and obs.opp_dev_count:
                    controls={}
                    for mode in ('root','own','full'):
                        control=module.Member4Policy('belief',forecast_mode=mode)
                        controls[mode]={'index':control.decide(obs,actions),'reply_nodes':control.reply_nodes,'comparisons':control.reply_comparisons,'samples':control.valid_samples,'cutoffs':control.cutoffs}
                    control_calls+=1
                    for mode in ('own','full'):control_changes[mode]+=controls[mode]['index']!=controls['root']['index']
                    row['controls']=controls
                decisions.append(row)
            else:index=anchor.decide(obs,actions)
            assert type(index) is int and 0<=index<len(actions)
            action=actions[index];result=game.execute(action)
            history.append({'step':step,'color':str(color),'action':repr(action),'engine_record':repr(result)})
        setattr(module,context_name,Original)
        records[bot]={'scope':'100-action partial legal game history against F, fixed seed, resource/dev outcomes are engine results; not original clock/private dice or strength evidence','seed':933600+num,'actions':len(history),'completed_game':game.winning_color() is not None,'winner':str(game.winning_color()),'source_sha256':hashlib.sha256(r.candidate(bot).read_bytes()).hexdigest(),'decisions':decisions,'history':history,'b07_control_calls':control_calls,'b07_changes_from_root':dict(control_changes)}
        print(json.dumps({'bot':bot,'actions':len(history),'profiled_decisions':len(decisions),'completed_game':game.winning_color() is not None,'controls':control_calls}),flush=True)
    for member in (3,4):
        relevant={b:x for b,x in records.items() if (b in ('B05','B06'))==(member==3)}
        (ROOT/f'team-work/member-{member}/implementation/round-2/diagnostics.json').write_text(json.dumps(relevant,indent=2)+'\n')
if __name__=='__main__':main()
