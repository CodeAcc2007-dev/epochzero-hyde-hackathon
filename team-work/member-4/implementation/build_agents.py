"""Assemble self-contained agents from reviewed source; no environment is copied."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
LOCAL={'race_math','public_context','route_math','member4_policies'}

def build(bot, destination, *, control=False):
    blocks=[];expected=[];inputs={}
    for name in ('race_math.py','public_context.py','route_math.py','member4_policies.py'):
        p=BASE/name;source=p.read_text();tree=ast.parse(source)
        inputs[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        remove=[]
        for n in tree.body:
            if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
                remove.append(n)
            elif isinstance(n,ast.ImportFrom) and n.module in LOCAL:
                remove.append(n)
            else: expected.append(ast.dump(n,include_attributes=False))
        lines=source.splitlines(keepends=True)
        for n in reversed(remove):del lines[n.lineno-1:n.end_lineno]
        blocks.append(''.join(lines).strip())
    mode='belief' if bot=='B07' else 'route'
    option=', sampled_replies=False' if control and bot=='B07' else ', adaptive=False' if control else ''
    wrapper=f"class Agent(Member4Policy):\n    def __init__(self):\n        super().__init__({mode!r}{option})\n"
    source=f'"""{bot}: Member 4 Anni; standalone first candidate. Requires organizer engine only."""\n\n'+'\n\n'.join(blocks)+'\n\n'+wrapper
    actual=ast.parse(source)
    assert [ast.dump(n,include_attributes=False) for n in actual.body[1:-1]]==expected
    compile(source,str(destination),'exec')
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists() and destination.read_text()!=source:
        raise FileExistsError('Preserve existing artifact: '+str(destination))
    destination.write_text(source)
    return {'bot':bot,'control':control,'source_inputs':inputs,
            'agent_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'executable_ast_preserved':True}

def main():
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
    for bot in ('B07','B08'):
        parent=BASE.parent/'bots'/bot/'v001' if a.freeze else BASE/'development'/bot
        manifest=build(bot,parent/'agent.py')
        manifest.update(version='v001' if a.freeze else 'development',
                        strategy='sampled-opponent planning' if bot=='B07' else 'adaptive VP-route planning',
                        kit_commit='04fffac90e00610f60e0b06d919f262f4b3ed9db',
                        engine_commit='d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816',
                        runtime='stdlib + pinned catanatron; no network, I/O or worker process')
        (parent/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if a.freeze:
            control=BASE/'controls'/bot/'agent.py'
            cm=build(bot,control,control=True)
            (control.parent/'manifest.json').write_text(json.dumps(cm,indent=2)+'\n')
        print(json.dumps({'path':str(parent/'agent.py'),**manifest}))
if __name__=='__main__':main()
