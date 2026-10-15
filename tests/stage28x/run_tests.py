#!/usr/bin/env python3
import pathlib,sys,argparse,subprocess,json,shutil
sys.dont_write_bytecode=True
from prepare_sources import ROOT,prepare,native_sources,load,sha,manifest
W=load(ROOT/'tests/stage28w/run_tests.py','w_runner')
def command(exe,s,main):
 # One physical header copy for every actual runtime source, avoiding pragma-once aliases.
 for row in manifest()['runtime_inputs']:
  if row['file'].startswith('tests/stage28'):(s/pathlib.Path(row['file']).name).write_bytes((ROOT/row['file']).read_bytes())
 cmd=W.command(exe,s)
 cmd=[x.replace(str(ROOT/'tests/stage28v/adapter.cpp'),str(s/'adapter.cpp')).replace(str(ROOT/'tests/stage28v/file_source.cpp'),str(s/'file_source.cpp')).replace('-I'+str(ROOT/'tests/stage28v'),'-I'+str(s)) if x!='-I'+str(ROOT/'tests/stage28v/mocks') else x for x in cmd]
 cmd=[x.replace(str(ROOT/'tests/stage28w/test_main.cpp'),str(main)).replace(str(ROOT/'tests/stage28v/coordinator.cpp'),str(s/'coordinator.cpp')) for x in cmd]
 cmd=[x.replace(str(ROOT/'tests/stage28v/allocations.cpp'),str(ROOT/'tests/stage28x/allocations.cpp')) for x in cmd]
 cmd[1:1]=['-DEVILDUCK_ROUTE_B_DIAGNOSTICS','-I'+str(ROOT/'tests/stage28x'),'-I'+str(s)]
 cmd[cmd.index('-o'):cmd.index('-o')]=[str(ROOT/'tests/stage28x/diagnostics.cpp')]
 return cmd
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
 s=prepare(a.build_dir/'sources');native_sources(s);cmd=command(a.build_dir/'native',s,ROOT/'tests/stage28x/test_main.cpp');subprocess.run(cmd,check=True)
 rows=[]
 for i in range(1,20):
  r=W.V.U.execute(a.build_dir/'native','X%02d'%i);rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
 # Same actual W scenarios on instrumented app, no expectation edits.
 oldcmd=command(a.build_dir/'w-comparison',s,ROOT/'tests/stage28w/test_main.cpp');subprocess.run(oldcmd,check=True)
 old=[W.V.U.execute(a.build_dir/'w-comparison','W%02d'%i) for i in range(1,35)]
 negdir=a.build_dir/'negative';negdir.mkdir();t=(ROOT/'tests/stage28x/diagnostics.cpp').read_text();assert t.count('>=1000')==1;(negdir/'diagnostics.cpp').write_text(t.replace('>=1000','>=1'))
 ncmd=[x.replace(str(ROOT/'tests/stage28x/diagnostics.cpp'),str(negdir/'diagnostics.cpp')) for x in cmd];ncmd[ncmd.index('-o')+1]=str(a.build_dir/'negative-test');subprocess.run(ncmd,check=True);negative=W.V.U.execute(a.build_dir/'negative-test','X02');assert negative['exit']==1 and 'sparse' in negative['stderr'],negative
 summary=lambda rs:dict(counts={k:sum(r['status']==k for r in rs) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rs),results=rs)
 out=dict(primary=summary(rows),w_instrumented_comparison=summary(old),negative_control=negative,commands=[cmd,oldcmd,ncmd],sanitizers=W.V.U.T.ENV['ASAN_OPTIONS']+'; '+W.V.U.T.ENV['UBSAN_OPTIONS'],hardware=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['primary']['counts'],out['primary']['assertions'],out['w_instrumented_comparison']['counts']);return bool(out['primary']['counts']['FAIL'] or out['w_instrumented_comparison']['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
