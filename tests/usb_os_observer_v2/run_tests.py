#!/usr/bin/env python3
"""Fresh V2 actual-module native probes; no hardware, target build, payload or network."""
import argparse,hashlib,importlib.util,json,os,pathlib,re,shutil,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
PARENT=pathlib.Path('/workspace/scratch/usb-os-observer-release/regressions-v2/native.json')
FOCUSED=pathlib.Path('/workspace/scratch/usb-os-observer-release/focused-v3.json')
PARENT_SHA='73c15f71571a2b9a2d12368cea050545d0c8853eaba2cccea9241e3fc908e9b5'
FOCUSED_SHA='5a941488e4e028278bf32df3b22a9dfeddd98928543775a5de15fc816c36e639'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser();p.add_argument('--target-composed',type=pathlib.Path,required=True);p.add_argument('--output-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
 assert not a.output_dir.exists() and not a.results.exists();assert not a.output_dir.resolve().is_relative_to(ROOT)
 m=load(HERE/'prepare_sources.py','v2_backend_source');inventory=m.verify_final(a.target_composed)
 assert sha(PARENT)==PARENT_SHA and sha(FOCUSED)==FOCUSED_SHA
 old=json.loads(PARENT.read_text());focused=json.loads(FOCUSED.read_text());assert old['counts']==dict(PASS=636,FAIL=0) and old['assertions']==27376;assert focused['counts']==dict(PASS=30,FAIL=0)
 command=list(old['command']);old_driver=next(pathlib.Path(x) for x in command if x.endswith('/previous_command_repeat_driver.cpp'));old_src=old_driver.parent;old_work=old_src.parent
 assert sha(old_driver)==old['driver_sha256']
 for row in old['source_bindings']:assert sha(row['native'])==row['sha256']
 a.output_dir.mkdir(parents=True);source=a.output_dir/'sources';shutil.copytree(old_src,source)
 m.delta(source)
 for arg in command:
  if arg.startswith('-I'):
   old_include=pathlib.Path(arg[2:])
   if old_include.is_relative_to(old_work) and not old_include.is_relative_to(old_src):
    new_include=a.output_dir/old_include.relative_to(old_work)
    if not new_include.exists():shutil.copytree(old_include,new_include)
 original_cpp=pathlib.Path(next(x for x in command if x.endswith('/mock_real.cpp')))
 if not (a.output_dir/original_cpp.relative_to(old_work)).exists():shutil.copytree(original_cpp.parent,(a.output_dir/original_cpp.relative_to(old_work)).parent)
 focused_src=pathlib.Path(focused['source_bindings'][0]['native']).parent
 for inc in focused_src.glob('*.inc'):
  destination=source/inc.name
  if destination.exists():
   if destination.read_bytes()!=inc.read_bytes():assert inc.name=='web_handlers.inc','unexpected historical snapshot divergence: '+inc.name
  else:shutil.copyfile(inc,destination)
 v1=ROOT/'tests/usb_os_observer/test_main.cpp';assert sha(v1)==focused['driver_sha256'];text=v1.read_text();assert text.count('int main(int argc,char**argv)')==1;(source/'observer_v1_parent.inc').write_text(text.replace('int main(int argc,char**argv)','int observer_v1_main(int argc,char**argv)',1))
 driver=source/'observer_v2_driver.cpp';driver.write_bytes((HERE/'test_main.cpp').read_bytes())
 command=[x.replace(str(old_work),str(a.output_dir)) for x in command];replaced_driver=str(source/old_driver.name);assert command.count(replaced_driver)==1;command[command.index(replaced_driver)]=str(driver);command[command.index('-o')+1]=str(a.output_dir/'native')
 bindings=[]
 for x in command:
  if x.endswith('.cpp'):
   f=pathlib.Path(x)
   if f.name==driver.name:continue
   if (a.target_composed/f.name).exists():
    assert f.read_bytes()==(a.target_composed/f.name).read_bytes(),f.name;bindings.append(dict(file=f.name,native=str(f),sha256=sha(f)))
 for name in ['core.h','shortcut_keys.h','adapter.h','seam.inc','backend_lease.inc','webfiles.h','webserver.cpp','hid_backend.h']:
  assert (source/name).read_bytes()==(a.target_composed/name).read_bytes(),name;bindings.append(dict(file=name,native=str(source/name),sha256=sha(source/name)))
 assert '-fsanitize=address,undefined' in command and '-fno-omit-frame-pointer' in command
 compiled=subprocess.run(command,capture_output=True,text=True,timeout=360);cases=sorted(set(re.findall(r'"(V2\d\d)"',driver.read_text())));assert cases==['V2%02d'%n for n in range(1,35)]
 out=dict(status='FAIL',command=command,compile_exit=compiled.returncode,compile_stdout=compiled.stdout,compile_stderr=compiled.stderr,results=[],source=str(a.target_composed),full_source_inventory=inventory,source_bindings=bindings,source_manifest_sha256=sha(HERE/'source-manifest.json'),runner_sha256=sha(__file__),driver_sha256=sha(driver),parent_receipt=str(PARENT),parent_receipt_sha256=PARENT_SHA,focused_parent_receipt=str(FOCUSED),focused_parent_sha256=FOCUSED_SHA,historical_case_bodies_unchanged=True,historical_cases_executed=False,sanitizer_flags_changed=False,sanitizers='ASan/UBSan/detect_leaks=1',hardware=False,real_hid=False,target_firmware_built=False)
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
 if compiled.returncode==0:
  for case in cases:
   run=subprocess.run([str(a.output_dir/'native'),case],capture_output=True,text=True,timeout=45,env=env);found=re.search(r'PASS '+case+r' \((\d+) assertions\)',run.stdout)
   out['results'].append(dict(id=case,exit=run.returncode,stdout=run.stdout,stderr=run.stderr,status='PASS' if run.returncode==0 and found and not run.stderr else 'FAIL',assertions=int(found[1]) if found else 0))
 out['counts']={x:sum(row['status']==x for row in out['results']) for x in ['PASS','FAIL']};out['assertions']=sum(row['assertions'] for row in out['results']);out['status']='PASS' if compiled.returncode==0 and out['counts']==dict(PASS=34,FAIL=0) else 'FAIL'
 assert m.verify_final(a.target_composed)==inventory;a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','compile_exit','counts','assertions']}))
 if compiled.returncode:print(compiled.stderr)
 for row in out['results']:
  if row['status']!='PASS':print(row)
 return int(out['status']!='PASS')
if __name__=='__main__':raise SystemExit(main())
