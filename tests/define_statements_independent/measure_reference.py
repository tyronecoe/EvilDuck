"""Explicit NEW reference creation and strictly compiler-free cache reading."""
import argparse,hashlib,importlib.util,json,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
BUILD=pathlib.Path('/workspace/scratch/define-statements-target-build-v1')
COMMIT='de683669135fe5ccc5922f9883709194400672e5'
CORE='b9c53bd3632e049e674ea66bf6c110bf22bb51c35f0d46ae75e0f5825d069d99'
REF={'core.cpp':'d567a199a247fc585bb8f61c7459323a14ca8ca4bd14ff60690284d334f5431d','core.h':'166912a9669b937b5d44515b706721f428782fd5a9361d4f607a8b6d47cc1a9a','shortcut_keys.h':'f55b9548aa1499cc5459d503d806040159c0e1cc96912d187d4d4d5b5b3badaa'}
COMPILER='d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3'
ARTIFACTS={'EvilDuckS3.ino.bin':'524805fbde1af49b908b156e0eb50de48393b8e2810efcf0eaddba931408012e','EvilDuckS3.ino.elf':'cd82758717bf0e6e78aa8a582dff7b01de99ac14a62923b12cd104de8c56f490'}
ORIGINAL_MANIFEST_SHA='ae35e5d72b2a6977725014e9b00b560e5d04880623cafba772d160279fc41b46'
ORIGINAL_REPORT_SHA='dbc505c2a4e96c3bcd86339e43db35fe494bdcd4a168e3590914e4f7f8a5c893'
BLOCKED_EVIDENCE=pathlib.Path('/workspace/artifacts/DEFINE-CANDIDATE-INDEPENDENT-v1')
BLOCKED_MANIFEST_SHA='29d7e3cbcc2b51e9422cc6c22a8127f28d975d7bfd0ea8c1412b55d85c1ae8f5'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def require(v,m):
 if not v:raise ValueError(m)
def dump(p,d):pathlib.Path(p).write_text(json.dumps(d,indent=2)+'\n')
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def parser():return load(ROOT/'tests/define_labels_release/layout_measurement.py','independent_dwarf_parser')
def code_ids():return {p.name:sha(p) for p in pathlib.Path(__file__).parent.glob('*.py')}
def original_manifest():
 p=BUILD/'build-inputs.json';require(sha(p)==ORIGINAL_MANIFEST_SHA,'Original manifest bytes differ from preserved receipts')
 value=json.loads(p.read_bytes());rows=value['files']
 require(value['source_commit']==COMMIT and value['source_commit_contains_changes'] is True and value['uncommitted_local_changes'] is False,'Wrong original source provenance')
 require(len(rows)==len({r['file'] for r in rows}) and rows,'Duplicate/empty input inventory')
 digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 require(digest==value['files_sha256'],'Internal inventory digest differs')
 require((pathlib.Path('/workspace/artifacts/ROUTEB-DEFINE-STATEMENTS-H1-v1-PREBUILD-EVIDENCE/build-inputs.json')).read_bytes()==p.read_bytes(),'Original prebuild receipt differs')
 return value
def frozen_measurement_file(out,relative):
 # Authenticate the old creator evidence before permitting a newer reader.
 # Neither this evidence manifest nor any measurement input/hash is repinned.
 manifest=BLOCKED_EVIDENCE/'MANIFEST.json';require(sha(manifest)==BLOCKED_MANIFEST_SHA,'Original blocked evidence manifest changed')
 records=json.loads(manifest.read_text())['files'];name='measurements/'+relative
 found=[r for r in records if r['file']==name];require(len(found)==1,'Measurement absent from original evidence')
 row=found[0];p=out/relative
 require(p.is_file() and p.stat().st_size==row['size'] and sha(p)==row['sha256'],'Preserved measurement changed: '+relative)
 return p
def cache_inputs(out,label):
 # Creator and current-reader code are distinct identities. All non-code
 # authentication facts must still agree, and the old creator is pinned by
 # the unchanged blocked-run evidence. Creation mode retains its strict check.
 auth=authenticate();saved=json.loads(frozen_measurement_file(out,'authentication.json').read_text())
 require({k:v for k,v in saved.items() if k in auth and k!='code'}=={k:v for k,v in auth.items() if k!='code'},'Stale measurement authentication')
 old_summary=json.loads((BLOCKED_EVIDENCE/'summary.json').read_text())
 creator={pathlib.Path(k).name:v for k,v in old_summary['verifier_files'].items()}
 require(saved['code']==creator,'Measurement creator identity differs')
 source=out/'reference-source' if label=='reference' else BUILD/'candidate/EvilDuckS3'
 expected=REF if label=='reference' else dict(REF,**{'core.cpp':CORE})
 for name,digest in expected.items():require(sha(source/name)==digest,'Probe source mismatch')
 return dict(auth=dict(auth,code=creator),source={n:sha(source/n) for n in REF},probe_sha256=hashlib.sha256(probe_text(source).encode()).hexdigest())
def authenticate():
 require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT,'Build checkpoint moved')
 manifest=original_manifest()
 for row in manifest['files']:
  require(sha(ROOT/row['file'])==row['sha256'],'Selected input drift: '+row['file'])
  require(subprocess.check_output(['git','show',COMMIT+':'+row['file']],cwd=ROOT)==(ROOT/row['file']).read_bytes(),'Git binding drift')
 for n,h in ARTIFACTS.items():require(sha(BUILD/'build'/n)==h,'Image drift: '+n)
 require(sha(BUILD/'report.json')==ORIGINAL_REPORT_SHA,'Original build report changed')
 rows=json.loads((BUILD/'usb-observer-composition.json').read_text())['source_inventory'];require(len(rows)==201,'201 sources required')
 for r in rows:require(sha(BUILD/'candidate'/r['file'])==r['sha256'],'Composition drift')
 require(sha(BUILD/'candidate/EvilDuckS3/core.cpp')==CORE,'Wrong DEFINE core')
 entry=next(e for e in json.loads((BUILD/'build/compile_commands.json').read_text()) if pathlib.Path(e['file']).name=='core.cpp')
 require(sha(entry['arguments'][0])==COMPILER,'Wrong compiler')
 responses={a[1:]:sha(a[1:]) for a in entry['arguments'] if a.startswith('@')}
 expected={'cpp_flags':'3488ef11d79369f1684ce6a4145f17a62667ea09c49d7c8b26f9f1acbb8235b7','defines':'58c4e7d0705edc05bc4af3c2a6b7b7d63e663aa99324f3287705ad5a17fa084a','includes':'d6f11de153cc93c7ca5ea36cf94712142d8c29c4fc0d6df2e376a03de0d32b4d','build_opt.h':hashlib.sha256(b'').hexdigest(),'file_opts':hashlib.sha256(b'').hexdigest()}
 require(len(responses)==5,'Unexpected response set')
 for p,h in responses.items():require(expected.get(pathlib.Path(p).name)==h,'Response pin mismatch: '+p)
 toolroot=pathlib.Path(entry['arguments'][0]).parent
 pre=json.loads(pathlib.Path('/workspace/artifacts/ROUTEB-DEFINE-STATEMENTS-H1-v1-PREBUILD-EVIDENCE/prebuild-receipt.json').read_text())
 for tool in pre['tool_identities']:require(sha(tool['file'])==tool['sha256'],'Pinned tool changed')
 old=pathlib.Path('/workspace/scratch/del-baseline-input-recovery-v1/recovery-receipt.json')
 return dict(source_commit=COMMIT,artifacts=ARTIFACTS,entry=entry,responses=responses,code=code_ids(),original_blocked_receipt_sha256=sha(old),original_status='BLOCKED / EXACT HISTORICAL INPUT UNAVAILABLE')
def prepare(out):
 require(not out.exists(),'Fresh external measurement directory required');require(not out.resolve().is_relative_to(ROOT),'External storage required');out.mkdir(parents=True)
 auth=authenticate();src=out/'reference-source';src.mkdir()
 paths=['language_preview/core.cpp','language_preview/core.h','tests/keyboard_shortcuts/shortcuts.patch']+['tests/'+n+'/application.patch' for n in ['keyboard_control','lock_feedback','source_compat','random_lowercase','random_uppercase','randomization_jitter','text_keyboard','payload_restart','source_text','source_text_v2','lock_wait_timeout','inject_var_experimental','h1_right_modifiers','previous_command_repeat','del_alias']]
 recipe=[]
 for p in paths:
  data=subprocess.check_output(['git','show',COMMIT+':'+p],cwd=ROOT);require(data==(ROOT/p).read_bytes(),'Reference Git input drift');recipe.append(dict(file=p,sha256=hashlib.sha256(data).hexdigest()))
  if p.startswith('language_preview/'):(src/pathlib.Path(p).name).write_bytes(data);continue
  sections=re.split(r'(?m)(?=^--- )',data.decode());selected=''.join(s for s in sections if s.startswith('--- ') and s.splitlines()[1][4:] in REF)
  if selected:
   r=subprocess.run(['patch','--batch','--fuzz=0','-p0'],input=selected,text=True,cwd=src,capture_output=True,check=True)
   require(not any(n in (r.stdout+r.stderr).lower() for n in ['offset','fuzz']),'Inexact reference transformation')
 for n,h in REF.items():require(sha(src/n)==h,'Reference source hash mismatch: '+n)
 dump(out/'authentication.json',dict(auth,reference_recipe=recipe,reference_sources=REF,classification='NEW reference measurements; reconstructed source matches independently pinned bytes'))
 return auth
def probe_text(src):
 expressions={'compiler_size':'sizeof(ds_preview::Compiler)','compiler_alignment':'alignof(ds_preview::Compiler)','session_size':'sizeof(ds_preview::CompileSession)','session_alignment':'alignof(ds_preview::CompileSession)','program_size':'sizeof(ds_preview::Program)','runtime_size':'sizeof(ds_preview::Runtime)','workspace':'ds_preview::CompileStorage'}
 return '#include '+json.dumps(str(src/'core.cpp'))+'\nextern "C" {\n'+''.join('extern __attribute__((used)) const unsigned char evilduck_layout_'+k+'['+v+'] = {};\n' for k,v in expressions.items())+'}\n'
def identities(out,label):
 auth=authenticate();saved=json.loads((out/'authentication.json').read_text());require(saved['code']==auth['code'],'Verifier code changed since authentication')
 src=out/'reference-source' if label=='reference' else BUILD/'candidate/EvilDuckS3'
 for n,h in (REF if label=='reference' else dict(REF,**{'core.cpp':CORE})).items():require(sha(src/n)==h,'Probe source mismatch')
 return dict(auth=auth,source={n:sha(src/n) for n in REF},probe_sha256=hashlib.sha256(probe_text(src).encode()).hexdigest())
def command(out,label):
 entry=authenticate()['entry'];args=list(entry['arguments']);dest=out/label;src=out/'reference-source' if label=='reference' else BUILD/'candidate/EvilDuckS3'
 require('-c' in args and not any(a in args for a in ['-MF','-MT','-MQ']),'Unsafe compile command')
 args[args.index(entry['file'])]=str(dest/'probe.cpp');args[args.index('-o')+1]=str(dest/'probe.o')
 if label=='reference':args=[a.replace('-I'+str(BUILD/'candidate/EvilDuckS3'),'-I'+str(src)) for a in args]
 return args

def create(out,label):
 inputs=identities(out,label);dest=out/label;require(not dest.exists(),'No auxiliary retry permitted')
 calls=list(out.glob('compiler-invocation-*.json'));require(len(calls)<2,'Two auxiliary calls exhausted')
 controls=json.loads((out/'controls.json').read_text());require(controls['status']=='PASS' and controls['code']==code_ids(),'Controls missing/stale')
 args=command(out,label);dest.mkdir();src=out/'reference-source' if label=='reference' else BUILD/'candidate/EvilDuckS3';(dest/'probe.cpp').write_text(probe_text(src))
 # Reserve before launch, including failed attempts. No cache miss ever calls this.
 with (out/('compiler-invocation-'+str(len(calls))+'.json')).open('x') as f:json.dump(dict(command=args,label=label,firmware_build=False,link=False),f)
 p=subprocess.run(args,capture_output=True,text=True);dump(dest/'execution.json',dict(command=args,exit=p.returncode,stdout=p.stdout,stderr=p.stderr));require(p.returncode==0 and not p.stderr,'Auxiliary compiler failure')
 deps=parser();_,includes=load(ROOT/'tests/privacy_fix1/verify_target.py','independent_dependencies').make_dependencies((dest/'probe.d').read_text())
 inventory={str(pathlib.Path(n)):sha(n) for n in includes if pathlib.Path(n).is_file()}
 dump(dest/'measurement.json',dict(inputs=inputs,command=args,dependencies=inventory,files={n:sha(dest/n) for n in ['probe.cpp','probe.o','probe.su','probe.d']},classification='NEW auxiliary probe; stack frames are probe measurements, not firmware frames'))
def read_cache(out,label):
 dest=out/label;require((dest/'measurement.json').is_file(),'Missing measurement cache; verification cannot compile')
 frozen_measurement_file(out,label+'/measurement.json')
 row=json.loads((dest/'measurement.json').read_text());require(row['inputs']==cache_inputs(out,label),'Stale measurement inputs');require(row['command']==command(out,label),'Stale measurement command')
 for n,h in row['files'].items():require(sha(dest/n)==h,'Stale cache file: '+n)
 for n,h in row['dependencies'].items():require(sha(n)==h,'Stale include closure: '+n)
 return row

def measure(out):
 tool=authenticate()['entry']['arguments'][0].rsplit('g++',1)[0];m=parser();layouts={};aux={}
 for label in ['reference','candidate']:
  row=read_cache(out,label);dest=out/label
  raw=subprocess.check_output([tool+'readelf','--debug-dump=info',str(dest/'probe.o')],text=True);layouts[label]=m.layout_from_dwarf(raw)
  nm=subprocess.check_output([tool+'nm','-S','--defined-only',str(dest/'probe.o')],text=True);values={}
  for line in nm.splitlines():
   match=re.fullmatch(r'[0-9a-fA-F]+ ([0-9a-fA-F]+) [A-Za-z] evilduck_layout_(\w+)',line)
   if match:require(match[2] not in values,'Ambiguous probe symbol');values[match[2]]=int(match[1],16)
  require(set(values)==set(['compiler_size','compiler_alignment','session_size','session_alignment','program_size','runtime_size','workspace']),'Missing probe symbols')
  require(values['compiler_size']==layouts[label]['compiler_bytes'] and values['workspace']==4096,'Workspace/DWARF mismatch');require(values['compiler_alignment']<=values['session_alignment'] and values['session_alignment']%values['compiler_alignment']==0,'Alignment mismatch')
  aux[label]=dict(receipt=row,values=values,probe_stack_measurements=m.stack_rows(dest/'probe.su'))
 m.validate_capacity(layouts['reference'],layouts['candidate']);require(layouts['candidate']['compiler_bytes']==3928,'Compiler size changed')
 actual=m.layout_from_dwarf(subprocess.check_output([tool+'readelf','--debug-dump=info',str(BUILD/'build/sketch/core.cpp.o')],text=True));require({k:v for k,v in actual.items() if k!='compiler_die'}=={k:v for k,v in layouts['candidate'].items() if k!='compiler_die'},'Actual candidate/probe mismatch')
 linked=subprocess.check_output([tool+'readelf','--debug-dump=info','--dwarf-depth=3',str(BUILD/'build/EvilDuckS3.ino.elf')],text=True);definitions=[]
 for block in re.split(r'(?=\n <[0-9]+><[0-9a-fA-F]+>:)',linked):
  if 'DW_TAG_class_type' in block and re.search(r'DW_AT_name\s*:\s*[^\n]*: Compiler\n',block):
   value=re.search(r'DW_AT_byte_size\s*:\s*([0-9]+)',block)
   if value:definitions.append(int(value[1]))
 require(definitions==[actual['compiler_bytes']],'Linked ELF/object layout mismatch')
 require('evilduck_layout_' not in subprocess.check_output([tool+'nm','--defined-only',str(BUILD/'build/EvilDuckS3.ino.elf')],text=True),'Probe linked into firmware')
 source=(BUILD/'candidate/EvilDuckS3/core.cpp').read_text();require('static_assert(sizeof(Compiler)<=CompileStorage' in source and 'static_assert(alignof(Compiler)<=alignof(max_align_t)' in source,'Static workspace assertions missing')
 return dict(status='PASS',workspace_bytes=4096,constant_cell_bytes=32,max_label_bytes=31,constant_slots=16,target_compiler_bytes=3928,compiler_byte_delta=128,target_compiler_alignment=aux['candidate']['values']['compiler_alignment'],workspace_static_assert_retained=True,alignment_static_assert_retained=True,workspace_margin_bytes=168,new_reference_layouts=layouts,new_probe_measurements=aux,actual_candidate_layout=actual,historical_layout_verified=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['authenticate','create','verify']);p.add_argument('--directory',type=pathlib.Path,required=True);a=p.parse_args()
 if a.mode=='authenticate':prepare(a.directory)
 elif a.mode=='create':
  for label in ['reference','candidate']:create(a.directory,label)
 else:dump(a.directory/'layout-result.json',measure(a.directory))
