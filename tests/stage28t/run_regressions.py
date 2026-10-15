#!/usr/bin/env python3
"""Actual production ownership/loss/jitter scheduler cases, default-off equivalence."""
import argparse,json,pathlib,re,subprocess,sys,hashlib
sys.dont_write_bytecode=True
from run_tests import ROOT,command,execute,load
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir(parents=True)
prototype=load(ROOT/'tests/stage28t/prepare_sources.py','prep').prepare(a.build_dir/'prototype');original=a.build_dir/'original';original.mkdir()
for n in ['com.cpp','com.h','hid_backend.cpp','hid_backend.h']:(original/n).write_bytes((ROOT/'EvilDuckS3'/n).read_bytes())
(original/'platform.cpp').write_bytes((ROOT/'tests/stage1/mocks/host.cpp').read_bytes())
cases=re.findall(r'n == "(\w+)"',(ROOT/'tests/stage14/test_main.cpp').read_text());assert len(cases)==len(set(cases));suites={};commands={}
for role,sources in [('unchanged_production',original),('candidate_optin_disabled',prototype)]:
 exe=a.build_dir/role;cmd=command(exe,sources,ROOT/'tests/stage14/test_main.cpp',opt=False);commands[role]=cmd;subprocess.run(cmd,check=True)
 rows=[execute(exe,n) for n in cases];suites[role]=dict(counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows)
 print(role,suites[role]['counts'],suites[role]['assertions'],flush=True)
for x,y in zip(suites['unchanged_production']['results'],suites['candidate_optin_disabled']['results']):assert (x['exit'],x['stdout'],x['stderr'])==(y['exit'],y['stdout'],y['stderr']),x['id']
a.results.write_text(json.dumps(dict(suites=suites,commands=commands,default_off='PASS exact output/exit for all cases',hardware=False),indent=2)+'\n')
assert not any(v['counts']['FAIL'] for v in suites.values())
