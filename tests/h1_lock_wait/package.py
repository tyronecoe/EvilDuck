#!/usr/bin/env python3
"""Assemble checksum-bound host/fixture kit only, without firmware or networking."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import stat
import subprocess
import sys
import zipfile
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[2]
PACKAGE='evilduck-h1-inherited-lock-wait-high-sierra-v1'
BASE='29cbfae7974abccf513c6d7ff1b7faa5a3fc58c6'

def digest(data):return hashlib.sha256(data).hexdigest()

def load(path):
    spec=importlib.util.spec_from_file_location('h1_wait_kit_check',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def prepare(out,archive,source_commit):
    out,archive=Path(out),Path(archive)
    assert re.fullmatch(r'[0-9a-f]{40}',source_commit)
    assert not out.exists() and not out.is_symlink() and ROOT not in out.resolve().parents
    assert not archive.exists() and not archive.is_symlink()
    subprocess.run(['git','merge-base','--is-ancestor',BASE,source_commit],cwd=ROOT,check=True)
    copies={'README.md':'docs/h1-lock-wait-readme.md','ACCEPTANCE.md':'docs/h1-lock-wait-acceptance.md',
            'source-evidence.json':'docs/h1-lock-wait-source-evidence.json',
            'test-results.json':'docs/h1-lock-wait-observer-tests.json','LICENSE.txt':'LICENSE'}
    names=['observe_wait.py','test_observe_wait.py','wait-settings-reset.txt','wait-new-run-default.txt','wait-passive-expiry.txt','wait-held-shift-stop.txt']
    copies.update({n:'tests/h1_lock_wait/'+n for n in names})
    for name in list(copies.values())+['tests/h1_lock_wait/package.py','tests/h1_lock_wait/validate_kit.py']:
        p=ROOT/name
        assert p.is_file() and not p.is_symlink()
        assert subprocess.check_output(['git','show',source_commit+':'+name],cwd=ROOT)==p.read_bytes(),name
    evidence=json.loads((ROOT/'docs/h1-lock-wait-source-evidence.json').read_text())
    assert digest((ROOT/'tests/lock_wait_timeout/observe_wait.py').read_bytes())==evidence['historical_observer_sha256']
    template=(ROOT/'tests/h1_lock_wait/validate_kit.py').read_text();assert template.count('RELEASE = None')==1
    binding=dict(source_commit=source_commit,observer_sha256=digest((ROOT/'tests/h1_lock_wait/observe_wait.py').read_bytes()))
    out.mkdir()
    for n,p in copies.items():(out/n).write_bytes((ROOT/p).read_bytes())
    (out/'validate_kit.py').write_text(template.replace('RELEASE = None','RELEASE = '+repr(binding)))
    files={p.name:dict(bytes=p.stat().st_size,sha256=digest(p.read_bytes())) for p in sorted(out.iterdir())}
    m=dict(package_id=PACKAGE,label='REVIEW ONLY — HOST HELPER AND FIXTURES — NO FIRMWARE',
           source_commit=source_commit,reviewed_base=BASE,target_build_id='ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1',
           application_bytes=1414080,application_sha256='8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd',
           rollback_bytes=1413200,rollback_sha256='cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02',
           firmware_included=False,hardware_access_authorized=False,physical_acceptance='PENDING_OWNER',
           unsigned_integrity_only=True,files=files)
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    load(out/'validate_kit.py').validate(out)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(out.iterdir()):
            info=zipfile.ZipInfo(p.name,(2026,10,31,0,0,0));info.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return dict(file=archive.name,bytes=archive.stat().st_size,sha256=digest(archive.read_bytes()),members=sorted(files)+['manifest.json'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True,type=Path);p.add_argument('--archive',required=True,type=Path);p.add_argument('--source-commit',required=True);a=p.parse_args()
    print(json.dumps(prepare(a.directory,a.archive,a.source_commit),indent=2))
