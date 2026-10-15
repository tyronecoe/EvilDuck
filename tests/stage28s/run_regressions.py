#!/usr/bin/env python3
"""Affected unchanged language suites and real production scheduler default-off comparison."""
import argparse,json,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
from run_tests import ROOT,load,command,execute
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir(parents=True)
scheduler=load(ROOT/'tests/stage28s/prepare_sources.py','prep').prepare(a.build_dir/'scheduler')
cases=re.findall(r'n == "(\w+)"',(ROOT/'tests/stage14/test_main.cpp').read_text());results={};commands={}
for kind,source in [('unchanged_production',ROOT/'EvilDuckS3/com.cpp'),('patched_optin_disabled',scheduler/'com.cpp')]:
 exe=a.build_dir/kind;cmd=command(exe,source,ROOT/'tests/stage14/test_main.cpp',opt=False,real_backend=True);commands[kind]=cmd;subprocess.run(cmd,check=True)
 rows=[execute(exe,n) for n in cases];results[kind]=dict(counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows)
 print(kind,results[kind]['counts'],results[kind]['assertions'],flush=True)
for old,new in zip(results['unchanged_production']['results'],results['patched_optin_disabled']['results']):assert (old['exit'],old['stdout'],old['stderr'])==(new['exit'],new['stdout'],new['stderr']),old['id']
# One execution each of directly reused unchanged function-continuation and multiline suites.
for stage in ['stage28a','stage28b']:
 subprocess.run([sys.executable,str(ROOT/'tests'/stage/'run_tests.py'),'--build-dir',str(a.build_dir/stage),'--results',str(a.build_dir/(stage+'.json'))],check=True)
 results[stage]=json.loads((a.build_dir/(stage+'.json')).read_text())
report=dict(suites=results,commands=commands,disabled_compatibility='PASS exact stdout/stderr/exit matched unchanged original for every Stage14 scheduler case',historical_classifications='unchanged; no controller/watchdog or Mac rerun',sanitizers='ASan/UBSan/leak detection enabled',hardware=False)
a.results.write_text(json.dumps(report,indent=2)+'\n')
assert not any(v['counts']['FAIL'] for v in results.values())
