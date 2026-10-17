#!/usr/bin/env python3
import pathlib,sys,argparse,json,subprocess
sys.dont_write_bytecode=True
from prepare_sources import ROOT,load,prepare,native_sources,overlay,manifest
K=load(ROOT/'tests/keyboard_shortcuts/run_tests.py','http_keyboard_runner')
def command(exe,s,main):
 text=(ROOT/'tests/keyboard_shortcuts/test_main.cpp').read_text().replace('int main(int argc,char**argv)','int historical_keyboard_main(int argc,char**argv)').replace('../stage28w/test_main.cpp',str(ROOT/'tests/stage28w/test_main.cpp'))
 (s/'keyboard_cases.inc').write_text(text)
 # Use the same execution header in production modules still compiled from ROOT.
 cmd=K.X.command(exe,s,main)
 cmd.insert(1,'-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1')
 for row in manifest()['runtime_inputs']:
  f=ROOT/row['file']
  if not (s/f.name).exists():(s/f.name).write_bytes(f.read_bytes())
 for n in ['bridge.cpp','bridge.h','keyboard.cpp','keyboard.h']:(s/n).write_bytes((ROOT/'language_preview'/n).read_bytes())
 overlay(s)
 cmd=[v.replace(str(ROOT/'language_preview/core.cpp'),str(s/'core.cpp')).replace('-I'+str(ROOT/'language_preview'),'-I'+str(s)) for v in cmd]
 cmd.insert(1,'-DEVILDUCK_ROUTE_B_STATUS_HARDENING=1')
 cmd.insert(1,'-I'+str(ROOT/'tests/http_snapshot/mocks'))
 # Diagnostics and all callers must use the same reviewed physical source/header.
 (s/'script_log.cpp').write_bytes((ROOT/'EvilDuckS3/script_log.cpp').read_bytes())
 cmd=[v.replace(str(ROOT/'tests/stage28x/diagnostics.cpp'),str(s/'diagnostics.cpp')).replace(str(ROOT/'EvilDuckS3/script_log.cpp'),str(s/'script_log.cpp')) for v in cmd]
 return cmd

def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
 s=prepare(a.build_dir/'sources');native_sources(s);cmd=command(a.build_dir/'native',s,ROOT/'tests/http_snapshot/test_main.cpp');subprocess.run(cmd,check=True)
 rows=[]
 for n in ['H%02d'%i for i in range(1,19)]+['K%02d'%i for i in range(1,26)]+['W%02d'%i for i in range(1,35) if i!=34]:
  r=K.X.W.V.U.execute(a.build_dir/'native',n);rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
 out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,command=cmd,not_run=[dict(id='W34',reason='Old contention auth401 replaced by bounded busy409; H tests cover new contract')],hardware=False,sanitizers='ASan/UBSan/leaks');a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts'],out['assertions']);return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
