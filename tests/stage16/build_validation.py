#!/usr/bin/env python3
"""Fail-closed dependency and full linked-firmware checks; no ports or downloads."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
sys.dont_write_bytecode = True
from patched_core import check_sources,prepare,sha,PATCH,tree_hash
from verify_patched_firmware import verify

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original-core',type=Path,required=True);p.add_argument('--patched-core',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);p.add_argument('--arduino-cli',required=True);p.add_argument('--original-config',type=Path,required=True);a=p.parse_args();results=[]
 def case(name,action):
  try:action();status='PASS';error=''
  except Exception as e:status='FAIL';error=str(e)
  results.append(dict(name=name,status=status,assertions=1,error=error));print(status,name,flush=True)
 def rejects(action):
  try:action()
  except (ValueError,OSError):return
  raise AssertionError('Unsafe input unexpectedly accepted')
 case('unpatched_tree_verified',lambda:check_sources(a.original_core))
 case('patched_tree_verified',lambda:check_sources(a.patched_core,True))
 case('unpatched_core_rejected_for_stage16',lambda:rejects(lambda:check_sources(a.original_core,True)))
 case('patched_core_rejected_as_upstream_original',lambda:rejects(lambda:check_sources(a.patched_core)))
 with tempfile.TemporaryDirectory(prefix='stage16-validation-') as d:
  temp=Path(d);core=temp/'3.3.0';shutil.copytree(a.original_core,core)
  original=(core/'platform.txt').read_bytes();(core/'platform.txt').write_bytes(original.replace(b'version=3.3.0',b'version=2.0.17'))
  case('unexpected_core_version_rejected',lambda:rejects(lambda:check_sources(core)))
  (core/'platform.txt').write_bytes(original)
  routing=core/'libraries/USB/src/USBHID.cpp';routing.write_bytes(routing.read_bytes()+b'\n// tamper\n')
  case('unexpected_source_bytes_rejected',lambda:rejects(lambda:check_sources(core)))
  case('installed_data_isolation_rejected',lambda:rejects(lambda:prepare(a.original_core,a.original_core.parents[4]/'unsafe-stage16-copy',ROOT)))
  case('installed_user_isolation_rejected',lambda:rejects(lambda:prepare(a.original_core,temp/'owner-user/unsafe-stage16-copy',temp/'owner-user')))
  case('existing_isolation_destination_rejected',lambda:rejects(lambda:prepare(a.original_core,temp,ROOT)))
  case('repository_isolation_destination_rejected',lambda:rejects(lambda:prepare(a.original_core,ROOT/'stage16-unsafe',ROOT)))
  r=subprocess.run([sys.executable,str(ROOT/'tools/build_s3.py'),'--build-dir',str(temp/'unguarded')],capture_output=True,text=True)
  case('build_requires_patched_core_argument',lambda:(_ for _ in ()).throw(AssertionError('guard absent')) if r.returncode==0 or '--patched-core-dir' not in r.stderr else None)
  guards=(ROOT/'EvilDuckS3/hid_backend.cpp').read_text().split('#include',1)[0]
  r=subprocess.run(['g++','-E','-x','c++','-'],input=guards,capture_output=True,text=True)
  case('ordinary_firmware_compile_rejected',lambda:(_ for _ in ()).throw(AssertionError('compile guard absent')) if r.returncode==0 or 'paired HID routing' not in r.stderr else None)
  r=subprocess.run(['g++','-E','-x','c++','-DEVILDUCK_VERIFIED_HID_ROUTING=1','-'],input=guards,capture_output=True,text=True)
  case('verified_firmware_compile_guard_enabled',lambda:(_ for _ in ()).throw(AssertionError('guard rejects validated build')) if r.returncode else None)
 with tempfile.TemporaryDirectory(prefix='stage16-fallback-') as d:
  r=subprocess.run([sys.executable,str(ROOT/'tools/build_s3.py'),'--build-dir',d,'--patched-core-dir',str(a.patched_core),'--arduino-cli',a.arduino_cli,'--config-file',str(a.original_config)],capture_output=True,text=True)
  case('cli_unpatched_fallback_rejected_before_compile',lambda:(_ for _ in ()).throw(AssertionError('unexpected CLI fallback result: '+r.stderr)) if r.returncode==0 or 'refusing unpatched fallback' not in r.stderr else None)
 case('full_linked_production_firmware_provenance',lambda:verify(a.patched_core,a.build_dir))
 report=dict(results=results,pass_count=sum(r['status']=='PASS' for r in results),fail_count=sum(r['status']=='FAIL' for r in results),assertions=len(results),hardware_access=False)
 a.results.write_text(json.dumps(report,indent=2)+'\n');return bool(report['fail_count'])
if __name__=='__main__':raise SystemExit(main())
