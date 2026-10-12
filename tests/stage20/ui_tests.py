#!/usr/bin/env python3
"""Actual CLI module and complete web save handler bodies; mocked services only."""
import argparse,hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
build=module('base_tests',ROOT/'tests/stage1/run_tests.py');slice_tool=module('slice_tool',ROOT/'tests/stage15/run_tests.py')
NAMES=['web_save_busy','web_led_busy','cli_save_success','cli_save_failure','cli_reset_success','cli_reset_failure','cli_autorun_success','cli_autorun_failure','web_save_success','web_save_failure','web_led_success','web_led_failure','web_led_missing']
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args();a.build_dir.mkdir(parents=True,exist_ok=True)
 source=(ROOT/'EvilDuckS3/webserver.cpp').read_text();body='\n'.join(slice_tool.body(source,'static void '+n+'(') for n in ['handleSaveSettings','handleSetLed']);(a.build_dir/'actual_web_handlers.inc').write_text(body)
 # Base build includes actual CLI and runtime modules; copy test main beside extracted include.
 main=a.build_dir/'ui.cpp';main.write_bytes((ROOT/'tests/stage20/ui.cpp').read_bytes());exe=build.compile_target(main,a.build_dir,'ui')
 rows=[]
 for n in NAMES:
  r=subprocess.run([str(exe),n],capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);s='PASS' if not r.returncode and m else 'FAIL';rows.append(dict(name=n,status=s,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr));print(s,n,flush=True)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),web_source_sha256=hashlib.sha256(source.encode()).hexdigest(),web_handlers_sha256=hashlib.sha256(body.encode()).hexdigest(),whole_webserver_executed=False,sanitizers='ASan/UBSan',hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
