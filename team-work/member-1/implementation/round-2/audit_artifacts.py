"""Verify preservation, runtime/package identity and exact harness/engine provenance."""
import ast,hashlib,importlib.metadata as md,json,os,platform,subprocess,sys,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 protected=json.loads((BASE/'preservation-before.json').read_text());changed=[];external_changes=[]
 allowed={'team-work/member-3/implementation/round-2/evaluation-status-main.json','team-work/member-4/implementation/round-2/evaluation-status-main.json','team-work/member-4/implementation/round-2/main/B08-v001-parent-vs-F-500/metadata.json','team-work/member-4/implementation/round-2/main/B08-v001-parent-vs-F-500/games.json'}
 allowed.update({'team-work/member-3/08-GLM-IMPROVEMENT-CONTEXT.md','team-work/member-4/README.md','team-work/member-4/08-GLM-IMPROVEMENT-CONTEXT.md','team-work/member-4/implementation/round-2/README.md','team-work/member-4/implementation/round-2/VERIFICATION-AND-SCOPE.md','team-work/member-3/implementation/round-2/README.md','team-work/member-3/implementation/round-2/write_results.py','team-work/member-3/implementation/round-2/VERIFICATION-AND-SCOPE.md'})
 for name,digest in protected.items():
  p=ROOT/name
  if not p.is_file() or sha(p)!=digest:
   if name in allowed and p.is_file():external_changes.append({'path':name,'before_sha256':digest,'after_sha256':sha(p),'reason':'Concurrent Member3/4 evaluation/report completion outside this task; result/status updates or local review documentation/report tooling, never edited by this task'})
   else:changed.append(name)
 assert not changed,changed
 (BASE/'preservation-verification.json').write_text(json.dumps({'protected_files':len(protected),'all_other_hash_protected_files_unchanged':True,'concurrent_external_evidence_updates':external_changes,'scope':'All preexisting team-work files except cache and this new round folder are compared. Explicitly record concurrent external edits separately. Original Member1 files, all frozen runtime bot files and research findings remain unchanged. This task edits only new Member1 files; no commit/push.'},indent=2)+'\n')
 kit=ROOT/'shared-local/organizer-kit';commit=subprocess.check_output(['git','-C',str(kit),'rev-parse','HEAD'],text=True).strip();assert commit=='04fffac90e00610f60e0b06d919f262f4b3ed9db'
 assert not subprocess.check_output(['git','-C',str(kit),'status','--porcelain'],text=True).strip()
 files={}
 for name in ('examples/f_agent.py','catan_kit/obs.py','catan_kit/host.py','catan_kit/match.py','catan_kit/evaluate.py','catan_kit/_patch.py'):
  original=subprocess.check_output(['git','-C',str(kit),'show',commit+':'+name]);assert hashlib.sha256(original).hexdigest()==sha(kit/name);files[name]=sha(kit/name)
 direct=json.loads(md.distribution('catanatron').read_text('direct_url.json'));engine=direct['vcs_info']['commit_id'];assert engine=='d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816'
 cpu=next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),'unknown')
 from catan_kit import match
 (BASE/'harness-and-hardware.json').write_text(json.dumps({'kit_commit':commit,'kit_tracked_clean':True,'files_unchanged_from_pin':files,'engine_commit':engine,'engine_version':md.version('catanatron'),'python':platform.python_version(),'executable':sys.executable,'platform':platform.platform(),'cpu':cpu,'runtime_env':{k:os.getenv(k) for k in ('PYTHONHASHSEED','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},'clock':{'base_s':match.CPU_BASE_S,'increment_s':match.CPU_PER_DECISION_S,'max_s':match.CPU_MAX_S},'peak_memory_measured':False,'scorer_hardware_certified':False,'quiet_host_certified':False,'known_concurrent_work':'Preexisting Member3/4 round-2 evaluator PID 83615; B08 parent/candidate evidence finished during this task. This task leaves that runner and its outputs untouched.'},indent=2)+'\n')
 parents=json.loads((BASE/'parent-inventory.json').read_text());packages=json.loads((BASE/'package-verification.json').read_text());runtime={}
 for bot in ('B01','B02'):
  parent=parents[bot];assert sha(ROOT/parent['path'])==parent['sha256']
  folder=ROOT/f'team-work/member-1/bots/{bot}/v002';manifest=json.loads((folder/'manifest.json').read_text());assert sha(folder/'agent.py')==manifest['agent_sha256']==packages[bot]['agent_sha256']
  zpath=ROOT/f'team-work/member-1/artifacts/{bot}-v002.zip';assert sha(zpath)==packages[bot]['zip_sha256']
  with zipfile.ZipFile(zpath) as z:
   assert z.namelist()==['agent.py'] and z.testzip() is None and z.read('agent.py')==(folder/'agent.py').read_bytes()
  assert sha(ROOT/f'shared-local/member1-round2-package-checks/{bot}/agent.py')==manifest['agent_sha256']
  for name,digest in manifest['source_inputs'].items():assert sha(BASE/'sources'/name)==digest
  for name in ('race_math.py','public_context.py','spatial_context.py','goal_math.py'):assert sha(BASE/'sources'/name)==parent['manifest']['source_inputs'][name]
  tree=ast.parse((folder/'agent.py').read_text());imports=[]
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):imports.extend(n.name for n in node.names)
   elif isinstance(node,ast.ImportFrom):imports.append(node.module)
   assert not isinstance(node,ast.Try),'No silent broad exception fallback expected'
  assert all(n.split('.')[0] in ('math','random','time','catanatron') for n in imports)
  runtime[bot]={'agent_sha256':manifest['agent_sha256'],'imports':sorted(set(imports)),'no_try_fallback':True,'four_unchanged_components':True,'manifest_inputs_match':True}
 (BASE/'source-review.json').write_text(json.dumps(runtime,indent=2)+'\n');print(json.dumps({'preserved_files':len(protected),'harness_clean':True,'source_review':runtime},indent=2))
if __name__=='__main__':main()
