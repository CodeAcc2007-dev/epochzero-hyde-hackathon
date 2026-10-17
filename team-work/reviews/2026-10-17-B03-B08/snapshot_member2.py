"""Materialize selected pinned Member2 files locally without merging or checking out.

Run after `git fetch origin member-2/avadooth-bots`. Uses only Git objects;
never downloads dependencies or changes tracked source. Refuses changed outputs.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
COMMIT='791e6705d09f62ceba691777e041980d673f1c69'
DEST=ROOT/'shared-local/review-B03-B08-20261017'
EXPECTED={'B03':'1a4a304932718ba2b76af1ff966bb08c55c5c00c7a0ef5c0f9cf788bdcc66e30',
          'B04':'763c88df0a815aeb97bf6cc1bb02865f8bb148c58bed6965ffb54911907d0b45'}

def main():
    files=subprocess.check_output(['git','ls-tree','-r','--name-only',COMMIT,'team-work/member-2/bots'],cwd=ROOT,text=True).splitlines()
    records=[]
    for name in files:
        data=subprocess.check_output(['git','show',f'{COMMIT}:{name}'],cwd=ROOT)
        p=DEST/name
        if p.exists() and p.read_bytes()!=data:raise FileExistsError(f'Changed local snapshot: {p}')
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        records.append({'path':name,'sha256':hashlib.sha256(data).hexdigest()})
    for b,h in EXPECTED.items():
        assert hashlib.sha256((DEST/f'team-work/member-2/bots/{b}/v002/agent.py').read_bytes()).hexdigest()==h
    (DEST/'snapshot.json').write_text(json.dumps({'remote_commit':COMMIT,'files':records},indent=2)+'\n')
    print(f'Verified {len(files)} source/evidence files at {COMMIT}; no merge or tracked source changes.')

if __name__=='__main__':main()
