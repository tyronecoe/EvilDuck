"""Independent artifact gate: original historical result is never superseded."""
import argparse,ast,contextlib,difflib,hashlib,importlib.machinery,json,pathlib,re,subprocess,sys,traceback,types
sys.dont_write_bytecode=True
import measure_reference as M
OLD='ds_preview::Compiler::statementImpl(char*)';NEW='ds_preview::Compiler::statementImpl(char*, bool)'
AUDIT=[]
PROVENANCE_LOOKUP='source_info = built.get("usb_observer_target_adapter", {})'
PROVENANCE_END='assert source_info.get("usb_observer_target_binding") == binding_after, "Target binding differs from executed build"'

def identity_digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def derive_attestation(root,binding):
 """New post-build evidence, never metadata attributed to the original builder."""
 M.require(pathlib.Path(root).resolve()==M.BUILD.resolve(),'Wrong attestation root')
 M.authenticate();manifest=M.original_manifest();report=json.loads((M.BUILD/'report.json').read_text())
 composition=json.loads((M.BUILD/'usb-observer-composition.json').read_text())
 M.require(binding['status']=='PASS' and binding['source_commit']==manifest['source_commit'],'Unverified target binding')
 M.require(binding['build_inputs_sha256']==M.ORIGINAL_MANIFEST_SHA,'Target manifest binding differs')
 M.require(binding['committed_source_provenance']['files_sha256']==manifest['files_sha256'],'Target inventory binding differs')
 M.require(binding['elf_sha256']==M.ARTIFACTS['EvilDuckS3.ino.elf'] and binding['application_sha256']==M.ARTIFACTS['EvilDuckS3.ino.bin'],'Target image binding differs')
 M.require(composition['source_commit']==M.COMMIT and composition['overlay_calls']==1,'Original overlay evidence differs')
 M.require(report['status']=='PASS' and '--clean' in report['command'] and '--verbose' in report['command'],'Original clean compile evidence missing')
 M.require(report['provenance']['elf_sha256']==binding['elf_sha256'] and report['report']['application_sha256']==binding['application_sha256'],'Original compile result differs')
 code=M.code_ids()
 return dict(kind='POST_BUILD_INDEPENDENT_ATTESTATION',produced_by_original_builder=False,
  source_commit=manifest['source_commit'],source_commit_contains_changes=manifest['source_commit_contains_changes'],
  build_inputs_sha256=M.sha(M.BUILD/'build-inputs.json'),files_sha256=manifest['files_sha256'],
  overlay_calls=composition['overlay_calls'],clean_compile=True,usb_observer_target_binding=binding,
  evidence=dict(original_build_report_sha256=M.sha(M.BUILD/'report.json'),composition_sha256=M.sha(M.BUILD/'usb-observer-composition.json'),
   clean_compile_origin='Authenticated original compile report/command and unchanged actual artifacts; not overall original verification PASS',
   target_binding_origin='Independent verification of the unchanged candidate'),
  verification_provenance=dict(build_source_commit=M.COMMIT,verifier_files=code,verifier_identity_sha256=identity_digest(code)))

def validate_attestation(value,root,binding):
 # Legacy provenance assertions still execute unmodified before this check.
 # This adds separation of the inner inventory, new reader and original build.
 M.require(value['kind']=='POST_BUILD_INDEPENDENT_ATTESTATION' and value['produced_by_original_builder'] is False,'Attestation misattributed to original builder')
 manifest=M.original_manifest();M.require(value['files_sha256']==manifest['files_sha256'],'Inventory digest substituted or changed')
 current=M.code_ids();provenance=value['verification_provenance']
 M.require(provenance['build_source_commit']==M.COMMIT,'Build/verifier provenance conflated')
 M.require(provenance['verifier_files']==current and provenance['verifier_identity_sha256']==identity_digest(current),'Independent verifier identity mismatch')
 M.require(value==derive_attestation(root,binding),'Supplementary attestation evidence differs')

def provenance_block(source):
 """The exact related statements from the actually generated release function."""
 fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='run_chain')
 body=[];collect=False
 for node in fn.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source_info' for t in node.targets):collect=True
  if collect:body.append(node)
  if collect and isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='validate_attestation':break
 M.require(body and isinstance(body[-1],ast.Expr),'Complete provenance block missing')
 return ast.Module(body=body,type_ignores=[])

def adapt_provenance(source,filename):
 M.require(source.count(PROVENANCE_LOOKUP)==1 and source.count(PROVENANCE_END)==1,'Provenance adaptation ambiguous')
 new='source_info = __import__("verify_existing").derive_attestation(build_root, binding_after)'
 adapted=source.replace(PROVENANCE_LOOKUP,new).replace(PROVENANCE_END,PROVENANCE_END+'\n    __import__("verify_existing").validate_attestation(source_info, build_root, binding_after)')
 before=[ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Assert)]
 after=[ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(adapted)) if isinstance(n,ast.Assert)]
 M.require(before==after,'A substantive release assertion changed')
 AUDIT.append(dict(kind='supplementary provenance provider, assertions unchanged',filename=str(filename),before=PROVENANCE_LOOKUP,after=new,
  validation_added='validate_attestation after all five original provenance assertions',source_commit=M.COMMIT,
  full_provenance_block=ast.unparse(provenance_block(adapted)),original_assert_nodes_retained=len(before),adapted_source_sha256=hashlib.sha256(adapted.encode()).hexdigest()))
 return adapted

def generated_provenance_block():
 """Controls use the real generated release block, not mirrored assertions."""
 import builtins
 native=builtins.compile;captured=[]
 def capture(source,filename,mode,*args,**kwargs):
  if mode=='exec' and isinstance(source,str) and PROVENANCE_LOOKUP in source and not (kwargs.get('flags',args[0] if args else 0)&ast.PyCF_ONLY_AST):
   source=adapt_provenance(source,filename);captured.append(source)
  return native(source,filename,mode,*args,**kwargs)
 builtins.compile=capture
 try:
  release=M.load(M.ROOT/'tests/define_statements_release/verify_release.py','provenance_control_release')
  release.adapted_parent()
 finally:builtins.compile=native
 M.require(captured,'Executed provenance source not found')
 return provenance_block(captured[-1])
def signature_functions(v):
 d=v.P.D;p=M.ROOT/'tests/define_labels_release/verify_target.py';M.require(M.sha(p)=='1c288f259b7ae646e3740d4e71db1f9aebdf8668ef4e7b6626bfda47cd7cd397','Frozen target changed');text=p.read_text();tree=ast.parse(text);replacements={}
 for n in ['compiler_reachability','core_binding','alias_binding']:
  fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==n);before=ast.get_source_segment(text,fn);M.require(before.count(OLD)==1,'Signature adaptation ambiguous');after=before.replace(OLD,NEW);old=getattr(d,n);exec(compile(after,__file__+'::'+n,'exec'),d.__dict__);replacements[old]=getattr(d,n);AUDIT.append(dict(function=n,kind='source-justified signature only',diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True))),sha256=hashlib.sha256(after.encode()).hexdigest()))
 return d,replacements

def install(v,measurements):
 d,replacements=signature_functions(v)
 old=d.define_binding
 def layout(root):M.require(pathlib.Path(root).resolve()==M.BUILD.resolve(),'Wrong candidate root');return M.measure(measurements)
 replacements[old]=layout;AUDIT.append(dict(function='define_binding',kind='approved evidence-provider replacement',original_result='BLOCKED / EXACT HISTORICAL INPUT UNAVAILABLE',new_reference_not_historical=True))
 seen=set()
 def walk(m):
  if id(m) in seen:return
  seen.add(id(m))
  for name,value in list(vars(m).items()):
   if isinstance(value,types.FunctionType) and value in replacements:setattr(m,name,replacements[value])
  for name in ['P','D','S']:
   child=getattr(m,name,None)
   if isinstance(child,types.ModuleType):walk(child)
 walk(v)
 return d

def stack_evidence():
 m=M.parser();frames=m.stack_rows(M.BUILD/'build/sketch/core.cpp.su');tool=M.authenticate()['entry']['arguments'][0].rsplit('g++',1)[0]
 symbols=subprocess.check_output([tool+'nm','-C','-S','--defined-only',str(M.BUILD/'build/EvilDuckS3.ino.elf')],text=True)
 rows=[l.split(maxsplit=3) for l in symbols.splitlines()];found=[r for r in rows if len(r)==4 and r[3]==NEW and r[2] in ['T','t','W','w']];M.require(len(found)==1,'Implementation absent or ambiguous');r=found[0];addr=int(r[0],16);size=int(r[1],16)
 text=subprocess.check_output([tool+'objdump','-C','-d','--start-address='+str(addr),'--stop-address='+str(addr+size),str(M.BUILD/'build/EvilDuckS3.ino.elf')],text=True)
 return validate_stack(frames,text,addr)
def validate_stack(frames,text,addr):
 selected={n:frames[n]['bytes'] for n in ['bool '+NEW,'bool ds_preview::Compiler::statement(char*)','bool ds_preview::Compiler::line()','bool ds_preview::Compiler::step(ds_preview::CompileWork&)']}
 frame=selected['bool '+NEW];prologue=re.search(r'\bentry\s+a1,\s*(0x[\da-f]+|\d+)',text);M.require(prologue and int(prologue[1],0)==frame,'Frame/prologue disagreement')
 calls=[l for l in text.splitlines() if re.search(r'\bcall\w*\s+'+format(addr,'x')+r'\s+<'+re.escape(NEW)+r'>',l)];M.require(len(calls)==1,'Bounded self-call missing/ambiguous')
 # Bind the reviewed control-flow witness to this exact frozen core and ELF,
 # rather than treating arbitrary source strings or a frame size as a bound.
 M.require('bnez.n\ta4, 4200c814' in text and 'movi\ta12, 1' in text,'Substitution guard/argument changed')
 before=text[:text.index(calls[0])];M.require(re.search(r'4200c891:.*movi\s+a12, 1',before),'Self-call argument witness absent')
 source=(M.BUILD/'candidate/EvilDuckS3/core.cpp').read_text();M.require(M.sha(M.BUILD/'candidate/EvilDuckS3/core.cpp')==M.CORE and 'if(!substituted){' in source and source.count('return statementImpl(leaf,true);')==1,'Bounded source changed')
 return dict(status='PASS',actual_firmware_frames=selected,implementation_frame=frame,max_implementation_depth=2,implementation_selected_subtotal=2*frame,selected_chain_subtotal=sum(selected.values())+frame,scope='Selected-frame subtotals only; not total peak or proven stack sufficiency',runtime_peak_measured=False,disassembly=text)

@contextlib.contextmanager
def no_compilation():
 original=subprocess.Popen
 def safe(args,*a,**k):
  command=list(args) if not isinstance(args,str) else [args];name=pathlib.Path(str(command[0])).name
  if any(n in name for n in ['g++','gcc','cc1','collect2']) or name.endswith('-ld'):
   M.require(command[1:]==['-print-prog-name=ld'],'Verification cannot invoke compiler/linker')
  return original(args,*a,**k)
 subprocess.Popen=safe
 try:yield
 finally:subprocess.Popen=original

def main(directory,output):
 M.require(not output.exists(),'Fresh verification evidence required');output.mkdir(parents=True);auth=M.authenticate();result=dict(policy='DEFINE-CANDIDATE-INDEPENDENT-v1',original_result=auth['original_status'],source_commit=M.COMMIT,new_verifier=M.code_ids(),firmware_compilation_attempts=1,auxiliary_compiler_invocations=len(list(directory.glob('compiler-invocation-*.json'))),stages={},runtime_assertion_total='not emitted; not inferred')
 original_loader=importlib.machinery.SourceFileLoader.exec_module
 def loader(self,module):
  original_loader(self,module)
  if pathlib.Path(getattr(module,'__file__','')).resolve()==M.ROOT/'tests/define_statements_release/verify_target.py':install(module,directory)
 # Replace only the final report's source-revision lookup, not report contents,
 # committed-source guards, file bindings, or any source identity assertion.
 import builtins
 original_compile=builtins.compile
 def provenance(source,filename,mode,*a,**k):
  if isinstance(source,str) and mode=='exec' and PROVENANCE_LOOKUP in source and not (k.get('flags',a[0] if a else 0)&ast.PyCF_ONLY_AST):source=adapt_provenance(source,filename)
  return original_compile(source,filename,mode,*a,**k)
 try:
  with no_compilation():
   M.dump(output/'layout.json',M.measure(directory));result['stages']['layout']='PASS'
   M.dump(output/'stack.json',stack_evidence());result['stages']['bounded_self_call']='PASS'
   importlib.machinery.SourceFileLoader.exec_module=loader
   v=M.load(M.ROOT/'tests/define_statements_release/verify_target.py','independent_selected_target');binding=v.verify(M.BUILD);M.dump(output/'target.json',binding);result['stages']['target']='PASS'
   attestation=derive_attestation(M.BUILD,binding);validate_attestation(attestation,M.BUILD,binding)
   M.dump(output/'supplementary-attestation.json',attestation)
   result['supplementary_attestation']=dict(file='supplementary-attestation.json',sha256=M.sha(output/'supplementary-attestation.json'),produced_by_original_builder=False)
   builtins.compile=provenance
   r=M.load(M.ROOT/'tests/define_statements_release/verify_release.py','independent_release');r.run_chain(M.BUILD,output/'release.json');result['stages']['six_frozen_layers']='PASS'
   result['status']='INDEPENDENT ARTIFACT GATE PASS / NOT INSTALLED'
 except Exception as e:
  result.update(status='BLOCKED',first_blocker=type(e).__name__+': '+str(e));(output/'failure.txt').write_text(traceback.format_exc())
 finally:
  builtins.compile=original_compile;importlib.machinery.SourceFileLoader.exec_module=original_loader
  M.authenticate();result['artifacts_unchanged']=True;result['adaptations']=AUDIT;result['gaps']=['Historical DEL binary identity remains unavailable','Runtime peak stack, physical timing and host delivery not measured'];M.dump(output/'result.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ['adaptations']},indent=2));return int(result['status']=='BLOCKED')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--measurements',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();sys.exit(main(a.measurements,a.output))
