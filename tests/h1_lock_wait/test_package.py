#!/usr/bin/env python3
"""Disposable public-copy kit checks; no network or hardware."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('directory','archive','results'):p.add_argument('--'+n,required=True,type=Path)
    args=p.parse_args();assert not args.results.exists();checks=[]
    module=load(args.directory/'validate_kit.py','h1_offline_validator')
    def need(v):assert v
    def check(name,fn):
        try:fn();checks.append(dict(name=name,status='PASS'))
        except Exception as e:checks.append(dict(name=name,status='FAIL',error=type(e).__name__))
    def reject(fn):
        try:fn()
        except (module.Rejected,ValueError,KeyError,OSError,TypeError):return
        raise AssertionError('Unsafe kit accepted')
    with tempfile.TemporaryDirectory(prefix='h1-public-kit-test-') as temporary:
        d=Path(temporary)/'kit with spaces';shutil.copytree(args.directory,d)
        check('valid_kit_no_permission_or_device_access',lambda:need(module.validate(d)['hardware_access'] is False and not module.validate(d)['physical_use_authorized']))
        for name in sorted(module.FILES):
            def tamper(name=name):
                path=d/name;data=path.read_bytes();path.write_bytes(data+b'\n');reject(lambda:module.validate(d));path.write_bytes(data)
            check('tamper_'+name,tamper)
        def missing():
            path=d/'wait-passive-expiry.txt';data=path.read_bytes();path.unlink();reject(lambda:module.validate(d));path.write_bytes(data)
        check('missing_fixture_rejected',missing)
        def extra():
            p=d/'private.json';p.write_text('{}');reject(lambda:module.validate(d));p.unlink()
        check('extra_member_rejected',extra)
        def symlink():
            p=d/'observe_wait.py';data=p.read_bytes();saved=Path(temporary)/'saved-public.py';saved.write_bytes(data);p.unlink();p.symlink_to(saved);reject(lambda:module.validate(d));p.unlink();p.write_bytes(data)
        check('symlink_rejected',symlink)
        manifest=(d/'manifest.json').read_bytes()
        for name,key,value in [('build','target_build_id','ROUTEB-LOCK-WAIT-TIMEOUT-v1'),('prefix','target_build_id',module.BUILD[:-1]),('application','application_sha256','0'*64),('rollback','rollback_sha256','0'*64),('permission','hardware_access_authorized',True),('firmware','firmware_included',True),('physical_claim','physical_acceptance','PASS'),('source','source_commit','0'*40)]:
            def wrong(key=key,value=value):
                m=json.loads(manifest);m[key]=value;(d/'manifest.json').write_text(json.dumps(m));reject(lambda:module.validate(d));(d/'manifest.json').write_bytes(manifest)
            check('wrong_'+name+'_rejected',wrong)
        def rebound_observer():
            path=d/'observe_wait.py';data=path.read_bytes();path.write_bytes(data+b'\n');m=json.loads(manifest);b=path.read_bytes();m['files']['observe_wait.py']=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest());(d/'manifest.json').write_text(json.dumps(m));reject(lambda:module.validate(d));path.write_bytes(data);(d/'manifest.json').write_bytes(manifest)
        check('observer_rehashed_manifest_still_rejected',rebound_observer)
        def archive():
            with zipfile.ZipFile(args.archive) as z:
                need(z.testzip() is None);names=z.namelist();need(len(names)==len(set(names)) and set(names)==module.FILES|{'manifest.json'})
                for i in z.infolist():
                    need('/' not in i.filename and '\\' not in i.filename and stat.S_ISREG(i.external_attr>>16));need(z.read(i)==(d/i.filename).read_bytes())
        check('archive_exact_flat_regular_inventory_crc_bytes',archive)
        def fixtures():
            blocks=[x.split('```')[0].encode() for x in (ROOT/'docs/lock-wait-timeout-acceptance.md').read_text().split('```ducky\n')[1:]]
            names=['wait-settings-reset.txt','wait-new-run-default.txt','wait-passive-expiry.txt','wait-held-shift-stop.txt']
            need(len(blocks)==4)
            for n,b in zip(names,blocks):need((d/n).read_bytes()==b)
        check('fixtures_exact_historical_contract',fixtures)
        def py38():
            for n in ['observe_wait.py','test_observe_wait.py','validate_kit.py']:ast.parse((d/n).read_text(),feature_version=(3,8))
        check('bundled_python38_grammar',py38)
        def guide():
            text=(d/'ACCEPTANCE.md').read_text();need('Control+J' in text and '115200' in text and 'socket-inactivity' in text and 'Actual assigned request ID' in text)
            for block in text.split('```bash')[1:]:subprocess.run(['bash','-n'],input=block.split('```')[0],text=True,check=True)
        check('acceptance_bash_syntax_and_scope',guide)
        def offline_cli():
            r=subprocess.run([sys.executable,str(d/'validate_kit.py'),'--directory',str(d)],capture_output=True,text=True);need(r.returncode==0 and json.loads(r.stdout)['hardware_access'] is False)
        check('actual_offline_cli_exit_and_no_permission',offline_cli)
        def repeated():
            package=load(ROOT/'tests/h1_lock_wait/package.py','h1_repackage');source=json.loads(manifest)['source_commit'];out=Path(temporary)/'repeated';z=Path(temporary)/'repeated.zip';package.prepare(out,z,source);need(z.read_bytes()==args.archive.read_bytes())
        check('deterministic_package_reproduction',repeated)
    out=dict(counts={k:sum(c['status']==k for c in checks) for k in ('PASS','FAIL')},checks=checks,hardware=False,network=False,native_high_sierra_tested=False)
    args.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['counts']));return int(bool(out['counts']['FAIL']))

if __name__=='__main__':raise SystemExit(main())
