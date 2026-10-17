from pathlib import Path
import ast,hashlib,json,sys,zipfile,io,unittest,subprocess
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE))
import verify_candidates as v
import test_sprint as extra
source=ROOT/'team-work/member-1/bots/B01/v004/agent.py';data=source.read_bytes();sha=hashlib.sha256(data).hexdigest()
assert sha=='a0ed4450b3aa23eff97ab44fbe185e2d089ddc9516a1703e4b483389ed8ff2fb'
manifest=json.loads((source.parent/'manifest.json').read_text());assert manifest['agent_sha256']==sha
out=ROOT/'team-work/member-1/artifacts/B01-v004.zip'
if not out.exists():
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('agent.py',data)
extract=ROOT/'shared-local/b01-sprint-tactical-package-check';extract.mkdir(exist_ok=True)
if (extract/'agent.py').exists():assert (extract/'agent.py').read_bytes()==data
with zipfile.ZipFile(out) as z:
 assert z.namelist()==['agent.py'] and z.testzip() is None
 assert z.read('agent.py')==data;z.extractall(extract)
records={}
for name,p in [('tactical-frozen',source),('tactical-zip-extracted',extract/'agent.py')]:
 records[name]=v.run(name,p)
 m=v.r.load('specific_'+name,p);extra.mods={'menu':m,'combined':m,'search':m}
 methods=['test_goal_reconsiders_changed_hand_instead_of_stale_family','test_reordered_opening_indices_and_observation_immutability','test_trade_retains_monotone_certificate_and_no_reexport','test_reordered_rich_turn_roots_legal_and_nonmutating']
 stream=io.StringIO();res=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(extra.SprintTests(x) for x in methods))
 (BASE/f'verification-extra-{name}.log').write_text(stream.getvalue());assert res.wasSuccessful(),stream.getvalue()
 records[name]['extra_sprint_methods']=res.testsRun;records[name]['extra_passed']=True
 import test_two_roads as road
 road.M=m
 roadstream=io.StringIO();roadresult=unittest.TextTestRunner(stream=roadstream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(road))
 (BASE/f'verification-road-{name}.log').write_text(roadstream.getvalue());assert roadresult.wasSuccessful(),roadstream.getvalue()
 records[name]['new_road_methods']=roadresult.testsRun;records[name]['road_passed']=True
 assert records[name]['terminal_passed'] and records[name]['economic_passed']
tree=ast.parse(data)
imports=[];forbidden=[]
for n in ast.walk(tree):
 if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
 if isinstance(n,ast.ImportFrom):imports.append(n.module)
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('open','eval','exec','compile','__import__','print'):forbidden.append(n.func.id)
assert not forbidden
assert all(x in ('math','random','time') or x.startswith('catanatron.') for x in imports)
kit=ROOT/'shared-local/organizer-kit';assert not subprocess.check_output(['git','-C',str(kit),'diff','--name-only'],text=True).strip()
fhash=hashlib.sha256((kit/'examples/f_agent.py').read_bytes()).hexdigest();assert fhash=='72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613'
record={'agent_sha256':sha,'zip_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zip_exact_agent_only':True,'f_sha256':fhash,'kit_tracked_source_clean':True,'runtime_imports':sorted(set(imports)),'forbidden_dynamic_io_calls':forbidden,'verification':records,'parent_preserved':hashlib.sha256((ROOT/'team-work/member-1/bots/B01/v002/agent.py').read_bytes()).hexdigest()==manifest['comparison_baseline_sha256']}
(BASE/'tactical-package-verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
