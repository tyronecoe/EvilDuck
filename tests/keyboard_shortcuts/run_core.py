#!/usr/bin/env python3
"""Selected unchanged compiler/continuation/text/preflight tests on the patched core."""
import pathlib,sys,argparse,re,json,os,subprocess
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
p=argparse.ArgumentParser();p.add_argument('--sources',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
for r in json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text())['after']:assert sha(a.sources/r['file'])==r['sha256']
selected=[('stage27b','test_core.cpp',{'unsupported_explicit_rejection','source_and_table_limits','nesting_and_expression_boundaries'}),('stage28a','test_calls.cpp',{'depth_limit_cycles_and_frames'}),('stage28b','test_blocks.cpp',{'nested_structure_and_call_boundaries'}),('stage28c','test_compile.cpp',set())]
rows=[];commands=[];skips=[]
mirror=a.build_dir/'source';(mirror/'language_preview').mkdir(parents=True)
(mirror/'language_preview/core.h').write_bytes((a.sources/'core.h').read_bytes())
for stage,filename,_ in selected:
 f=mirror/'tests'/stage/filename;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((ROOT/'tests'/stage/filename).read_bytes());assert f.read_bytes()==(ROOT/'tests'/stage/filename).read_bytes()

env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for stage,filename,excluded in selected:
 cases=re.search(r"CASES='([^']+)'",(ROOT/'tests'/stage/'run_tests.py').read_text())[1].split();skips.extend(dict(stage=stage,id=c,status='NOT_RUN_CHANGED_VOCABULARY',reason='Historical test expects CTRL rejection or uses newly reserved function-key identifiers; unchanged historical source retained') for c in cases if c in excluded)
 cmd=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(a.sources),'-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-DPREVIEW_CALL_FIXTURES="'+str(ROOT/'tests/stage28a/fixtures')+'"','-DPREVIEW_BLOCK_FIXTURES="'+str(ROOT/'tests/stage28b/fixtures')+'"',str(a.sources/'core.cpp'),str(mirror/'tests'/stage/filename),'-o',str(a.build_dir/stage)];commands.append(cmd);subprocess.run(cmd,check=True)
 for n in cases:
  if n in excluded:continue
  r=subprocess.run([str(a.build_dir/stage),n],env=env,capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);row=dict(stage=stage,id=n,status='PASS' if not r.returncode and m else 'FAIL',exit=r.returncode,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(stage,n,row['status'],r.stderr if r.returncode else '',flush=True)
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,not_run=skips,commands=commands,sanitizers='ASan/UBSan/leaks',hardware=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
