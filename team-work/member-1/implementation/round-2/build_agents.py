"""Assemble reviewed B01/B02 source into self-contained files; no environment copies."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
SOURCE=BASE/'sources'
LOCAL={'race_math','public_context','spatial_context','goal_math','terminal_math','economy_policies'}

def build(bot,dest):
    blocks=[];expected=[];inputs={}
    for name in ('race_math.py','public_context.py','spatial_context.py','goal_math.py','terminal_math.py','economy_policies.py'):
        p=SOURCE/name;source=p.read_text();tree=ast.parse(source)
        inputs[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        remove=[]
        for n in tree.body:
            if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):remove.append(n)
            elif isinstance(n,ast.ImportFrom) and n.module in LOCAL:remove.append(n)
            else:expected.append(ast.dump(n,include_attributes=False))
        lines=source.splitlines(keepends=True)
        for n in reversed(remove):del lines[n.lineno-1:n.end_lineno]
        blocks.append(''.join(lines).strip())
    wrapper=f'class Agent(EconomyPolicy):\n    def __init__(self):\n        super().__init__(engine={bot=="B02"})\n'
    source=f'"""{bot}: Aroosh Member 1, standalone v002 correctness revision. Pinned organizer engine required."""\n\n'+'\n\n'.join(blocks)+'\n\n'+wrapper
    tree=ast.parse(source)
    assert [ast.dump(n,include_attributes=False) for n in tree.body[1:-1]]==expected
    compile(source,str(dest),'exec')
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_text()!=source:raise FileExistsError('Preserve existing artifact: '+str(dest))
    dest.write_text(source)
    return {'bot':bot,'source_inputs':inputs,'agent_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
            'executable_ast_preserved':True,'strategy':'bottleneck economy' if bot=='B01' else 'city/dev engine',
            'kit_commit':'04fffac90e00610f60e0b06d919f262f4b3ed9db',
            'engine_commit':'d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
    for bot in ('B01','B02'):
        folder=BASE.parents[1]/'bots'/bot/'v002' if a.freeze else BASE/'development'/bot
        if a.freeze and folder.exists():raise FileExistsError('Preserve existing freeze: '+str(folder))
        manifest=build(bot,folder/'agent.py')
        manifest['version']='v002' if a.freeze else 'development'
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps({'path':str(folder/'agent.py'),**manifest}))
if __name__=='__main__':main()
