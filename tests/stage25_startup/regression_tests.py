#!/usr/bin/env python3
"""Only affected legacy settings/startup/save behavior; not a full language rerun."""
import argparse,importlib.util,json,re,subprocess,sys,os
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from nvs_source_prepare import verify
p=argparse.ArgumentParser();p.add_argument('--sdk-source',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args();verify(a.sdk_source)
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh outputs required')
a.build_dir.mkdir()
def load(stage):
 spec=importlib.util.spec_from_file_location('legacy'+str(stage),ROOT/f'tests/stage{stage}/run_tests.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m19=load(19);m20=load(20);rows=[]
common=['g++','-std=gnu++17','-DEVILDUCK_HOST_TEST','-pthread','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage19/mocks'),'-I'+str(a.sdk_source/'components/nvs_flash/include'),'-I'+str(a.sdk_source/'components/esp_common/include')]
targets=[]
for safe in [False,True]:
 exe=a.build_dir/('safe' if safe else 'normal');args=common+['-I'+str(ROOT/'tests/stage17/mocks'),'-I'+str(ROOT/'tests/stage1/mocks')]
 if safe:args+=['-DEVILDUCK_DEPLOYMENT_SAFE_START=1']
 subprocess.run(args+[str(ROOT/'tests/stage19/settings_startup.cpp'),'-o',str(exe)],check=True);targets.append(('legacy-safe' if safe else 'legacy-normal',exe,m19.SETTINGS))
exe=a.build_dir/'save';subprocess.run(common+[str(ROOT/'tests/stage20/settings_save.cpp'),'-o',str(exe)],check=True);targets.append(('legacy-checked-save',exe,m20.SAVES+['interrupted_save']))
for target,exe,names in targets:
 for name in names:
  r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
  status='PASS' if not r.returncode and m else 'FAIL';assertions=int(m[1]) if m else 0
  if name=='interrupted_save':status='OBSERVED' if r.returncode==77 and 'SIMULATED_POWER_LOSS sets=4 commits=0' in r.stdout else 'FAIL';assertions=2
  row=dict(name=name,target=target,status=status,assertions=assertions,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(status,target,name)
a.results.write_text(json.dumps(dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL','OBSERVED']},assertions=sum(r['assertions'] for r in rows),sanitizers='ASan/UBSan; leak detection enabled except intentional interruption observation',language_suites_not_repeated=True,hardware_access=False),indent=2)+'\n');raise SystemExit(any(r['status']=='FAIL' for r in rows))
