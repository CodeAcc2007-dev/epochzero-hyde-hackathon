from pathlib import Path
import hashlib
base=Path(__file__).resolve().parent;root=base.parents[3]
s=(root/'team-work/member-1/bots/B01/v003/agent.py').read_text()
s=s.replace('standalone v003 flexible-purchase revision','development tactical two-road completion')
helper=(base/'terminal_two_roads.py').read_text()
s=s.replace('class EconomyPolicy:',helper+'\n\nclass EconomyPolicy:')
old='''        world=obs.sample_world(random.Random(0))'''
new='''        terminal,nodes,cut=terminal_two_roads(obs,actions,min(deadline,start+.008))
        self.terminal_nodes+=nodes;self.terminal_cutoffs+=cut
        if terminal is not None:
            self.terminal_trades+=1
            return int(terminal)
        world=obs.sample_world(random.Random(0))'''
assert s.count(old)==1;s=s.replace(old,new)
p=base/'candidates/tactical/agent.py';p.parent.mkdir(exist_ok=False)
compile(s,str(p),'exec');p.write_text(s);print(hashlib.sha256(p.read_bytes()).hexdigest())
