#!/usr/bin/env python3
"""Pinned upstream routing slices + actual firmware; never install patch or use hardware."""
import argparse,hashlib,json,re,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
NORMAL=['known_hid_vectors_no_numeric_encoding','normalized_interrupt_output','legacy_type_zero_interrupt','nonzero_control_output','feature_led_type_separation','input_type_rejected','invalid_type_rejected','invalid_instance','zero_transfer_backed_buffer','report_id_only_interrupt','zero_length_control_output','null_control_output','unknown_report_id','zero_id_device_no_prefix_stripping','all_led_masks_through_actual_route','padding_and_length_rejection','repeated_report_not_transition','detached_feedback_rejection','stale_explicit_token_rejection','routing_during_owned_injection','stock_output_queue_wait_policy']
FAULTS=['null_zero_interrupt','empty_onepast_interrupt','null_nonzero_interrupt','debug_invalid_type_unknown_id','stock_output_null','stock_output_empty_onepast']
def body(text,marker):
 start=text.index(marker);p=text.index('{',start);depth=1;end=p+1
 while depth:
  depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]
def compile_exe(core,backend,build,name,paired,main_source=None):
 build.mkdir(parents=True,exist_ok=True)
 source=(core/'libraries/USB/src/USBHID.cpp').read_text()
 markers=['USBHIDDevice *tinyusb_get_device_by_report_id(','static bool tinyusb_on_set_feature(','static bool tinyusb_on_set_output(','void tud_hid_set_report_cb(']
 (build/'routing_slice.inc').write_text('// Exact bodies extracted from reviewed Arduino3.3.0 source; Apache-2.0\n'+'\n'.join(body(source,m) for m in markers)+'\n')
 stock=body((core/'libraries/USB/src/USBHIDKeyboard.cpp').read_text(),'void USBHIDKeyboard::_onOutput(').replace('USBHIDKeyboard::_onOutput','StockOutput',1)
 (build/'stock_keyboard_slice.inc').write_text('// Extracted Apache-2.0 stock keyboard callback, name-only adaptation\n'+stock+'\n')
 modules=['com','duckscript','duck_vars','duck_keys','keyboard_locale','locales','script_log','cli','script_source','script_parser','duck_expr','duck_constants','script_functions','script_preprocessor','duck_random','attackmode','usb_msc','sd_card']
 fw=ROOT/'EvilDuckS3';exe=build/name
 args=['g++','-std=gnu++17','-g','-O1','-pthread','-DEVILDUCK_HOST_TEST','-DEVILDUCK_PRODUCTION_STORAGE','-DCONFIG_TINYUSB_MSC_ENABLED=1','-DCONFIG_TINYUSB_MSC_BUFSIZE=4096','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(build),'-I'+str(ROOT/'tests/stage10/mocks'),'-I'+str(ROOT/'tests/stage1/mocks'),'-I'+str(fw),str(main_source or ROOT/'tests/stage15/routing.cpp'),str(ROOT/'tests/stage1/mocks/host.cpp'),str(backend),*[str(fw/(m+'.cpp')) for m in modules],'-o',str(exe)]
 if paired:args.insert(1,'-DPAIRED_PROPOSAL')
 subprocess.run(args,check=True);return exe
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--build-dir',type=Path);p.add_argument('--results',type=Path);p.add_argument('--baseline-backend',type=Path,help='Exact Stage15 backend for historical observations on later branches');a=p.parse_args();b=a.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage15-'))
 before={}
 metadata=json.loads((ROOT/'docs/stage15-upstream-sources.json').read_text())
 for record in metadata['sources']:
  saved=record['path']
  path=a.core_dir/saved.split('/hardware/esp32/3.3.0/',1)[1] if '/hardware/esp32/3.3.0/' in saved else a.core_dir.parents[2]/'tools'/saved.split('/tools/',1)[1]
  before[path]=hashlib.sha256(path.read_bytes()).hexdigest();assert before[path]==record['sha256'],'Pinned upstream source mismatch'
 assert hashlib.sha256((a.core_dir/'libraries/USB/src/USBHID.cpp').read_bytes()).hexdigest()==metadata['sources'][0]['sha256']
 backend=a.baseline_backend or ROOT/'EvilDuckS3/hid_backend.cpp'
 if a.baseline_backend:
  expected=subprocess.run(['git','show','7a8229f9c04d2a5423c179fe8daa42e048554560:EvilDuckS3/hid_backend.cpp'],cwd=ROOT,check=True,capture_output=True).stdout
  assert backend.read_bytes()==expected,'Historical backend must match Stage15 commit exactly'
 original=compile_exe(a.core_dir,backend,b/'original','routing',False)
 temp=b/'proposal';(temp/'libraries/USB/src').mkdir(parents=True,exist_ok=True);(temp/'EvilDuckS3').mkdir()
 for name in ['USBHID.cpp','USBHIDKeyboard.cpp']:shutil.copyfile(a.core_dir/'libraries/USB/src'/name,temp/'libraries/USB/src'/name)
 shutil.copyfile(backend,temp/'EvilDuckS3/hid_backend.cpp')
 for patch in ['arduino-esp32-3.3.0-hid-routing.patch','evilduck-hid-feature-companion.patch']:subprocess.run(['patch','--batch','--forward','-p1','-i',str(ROOT/'proposals'/patch)],cwd=temp,check=True,capture_output=True)
 paired=compile_exe(temp,temp/'EvilDuckS3/hid_backend.cpp',b/'paired','routing',True)
 results=[]
 for variant,exe,names in [('unpatched',original,NORMAL+FAULTS),('paired_proposal',paired,NORMAL+FAULTS[:4])]:
  for name in names:
   r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30)
   fault=variant=='unpatched' and name in FAULTS
   expected=bool(r.returncode and ('AddressSanitizer' in r.stderr or 'runtime error:' in r.stderr) and ('routing_slice.inc' in r.stderr or 'stock_keyboard_slice.inc' in r.stderr)) if fault else r.returncode==0
   status=('XFAIL' if fault else 'OBSERVED' if variant=='unpatched' and name in ['nonzero_control_output','feature_led_type_separation','input_type_rejected','invalid_type_rejected','invalid_instance','zero_transfer_backed_buffer','stock_output_queue_wait_policy'] else 'PASS') if expected else 'FAIL'
   match=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
   results.append(dict(variant=variant,name=name,status=status,assertions=int(match[1]) if match else 0,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
   print(status,variant,name,flush=True)
 for path,digest in before.items():assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Installed dependency changed'
 report=dict(results=results,counts={s:sum(r['status']==s for r in results) for s in ['PASS','FAIL','XFAIL','XPASS','OBSERVED']},assertions=sum(r['assertions'] for r in results),sanitizers='ASan/UBSan; expected unpatched faults separated from clean proposal passes',installed_dependencies_unchanged=True,hardware_access=False,proposal_applied_to_firmware=False)
 if a.results:a.results.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2));return bool(report['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
