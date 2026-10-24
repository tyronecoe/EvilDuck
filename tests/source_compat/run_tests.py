"""Composed compiler regressions on actual modules; mocked transport/storage only."""
import ast,hashlib,importlib.util,json,pathlib,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT=ROOT/'tests/lock_feedback/run_tests.py'
# The wrapper preserves the complete existing runner and only adds this overlay,
# test driver/case selection and generated test-only build identity substitutions.
PIN='e7322e1b529039a07e0ec2545d94fa0a1d8db87a74c6b87f1bc126e4366d5df5'

def main():
 text=PARENT.read_text();assert hashlib.sha256(text.encode()).hexdigest()==PIN
 spec=importlib.util.spec_from_file_location('source_compat_prepare',ROOT/'tests/source_compat/prepare_sources.py');layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
 cases=['P%02d'%i for i in range(1,38)]
 old='lock.delta(source_dir)';assert text.count(old)==1
 text=text.replace(old,old+'\n        source_delta(source_dir, command)')
 text=text.replace('keyboard_before_compile=before_compile)', 'keyboard_before_compile=lambda s,c: source_finalize(before_compile,s,c))')
 assert text.count('"tests/lock_feedback/test_main.cpp"')==1
 text=text.replace('"tests/lock_feedback/test_main.cpp"','"tests/source_compat/test_main.cpp"')
 tree=ast.parse(text)
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NEW' for t in node.targets):node.value=ast.parse(repr(cases),mode='eval').body
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REGRESSION' for t in node.targets):node.value=ast.BinOp(left=ast.parse(repr(['N%02d'%i for i in range(1,45)]),mode='eval').body,op=ast.Add(),right=node.value)
 ast.fix_missing_locations(tree)
 guards=[]
 def source_delta(source,cmd):
  layer.delta(source);cmd.insert(1,'-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1')
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-FEEDBACK-','ROUTEB-PREPROCESS-'))
  parent=(ROOT/'tests/lock_feedback/test_main.cpp').read_text();assert parent.count('int main(int argc,char**argv)')==1
  (source/'lock_parent_cases.inc').write_text(parent.replace('int main(int argc,char**argv)','int lock_feedback_main(int argc,char**argv)'))
  base=[v for v in cmd if not v.endswith('.cpp') and v!='-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1'];idx=base.index('-o');del base[idx:idx+2];base+=['-E',str(source/'core.cpp')]
  for label,flag in [('missing',[]),('zero',['-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=0'])]:
   r=subprocess.run(base+flag,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,timeout=30)
   assert r.returncode and 'Explicit Route B source-compat candidate profile required' in r.stderr
   guards.append(dict(selector=label,result='EXPECTED_REJECTION',exit=r.returncode))
 def source_finalize(callback,source,command):
  callback(source,command)
  for f in source.glob('*_cases.inc'):f.write_text(f.read_text().replace('ROUTEB-LOCK-FEEDBACK-','ROUTEB-PREPROCESS-'))
 ns=dict(__name__='__main__',__file__=str(__file__),source_delta=source_delta,source_finalize=source_finalize)
 code=0
 try:exec(compile(tree,str(PARENT),'exec'),ns)
 except SystemExit as e:code=e.code if isinstance(e.code,int) else 1
 path=pathlib.Path(sys.argv[sys.argv.index('--results')+1]);result=json.loads(path.read_text());result['source_compat']=result.pop('lock_feedback');result['source_selector_negative_controls']=guards;result['lock_runner_sha256']=PIN
 result['profile']='ROUTEB-PREPROCESS-20261024-v1';path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['counts','assertions','source_compat','selected_unchanged_regressions','sanitizers']},indent=2))
 return code
if __name__=='__main__':raise SystemExit(main())
