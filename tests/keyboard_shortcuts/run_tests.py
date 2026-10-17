#!/usr/bin/env python3
"""New shortcut cases + unchanged selected regression cases, memory-only endpoints."""
import pathlib,sys,subprocess,json,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,prepare,native_sources,overlay,load,manifest
X=load(ROOT/'tests/stage28x/run_tests.py','shortcut_x_runner')
def command(exe,s,main):
 cmd=X.command(exe,s,main)
 cmd.insert(1,'-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1')
 for r in manifest()['runtime_inputs']:
  p=ROOT/r['file']
  if not (s/p.name).exists():(s/p.name).write_bytes(p.read_bytes())
 for n in ['bridge.cpp','bridge.h','keyboard.cpp','keyboard.h']:(s/n).write_bytes((ROOT/'language_preview'/n).read_bytes())
 overlay(s)
 # Use a single physical header/source copy in every translation unit.
 cmd=[v.replace(str(ROOT/'language_preview/core.cpp'),str(s/'core.cpp')).replace('-I'+str(ROOT/'language_preview'),'-I'+str(s)) for v in cmd]
 return cmd

def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
 s=prepare(a.build_dir/'sources');native_sources(s);cmd=command(a.build_dir/'native',s,ROOT/'tests/keyboard_shortcuts/test_main.cpp');subprocess.run(cmd,check=True)
 groups=[('new_shortcuts',['K%02d'%i for i in range(1,26)]),('unchanged_w',['W%02d'%i for i in range(1,35)])]
 rows=[]
 for group,names in groups:
  for n in names:
   r=X.W.V.U.execute(a.build_dir/'native',n);r['group']=group;rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
 # Direct backend fault-injection and admission tests on the same changed composition.
 tmain=s/'test_main.cpp';tmain.write_bytes((ROOT/'tests/stage28t/test_main.cpp').read_bytes()+b'\nuint32_t esp_random(){return 0;}\n')
 tcmd=list(cmd);tcmd=[v.replace(str(ROOT/'tests/keyboard_shortcuts/test_main.cpp'),str(tmain)) for v in tcmd];tcmd[tcmd.index('-o')+1]=str(a.build_dir/'t-regression');subprocess.run(tcmd,check=True)
 for i in range(1,48):
  if i==34:continue # T34 assumes Linux thread identity; K25 tests the full RTOS-task mock.
  r=X.W.V.U.execute(a.build_dir/'t-regression','T%02d'%i);r['group']='unchanged_t';rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
 out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,not_run=[dict(id='T34',reason='Linux-thread fixture does not assign foreign RTOS-task identity; covered by K25')],commands=[cmd,tcmd],sanitizers={k:X.W.V.U.T.ENV[k] for k in ['ASAN_OPTIONS','UBSAN_OPTIONS']},hardware=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts'],out['assertions']);return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
