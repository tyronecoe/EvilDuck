#!/usr/bin/env python3
"""Affected production cases and exact final-selector-disabled comparison."""
import pathlib,json,subprocess,re,sys
sys.dont_write_bytecode=True
from run_tests import ROOT,T,load
import argparse
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir(parents=True)
candidate=load(ROOT/'tests/stage28u/prepare_sources.py','u_prep').prepare(a.build_dir/'candidate');original=a.build_dir/'original';original.mkdir()
for name in ['com.cpp','com.h','hid_backend.cpp','hid_backend.h']:(original/name).write_bytes((ROOT/'EvilDuckS3'/name).read_bytes())
(original/'platform.cpp').write_bytes((ROOT/'tests/stage1/mocks/host.cpp').read_bytes())
cases=re.findall(r'n == "(\w+)"',(ROOT/'tests/stage14/test_main.cpp').read_text());suites={};commands={}
for role,source in [('original',original),('disabled',candidate)]:
 exe=a.build_dir/(role+"-tests");cmd=T.command(exe,source,ROOT/'tests/stage14/test_main.cpp',opt=False)
 if role=='disabled':
  for name in ['duckscript.cpp','cli.cpp','keyboard_locale.cpp']:cmd=[x.replace(str(ROOT/'EvilDuckS3'/name),str(source/name)) for x in cmd]
 subprocess.run(cmd,check=True);rows=[T.execute(exe,n) for n in cases];suites[role]=dict(counts={s:sum(x['status']==s for x in rows) for s in ['PASS','FAIL']},assertions=sum(x['assertions'] for x in rows),results=rows);commands[role]=cmd;print(role,suites[role]['counts'],suites[role]['assertions'],flush=True)
for x,y in zip(suites['original']['results'],suites['disabled']['results']):assert (x['exit'],x['stdout'],x['stderr'])==(y['exit'],y['stdout'],y['stderr']),x['id']
assert all(x['counts']['FAIL']==0 for x in suites.values())
a.results.write_text(json.dumps(dict(suites=suites,commands=commands,comparison='exact exit/stdout/stderr',hardware=False),indent=2)+'\n')
