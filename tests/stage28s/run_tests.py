#!/usr/bin/env python3
"""Real com scheduler + unchanged Runtime; native mocked backend only."""
import argparse,hashlib,importlib.util,json,os,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
MODULES=['duckscript','duck_vars','duck_keys','keyboard_locale','locales','script_log','cli','script_source','script_parser','duck_expr','duck_constants','script_functions','script_preprocessor','duck_random']
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ENV=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
def command(build,scheduler,main,opt=True,real_backend=False):
 fw=ROOT/'EvilDuckS3'
 sources=[main,ROOT/'tests/stage1/mocks/host.cpp',scheduler,*[fw/(m+'.cpp') for m in MODULES]]
 if real_backend:sources.append(fw/'hid_backend.cpp')
 else:sources.extend([ROOT/'tests/stage28s/adapter.cpp',ROOT/'tests/stage28s/backend.cpp',ROOT/'language_preview/core.cpp'])
 return ['g++','-std=c++17','-g','-O1','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-pthread','-DEVILDUCK_HOST_TEST',*(['-DEVILDUCK_NATIVE_SCHEDULER_ROUTE_B'] if opt else []),'-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','--coverage',*['-I'+str(p) for p in [ROOT/'tests/stage28s',ROOT/'tests/stage1/mocks',fw,ROOT/'language_preview']],*map(str,sources),'-o',str(build)]
def execute(exe,case):
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=30,env=ENV)
 count=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 traces=[json.loads(s[6:]) for s in r.stdout.splitlines() if s.startswith('TRACE ')]
 return dict(id=case,exit=r.returncode,status='PASS' if r.returncode==0 and count else 'FAIL',assertions=int(count[1]) if count else 0,stdout=r.stdout,stderr=r.stderr,traces=traces)
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
 if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh output paths required')
 if a.build_dir.resolve().is_relative_to(ROOT):raise ValueError('Build outside checkout')
 a.build_dir.mkdir(parents=True);prep=load(ROOT/'tests/stage28s/prepare_sources.py','prep');scratch=prep.prepare(a.build_dir/'scheduler')
 exe=a.build_dir/'native';cmd=command(exe,scratch/'com.cpp',ROOT/'tests/stage28s/test_main.cpp');subprocess.run(cmd,check=True)
 rows=[]
 for i in range(1,57):
  row=execute(exe,'S%02d'%i);rows.append(row);print(row['id'],row['status'],row['stderr'] if row['exit'] else '',flush=True)
 # Same native sources, deliberate oracle corruption only; no repeated assertions counted.
 neg=a.build_dir/'negative';ncmd=command(neg,scratch/'com.cpp',ROOT/'tests/stage28s/test_main.cpp');ncmd.insert(1,'-DSTAGE28S_NEGATIVE_CONTROL');subprocess.run(ncmd,check=True);negative=execute(neg,'S01');assert negative['exit']==1 and 'deliberate negative control' in negative['stderr']
 report=dict(primary=dict(counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows),negative_control=negative,command=cmd,negative_command=ncmd,sanitizers='ASan/UBSan/detect_leaks=1 for completed cases',hardware=False,target_build=False,route='B selected for native only; LOCAL_SCHEDULER_DONE',fixtures=[dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((ROOT/'tests/stage28s').glob('*')) if p.is_file()])
 a.results.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['primary']['counts']),report['primary']['assertions'],flush=True)
 return bool(report['primary']['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
