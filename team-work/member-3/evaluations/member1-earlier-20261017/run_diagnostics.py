#!/usr/bin/env python3
"""Separate four-game diagnostics for caught-exception fallbacks, not strength estimates."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from collections import Counter
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent

def prepare_wrapper(source, sites):
    folder=ROOT/'shared-local/member1-earlier-diagnostics'/source.stem
    folder.mkdir(parents=True,exist_ok=True)
    entry=folder/'agent.py'
    text='''"""Diagnostic only: imports original source unchanged; no benchmark claim."""
import importlib.util
import json
import sys
SOURCE = {source}
SITES = {sites}
NAME = {name}
spec=importlib.util.spec_from_file_location('original_member1', SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class _RngProxy:
    def __init__(self, rng): self._rng=rng
    def __getattr__(self, name): return getattr(self._rng,name)
    def randrange(self, *args, **kwargs):
        frame=sys._getframe(1)
        if frame.f_code.co_filename==SOURCE and frame.f_lineno in SITES:
            error=sys.exception()
            print('INTERNAL_FALLBACK '+json.dumps(dict(bot=NAME,line=frame.f_lineno,
                  exception=type(error).__name__ if error else None,
                  message=str(error)[:200] if error else None)),file=sys.stderr,flush=True)
        return self._rng.randrange(*args,**kwargs)
class Agent(module.Agent):
    def __init__(self):
        super().__init__()
        self.rng=_RngProxy(self.rng)
'''.format(source=repr(str(source)),sites=repr(sites),name=repr(source.stem))
    entry.write_text(text)
    return entry.relative_to(ROOT)

def main():
    status=json.loads((BASE/"batch-status.json").read_text())
    assert status["status"]=="completed", "Keep diagnostic games sequential after main runs"
    items=json.loads((BASE/"source-inventory.json").read_text())
    sites={i['path']:i['exception_random_return_lines'] for i in json.loads((BASE/'internal-fallback-sites.json').read_text())}
    env=os.environ.copy();env.pop("W",None);env.pop("OPP",None)
    logs=ROOT/"shared-local/logs/member1-earlier-diagnostics"
    logs.mkdir(parents=True,exist_ok=True)
    rows=[]
    for item in items:
        source=ROOT/item["path"]
        assert hashlib.sha256(source.read_bytes()).hexdigest()==item["sha256"]
        name=source.stem
        entry=prepare_wrapper(source,sites[item['path']])
        out=BASE/"diagnostics"/name
        log=logs/f"{name}.txt"
        cmd=[str(ROOT/"team-work/run-python.sh"),"team-work/member-3/implementation/run_comparison.py",
             "--a",str(entry),"--b","shared-local/organizer-kit/examples/f_agent.py",
             "--games","4","--seed0","870500","--out",str(out.relative_to(ROOT))]
        with log.open("w") as stream:
            process=subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        hits=[]
        for line in log.read_text().splitlines():
            if line.startswith("INTERNAL_FALLBACK "):
                hits.append(json.loads(line[len("INTERNAL_FALLBACK "):]))
        kinds=Counter((x["line"],x["exception"],x["message"]) for x in hits)
        row={"bot":name,"exit_code":process.returncode,"diagnostic_games":4,
             "wrapper_sha256":hashlib.sha256((ROOT/entry).read_bytes()).hexdigest(),
             "observed_internal_exception_fallbacks":len(hits),
             "exceptions":[{"line":line,"type":kind,"message":msg,"count":count}
                           for (line,kind,msg),count in kinds.items()],
             "method":"Unchanged original import with RNG proxy recording only randrange calls at source-verified exception-return sites; separate instrumented four-game diagnostic, not a benchmark."}
        if process.returncode==0:
            row["diagnostic_decisions"]=json.loads((out/"summary.json").read_text())["a"]["decisions"]
        rows.append(row)
        (BASE/"internal-fallback-diagnostics.json").write_text(json.dumps(rows,indent=2)+"\n")
        print(json.dumps(row),flush=True)
    for item in items:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"]

if __name__=="__main__":main()
