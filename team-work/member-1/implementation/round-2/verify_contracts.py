"""Run original nineteen economic contract tests against new standalone classes."""
import importlib.util,sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import test_round2 as r
p=BASE.parent/'test_economy.py'
spec=importlib.util.spec_from_file_location('adapted_economy',p);t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
t.EconomyContext=r.NEW['B01'].EconomyContext;t.EconomyPolicy=r.NEW['B01'].EconomyPolicy
for name in ('Context','conversion_gap','goal_priority','improves_goal','hand'):setattr(t,name,getattr(r.NEW['B01'],name))
# Existing standalone entrypoint test loads both assembled v002 development files.
t.BASE=BASE
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t))
raise SystemExit(not result.wasSuccessful())
