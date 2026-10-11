#!/usr/bin/env python3
"""Actual production keyboard ownership/scheduler, RAM endpoints; no hardware."""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/stage1'))
from run_tests import compile_target as prior_compile
# Actual production Stage 10 storage modules as well as the real HID/parser/runtime.
def compile_target(main, build, name):
    build.mkdir(parents=True, exist_ok=True)
    fw=ROOT/'EvilDuckS3'
    modules=['com','duckscript','duck_vars','duck_keys','keyboard_locale','locales','hid_backend','script_log','cli','script_source','script_parser','duck_expr','duck_constants','script_functions','attackmode','usb_msc','sd_card']
    exe=build/name
    subprocess.run(['g++','-std=gnu++17','-g','-O1','-Wall','-Wextra','-pthread','-DEVILDUCK_HOST_TEST','-DEVILDUCK_PRODUCTION_STORAGE','-DCONFIG_TINYUSB_MSC_ENABLED=1','-DCONFIG_TINYUSB_MSC_BUFSIZE=4096','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage10/mocks'),'-I'+str(ROOT/'tests/stage1/mocks'),'-I'+str(fw),str(main),str(ROOT/'tests/stage1/mocks/host.cpp'),*[str(fw/(m+'.cpp')) for m in modules],'-o',str(exe)], check=True)
    return exe
TESTS = re.findall(r'n == "(\w+)"', (ROOT/'tests/stage12/test_main.cpp').read_text())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-dir',type=Path)
    p.add_argument('--results',type=Path)
    a=p.parse_args(); b=a.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage12-'))
    exe=compile_target(ROOT/'tests/stage12/test_main.cpp', b, 'stage12_tests')
    results=[]
    probe=compile_target(ROOT/'tests/stage12/no_alloc.cpp', b, 'stage12_no_alloc')
    for name in TESTS + ['feedback_registry_allocation_probe']:
        r=subprocess.run([str(probe)] if name == 'feedback_registry_allocation_probe' else [str(exe),name],capture_output=True,text=True,timeout=30)
        print(r.stdout,r.stderr,end='',flush=True)
        count=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
        results.append(dict(name=name,status='PASS' if r.returncode==0 else 'FAIL',assertions=int(count[1]) if count else 0,stdout=r.stdout,stderr=r.stderr))
    report=dict(pass_count=sum(r['status']=='PASS' for r in results),fail_count=sum(r['status']=='FAIL' for r in results),assertions=sum(r['assertions'] for r in results),results=results,sanitizers='ASan/UBSan',hardware_access=False)
    if a.results:a.results.write_text(json.dumps(report,indent=2)+'\n')
    print('Stage12: {pass_count} PASS, {fail_count} FAIL, {assertions} assertions'.format(**report))
    return bool(report['fail_count'])
if __name__=='__main__':raise SystemExit(main())
