#!/usr/bin/env python3
"""Offline local-file kit check. No network, USB, credential or device operation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
RELEASE = None
PACKAGE = 'evilduck-h1-inherited-lock-wait-high-sierra-v1'
BUILD = 'ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1'
APPLICATION = '8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd'
ROLLBACK = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
FILES = {'README.md','ACCEPTANCE.md','observe_wait.py','test_observe_wait.py',
         'validate_kit.py','source-evidence.json','test-results.json','LICENSE.txt',
         'wait-settings-reset.txt','wait-new-run-default.txt',
         'wait-passive-expiry.txt','wait-held-shift-stop.txt'}

class Rejected(ValueError): pass

def require(ok, code):
    if not ok: raise Rejected(code)

def read(path):
    require(not path.is_symlink() and path.is_file(), 'NONREGULAR_OR_MISSING_MEMBER')
    require(path.stat().st_size <= 1024*1024, 'OVERSIZE_MEMBER')
    data=path.read_bytes()
    require(len(data)<=1024*1024, 'OVERSIZE_MEMBER')
    return data

def validate(directory):
    require(RELEASE is not None,'UNBOUND_KIT')
    root=Path(directory)
    require(not root.is_symlink() and root.is_dir(),'INVALID_DIRECTORY')
    require({p.name for p in root.iterdir()}==FILES|{'manifest.json'},'WRONG_INVENTORY')
    manifest=json.loads(read(root/'manifest.json'))
    require(manifest.get('package_id')==PACKAGE and manifest.get('source_commit')==RELEASE['source_commit'],'WRONG_KIT_IDENTITY')
    require(manifest.get('target_build_id')==BUILD and manifest.get('application_sha256')==APPLICATION and manifest.get('application_bytes')==1414080,'WRONG_TARGET')
    require(manifest.get('rollback_sha256')==ROLLBACK and manifest.get('rollback_bytes')==1413200,'WRONG_ROLLBACK')
    require(manifest.get('firmware_included') is False and manifest.get('hardware_access_authorized') is False and manifest.get('physical_acceptance')=='PENDING_OWNER','UNSUPPORTED_PERMISSION_OR_CLAIM')
    require(set(manifest['files'])==FILES,'WRONG_MANIFEST_INVENTORY')
    for name in sorted(FILES):
        data=read(root/name);row=manifest['files'][name]
        require(row==dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest()),'MEMBER_INTEGRITY_FAILED')
    require(manifest['files']['observe_wait.py']['sha256']==RELEASE['observer_sha256'],'WRONG_OBSERVER_BINDING')
    return dict(kit_integrity='PASS',package_id=PACKAGE,target_build_id=BUILD,
                source_commit=RELEASE['source_commit'],hardware_access=False,
                physical_use_authorized=False,physical_acceptance='PENDING_OWNER')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
    try:
        print(json.dumps(validate(a.directory),indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError):
        print(json.dumps(dict(kit_integrity='REJECTED',hardware_access=False,physical_use_authorized=False)));return 1

if __name__=='__main__':raise SystemExit(main())
