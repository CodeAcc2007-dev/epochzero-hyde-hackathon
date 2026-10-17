"""Verify exact frozen and ZIP sources; reuse side-effect-free regression fixtures."""
from pathlib import Path
import sys,io,unittest,json,hashlib,zipfile,ast,types
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3];PREV=BASE.parent/'final-sprint'
sys.path.insert(0,str(PREV))
import verify_candidates as original
# Preserve historical logs: redirect only the verifier's output path.
v=types.ModuleType('tempo_verifier');v.__file__=str(PREV/'verify_candidates.py');v.OUTPUT=BASE
exec(compile((PREV/'verify_candidates.py').read_text().replace("(BASE/f'verification-{name}.log')","(OUTPUT/f'verification-{name}.log')"),v.__file__,'exec'),v.__dict__)
import test_sprint as extra
import test_two_roads as road
source=ROOT/'team-work/member-1/bots/B01/v005/agent.py';data=source.read_bytes()
archive=ROOT/'team-work/member-1/artifacts/B01-v005.zip'
if not archive.exists():
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('agent.py',data)
extract=ROOT/'shared-local/b01-tempo-package-check';extract.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
 assert z.namelist()==['agent.py'] and z.testzip() is None and z.read('agent.py')==data
 z.extractall(extract)
records={}
for name,p in [('frozen',source),('zip',extract/'agent.py')]:
 records[name]=v.run(name,p)
 m=v.r.load('tempo_'+name,p);extra.mods={'menu':m,'combined':m,'search':m};road.M=m
 methods=['test_goal_reconsiders_changed_hand_instead_of_stale_family','test_reordered_opening_indices_and_observation_immutability','test_trade_retains_monotone_certificate_and_no_reexport','test_reordered_rich_turn_roots_legal_and_nonmutating']
 suite=unittest.TestSuite([extra.SprintTests(x) for x in methods]);suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(road))
 class ProductionTests(unittest.TestCase):
  def test_affordable_and_convertible_keep_full_value(self):
   for h in ((0,0,0,2,3),(4,0,0,2,2)):
    self.assertEqual(m.production_readiness(h,m.CITY,(4,)*5,(19,)*5,(0,)*5),1.0)
  def test_faster_missing_resource_improves_priority(self):
   h=(0,0,0,2,2);slow=(.05,.05,.05,.05,0);fast=(.05,.05,.05,.05,.25)
   self.assertGreater(m.production_readiness(h,m.CITY,(4,)*5,(19,)*5,fast),m.production_readiness(h,m.CITY,(4,)*5,(19,)*5,slow))
  def test_zero_supply_is_finite_bounded(self):
   self.assertAlmostEqual(m.production_readiness((0,)*5,m.CITY,(4,)*5,(19,)*5,(0,)*5),.625)
  def test_port_supply_and_resource_monotonicity(self):
   cost=m.CITY;h=(0,0,0,2,2);prod=(.2,0,0,0,0)
   self.assertGreater(m.production_readiness(h,cost,(2,4,4,4,4),(19,)*5,prod),m.production_readiness(h,cost,(4,)*5,(19,)*5,prod))
   self.assertGreaterEqual(m.production_readiness((0,0,0,2,3),cost,(4,)*5,(19,)*5,prod),m.production_readiness(h,cost,(4,)*5,(19,)*5,prod))
 suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ProductionTests))
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (BASE/f'verification-extra-{name}.log').write_text(stream.getvalue())
 records[name].update(extra_methods=result.testsRun,extra_passed=result.wasSuccessful())
 assert result.wasSuccessful(),stream.getvalue()
 assert records[name]['terminal_passed'] and records[name]['economic_passed']
imports=[]
for n in ast.walk(ast.parse(data)):
 if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
 if isinstance(n,ast.ImportFrom):imports.append(n.module)
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):assert n.func.id not in ('open','eval','exec','compile','__import__','print')
assert all(x in ('math','time','random') or x.startswith('catanatron.') for x in imports)
assert hashlib.sha256((ROOT/'team-work/member-1/bots/B01/v004/agent.py').read_bytes()).hexdigest()=='a0ed4450b3aa23eff97ab44fbe185e2d089ddc9516a1703e4b483389ed8ff2fb'
assert hashlib.sha256((ROOT/'shared-local/organizer-kit/examples/f_agent.py').read_bytes()).hexdigest()=='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'
out={'agent_sha256':hashlib.sha256(data).hexdigest(),'zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'zip_exact':True,'parent_preserved':True,'F_unchanged':True,'verification':records}
(BASE/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
