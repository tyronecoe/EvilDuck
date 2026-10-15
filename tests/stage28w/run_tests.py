#!/usr/bin/env python3
"""Actual W application bodies with named memory-only lower interfaces."""
import pathlib,sys,argparse,json,subprocess,shutil
sys.dont_write_bytecode=True
from prepare_sources import ROOT,prepare,native_sources,load,sha
V=load(ROOT/'tests/stage28v/run_tests.py','v_runner')
def command(exe,scratch):
 cmd=V.command(exe,scratch,ROOT/'tests/stage28w/test_main.cpp');cmd[1:1]=['-I'+str(ROOT/'tests/stage28w/mocks')]
 cmd[cmd.index('-o'):cmd.index('-o')]=[str(ROOT/'tests/stage28w/boot_fixture.cpp')]
 return cmd
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir()
 s=prepare(a.build_dir/'sources');native_sources(s);cmd=command(a.build_dir/'native',s);subprocess.run(cmd,check=True)
 rows=[]
 for i in range(1,35):
  row=V.U.execute(a.build_dir/'native','W%02d'%i);rows.append(row);print(row['id'],row['status'],row['stderr'],flush=True)
 negsrc=a.build_dir/'negative-sources';shutil.copytree(s,negsrc);p=negsrc/'cli.cpp';before=sha(p);text=p.read_text();assert text.count('SerialWorkBudget=64')==1;p.write_text(text.replace('SerialWorkBudget=64','SerialWorkBudget=65'))
 neg=command(a.build_dir/'negative',negsrc);subprocess.run(neg,check=True);nr=V.U.execute(a.build_dir/'negative','W10');assert nr['exit']==1 and 'serial budget' in nr['stderr'],nr
 out=dict(counts={k:sum(x['status']==k for x in rows) for k in ['PASS','FAIL']},assertions=sum(x['assertions'] for x in rows),results=rows,negative_control=dict(result=nr,change='actual CLI budget changed from64 to65 in separate disposable source; no forced assert',before_sha256=before,after_sha256=sha(p)),commands=[cmd,neg],tested_w_files=[dict(file=str(f.relative_to(ROOT)),sha256=sha(f)) for f in sorted((ROOT/'tests/stage28w').rglob('*')) if f.is_file()],sanitizers=V.U.T.ENV['ASAN_OPTIONS']+'; '+V.U.T.ENV['UBSAN_OPTIONS'],actual_framework_execution=False,complete_application_bodies=True,hardware=False,target_firmware=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts'],out['assertions']);return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
