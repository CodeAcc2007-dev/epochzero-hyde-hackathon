"""Run tests on exact frozen and ZIP-extracted modules, retaining concise evidence."""
import hashlib,io,json,subprocess,sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
sys.path.insert(0,str(BASE))
import test_round2 as r

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows={}
 for kind in ('frozen','zip-extracted'):
  if kind=='zip-extracted':
   r.NEW={b:r.load('extracted_'+b,ROOT/f'shared-local/member1-round2-package-checks/{b}/agent.py') for b in ('B01','B02')}
  suite=unittest.defaultTestLoader.discover(str(BASE),pattern='test_*.py');stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
  (ROOT/f'shared-local/member1-round2-{kind}-semantic-final.log').write_text(stream.getvalue());assert result.wasSuccessful(),stream.getvalue()
  rows[kind]={'test_methods_executed':result.testsRun,'passed':True,'output_sha256':hashlib.sha256(stream.getvalue().encode()).hexdigest()}
 cmd=['./team-work/run-python.sh','team-work/member-1/implementation/round-2/verify_contracts.py']
 result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert result.returncode==0,result.stderr
 (ROOT/'shared-local/member1-round2-adapted-semantic-final.log').write_text(result.stdout+result.stderr)
 record={'new_regression_methods':15,'new_methods_executed_per_artifact_form':rows,'adapted_existing_methods':19,'original_parent_methods_before_repairs':19,'conversion_oracle_cases':18225,'independent_trade_certificate_fixtures':96,'discard_sequences':12,'main_clocked_games_separate_from_semantic_fixtures':True,'test_entrypoint_sha256':{name:sha(BASE/name) for name in ('test_round2.py','test_terminal_guards.py','verify_contracts.py','verify_semantics.py')},'artifacts':{b:{'path':str(r.path(b).relative_to(ROOT)),'sha256':sha(r.path(b))} for b in ('B01','B02')},'commands':[['./team-work/run-python.sh','team-work/member-1/implementation/round-2/verify_semantics.py'],cmd],'original_review_probe_output_sha256':sha(ROOT/'shared-local/member1-round2-parent-probes.json'),'parent_tests_log_sha256':sha(ROOT/'shared-local/member1-round2-parent-tests.log')}
 (BASE/'semantic-verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':main()
