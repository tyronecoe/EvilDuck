#!/usr/bin/env python3
"""Offline fake-phrase unit checks and mock-only public launcher execution."""
import sys,pathlib,argparse,json,subprocess,hashlib,os
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--candidate-sources',type=pathlib.Path,required=True);p.add_argument('--output-dir',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output_dir.exists();a.output_dir.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin=json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text());pins={r['file']:r['sha256'] for r in pin['after']}
for name in ['core.cpp','core.h']:assert sha(a.candidate_sources/name)==pins[name]
unit=subprocess.run([sys.executable,str(ROOT/'tests/host_capture/test_capture.py')],capture_output=True,text=True);assert unit.returncode==0 and 'Ran 11 tests' in unit.stderr
exe=a.output_dir/'launcher-mock';cmd=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(a.candidate_sources),str(ROOT/'tests/host_capture/compile_launchers.cpp'),str(a.candidate_sources/'core.cpp'),'-o',str(exe)];subprocess.run(cmd,check=True)
run_cmd=[str(exe),str(ROOT/'host_tests/capture/launchers/windows.duck'),str(ROOT/'host_tests/capture/launchers/macos.duck'),str(ROOT/'host_tests/led_return/launchers/windows.duck'),str(ROOT/'host_tests/led_return/launchers/macos.duck')];env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1');run=subprocess.run(run_cmd,capture_output=True,text=True,env=env);assert run.returncode==0 and run.stdout.count('PASS public launcher')==4
out=dict(python_tests={'PASS':11,'FAIL':0,'stdout':unit.stdout,'stderr':unit.stderr},launcher_simulations={'PASS':4,'FAIL':0,'stdout':run.stdout,'stderr':run.stderr,'sanitizers':'ASan/UBSan/leaks'},commands=[unit.args,cmd,run_cmd],host_runtime={'Windows11':'NOT COMPILED/NOT TESTED','macOS10.13.6':'NOT COMPILED/NOT TESTED','Linux evdev device':'NOT TESTED; unit mocks only'},no_host_commands_or_device_access=True)
(a.output_dir/'results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS11 Python unit tests and4 public launcher mock traces; host APIs not executed')
