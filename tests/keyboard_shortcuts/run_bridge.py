#!/usr/bin/env python3
import sys,pathlib,argparse,subprocess,json,re,os
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
p=argparse.ArgumentParser();p.add_argument('--sources',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
s=a.sources
for r in json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text())['after']:assert sha(s/r['file'])==r['sha256']
cmd=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(s),str(ROOT/'tests/keyboard_shortcuts/bridge_tests.cpp'),*[str(s/n) for n in ['core.cpp','keyboard.cpp','bridge.cpp']],'-o',str(a.build_dir/'native')];subprocess.run(cmd,check=True)
rows=[]
for i in range(1,9):
 n='B%02d'%i;r=subprocess.run([str(a.build_dir/'native'),n],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);row=dict(id=n,status='PASS' if r.returncode==0 and m else 'FAIL',exit=r.returncode,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(n,row['status'],r.stderr,flush=True)
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,command=cmd,sanitizers='ASan/UBSan/detect_leaks=1',hardware=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
