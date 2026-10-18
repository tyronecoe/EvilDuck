"""Reuse the exact final native composition/flags for a focused timing/allocation probe."""
import argparse,json,pathlib,subprocess,sys,os
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--native-results',type=pathlib.Path,required=True);p.add_argument('--executable',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.executable.exists() and not a.results.exists()
r=json.loads(a.native_results.read_text());sources=next(pathlib.Path(x).parent for x in r['command'] if x.endswith('/core.cpp'));(sources/'probe_cases.inc').write_text((ROOT/'tests/led_feedback/test_main.cpp').read_text().replace('int main(int argc,char**argv)','int feedback_existing_main(int argc,char**argv)'));command=[x.replace(str(ROOT/'tests/led_feedback/test_main.cpp'),str(ROOT/'tests/led_feedback/caps_probe.cpp')) for x in r['command']];command[command.index('-o')+1]=str(a.executable);subprocess.run(command,check=True)
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1');run=subprocess.run([str(a.executable)],capture_output=True,text=True,env=env,timeout=30);assert run.returncode==0,(run.stdout,run.stderr);report=json.loads(run.stdout);assert report['status']=='PASS' and not run.stderr
report.update(command=command,sanitizers='ASan/UBSan/leak detection',scope='Actual final production source + pinned dispatcher slices, mock transport/clock and native C++ new instrumentation; not physical dwell or ESP heap')
a.results.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='command'},indent=2))
