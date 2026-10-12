#!/usr/bin/env python3
"""Patched exact routing bodies with current production backend, all mock endpoints."""
import argparse,importlib.util,json,re,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
sys.dont_write_bytecode = True
from patched_core import check_sources,sha
spec=importlib.util.spec_from_file_location('historical',ROOT/'tests/stage15/run_tests.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
EXTRA=re.findall(r'n=="(\w+)"',(ROOT/'tests/stage16/routing.cpp').read_text())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--build-dir',type=Path);p.add_argument('--results',type=Path);a=p.parse_args()
 check_sources(a.core_dir,True);b=a.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage16-tests-'))
 exe=old.compile_exe(a.core_dir,ROOT/'EvilDuckS3/hid_backend.cpp',b,'routing',True,ROOT/'tests/stage16/routing.cpp')
 results=[]
 for name in old.NORMAL+old.FAULTS[:4]+EXTRA:
  r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30);count=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
  status='FAIL' if r.returncode else 'OBSERVED' if name=='stock_output_queue_wait_policy' else 'PASS'
  results.append(dict(name=name,status=status,assertions=int(count[1]) if count else 0,stdout=r.stdout,stderr=r.stderr));print(status,name,flush=True)
 check_sources(a.core_dir,True)
 report=dict(results=results,counts={s:sum(r['status']==s for r in results) for s in ['PASS','FAIL','XFAIL','XPASS','OBSERVED']},assertions=sum(r['assertions'] for r in results),sanitizers='ASan/UBSan',routing_sha256=sha(a.core_dir/'libraries/USB/src/USBHID.cpp'),backend_sha256=sha(ROOT/'EvilDuckS3/hid_backend.cpp'),hardware_access=False)
 if a.results:a.results.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2));return bool(report['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
