#!/usr/bin/env python3
import pathlib,subprocess,sys,json,importlib.util,os,re,argparse,hashlib
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
T=load(ROOT/'tests/stage28t/run_tests.py','t_runner')
def command(exe,scratch,main,opt=True):
 cmd=T.command(exe,scratch,main,opt=False)
 if opt:
  cmd.insert(1,'-DEVILDUCK_PORTABLE_ROUTE_B');cmd.insert(1,'-DEVILDUCK_PRODUCTION_STORAGE')
  for name in ['duckscript.cpp','cli.cpp','keyboard_locale.cpp']:cmd=[x.replace(str(ROOT/'EvilDuckS3'/name),str(scratch/name)) for x in cmd]
  idx=cmd.index('-o');cmd[idx:idx]=[str(ROOT/'tests/stage28u'/f) for f in ['adapter.cpp','file_source.cpp','coordinator.cpp','lower.cpp','msc_platform.cpp']]+[str(scratch/'attackmode.cpp'),str(ROOT/'language_preview/core.cpp'),str(ROOT/'tests/stage28t/allocations.cpp')]
  cmd.insert(1,'-I'+str(ROOT/'tests/stage28u/mocks'));cmd.insert(1,'-I'+str(ROOT/'tests/stage28u'))
 return cmd
def execute(exe,name):return T.execute(exe,name)
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir(parents=True)
 fixtures=lambda:[dict(file=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted((ROOT/'tests/stage28u').rglob('*')) if f.is_file()]
 before=fixtures()
 scratch=load(ROOT/'tests/stage28u/prepare_sources.py','prep_u').prepare(a.build_dir/'sources');cmd=command(a.build_dir/'native',scratch,ROOT/'tests/stage28u/test_main.cpp');subprocess.run(cmd,check=True)
 rows=[]
 for i in range(1,65):
  row=execute(a.build_dir/'native','U%02d'%i);rows.append(row);print(row['id'],row['status'],row['stderr'],flush=True)
 neg=command(a.build_dir/'negative',scratch,ROOT/'tests/stage28u/test_main.cpp');neg.insert(1,'-DSTAGE28U_NEGATIVE_CONTROL');subprocess.run(neg,check=True);nr=execute(a.build_dir/'negative','U03');assert nr['exit']==1 and 'deliberate negative control' in nr['stderr']
 assert before==fixtures(),'fixture changed during build/test'
 report=dict(counts={k:sum(x['status']==k for x in rows) for k in ['PASS','FAIL']},assertions=sum(x['assertions'] for x in rows),results=rows,negative_control=nr,commands=[cmd,neg],tested_fixtures=before,sanitizers=T.ENV['ASAN_OPTIONS']+'; '+T.ENV['UBSAN_OPTIONS'],hardware=False,firmware=False)
 a.results.write_text(json.dumps(report,indent=2)+'\n');print(report['counts'],report['assertions']);return bool(report['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
