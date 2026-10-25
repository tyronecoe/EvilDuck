"""Composed compiler regressions on actual modules; mocked transport/storage only."""
import ast,hashlib,importlib.util,json,pathlib,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT=ROOT/'tests/lock_feedback/run_tests.py'
# The wrapper preserves the complete existing runner and only adds this overlay,
# test driver/case selection and generated test-only build identity substitutions.
UPPER_DRIVER_PIN='84b6f34729ca98e4986fb9c22a375c456c88479fc353f568feccb93aa42c4457'
PIN='e7322e1b529039a07e0ec2545d94fa0a1d8db87a74c6b87f1bc126e4366d5df5'
HISTORICAL_INPUT_PINS={'tests/random_lowercase/test_main.cpp': '9ece62cd9bc9c16a92a7930cfc5571a6be0c7285e3ef7b5988e7b9ddfdcc5314', 'tests/source_compat/test_main.cpp': '14617da0ba83bca807223aec6a5db6f80d0b4ae1153628ac6e6dc4e404cfa3d9', 'tests/lock_feedback/test_main.cpp': 'e18d33da1b009820fc96c80049c42046ef684ce0f68e01e15c2660dbd24b528e', 'tests/random_lowercase/esp_random_mock.h': '1e4e6f6295d161674b8acc1c85ab94ba9ef0e646ce9dde8f8751efb550ff4d37'}
for name,expected in HISTORICAL_INPUT_PINS.items():
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name

def main():
 text=PARENT.read_text();assert hashlib.sha256(text.encode()).hexdigest()==PIN
 spec=importlib.util.spec_from_file_location('source_compat_prepare',ROOT/'tests/randomization_jitter/prepare_sources.py');layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
 cases=['T%02d'%i for i in range(1,47)]
 old='lock.delta(source_dir)';assert text.count(old)==1
 text=text.replace(old,old+'\n        source_delta(source_dir, command)')
 text=text.replace('keyboard_before_compile=before_compile)', 'keyboard_before_compile=lambda s,c: source_finalize(before_compile,s,c))')
 assert text.count('"tests/lock_feedback/test_main.cpp"')==1
 text=text.replace('"tests/lock_feedback/test_main.cpp"','"tests/randomization_jitter/test_main.cpp"')
 tree=ast.parse(text)
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NEW' for t in node.targets):node.value=ast.parse(repr(cases),mode='eval').body
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REGRESSION' for t in node.targets):node.value=ast.BinOp(left=ast.parse(repr(['U%02d'%i for i in range(1,35)]+['R%02d'%i for i in range(1,31)]+['P%02d'%i for i in range(1,38)]+['N%02d'%i for i in range(1,45)]),mode='eval').body,op=ast.Add(),right=node.value)
 ast.fix_missing_locations(tree)
 guards=[]
 def source_delta(source,cmd):
  layer.B.B.B.delta(source);layer.B.B.delta(source);layer.B.delta(source);layer.delta(source);cmd.insert(1,'-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_RANDOM_LOWERCASE=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_RANDOM_UPPERCASE=1');cmd.insert(1,'-DEVILDUCK_ROUTE_B_RANDOMIZATION_JITTER=1')
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-FEEDBACK-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-PREPROCESS-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-RANDOM-LOWER-','ROUTEB-RANDOM-UPPER-').replace('ROUTEB-RANDOM-UPPER-20261025-v1','ROUTEB-RANDOMIZATION-JITTER-v1').replace('ROUTEB-RANDOM-UPPER-','ROUTEB-RANDOMIZATION-JITTER-'))
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
  base=[v for v in cmd if not v.endswith('.cpp') and v!='-DEVILDUCK_ROUTE_B_RANDOMIZATION_JITTER=1'];idx=base.index('-o');del base[idx:idx+2];base+=['-E',str(source/'core.cpp')]
  for label,flag in [('missing',[]),('zero',['-DEVILDUCK_ROUTE_B_RANDOMIZATION_JITTER=0'])]:
   r=subprocess.run(base+flag,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=30)
   assert r.returncode and 'Explicit Route B randomization-jitter candidate profile required' in r.stderr
   guards.append(dict(selector=label,result='EXPECTED_REJECTION',exit=r.returncode))
 def source_finalize(callback,source,command):
  callback(source,command)
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-FEEDBACK-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-PREPROCESS-','ROUTEB-RANDOM-LOWER-').replace('ROUTEB-RANDOM-LOWER-','ROUTEB-RANDOM-UPPER-').replace('ROUTEB-RANDOM-UPPER-20261025-v1','ROUTEB-RANDOMIZATION-JITTER-v1').replace('ROUTEB-RANDOM-UPPER-','ROUTEB-RANDOMIZATION-JITTER-'))
 ns=dict(__name__='__main__',__file__=str(__file__),source_delta=source_delta,source_finalize=source_finalize)
 code=0
 try:exec(compile(tree,str(PARENT),'exec'),ns)
 except SystemExit as e:code=e.code if isinstance(e.code,int) else 1
 path=pathlib.Path(sys.argv[sys.argv.index('--results')+1]);result=json.loads(path.read_text());result['randomization_jitter']=result.pop('lock_feedback');result['source_selector_negative_controls']=guards;result['lock_runner_sha256']=PIN
 result['historical_R27_adaptation']='Generated copies only: R27/U27 remove now-implemented character commands; RANDOM_SEED rejection retained; historical files unchanged';result['profile']='ROUTEB-RANDOMIZATION-JITTER-v1';path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['counts','assertions','randomization_jitter','selected_unchanged_regressions','sanitizers']},indent=2))
 return code
if __name__=='__main__':raise SystemExit(main())
