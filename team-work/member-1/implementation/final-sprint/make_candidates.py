"""Reproducible bounded B01 experiments; parent is never overwritten."""
from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
PARENT=ROOT/'team-work/member-1/bots/B01/v002/agent.py'
source=PARENT.read_text()
assert hashlib.sha256(PARENT.read_bytes()).hexdigest()=='cc53c58ca1867678ad6be9ca074ed6dabdffb54aa9b1c7ca1d83f52271c723f4'

def menu(s):
 s=s.replace('''        retained=[p for p in plans if p[0]==self.family]
        return max(retained or plans,key=lambda p:self.priority(g,h,p),default=None)''','''        # Re-evaluate legal purchase alternatives after every simulated change.
        return max(plans,key=lambda p:self.priority(g,h,p),default=None)''')
 old='''        return improves_goal(h,hand(child.state,self.key),goal[1],self.board_features(g)[3],
                             tuple(g.state.resource_freqdeck),tuple(child.state.resource_freqdeck))'''
 new='''        # Alternative targets must remain competitive before trading and retain
        # their own ingredients. The history guard above still forbids re-export.
        threshold=.85*self.priority(g,h,goal)
        return any(self.priority(g,h,p)>=threshold and
                   improves_goal(h,hand(child.state,self.key),p[1],self.board_features(g)[3],
                                 tuple(g.state.resource_freqdeck),tuple(child.state.resource_freqdeck))
                   for p in self.specs(g))'''
 assert old in s;s=s.replace(old,new)
 old="        frontier=sorted((r for r in ranked if r[2] is not None and r[2].state.current_color()==ctx.me),key=lambda r:(-r[0],r[1]))[:4]"
 new="""        ordered=sorted((r for r in ranked if r[2] is not None and r[2].state.current_color()==ctx.me),key=lambda r:(-r[0],r[1]))
        frontier=ordered[:3]
        # Keep one different action-family root, within the original width4.
        families={world.playable_actions[r[1]].action_type for r in frontier}
        alternative=next((r for r in ordered[3:] if world.playable_actions[r[1]].action_type not in families),None)
        if alternative is not None:frontier.append(alternative)
        elif len(ordered)>3:frontier.append(ordered[3])"""
 # NOTE playable_actions indices are not necessarily the supplied root order:
 # use child action history for family, preserving arbitrary original indices.
 new=new.replace('world.playable_actions[r[1]].action_type','r[2].state.action_records[-1].action.action_type')
 assert old in s;s=s.replace(old,new)
 old='child.state.current_prompt,child.state.free_roads_available)'
 new='''child.state.current_prompt,child.state.free_roads_available,
                                   tuple(child.state.resource_freqdeck),
                                   tuple(record.action.value for record in child.state.action_records
                                         if record.action.action_type==AT.MARITIME_TRADE))'''
 assert old in s;s=s.replace(old,new)
 return s

def opening(s):
 old='return sum(x*w for x,w in zip(combined,(1,1,1,1.15,1.1)))+.11*sum(min(x/.08,1) for x in combined)'
 new='return opening_score(combined)'
 assert old in s;s=s.replace(old,new)
 helper='''def opening_score(combined):
    """Hand-chosen economy heuristic, not predicted win probability.

    Preserve all-resource access while crediting wheat/ore and balanced inputs
    to roads/cities. No board seed, dice sequence or enemy hidden state is used.
    """
    return (sum(x*w for x,w in zip(combined,(.95,.95,1.0,1.35,1.4)))
            +.11*sum(min(x/.08,1) for x in combined)
            +.25*min(combined[0],combined[1])
            +.35*min(combined[3]/2,combined[4]/3))

'''
 return s.replace('class Agent(EconomyPolicy):',helper+'class Agent(EconomyPolicy):')

for name,fn in [('menu',menu),('opening',opening),('combined',lambda s:opening(menu(s)))]:
 text=fn(source).replace('standalone v002 correctness revision','final sprint development '+name)
 compile(text,name,'exec')
 out=BASE/'candidates'/name/'agent.py';out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():assert out.read_text()==text
 else:out.write_text(text)
 print(name,hashlib.sha256(out.read_bytes()).hexdigest())
