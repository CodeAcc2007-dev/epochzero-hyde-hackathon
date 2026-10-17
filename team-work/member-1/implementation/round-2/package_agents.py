"""Freeze v002 with AST/hash checks and clean ZIP extraction; never overwrite."""
import hashlib,importlib.util,json,zipfile
from pathlib import Path
from build_agents import build
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows={}
 for bot in ('B01','B02'):
  folder=BASE.parents[1]/'bots'/bot/'v002';assert not folder.exists()
  manifest=build(bot,folder/'agent.py');manifest.update(version='v002',parent_version='v001',parent_sha256=sha(folder.parent/'v001/agent.py'),changes=['M1-C01 deterministic one-trade building terminal certificate','M1-C02 immediate public terminal before low-clock fallback'])
  (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  assert (folder/'agent.py').read_bytes()==(BASE/'development'/bot/'agent.py').read_bytes()
  zpath=BASE.parents[1]/'artifacts'/f'{bot}-v002.zip';assert not zpath.exists()
  with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:z.write(folder/'agent.py','agent.py')
  extract=ROOT/'shared-local/member1-round2-package-checks'/bot;extract.mkdir(parents=True,exist_ok=False)
  with zipfile.ZipFile(zpath) as z:
   assert z.namelist()==['agent.py'];assert z.testzip() is None;z.extractall(extract)
  assert sha(extract/'agent.py')==manifest['agent_sha256']
  spec=importlib.util.spec_from_file_location('zip_'+bot,extract/'agent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.Agent()
  rows[bot]={'agent_sha256':sha(folder/'agent.py'),'zip_sha256':sha(zpath),'zip_members':['agent.py'],'crc_ok':True,'extracted_byte_equal':True,'clean_standalone_import':True,'development_frozen_equal':True,'executable_ast_preserved':True}
  (folder/'README.md').write_text(f'# {bot} v002: Member 1 review candidate\n\nOwner Aroosh. New correctness revision; frozen parent v001 preserved. See [round-2 plan](../../../implementation/round-2/PLAN-AND-DECISIONS.md) and [results](../../../implementation/round-2/BUILD-AND-RESULTS.md). Human review pending. Local evaluation does not certify private event strength.\n\nSHA-256 `{rows[bot]["agent_sha256"]}`. Standalone stdlib + pinned organizer engine only; ZIP has exact agent.py. No runtime LLM, network, workers or logging.\n')
 (BASE/'package-verification.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
