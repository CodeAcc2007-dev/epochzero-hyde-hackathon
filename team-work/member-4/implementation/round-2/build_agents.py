"""Explicit new-version assembly; preserve original artifacts and executable AST."""
import ast, argparse, hashlib, json
from pathlib import Path
BASE=Path(__file__).resolve().parent
NAMES=('race_math.py', 'round2_math.py', 'terminal_math.py', 'public_context.py', 'route_math.py', 'member4_policies.py')
BOTS={'B07': ('belief', 'v002'), 'B08': ('route', 'v002')}
LOCAL={Path(n).stem for n in NAMES}

def build(bot,freeze=False):
    mode,version=BOTS[bot]
    dest=BASE.parents[1]/'bots'/bot/version if freeze else BASE/'development'/bot
    blocks=[];expected=[];inputs={}
    for name in NAMES:
        p=BASE/'sources'/name;source=p.read_text();tree=ast.parse(source)
        inputs[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        remove=[]
        for n in tree.body:
            if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):remove.append(n)
            elif isinstance(n,ast.ImportFrom) and n.module in LOCAL:remove.append(n)
            else:expected.append(ast.dump(n,include_attributes=False))
        lines=source.splitlines(keepends=True)
        for n in reversed(remove):del lines[n.lineno-1:n.end_lineno]
        blocks.append(''.join(lines).strip())
    wrapper="class Agent(Member4Policy):\n    def __init__(self):\n        super().__init__("+repr(mode)+")\n"
    source='"""'+bot+' '+version+': reviewed corrections; standalone organizer-engine agent."""\n\n'+'\n\n'.join(blocks)+'\n\n'+wrapper
    assert [ast.dump(n,include_attributes=False) for n in ast.parse(source).body[1:-1]]==expected
    compile(source,str(dest/'agent.py'),'exec')
    dest.mkdir(parents=True,exist_ok=True)
    p=dest/'agent.py'
    if p.exists() and p.read_text()!=source:raise FileExistsError('Preserve artifact: '+str(p))
    p.write_text(source)
    manifest={'bot':bot,'version':version,'mode':mode,'source_inputs':inputs,'agent_sha256':hashlib.sha256(source.encode()).hexdigest(),'executable_ast_preserved':True,'parent_version':'v001','parent_repository_commit':'6406587588131d904054d40327fdb0fc5c02a5a5','kit_commit':'04fffac90e00610f60e0b06d919f262f4b3ed9db','engine_commit':'d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816'}
    mp=dest/'manifest.json'
    text=json.dumps(manifest,indent=2)+'\n'
    if mp.exists() and mp.read_text()!=text:raise FileExistsError(str(mp))
    mp.write_text(text)
    return {'path':str(p),**manifest}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');a=p.parse_args()
    for bot in BOTS:print(json.dumps(build(bot,a.freeze)))
