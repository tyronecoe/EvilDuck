#!/usr/bin/env python3
import pathlib,sys,json,subprocess,os,re,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
p=argparse.ArgumentParser();p.add_argument('--sources',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir();s=a.sources
for row in json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text())['after']:assert sha(s/row['file'])==row['sha256']
base=(ROOT/'tests/stage27b/test_core.cpp').read_text();assert base.startswith('#include "../../language_preview/core.h"');base=base.replace('#include "../../language_preview/core.h"','#include "core.h"',1);(a.build_dir/'base.cpp').write_text(base)
(a.build_dir/'main.cpp').write_text('#define main base_main\n#include "base.cpp"\n#undef main\n#include '+json.dumps(str(ROOT/'tests/keyboard_shortcuts/core_new.inc'))+'\n')
cmd=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1','-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(s),str(s/'core.cpp'),str(a.build_dir/'main.cpp'),'-o',str(a.build_dir/'native')];subprocess.run(cmd,check=True);rows=[]
for n in ['C01','C02','C03']:
 r=subprocess.run([str(a.build_dir/'native'),n],capture_output=True,text=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);rows.append(dict(id=n,status='PASS' if not r.returncode and m else 'FAIL',exit=r.returncode,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr));print(n,rows[-1]['status'],r.stderr,flush=True)
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,command=cmd,sanitizers='ASan/UBSan/leaks',hardware=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
