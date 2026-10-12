#!/usr/bin/env python3
"""Exact initArduino + actual EvilDuck setup/loop; instrumented synthetic NVS only."""
import argparse,hashlib,importlib.util,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources
spec=importlib.util.spec_from_file_location('routing_history',ROOT/'tests/stage15/run_tests.py');history=importlib.util.module_from_spec(spec);spec.loader.exec_module(history)
NAMES=['protected_initial_unknown','protected_success','protected_no_free_pages','protected_new_version','protected_invalid_metadata','protected_missing_partition','protected_flash_read_failure','protected_flash_initialization_failure','protected_flash_operation_failure','protected_no_memory','protected_unexpected_positive','protected_unexpected_negative','protected_repeat_failure','protected_retry_never_arms_failed_app','observed_sdk_side_effect_outside_policy']
def compile(core,build,protected,safe):
 build.mkdir(parents=True);source=(core/'cores/esp32/esp32-hal-misc.c').read_text();body=history.body(source,'void initArduino(')
 if protected:body=source[source.index('static esp_err_t evilduck_nvs_error'):source.index('void initArduino()')]+body
 (build/'core_startup.inc').write_text('// Exact pinned Apache-2.0 core source bodies\n'+body+'\n')
 exe=build/'startup';args=['g++','-std=gnu++17','-O1','-g','-DEVILDUCK_HOST_TEST','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(build),'-I'+str(ROOT/'tests/stage17/mocks'),'-I'+str(ROOT/'tests/stage1/mocks'),str(ROOT/'tests/stage18/startup.cpp'),'-o',str(exe)]
 if protected:args.insert(1,'-DPROTECTED_NVS')
 if safe:args.insert(1,'-DEVILDUCK_DEPLOYMENT_SAFE_START=1')
 subprocess.run(args,check=True);return exe

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original-core',type=Path,required=True);p.add_argument('--patched-core',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args();check_sources(a.original_core);check_sources(a.patched_core,True);results=[]
 variants=[('historical_unpatched',compile(a.original_core,a.build_dir/'unpatched',False,False),['historical_no_free_pages_erase','historical_new_version_erase','historical_erase_failure_error_replaced'])]
 for safe in [False,True]:variants.append(('safe' if safe else 'normal',compile(a.patched_core,a.build_dir/('safe' if safe else 'normal'),True,safe),NAMES))
 for variant,exe,names in variants:
  for n in names:
   r=subprocess.run([str(exe),n],capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
   status='FAIL' if r.returncode else 'OBSERVED' if variant=='historical_unpatched' or n.startswith('observed_') else 'PASS'
   results.append(dict(name=n,variant=variant,status=status,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr));print(status,variant,n,flush=True)
 check_sources(a.original_core);check_sources(a.patched_core,True)
 out=dict(results=results,counts={s:sum(r['status']==s for r in results) for s in ['PASS','FAIL','OBSERVED','XPASS','XFAIL']},assertions=sum(r['assertions'] for r in results),sanitizers='ASan/UBSan',hardware_access=False,owner_files_verified=False,sdk_nvs_implementation_executed=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
