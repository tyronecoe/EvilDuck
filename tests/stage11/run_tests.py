#!/usr/bin/env python3
"""Actual production keyboard ownership/scheduler, RAM endpoints; no hardware."""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/stage1'))
from run_tests import compile_target
TESTS = re.findall(r'n == "(\w+)"', (ROOT/'tests/stage11/test_main.cpp').read_text())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-dir',type=Path)
    p.add_argument('--results',type=Path)
    a=p.parse_args(); b=a.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage11-'))
    exe=compile_target(ROOT/'tests/stage11/test_main.cpp', b, 'stage11_tests')
    results=[]
    probe=compile_target(ROOT/'tests/stage11/no_alloc.cpp', b, 'stage11_no_alloc')
    for name in TESTS + ['ownership_allocation_probe']:
        r=subprocess.run([str(probe)] if name == 'ownership_allocation_probe' else [str(exe),name],capture_output=True,text=True,timeout=30)
        print(r.stdout,r.stderr,end='',flush=True)
        count=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
        results.append(dict(name=name,status='PASS' if r.returncode==0 else 'FAIL',assertions=int(count[1]) if count else 0,stdout=r.stdout,stderr=r.stderr))
    report=dict(pass_count=sum(r['status']=='PASS' for r in results),fail_count=sum(r['status']=='FAIL' for r in results),assertions=sum(r['assertions'] for r in results),results=results,sanitizers='ASan/UBSan',hardware_access=False)
    if a.results:a.results.write_text(json.dumps(report,indent=2)+'\n')
    print('Stage11: {pass_count} PASS, {fail_count} FAIL, {assertions} assertions'.format(**report))
    return bool(report['fail_count'])
if __name__=='__main__':raise SystemExit(main())
