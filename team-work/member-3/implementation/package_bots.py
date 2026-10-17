#!/usr/bin/env python3
"""Create explicit-file standalone ZIPs and prepare clean local extraction checks."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[3]
MEMBER=ROOT/'team-work/member-3'
FILES=('agent.py','member3_core.py','race_math.py','manifest.json')


def main():
    artifacts=MEMBER/'artifacts';artifacts.mkdir(exist_ok=True)
    checks=ROOT/'shared-local/member3-package-checks';checks.mkdir(exist_ok=True)
    report={}
    for bot in ['B05','B06']:
        source=MEMBER/'bots'/bot/'v003'
        manifest=json.loads((source/'manifest.json').read_text())
        assert all(hashlib.sha256((source/f).read_bytes()).hexdigest()==d for f,d in manifest['files_sha256'].items())
        target=artifacts/(bot+'-v003.zip')
        assert not target.exists(), 'Refuse to replace a frozen artifact'
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
            for name in FILES:
                info=zipfile.ZipInfo(name,date_time=(2026,10,17,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                archive.writestr(info,(source/name).read_bytes())
        destination=checks/bot
        destination.mkdir(exist_ok=False)
        with zipfile.ZipFile(target) as archive:
            assert tuple(archive.namelist())==FILES and archive.testzip() is None
            archive.extractall(destination)
        assert all((source/n).read_bytes()==(destination/n).read_bytes() for n in FILES)
        assert target.stat().st_size<100_000_000
        report[bot]={'zip':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,
                     'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':list(FILES),
                     'clean_extract':str(destination.relative_to(ROOT)),
                     'content_hashes_match':True,'clocked_load_smoke':'Pending separate official harness run'}
    (artifacts/'package-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
