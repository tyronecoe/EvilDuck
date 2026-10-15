#!/usr/bin/env python3
"""Actual com + actual hid_backend + unchanged preview; explicit RAM-only lower API."""
import argparse,pathlib,json,subprocess,hashlib,sys,os,re,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
ENV=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
MODULES=['duckscript','duck_vars','duck_keys','keyboard_locale','locales','script_log','cli','script_source','script_parser','duck_expr','duck_constants','script_functions','script_preprocessor','duck_random']
def command(exe,scratch,main,opt=True):
 fw=ROOT/'EvilDuckS3'
 sources=[main,scratch/'platform.cpp',scratch/'com.cpp',scratch/'hid_backend.cpp',*[fw/(n+'.cpp') for n in MODULES]]
 if opt:sources.extend([ROOT/'tests/stage28t/adapter.cpp',ROOT/'tests/stage28t/lower.cpp',ROOT/'tests/stage28t/allocations.cpp',ROOT/'language_preview/core.cpp'])
 includes=[scratch,ROOT/'tests/stage28t',*([ROOT/'tests/stage28t/mocks'] if opt else []),ROOT/'tests/stage1/mocks',fw,ROOT/'language_preview']
 return ['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-pthread','-DEVILDUCK_HOST_TEST',*(['-DEVILDUCK_NATIVE_SCHEDULER_ROUTE_B','-DEVILDUCK_NATIVE_REAL_BACKEND_B'] if opt else []),'-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','--coverage',*['-I'+str(x) for x in includes],*map(str,sources),'-o',str(exe)]
def execute(exe,case):
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=30,env=ENV);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 return dict(id=case,status='PASS' if r.returncode==0 and m else 'FAIL',exit=r.returncode,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr)
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir(parents=True)
 scratch=load(ROOT/'tests/stage28t/prepare_sources.py','prep').prepare(a.build_dir/'sources');exe=a.build_dir/'native';cmd=command(exe,scratch,ROOT/'tests/stage28t/test_main.cpp');subprocess.run(cmd,check=True)
 rows=[]
 for i in range(1,48):
  r=execute(exe,'T%02d'%i);rows.append(r);print(r['id'],r['status'],r['stderr'] if r['exit'] else '',flush=True)
 neg=a.build_dir/'negative';ncmd=command(neg,scratch,ROOT/'tests/stage28t/test_main.cpp');ncmd.insert(1,'-DSTAGE28T_NEGATIVE_CONTROL');subprocess.run(ncmd,check=True);negative=execute(neg,'T01');assert negative['exit']==1 and 'deliberate negative control' in negative['stderr']
 report=dict(primary=dict(counts={s:sum(x['status']==s for x in rows) for s in ['PASS','FAIL']},assertions=sum(x['assertions'] for x in rows),results=rows),negative_control=negative,commands=dict(primary=cmd,negative=ncmd),sanitizers='ASan/UBSan/detect_leaks=1 for completed cases',hardware=False,firmware=False,fixture_hashes=[dict(file=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted((ROOT/'tests/stage28t').rglob('*')) if f.is_file()])
 a.results.write_text(json.dumps(report,indent=2)+'\n');print(report['primary']['counts'],report['primary']['assertions']);return bool(report['primary']['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
