#!/usr/bin/env python3
"""NVS-specific fail-closed dependency tests; no devices or installed mutations."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources,sha,tree_hash,PATCH
from verify_patched_firmware import verify

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original-core',type=Path,required=True);p.add_argument('--patched-core',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args();rows=[]
 def case(n,fn):
  try:fn();s='PASS';err=''
  except Exception as e:s='FAIL';err=str(e)
  rows.append(dict(name=n,status=s,assertions=1,error=err));print(s,n,err,flush=True)
 def rejects(fn):
  try:fn()
  except (RuntimeError,ValueError,OSError):return
  raise AssertionError('unexpected acceptance')
 case('stage18_original_source_preserved',lambda:check_sources(a.original_core))
 main_source=(a.original_core/'cores/esp32/main.cpp').read_text()
 # Actual task creation follows initArduino; USB boot support can precede it.
 case('stage18_actual_init_before_setup_task',lambda:(_ for _ in ()).throw(ValueError('startup order changed')) if main_source.index('  initArduino();')>main_source.index('  xTaskCreateUniversal(loopTask') else None)
 case('stage18_combined_patched_source_verified',lambda:check_sources(a.patched_core,True))
 with tempfile.TemporaryDirectory(prefix='stage18-dependency-') as t:
  # Preserve the package/tool layout while testing only disposable source copies.
  c=Path(t)/'data/packages/esp32/hardware/esp32/3.3.0';c.parent.mkdir(parents=True);shutil.copytree(a.original_core,c)
  tools=c.parents[2]/'tools';tools.symlink_to(a.original_core.parents[2]/'tools',target_is_directory=True)
  subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(PATCH)],cwd=c,check=True,capture_output=True)
  case('stage18_hid_only_core_rejected',lambda:rejects(lambda:check_sources(c,True)))
  subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(ROOT/'proposals/arduino-esp32-3.3.0-nvs-preservation.patch')],cwd=c,check=True,capture_output=True)
  path=c/'cores/esp32/esp32-hal-misc.c';path.write_bytes(path.read_bytes()+b'\n// mutation\n')
  case('stage18_modified_policy_bytes_rejected',lambda:rejects(lambda:check_sources(c,True)))
  header=(ROOT/'EvilDuckS3/nvs_startup.h').read_text()
  r=subprocess.run(['g++','-E','-x','c++','-'],input=header,capture_output=True,text=True)
  case('stage18_native_missing_policy_guard_rejected',lambda:(_ for _ in ()).throw(ValueError('missing guard diagnostic')) if r.returncode==0 or 'early NVS preservation patch is required' not in r.stderr else None)
  guarded=subprocess.run(['g++','-E','-x','c++','-DEVILDUCK_VERIFIED_NVS_PRESERVATION=1','-'],input=header,capture_output=True,text=True)
  case('stage18_verified_policy_compile_guard',lambda:(_ for _ in ()).throw(ValueError(guarded.stderr)) if guarded.returncode else None)
  source=Path(t)/'missing-hook.cpp';source.write_text('#include "'+str(ROOT/'EvilDuckS3/nvs_startup.h')+'"\nint main(){return evilduck_nvs_startup_error();}\n')
  linked=subprocess.run(['g++','-DEVILDUCK_VERIFIED_NVS_PRESERVATION=1',str(source),'-o',str(Path(t)/'missing-hook')],capture_output=True,text=True)
  case('stage18_missing_core_hook_cannot_link',lambda:(_ for _ in ()).throw(ValueError('missing link dependency guard')) if linked.returncode==0 or 'evilduck_nvs_startup_error' not in linked.stderr else None)
 case('stage18_final_linked_nvs_policy',lambda:verify(a.patched_core,a.build_dir))
 out=dict(results=rows,pass_count=sum(r['status']=='PASS' for r in rows),fail_count=sum(r['status']=='FAIL' for r in rows),assertions=len(rows),hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['fail_count'])
if __name__=='__main__':raise SystemExit(main())
