#!/usr/bin/env python3
"""Additive offline cases over pinned complete static-response native regressions.

Only disposable generated driver includes and mocks change. All 586 historical
native case bodies, expectations, selectors and sanitizer flags remain intact.
No target compiler, package, real transport, owner data or external server.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / 'tests/static_response_privacy_regression/run_tests.py'
PINS = {
 'tests/static_response_privacy_regression/run_tests.py':'2f3e08d0f40db1a81c816bdccf04563ed5bc9a3e84cdcace186ea81008cb2cab',
 'tests/editor_build_integration/run_privacy_tests.py':'8ac89aa0029ad654e8cdb15a063c1aa96895e21819ab4a9e835eb3ef08fd2a30',
 'tests/privacy_fix1/run_tests.py':'fd67a67dfc99dfcb0d07a38d84542ce500bcfeb5aaa612681f6ab2d5d631584a',
 'tests/privacy_fix1/test_main.cpp':'ca264782966ee06cefe14d49a2be069d8f057ee22ecb73b5cc08fa3343031a84',
}

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def replace(text,old,new):
 assert text.count(old)==1,(old,text.count(old))
 return text.replace(old,new)

def causal_controls(result,target,layer,output):
 """Compile only the actual old/new core under the inherited host sanitizers."""
 folder=pathlib.Path(output).with_name(pathlib.Path(output).stem+'-causal-controls')
 assert not folder.exists(),'Preserve earlier causal controls'
 folder.mkdir()
 pin=layer.pin();old=folder/'old';new=folder/'new';old.mkdir();new.mkdir()
 for directory in [old,new]:
  for name in ['core.cpp','core.h','shortcut_keys.h']:shutil.copyfile(target/name,directory/name)
 reversed_patch=subprocess.run(['patch','--batch','--reverse','--fuzz=0','--no-backup-if-mismatch','-p0','-i',str(ROOT/'tests/previous_command_repeat/application.patch')],cwd=old,capture_output=True,text=True,check=True)
 assert 'offset' not in reversed_patch.stdout.lower() and 'fuzz' not in reversed_patch.stdout.lower()
 assert sha(old/'core.cpp')==pin['before'][0]['sha256'] and sha(new/'core.cpp')==pin['after'][0]['sha256']
 source=folder/'probe.cpp'
 source.write_text(r'''#include "core.h"
#include <cstdio>
#include <cstring>
using namespace ds_preview;
struct Out{char text[128]={};unsigned n=0;static Accept sink(void*c,const Event&e){Out&o=*static_cast<Out*>(c);if(e.type==EventType::Character)o.text[o.n++]=char(e.value);else if(e.type==EventType::KeyTap&&e.value==40)o.text[o.n++]='\n';return Accept::Accepted;}};
static bool run(Program&p,const char*s,const char*expected){if(!p.compile(s,strlen(s)))return false;Runtime rt;Out out;if(!rt.start(p,Out::sink,&out))return false;for(unsigned i=0;i<20000&&rt.state()==State::Running;++i)rt.tick(i);return rt.state()==State::Completed&&!strcmp(out.text,expected);}
int main(int argc,char**argv){if(argc!=2)return 1;bool old=!strcmp(argv[1],"old");Program p;const char*legacy="DELAY 5000\nSTRING T05R:\nSTRING x\nREPEAT 3\nSTRING :DONE\nENTER\n";
if(old){if(p.compile(legacy,strlen(legacy))||p.error().line!=4||p.error().code!=ErrorCode::Syntax)return 2;std::printf("DIAGNOSTIC old Request11 line=%u code=%u\n",p.error().line,unsigned(p.error().code));}else if(!run(p,legacy,"T05R:xxxx:DONE\n"))return 3;
if(!run(p,"DELAY 5000\nSTRING T05I:\nREPEAT 3 STRING x\nSTRING :DONE\nENTER\n","T05I:xxx:DONE\n"))return 4;
if(!run(p,"REPEAT 2 STRING a\nREPEAT 3 STRING b\n","aabbb"))return 5;
if(p.compile("REPEAT 3\n",9)||p.error().line!=1||p.error().code!=(old?ErrorCode::Syntax:ErrorCode::Unsupported))return 6;
std::printf("PASS causal mode=%s checks=4 compilerBytes=%zu Program=%zu Runtime=%zu\n",argv[1],CompileSession::compilerBytes(),sizeof(Program),sizeof(Runtime));}
''')
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
 rows=[]
 for label,directory in [('old',old),('new',new)]:
  command=[v for v in result['command'] if not v.endswith('.cpp')]
  i=command.index('-o');del command[i:i+2]
  command[1:1]=['-I'+str(directory)]
  command += [str(source),str(directory/'core.cpp'),'-o',str(directory/'probe')]
  compiled=subprocess.run(command,capture_output=True,text=True,timeout=120)
  row=dict(mode=label,command=command,compile_exit=compiled.returncode,compile_stdout=compiled.stdout,compile_stderr=compiled.stderr,core_sha256=sha(directory/'core.cpp'),status='FAIL')
  if compiled.returncode==0:
   run=subprocess.run([str(directory/'probe'),label],capture_output=True,text=True,timeout=30,env=env)
   row.update(exit=run.returncode,stdout=run.stdout,stderr=run.stderr,status='PASS' if run.returncode==0 and not run.stderr else 'FAIL',checks=4 if run.returncode==0 else 0)
  rows.append(row)
 return dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},checks=sum(r.get('checks',0) for r in rows),probe_sha256=sha(source),firmware_built=False,hardware=False)

def focused_existing(receipt,target,output):
 """Four added control/evaluation cases; do not repeat successful old suites."""
 receipt=pathlib.Path(receipt);target=pathlib.Path(target);output=pathlib.Path(output)
 assert not output.exists()
 old=json.loads(receipt.read_text());assert old['counts']==dict(PASS=632,FAIL=0)
 spec=importlib.util.spec_from_file_location('previous_repeat_focused_preparer',ROOT/'tests/previous_command_repeat/prepare_sources.py');layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer);layer.verify_final(target)
 driver=ROOT/'tests/previous_command_repeat/test_main.cpp';current=driver.read_bytes()
 frozen=receipt.parent/'native-build-v2/driver-executed.cpp';before=frozen.read_bytes()
 assert sha(frozen)==old['previous_command_repeat_binding']['new_driver_sha256']
 marker=b'}else check(false,"unknown previous-command repeat case");'
 left,right=before.split(marker)
 added,tail=current[len(left):].split(marker)
 assert current.startswith(left) and tail==right and added.startswith(b'}else if(id=="PR47")')
 assert sorted(set(re.findall(rb'"(PR\d\d)"',added)))==[b'PR47',b'PR48',b'PR49',b'PR50']
 folder=output.with_name(output.stem+'-build');assert not folder.exists();folder.mkdir()
 snapshot=folder/'driver-executed.cpp';snapshot.write_bytes(current)
 command=list(old['command']);assert command.count(str(driver))==1;command[command.index(str(driver))]=str(snapshot)
 index=command.index('-o');command[index+1]=str(folder/'native')
 for binding in old['previous_command_repeat_binding']['source_bindings']:
  assert sha(binding['native'])==binding['sha256'] and pathlib.Path(binding['native']).read_bytes()==(target/binding['file']).read_bytes()
 compiled=subprocess.run(command,capture_output=True,text=True,timeout=300)
 result=dict(command=command,compile_exit=compiled.returncode,compile_stdout=compiled.stdout,compile_stderr=compiled.stderr,
    reused_successful_receipt=str(receipt),reused_successful_receipt_sha256=sha(receipt),first46_driver_snapshot=str(frozen),first46_driver_sha256=sha(frozen),
    current_driver_snapshot=str(snapshot),current_driver_sha256=sha(snapshot),first46_case_bodies_unchanged=True,
    cases_added=['PR47','PR48','PR49','PR50'],historical_cases_reexecuted=False,results=[],sanitizers='ASan/UBSan/detect_leaks=1',firmware_built=False,hardware=False,packaging=False)
 if compiled.returncode==0:
  env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
  for case in result['cases_added']:
   run=subprocess.run([str(folder/'native'),case],capture_output=True,text=True,timeout=30,env=env)
   match=re.search(r'PASS '+case+r' \((\d+) assertions\)',run.stdout)
   result['results'].append(dict(id=case,status='PASS' if run.returncode==0 and match and not run.stderr else 'FAIL',exit=run.returncode,assertions=int(match[1]) if match else 0,stdout=run.stdout,stderr=run.stderr))
 result['counts']={s:sum(r['status']==s for r in result['results']) for s in ['PASS','FAIL']};result['assertions']=sum(r['assertions'] for r in result['results'])
 assert driver.read_bytes()==current and sha(receipt)==result['reused_successful_receipt_sha256'];layer.verify_final(target)
 output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 return int(compiled.returncode!=0 or result['counts']!=dict(PASS=4,FAIL=0))

def main():
 for name,pin in PINS.items():assert sha(ROOT/name)==pin,name
 spec=importlib.util.spec_from_file_location('previous_command_repeat_preparer',ROOT/'tests/previous_command_repeat/prepare_sources.py')
 layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
 driver=ROOT/'tests/previous_command_repeat/test_main.cpp'
 driver_bytes=driver.read_bytes();driver_sha=sha(driver)
 cases=sorted(set(re.findall(r'"(PR\d\d)"',driver_bytes.decode())))
 assert cases==['PR%02d'%i for i in range(1,len(cases)+1)] and len(cases)>=50
 bindings=[]
 target=pathlib.Path(sys.argv[sys.argv.index('--target-composed')+1]).resolve()
 layer.verify_final(target)

 def finalize(source,command):
  source=pathlib.Path(source)
  layer.delta(source)
  parent=(ROOT/'tests/privacy_fix1/test_main.cpp').read_text()
  old='int main(int argc, char **argv)';assert parent.count(old)==1
  (source/'privacy_parent_cases.inc').write_text(parent.replace(old,'int privacy_fix1_main(int argc, char **argv)'))
  assert sha(driver)==driver_sha,'New driver changed during native preparation'
  snapshot=source/'previous_command_repeat_driver.cpp';snapshot.write_bytes(driver_bytes)
  assert command.count(str(driver))==1;command[command.index(str(driver))]=str(snapshot)
  for name in ['core.cpp','core.h','cli.cpp','webserver.cpp','settings.cpp','webfiles.h']:
   physical=source/name
   if not physical.exists():physical=ROOT/'EvilDuckS3'/name
   assert physical.read_bytes()==(target/name).read_bytes(),name
   bindings.append(dict(file=name,native=str(physical),target=str(target/name),sha256=sha(physical)))

 def adapt_privacy(text):
  text=replace(text,'"tests/privacy_fix1/test_main.cpp"\',','"tests/previous_command_repeat/test_main.cpp"\',')
  text=replace(text,'repr(privacy_cases + ["AD%02d" % i for i in range(1, 37)])','repr(REPEAT_CASES + privacy_cases + ["AD%02d" % i for i in range(1, 37)])')
  text=replace(text,'    status = 0','        REPEAT_FINALIZE(source, command)\n\n    status = 0')
  text=replace(text,'if not r["id"].startswith("PF")','if not r["id"].startswith(("PF", "PR"))')
  return text

 def adapt_editor(text):
  text=replace(text,'    text = PARENT.read_text()','    text = REPEAT_ADAPT_PRIVACY(PARENT.read_text())')
  return text

 text=PARENT.read_text()
 text=replace(text,"'tests/static_response_build_integration/source-manifest.json'","'tests/previous_command_repeat/source-manifest.json'")
 text=replace(text,'    text, changes = PARENT.read_text(), []','    text, changes = REPEAT_ADAPT_EDITOR(PARENT.read_text()), []')
 text=replace(text,'EDITOR_BROWSER_OUTPUT=browser_output, STATIC_NATIVE_PREPARE=STATIC_NATIVE_PREPARE)',
              'EDITOR_BROWSER_OUTPUT=browser_output, STATIC_NATIVE_PREPARE=STATIC_NATIVE_PREPARE, REPEAT_CASES=REPEAT_CASES, REPEAT_FINALIZE=REPEAT_FINALIZE)')
 text=replace(text,'STATIC_NATIVE_PREPARE=native_prepare)',
              'STATIC_NATIVE_PREPARE=native_prepare, REPEAT_ADAPT_PRIVACY=REPEAT_ADAPT_PRIVACY, REPEAT_CASES=REPEAT_CASES, REPEAT_FINALIZE=REPEAT_FINALIZE)')
 namespace=dict(__name__='previous_command_repeat_native_adapter',__file__=str(PARENT),
                REPEAT_ADAPT_EDITOR=adapt_editor,REPEAT_ADAPT_PRIVACY=adapt_privacy,
                REPEAT_CASES=cases,REPEAT_FINALIZE=finalize)
 exec(compile(text,str(PARENT),'exec'),namespace)
 status=namespace['main']()
 path=pathlib.Path(sys.argv[sys.argv.index('--results')+1]);result=json.loads(path.read_text())
 rows=[r for r in result['results'] if r['id'].startswith('PR')]
 assert sorted(r['id'] for r in rows)==cases
 result['previous_command_repeat']=dict(PASS=sum(r['status']=='PASS' for r in rows),FAIL=sum(r['status']=='FAIL' for r in rows),assertions=sum(r['assertions'] for r in rows))
 assert sha(driver)==driver_sha,'New driver changed during native execution'
 result['previous_command_repeat_binding']=dict(parent_pins=PINS,new_driver_sha256=driver_sha,runner_sha256=sha(__file__),
    final_composed_source=str(target),source_bindings=bindings,new_cases_added=len(cases),historical_cases_unchanged=586,
    historical_case_expectations_changed=False,firmware_built=False,packaging=False,hardware=False,
    lower_transport='RAM-only inherited transport mocks; no USB or HID output',identity='Historical fixture ID retained; real target application sources bound by bytes')
 result['static_response_privacy_adapter']['native_cpp_cases_or_expectations_changed']=str(len(cases))+' additive cases; all586 historical case bodies and expectations unchanged'
 result['setup_attempts']=[dict(stage='adapter composition before compilation',status='HARNESS_ASSERTION',diagnostic="EDITOR_BROWSER_OUTPUT=browser_output) anchor missing after premature namespace adaptation",resolution='Apply extra namespace bindings after the inherited static-response adapter replacement; only the new runner changed',tests_executed=False)]
 earlier=path.with_name('native-v1.json')
 if earlier.exists() and earlier!=path:
  old=json.loads(earlier.read_text())
  result['development_attempts']=[dict(receipt=str(earlier),sha256=sha(earlier),counts=old['counts'],failures=[r for r in old['results'] if r['status']!='PASS'],resolution='PR33 stopwatch now checked before the existing1000tick noReplay probe; PR46 keeps unchanged REPLAY UnknownStatement13 diagnostic. New test corrections only; production source unchanged.')]
 result['causal_controls']=causal_controls(result,target,layer,path)
 if result['causal_controls']['counts']['FAIL']:status=1
 layer.verify_final(target)
 for name,pin in PINS.items():assert sha(ROOT/name)==pin,name
 path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['previous_command_repeat','privacy_fix1','all_existing_composed_regressions','sanitizers']},indent=2))
 return status

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--focused-existing':raise SystemExit(focused_existing(*sys.argv[2:]))
 if len(sys.argv)>1 and sys.argv[1]=='--controls-only':
  path=pathlib.Path(sys.argv[2]);result=json.loads(path.read_text());target=pathlib.Path(sys.argv[3])
  spec=importlib.util.spec_from_file_location('previous_command_repeat_control_preparer',ROOT/'tests/previous_command_repeat/prepare_sources.py');layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
  result['causal_controls']=causal_controls(result,target,layer,path);path.write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps(result['causal_controls'],indent=2));raise SystemExit(bool(result['causal_controls']['counts']['FAIL']))
 raise SystemExit(main())
