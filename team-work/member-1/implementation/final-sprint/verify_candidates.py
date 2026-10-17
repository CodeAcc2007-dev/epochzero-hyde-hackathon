"""Independent regression reuse on actual candidate modules, no old evidence edits."""
import importlib.util,sys,unittest,io,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3];R2=BASE.parent/'round-2'
sys.path.insert(0,str(R2))
import test_terminal_regressions as r
import test_sprint_terminal_guards as guards

def run(name,path):
 m=r.load('sprint_'+name,path);r.NEW={'B01':m}
 suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(r),unittest.defaultTestLoader.loadTestsFromModule(guards)])
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 records={'terminal_regression_methods':result.testsRun,'terminal_passed':result.wasSuccessful()}
 spec=importlib.util.spec_from_file_location('adapted_'+name,BASE.parent/'test_economy.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
 for key in ('EconomyContext','EconomyPolicy','Context','conversion_gap','goal_priority','improves_goal','hand'):setattr(t,key,getattr(m,key))
 # Packaging test below targets old hardcoded paths; separately verify current module.
 suite=unittest.TestSuite()
 for cls in vars(t).values():
  if isinstance(cls,type) and issubclass(cls,unittest.TestCase):
   for method in unittest.defaultTestLoader.getTestCaseNames(cls):
    if method!='test_standalone_legal_entrypoints':suite.addTest(cls(method))
 res=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 records.update(economic_methods=res.testsRun,economic_passed=res.wasSuccessful(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 (BASE/f'verification-{name}.log').write_text(stream.getvalue())
 print(name,json.dumps(records),flush=True)
 return records

if __name__=='__main__':
 records={name:run(name,BASE/'candidates'/name/'agent.py') for name in ('menu','opening','combined')}
 (BASE/'verification.json').write_text(json.dumps(records,indent=2)+'\n')
