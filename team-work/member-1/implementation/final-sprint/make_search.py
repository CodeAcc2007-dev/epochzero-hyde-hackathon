from pathlib import Path
import hashlib
base=Path(__file__).resolve().parent
s=(base/'candidates/menu/agent.py').read_text()
s=s.replace('final sprint development menu','final sprint development search')
s=s.replace('frontier=ordered[:3]','frontier=ordered[:4]').replace('ordered[3:]','ordered[4:]').replace('elif len(ordered)>3:frontier.append(ordered[3])','elif len(ordered)>4:frontier.append(ordered[4])').replace('within the original width4','within width5')
s=s.replace('for depth in (2,3):','for depth in (2,3,4):').replace('count>=52','count>=80').replace("frontier=sorted(following,key=lambda r:(-r[0],r[1]))[:4]","frontier=sorted(following,key=lambda r:(-r[0],r[1]))[:5]")
p=base/'candidates/search/agent.py';p.parent.mkdir(exist_ok=True)
assert not p.exists();compile(s,str(p),'exec');p.write_text(s)
print(hashlib.sha256(p.read_bytes()).hexdigest())
