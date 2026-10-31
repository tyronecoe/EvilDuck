# Additive H1 right-modifier runner; parent SHA256 9188440ad19755057d0e69e18bc67c087adc03448395409aeed8e35663d8d4d2
# Pinned additive H1 experiment over lock-wait composed runner.
# Parent SHA256: 7344b2ded53131a1da7d331733533e453bc119a3164cc23d30812e5d1753121e
"""Experimental H1 cases plus all492 candidate-adapted lock-wait regressions.
Historical files remain unchanged; only generated copies and test-only access differ.
"""
import ast,hashlib,importlib.util,json,pathlib,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
assert hashlib.sha256((ROOT/'tests/source_text_v2/run_tests.py').read_bytes()).hexdigest()=='4733a2db7faab68a6b0524f695d77cbe9f454bb55bd1b6bba7d46fcc0147f1b5'
TIMEOUT_PARENT_DRIVER_PIN='8f1a02ee30c8930c3534a28d1e956d0d20d3b6ec26badbf4c60d7872800eee02'
assert hashlib.sha256((ROOT/'tests/text_keyboard/run_tests.py').read_bytes()).hexdigest()=='69151e4341cfde41ef1967bb0040fda53483412ec76551b0f13ce1a3a5b5f0e2'
PAYLOAD_DRIVER_PIN='a5977c2424f0840cf98c3f565370c1d2a4b30653397e8ef3a441ac8f4012b337'
assert hashlib.sha256((ROOT/'tests/payload_restart/run_tests.py').read_bytes()).hexdigest()=='97f32bfb1ae3fb09343adf4ea74df79fe01fc0f4ac07e6f4b5e27802fdb5709b'
SOURCE_DRIVER_PIN='621b29e3d47da5190d9bebe8ae4309f1b57ce1266116794ed981dc7ff6790006'
PARENT=ROOT/'tests/lock_feedback/run_tests.py'
# The wrapper preserves the complete existing runner and only adds this overlay,
# test driver/case selection and generated test-only build identity substitutions.
UPPER_DRIVER_PIN='84b6f34729ca98e4986fb9c22a375c456c88479fc353f568feccb93aa42c4457'
RANDOM_DRIVER_PIN='a263a99d65eeb68bbcb006f76766a14584d07b42e4bd9483be2c0313d1abd6f9'
PIN='e7322e1b529039a07e0ec2545d94fa0a1d8db87a74c6b87f1bc126e4366d5df5'
HISTORICAL_INPUT_PINS={'tests/random_lowercase/test_main.cpp': '9ece62cd9bc9c16a92a7930cfc5571a6be0c7285e3ef7b5988e7b9ddfdcc5314', 'tests/source_compat/test_main.cpp': '14617da0ba83bca807223aec6a5db6f80d0b4ae1153628ac6e6dc4e404cfa3d9', 'tests/lock_feedback/test_main.cpp': 'e18d33da1b009820fc96c80049c42046ef684ce0f68e01e15c2660dbd24b528e', 'tests/random_lowercase/esp_random_mock.h': '1e4e6f6295d161674b8acc1c85ab94ba9ef0e646ce9dde8f8751efb550ff4d37'}
for name,expected in HISTORICAL_INPUT_PINS.items():
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name

def core_probe(command, source, output):
 original=list(command)
 cmd=[v for v in original if not v.endswith('.cpp')]
 i=cmd.index('-o');del cmd[i:i+2]
 binary=pathlib.Path(output).parent/'core-edge-probe'
 cmd+=['-o',str(binary),str(ROOT/'tests/inject_var_experimental/core_edge_probe.cpp'),str(pathlib.Path(source)/'core.cpp')]
 compile_result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 record=dict(command=cmd,compile_exit=compile_result.returncode,compile_stdout=compile_result.stdout,compile_stderr=compile_result.stderr,source_sha256=hashlib.sha256((ROOT/'tests/inject_var_experimental/core_edge_probe.cpp').read_bytes()).hexdigest(),hardware=False,scope='Actual core uninitialized-variable and cached-operand fault probes; separate from composed-module counts')
 if compile_result.returncode:
  record.update(status='FAIL');return record
 import os
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
 result=subprocess.run([str(binary)],env=env,capture_output=True,text=True,timeout=30)
 record.update(exit=result.returncode,stdout=result.stdout,stderr=result.stderr,status='PASS' if result.returncode==0 else 'FAIL',checks=2 if result.returncode==0 else 0)
 return record

def main():
 assert hashlib.sha256((ROOT/'tests/inject_var_experimental/run_tests.py').read_bytes()).hexdigest()=='9188440ad19755057d0e69e18bc67c087adc03448395409aeed8e35663d8d4d2'
 assert hashlib.sha256((ROOT/'tests/lock_wait_timeout/run_tests.py').read_bytes()).hexdigest()=='7344b2ded53131a1da7d331733533e453bc119a3164cc23d30812e5d1753121e'
 text=PARENT.read_text();assert hashlib.sha256(text.encode()).hexdigest()==PIN
 spec=importlib.util.spec_from_file_location('source_compat_prepare',ROOT/'tests/source_text_v2/prepare_sources.py');layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
 cases=['AD%02d'%i for i in range(1,37)]
 old='lock.delta(source_dir)';assert text.count(old)==1
 text=text.replace(old,old+'\n        source_delta(source_dir, command)')
 text=text.replace('keyboard_before_compile=before_compile)', 'keyboard_before_compile=lambda s,c: source_finalize(before_compile,s,c))')
 assert text.count('"tests/lock_feedback/test_main.cpp"')==1
 text=text.replace('"tests/lock_feedback/test_main.cpp"','"tests/h1_right_modifiers/test_main.cpp"')
 tree=ast.parse(text)
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NEW' for t in node.targets):node.value=ast.parse(repr(cases),mode='eval').body
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REGRESSION' for t in node.targets):node.value=ast.BinOp(left=ast.parse(repr(['AC%02d'%i for i in range(1,31)]+['AB%02d'%i for i in range(1,36)]+['AA%02d'%i for i in range(1,23)]+['Z%02d'%i for i in range(1,33)]+['Y%02d'%i for i in range(1,33)]+['V%02d'%i for i in range(1,41)]+['T%02d'%i for i in range(1,47)]+['U%02d'%i for i in range(1,35)]+['R%02d'%i for i in range(1,31)]+['P%02d'%i for i in range(1,38)]+['N%02d'%i for i in range(1,45)]),mode='eval').body,op=ast.Add(),right=node.value)
 ast.fix_missing_locations(tree)
 guards=[];timeout_guards=[];h1_guards=[];right_guards=[]
 def source_delta(source,cmd):
  layer.B.B.B.B.B.B.B.delta(source);layer.B.B.B.B.B.B.delta(source);layer.B.B.B.B.B.delta(source);layer.B.B.B.B.delta(source);layer.B.B.B.delta(source);layer.B.B.delta(source);layer.B.delta(source);layer.delta(source);cmd.insert(1,'-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_RANDOM_LOWERCASE=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_RANDOM_UPPERCASE=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_RANDOMIZATION_JITTER=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_TEXT_KEYBOARD=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_PAYLOAD_RESTART=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_SOURCE_TEXT=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_SOURCE_TEXT_V2=1')
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-FEEDBACK-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-PREPROCESS-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-RANDOM-LOWER-','ROUTEB-RANDOM-UPPER-').replace('ROUTEB-RANDOM-UPPER-20261025-v1','ROUTEB-RANDOMIZATION-JITTER-v1').replace('ROUTEB-RANDOM-UPPER-','ROUTEB-RANDOMIZATION-JITTER-').replace('ROUTEB-RANDOMIZATION-JITTER-','ROUTEB-TEXT-KEYBOARD-').replace('ROUTEB-TEXT-KEYBOARD-','ROUTEB-PAYLOAD-RESTART-').replace('ROUTEB-PAYLOAD-RESTART-','ROUTEB-SOURCE-TEXT-PORTABILITY-').replace('ROUTEB-SOURCE-TEXT-PORTABILITY-v1','ROUTEB-SOURCE-TEXT-PORTABILITY-v2'))
  (source/'esp_random.h').write_text((ROOT/'tests/random_lowercase/esp_random_mock.h').read_text())
  extra=(ROOT/'tests/source_compat/test_main.cpp').read_text();assert extra.count('int main(int argc,char**argv)')==1
  (source/'source_parent_cases.inc').write_text(extra.replace('int main(int argc,char**argv)','int source_compat_main(int argc,char**argv)'))
  parent=(ROOT/'tests/lock_feedback/test_main.cpp').read_text();assert parent.count('int main(int argc,char**argv)')==1
  (source/'lock_parent_cases.inc').write_text(parent.replace('int main(int argc,char**argv)','int lock_feedback_main(int argc,char**argv)'))
  historical=(ROOT/'tests/random_lowercase/test_main.cpp').read_text()
  obsolete='"RANDOM_UPPERCASE_LETTER\\n",'
  assert historical.count(obsolete)==1
  historical=historical.replace(obsolete,'').replace('int main(int argc,char**argv)','int random_lowercase_main(int argc,char**argv)')
  for obsolete in ['"RANDOM_NUMBER\\n",','"RANDOM_CHAR\\n",']:
   assert historical.count(obsolete)==1;historical=historical.replace(obsolete,'')
  (source/'lowercase_parent_cases.inc').write_text(historical)
  upper=(ROOT/'tests/random_uppercase/test_main.cpp').read_text()
  assert hashlib.sha256(upper.encode()).hexdigest()==UPPER_DRIVER_PIN
  for obsolete in ['"RANDOM_NUMBER\\n",','"RANDOM_CHAR\\n",']:
   assert upper.count(obsolete)==1;upper=upper.replace(obsolete,'')
  (source/'uppercase_parent_cases.inc').write_text(upper.replace('int main(int argc,char**argv)','int random_uppercase_main(int argc,char**argv)'))
  original=(ROOT/'tests/randomization_jitter/test_main.cpp').read_bytes()
  assert hashlib.sha256(original).hexdigest()==RANDOM_DRIVER_PIN
  (source/'random_parent_cases.inc').write_text(original.decode().replace('int main(int argc,char** argv)','int randomization_jitter_main(int argc,char** argv)'))
  original=(ROOT/'tests/text_keyboard/test_main.cpp').read_bytes()
  assert hashlib.sha256(original).hexdigest()=='6ccfad5a58fe6ab48062cbde684aef853fbaf0e4eb54c585203f504e7cc869a8'
  (source/'text_keyboard_parent_cases.inc').write_text(original.decode().replace('int main(int argc,char** argv)','int text_keyboard_main(int argc,char** argv)'))
  original=(ROOT/'tests/payload_restart/test_main.cpp').read_bytes()
  assert hashlib.sha256(original).hexdigest()==PAYLOAD_DRIVER_PIN
  (source/'payload_restart_parent_cases.inc').write_text(original.decode().replace('int main(int argc,char** argv)','int payload_restart_main(int argc,char** argv)'))
  # Only obsolete feature refusals change, in disposable generated copies.
  f=source/'source_parent_cases.inc';v=f.read_text()
  old='rejected(bom);check(route_u::status().reason==route_u::Reason::Capability,"existing composed ASCII admission rejects BOM before compiler");'
  assert v.count(old)==1;v=v.replace(old,'completed(bom);onlyA();');f.write_text(v)
  f=source/'text_keyboard_parent_cases.inc';v=f.read_text()
  for old in ['"STRINGLN_HTML a\\n",','"STRING_PYTHON a\\n",']:
   assert v.count(old)==1;v=v.replace(old,'')
  old='rejected("\\xef\\xbb\\xbfSTRING_HTML\\na\\nEND_STRING\\n");check(lower::count==0,"production adapter ASCII/BOM boundary remains unchanged");'
  assert v.count(old)==1;v=v.replace(old,'completed("\\xef\\xbb\\xbfSTRING_HTML\\na\\nEND_STRING\\n");oneA();');f.write_text(v)
  original=(ROOT/'tests/source_text/test_main.cpp').read_bytes()
  assert hashlib.sha256(original).hexdigest()==SOURCE_DRIVER_PIN
  original=original.decode().replace('int main(int argc,char** argv)','int source_text_main(int argc,char** argv)')
  old='=="a END_STRINGb END_STRINGLN\\n","ordinary inline alias extension does not strip official-looking terminator text"'
  assert original.count(old)==1
  original=original.replace(old,'=="ab\\n","v2 matching terminated alias syntax takes precedence"')
  (source/'source_text_parent_cases.inc').write_text(original)
  timeout_spec=importlib.util.spec_from_file_location('lock_timeout_prepare',ROOT/'tests/lock_wait_timeout/prepare_sources.py');timeout_layer=importlib.util.module_from_spec(timeout_spec);timeout_spec.loader.exec_module(timeout_layer)
  timeout_layer.delta(source);cmd.insert(1,'-DEVILDUCK_ROUTE_B_LOCK_WAIT_TIMEOUT=1');cmd.insert(1,'-fno-access-control')
  spec=importlib.util.spec_from_file_location('inject_h1_prepare',ROOT/'tests/inject_var_experimental/prepare_sources.py');h1=importlib.util.module_from_spec(spec);spec.loader.exec_module(h1)
  h1.delta(source);cmd.insert(1,'-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1')
  spec=importlib.util.spec_from_file_location('right_modifier_prepare',ROOT/'tests/h1_right_modifiers/prepare_sources.py');right=importlib.util.module_from_spec(spec);spec.loader.exec_module(right)
  right.delta(source);cmd.insert(1,'-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1')
  old_driver=(ROOT/'tests/inject_var_experimental/test_main.cpp').read_text()
  assert old_driver.count('int main(int argc,char**argv)')==1
  (source/'h1_parent_cases.inc').write_text(old_driver.replace('int main(int argc,char**argv)','int inject_var_h1_main(int argc,char**argv)'))
  negative_right=[v for v in cmd if not v.endswith('.cpp') and v!='-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1'];idx=negative_right.index('-o');del negative_right[idx:idx+2];negative_right+=['-E',str(source/'core.cpp')]
  for label,flag in [('right-missing',[]),('right-zero',['-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=0'])]:
   rejection=subprocess.run(negative_right+flag,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=30)
   assert rejection.returncode and 'Explicit H1 right-modifier candidate profile required' in rejection.stderr
   right_guards.append(dict(selector=label,result='EXPECTED_REJECTION',exit=rejection.returncode))

  driver=(ROOT/'tests/lock_wait_timeout/test_main.cpp').read_bytes()
  assert hashlib.sha256(driver).hexdigest()=='913ce8c241edaf882f7f5846620432f9d2771ed08f4fc68769f9863b07cd1409'
  (source/'timeout_parent_cases.inc').write_text(driver.decode().replace('int main(int argc,char**argv)','int lock_timeout_main(int argc,char**argv)'))
  # New opt-in support supersedes only these old compile-refusal vectors.
  for name in ['lowercase_parent_cases.inc','uppercase_parent_cases.inc']:
   f=source/name;v=f.read_text()
   for old in ['"VAR $x=1234\\nINJECT_VAR $x\\n",','"VAR $x=$_RANDOM_LOWER_LETTER_KEYCODE\\n"']:
    assert v.count(old)==1,(name,old);v=v.replace(old,'')
   f.write_text(v)
  negative=[v for v in cmd if not v.endswith('.cpp') and v!='-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1'];idx=negative.index('-o');del negative[idx:idx+2];negative+=['-E',str(source/'core.cpp')]
  for label,flag in [('h1-missing',[]),('h1-zero',['-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=0'])]:
   r=subprocess.run(negative+flag,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=30)
   assert r.returncode and 'Explicit experimental INJECT_VAR H1 profile required' in r.stderr
   h1_guards.append(dict(selector=label,result='EXPECTED_REJECTION',exit=r.returncode))

  prior=(ROOT/'tests/source_text_v2/test_main.cpp').read_bytes();assert hashlib.sha256(prior).hexdigest()==TIMEOUT_PARENT_DRIVER_PIN
  (source/'source_text_v2_parent_cases.inc').write_text(prior.decode().replace('int main(int argc,char** argv)','int source_text_v2_main(int argc,char** argv)'))
  negative_base=[v for v in cmd if not v.endswith('.cpp') and v!='-DEVILDUCK_ROUTE_B_LOCK_WAIT_TIMEOUT=1'];idx=negative_base.index('-o');del negative_base[idx:idx+2];negative_base+=['-E',str(source/'core.cpp')]
  for label,flag in [('timeout-missing',[]),('timeout-zero',['-DEVILDUCK_ROUTE_B_LOCK_WAIT_TIMEOUT=0'])]:
   r=subprocess.run(negative_base+flag,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=30)
   assert r.returncode and 'Explicit Route B lock-wait-timeout candidate profile required' in r.stderr
   timeout_guards.append(dict(selector=label,result='EXPECTED_REJECTION',exit=r.returncode))
  base=[v for v in cmd if not v.endswith('.cpp') and v!='-DEVILDUCK_ROUTE_B_SOURCE_TEXT_V2=1'];idx=base.index('-o');del base[idx:idx+2];base+=['-E',str(source/'core.cpp')]
  for label,flag in [('missing',[]),('zero',['-DEVILDUCK_ROUTE_B_SOURCE_TEXT_V2=0'])]:
   r=subprocess.run(base+flag,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=30)
   assert r.returncode and 'Explicit Route B source-text-v2 candidate profile required' in r.stderr
   guards.append(dict(selector=label,result='EXPECTED_REJECTION',exit=r.returncode))
 def source_finalize(callback,source,command):
  callback(source,command)
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-SOURCE-TEXT-PORTABILITY-v2','ROUTEB-LOCK-WAIT-TIMEOUT-v1').replace('ROUTEB-SOURCE-TEXT-PORTABILITY-','ROUTEB-LOCK-WAIT-TIMEOUT-'))
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-FEEDBACK-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-PREPROCESS-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-RANDOM-LOWER-','ROUTEB-RANDOM-UPPER-').replace('ROUTEB-RANDOM-UPPER-20261025-v1','ROUTEB-RANDOMIZATION-JITTER-v1').replace('ROUTEB-RANDOM-UPPER-','ROUTEB-RANDOMIZATION-JITTER-').replace('ROUTEB-RANDOMIZATION-JITTER-','ROUTEB-TEXT-KEYBOARD-').replace('ROUTEB-TEXT-KEYBOARD-','ROUTEB-PAYLOAD-RESTART-').replace('ROUTEB-PAYLOAD-RESTART-','ROUTEB-SOURCE-TEXT-PORTABILITY-').replace('ROUTEB-SOURCE-TEXT-PORTABILITY-v1','ROUTEB-SOURCE-TEXT-PORTABILITY-v2'))
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-SOURCE-TEXT-PORTABILITY-v2','ROUTEB-LOCK-WAIT-TIMEOUT-v1').replace('ROUTEB-SOURCE-TEXT-PORTABILITY-','ROUTEB-LOCK-WAIT-TIMEOUT-'))
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-WAIT-TIMEOUT-v1','ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1').replace('ROUTEB-LOCK-WAIT-TIMEOUT-','ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-'))
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1','ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1').replace('ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-','ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-'))
 ns=dict(__name__='__main__',__file__=str(__file__),source_delta=source_delta,source_finalize=source_finalize)
 code=0
 try:exec(compile(tree,str(PARENT),'exec'),ns)
 except SystemExit as e:code=e.code if isinstance(e.code,int) else 1
 path=pathlib.Path(sys.argv[sys.argv.index('--results')+1]);result=json.loads(path.read_text());result['right_modifiers']=result.pop('lock_feedback');result['right_selector_negative_controls']=right_guards;result['h1_selector_negative_controls']=h1_guards;result['hypothesis_limits']='H1 scalar is an explicit EvilDuck policy, not observed official runtime encoding; independent HID/US mapping expectations test downstream reports only';result['h1_superseded_refusals']='Generated R06/U06 remove stored1234 injection compile refusal and supported lower getter assignment; new AC cases separately cover runtime invalid encoding and supported capture. Historical sources remain unchanged.';result['timeout_selector_negative_controls']=timeout_guards;result['timeout_generated_identity_adaptation']='Generated include copies replace both exact v2 build ID and generic ROUTEB-SOURCE-TEXT-PORTABILITY- prefix with the new candidate identity. Native-v2 D12 failure exposed the initially missed generic prefix; its historical assertion and other checks remain unchanged.';result['test_access_control']='Native-only -fno-access-control permits direct fault injection into actual private Adapter methods/state; target builds retain normal access control.';result['source_selector_negative_controls']=guards;result['lock_runner_sha256']=PIN
 result['historical_timeout_development_diagnostics']=[dict(run='native-v1',kind='test-driver-compile-error',detail='unused lambda parameter under unchanged -Werror; parameter name removed'),dict(run='native-v2',counts=dict(PASS=491,FAIL=1),failure='D12 generated include still expected generic prior source/text build prefix; fixed candidate identity adaptation only; partial result retained separately')];
 result['development_diagnostics']=[dict(run='native-v1',counts=dict(PASS=521,FAIL=1),failure='AC30 reused prior UpperProvider sink that requires Character/A; experimental KeyTap correctly triggered its assertion and exception allocation. Corrected test sink checks exact KeyTap/usage4 and retains allocation assertion; production source unchanged.')]
 if code==0:
  result['core_edge_probe']=core_probe(result['command'],pathlib.Path(sys.argv[sys.argv.index('--build-dir')+1])/'sources',path)
  if result['core_edge_probe']['status']!='PASS':code=1
 result['historical_V14_provenance_gap']=dict(historical_assertions=53,fresh_assertions=79,additional_assertions=26,explanation='Historical text-keyboard native binary omitted the late held-key/jitter V14 branch despite a later executable timestamp; the unchanged historical driver contains it. This fresh run executes it. Historical files/receipts remain unchanged; no regression expectation was weakened.')
 result['historical_R27_adaptation']='Generated copies only: R27/U27 remove now-implemented character commands; RANDOM_SEED rejection retained; historical files unchanged';result['superseded_expectations']=['P14 generated BOM refusal replaced by composed acceptance','V11 generated BOM refusal replaced by composed acceptance','V06 generated inline STRING_PYTHON/STRINGLN_HTML refusals removed; remaining malformed block cases retained'];result['profile']='ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1';result['v2_superseded_expectation']='Generated Z12 terminated aliases now emit payload without closers; historical file unchanged';path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['counts','assertions','right_modifiers','selected_unchanged_regressions','sanitizers']},indent=2))
 return code
def default_probe():
 import argparse,os
 parser=argparse.ArgumentParser(description='Exact unchanged default vocabulary probe, no hardware')
 parser.add_argument('--default-probe',action='store_true');parser.add_argument('--header',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True)
 a=parser.parse_args();assert not a.output.exists()
 pin=json.loads((ROOT/'tests/h1_right_modifiers/source-manifest.json').read_text())
 expected=next(v['sha256'] for v in pin['before'] if v['file']=='shortcut_keys.h')
 data=a.header.read_bytes();assert hashlib.sha256(data).hexdigest()==expected
 header=a.output.parent/'default-probe-shortcut_keys.h';header.write_bytes(data)
 code='#include "default-probe-shortcut_keys.h"\n#include <stdio.h>\nint main(){const char* names[]={"CTRL","CONTROL","SHIFT","ALT","OPTION","GUI","WINDOWS","COMMAND","RCTRL","RSHIFT","RALT","RGUI"};const unsigned expected[]={1,1,2,4,4,8,8,8,0,0,0,0};for(unsigned i=0;i<12;++i)if(ds_shortcut::modifier(names[i])!=expected[i])return 1;uint8_t u=0,m=0;if(!ds_shortcut::mapUS(65,u,m)||u!=4||m!=2)return 2;if(!ds_shortcut::mapUS(97,u,m)||u!=4||m!=0)return 3;puts("PASS unchanged-default-vocabulary (14 checks)");}\n'
 source=a.output.parent/'default-probe.cpp';source.write_text(code);binary=a.output.parent/'default-probe'
 command=['g++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-g','-O1','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1',str(source),'-o',str(binary)]
 compiled=subprocess.run(command,capture_output=True,text=True,timeout=60)
 record=dict(scope='Unchanged shared production vocabulary from before right overlay; no default firmware build',header_sha256=expected,source=code,command=command,compile_exit=compiled.returncode,compile_stdout=compiled.stdout,compile_stderr=compiled.stderr,hardware=False)
 if compiled.returncode==0:
  result=subprocess.run([str(binary)],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'),capture_output=True,text=True,timeout=30)
  record.update(exit=result.returncode,stdout=result.stdout,stderr=result.stderr,status='PASS' if result.returncode==0 else 'FAIL',checks=14 if result.returncode==0 else 0)
 else:record['status']='FAIL'
 a.output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));return 0 if record['status']=='PASS' else 1

def syntax_probe():
 import argparse,os
 parser=argparse.ArgumentParser(description='Actual candidate-core syntax edge probe; no transport')
 parser.add_argument('--syntax-probe',action='store_true');parser.add_argument('--native-results',type=pathlib.Path,required=True);parser.add_argument('--source',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True)
 a=parser.parse_args();assert not a.output.exists()
 parent=json.loads(a.native_results.read_text());original=parent['command'];cmd=[v for v in original if not v.endswith('.cpp')];i=cmd.index('-o');del cmd[i:i+2]
 source=a.output.parent/'syntax-edge-probe.cpp';binary=a.output.parent/'syntax-edge-probe'
 code=r'''#include "core.h"
#include <stdio.h>
#include <string.h>
struct Capture {ds_preview::Event events[32]{};unsigned n=0;static ds_preview::Accept sink(void*c,const ds_preview::Event&e){auto& p=*static_cast<Capture*>(c);if(p.n>=32)return ds_preview::Accept::Failed;p.events[p.n++]=e;return ds_preview::Accept::Accepted;}};
int main(){ds_preview::Program p;ds_preview::Runtime rt;Capture c;const char*src="REPEAT 2 RSHIFT a\nSTRING RSHIFT\nSTRINGLN RSHIFT\n";if(!p.compile(src,strlen(src))||!rt.start(p,Capture::sink,&c))return 1;for(unsigned i=0;i<1000&&rt.state()==ds_preview::State::Running;++i)rt.tick(i);if(rt.state()!=ds_preview::State::Completed||c.n!=15)return 2;for(unsigned i=0;i<2;++i)if(c.events[i].type!=ds_preview::EventType::KeyTap||c.events[i].value!=4||c.events[i].modifiers!=32)return 3;const char*literal="RSHIFTRSHIFT";for(unsigned i=0;i<12;++i)if(c.events[i+2].type!=ds_preview::EventType::Character||c.events[i+2].value!=unsigned(literal[i]))return 4;if(c.events[14].type!=ds_preview::EventType::KeyTap||c.events[14].value!=40||c.events[14].modifiers)return 5;const char*bad="STRING BAD\nREPEAT 2 RSHIFT RSHIFT a\n";if(p.compile(bad,strlen(bad)))return 6;puts("PASS inline-repeat/literal-text/preflight (3 checks)");}
'''
 source.write_text(code);cmd+=['-o',str(binary),str(source),str(a.source/'core.cpp')]
 compiled=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 record=dict(scope='Actual candidate compiler/runtime events only; no adapter/backend execution in this separate probe',command=cmd,source=code,core_sha256=hashlib.sha256((a.source/'core.cpp').read_bytes()).hexdigest(),compile_exit=compiled.returncode,compile_stdout=compiled.stdout,compile_stderr=compiled.stderr,hardware=False)
 if compiled.returncode==0:
  result=subprocess.run([str(binary)],env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'),capture_output=True,text=True,timeout=30)
  record.update(exit=result.returncode,stdout=result.stdout,stderr=result.stderr,status='PASS' if result.returncode==0 else 'FAIL',checks=3 if result.returncode==0 else 0)
 else:record['status']='FAIL'
 a.output.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));return 0 if record['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(default_probe() if '--default-probe' in sys.argv else syntax_probe() if '--syntax-probe' in sys.argv else main())
