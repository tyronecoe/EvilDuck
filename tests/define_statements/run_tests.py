"""Focused host-only tests; reconstruct and hash-check composed modules, no firmware build."""
import pathlib,subprocess,re,hashlib,json
import sys
sys.dont_write_bytecode = True
r=pathlib.Path(__file__).resolve().parents[2]
import argparse,importlib.util,os
p=argparse.ArgumentParser();p.add_argument('--output-dir',type=pathlib.Path,required=True);a=p.parse_args()
out=a.output_dir.resolve();assert not out.exists() and not out.is_relative_to(r);out.mkdir(parents=True)
for n in ['core.cpp','core.h']:(out/n).write_bytes((r/'language_preview'/n).read_bytes())
paths=['keyboard_shortcuts/shortcuts.patch']+[p+'/application.patch' for p in ['keyboard_control','lock_feedback','source_compat','random_lowercase','random_uppercase','randomization_jitter','text_keyboard','payload_restart','source_text','source_text_v2','lock_wait_timeout','inject_var_experimental','h1_right_modifiers','previous_command_repeat','del_alias','define_labels']]
for p in paths:
 text=(r/'tests'/p).read_text();sections=re.split(r'(?m)(?=^--- )',text)
 selected=''.join(s for s in sections if s.startswith('--- ') and s.splitlines()[1][4:] in ['core.cpp','core.h','shortcut_keys.h'])
 if selected:subprocess.run(['patch','--batch','--fuzz=0','-p0'],input=selected,text=True,cwd=out,check=True,capture_output=True)
inv=json.loads((r/'docs/admission-diagnostics-source-inventory.json').read_text())['final_source_inventory']
for n in ['core.cpp','core.h','shortcut_keys.h']:
 assert hashlib.sha256((out/n).read_bytes()).hexdigest()==next(x['sha256'] for x in inv if x['file']=='EvilDuckS3/'+n),n

spec=importlib.util.spec_from_file_location('feature',r/'tests/define_statements/prepare_sources.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.delta(out)
command=['g++','-std=c++17','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1','-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1','-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1','-I'+str(out),str(out/'core.cpp'),str(r/'tests/define_statements/test_main.cpp'),'-o',str(out/'focused')]
command[1:1]=['-D'+flag+'=1' for flag in ['EVILDUCK_ROUTE_B_'+name for name in ['LOCK_WAIT_TIMEOUT','SOURCE_TEXT_V2','SOURCE_TEXT','PAYLOAD_RESTART','TEXT_KEYBOARD','RANDOMIZATION_JITTER','RANDOM_UPPERCASE','RANDOM_LOWERCASE','SOURCE_COMPAT','KEYBOARD_CONTROL']]]
subprocess.run(command,check=True)
subprocess.run([str(out/'focused')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
(out/'results.json').write_text(json.dumps(dict(status='PASS',command=command,core_sha256=m.sha(out/'core.cpp'),historical_tests_run=False,firmware_built=False,hardware_access=False),indent=2)+'\n')
