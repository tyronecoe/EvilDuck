#!/usr/bin/env python3
"""Unchanged 30 controlled startup cases, applied to selector-off V scratch sources."""
import argparse,pathlib,sys,json,subprocess,re,os
sys.dont_write_bytecode=True
from prepare_sources import ROOT,load,prepare,sha
old=load(ROOT/'tests/stage25_startup/run_tests.py','startup25')
p=argparse.ArgumentParser();p.add_argument('--sdk-source',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
sys.path.insert(0,str(ROOT/'tools'));from nvs_source_prepare import verify
verify(a.sdk_source);assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir()
s=prepare(a.build_dir/'sources');main=a.build_dir/'startup.cpp';text=(ROOT/'tests/stage25_startup/test_main.cpp').read_text()
for n in ['spiffs.cpp','storage.cpp','settings.cpp','EvilDuckS3.ino']:text=text.replace('../../EvilDuckS3/'+n,str(s/n))
main.write_text(text)
includes=[ROOT/'EvilDuckS3',ROOT/'tests/stage25_startup/mocks',ROOT/'tests/stage10/mocks',ROOT/'tests/stage19/mocks',ROOT/'tests/stage17/mocks',ROOT/'tests/stage1/mocks',a.sdk_source/'components/nvs_flash/include',a.sdk_source/'components/esp_common/include']
cmd=['g++','-std=gnu++17','-O1','-g','-DEVILDUCK_HOST_TEST','-DEVILDUCK_CONTROLLED_START=1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']+['-I'+str(d) for d in includes]+[str(main),'-o',str(a.build_dir/'startup')]
subprocess.run(cmd,check=True);rows=[]
for name in old.CASES:
 r=subprocess.run([str(a.build_dir/'startup'),name],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 row=dict(id=name,status='PASS' if r.returncode==0 and m else 'FAIL',exit=r.returncode,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['id'],row['status'],flush=True)
out=dict(counts={k:sum(x['status']==k for x in rows) for k in ['PASS','FAIL']},assertions=sum(x['assertions'] for x in rows),results=rows,command=cmd,fixture_original_sha256=sha(ROOT/'tests/stage25_startup/test_main.cpp'),native_copy_sha256=sha(main),classification='selector-off candidate comparison; not new case coverage',hardware=False)
a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
