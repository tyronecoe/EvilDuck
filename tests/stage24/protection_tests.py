#!/usr/bin/env python3
"""Actual pinned plaintext NVS C API with synthetic flash; no RTOS/target execution."""
import argparse, hashlib, importlib.util, json, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from nvs_source_prepare import verify
CASES='readonly_clean readonly_repeat readonly_cross_page_blob readonly_interrupted_entry readonly_bad_entry_crc readonly_bad_page_crc readonly_invalid_state readonly_freeing readonly_future_version readonly_read_failure readonly_partial_read readonly_missing_partition readonly_encrypted_partition readonly_empty_partition readonly_no_free_page readonly_orphan_blob readonly_mismatched_index readonly_corrupt_string readonly_corrupt_blob readonly_blob_gap readonly_open_write readonly_set readonly_erase_api readonly_gc_request partition_api_write partition_api_raw partition_api_erase writable_readonly_handle_corrupt_string main_direct_write_rejected main_direct_erase_rejected main_descriptor_alias_rejected callback_missing_write callback_missing_erase canonical_flag_changed main_region_no_protect main_region_boundaries'.split()
CASES+=['readonly_retry_failure','readonly_backend_write_error']
CASES+=['readonly_partition_ptr','main_partition_ptr_alias_rejected']
CASES+=['region_scan_missing_table']
OBS={'writable_readonly_handle_corrupt_string','callback_missing_write','callback_missing_erase','canonical_flag_changed','readonly_no_free_page','readonly_freeing','readonly_orphan_blob','readonly_mismatched_index','readonly_blob_gap'}
# Stage 24 independently resolves the missing-table permission observation.
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['sdk-source','partition-source','build-dir','results','patched-core','reference-source']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();pin=verify(a.sdk_source)
 if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external build/results required')
 if ROOT==a.build_dir.resolve() or ROOT in a.build_dir.resolve().parents:raise ValueError('Build must be external')
 source=a.partition_source.read_text();ref=json.loads((ROOT/'docs/stage20-partition-reference.json').read_text())
 expected=next(r['sha256'] for r in ref if r['url'].endswith('/partition_target.c'))
 if hashlib.sha256(a.partition_source.read_bytes()).hexdigest()!=expected:raise ValueError('Partition source pin mismatch')
 spec=importlib.util.spec_from_file_location('slice_tool',ROOT/'tests/stage15/run_tests.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
 from patched_core import check_sources
 from startup_reference_prepare import verify as verify_reference
 verify_reference(a.reference_source)
 check_sources(a.patched_core,True)
 a.build_dir.mkdir(parents=True);(a.build_dir/'partition_bodies.inc').write_text('\n'.join(s.body(source,'esp_err_t '+n+'(') for n in ['esp_partition_read','esp_partition_read_raw','esp_partition_write','esp_partition_write_raw','esp_partition_erase_range']))
 os_source=(a.reference_source/'components/spi_flash/spi_flash_os_func_app.c').read_text()
 patched_dir=a.build_dir/'patch/components/esp_partition';patched_dir.mkdir(parents=True)
 (patched_dir/'partition_target.c').write_text(source)
 subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(ROOT/'proposals/esp-idf-5.5-stage24-failclosed-scanner.patch')],cwd=a.build_dir/'patch',check=True)
 patched_source=(patched_dir/'partition_target.c').read_text()
 (a.build_dir/'main_region_bodies.inc').write_text(s.body(patched_source,'bool esp_partition_is_flash_region_writable(')+'\n'+s.body(os_source,'static esp_err_t main_flash_region_protected('))
 flash_source=(a.reference_source/'components/spi_flash/esp_flash_api.c').read_text()
 macro=flash_source[flash_source.index('#define CHECK_WRITE_ADDRESS('):].split('\n\n',1)[0]
 (a.build_dir/'check_write_address.inc').write_text(macro+'\n')
 src=a.sdk_source/'components/nvs_flash';exe=a.build_dir/'readonly'
 command=['g++','-std=gnu++17','-O1','-g','-DNO_DEBUG_STORAGE','-DLINUX_TARGET=1','-DESP_PLATFORM=1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
 command+=['-I'+str(d) for d in [ROOT/'tests/stage21/mocks',ROOT/'tests/stage19/mocks',src/'src',src/'include',src/'private_include',a.sdk_source/'components/esp_common/include',a.build_dir]]
 command+=[str(ROOT/'tests/stage24/protection.cpp')]+[str(src/'src'/n) for n in ['nvs_page.cpp','nvs_pagemanager.cpp','nvs_types.cpp','nvs_item_hash_list.cpp','nvs_storage.cpp','nvs_partition.cpp','nvs_partition_lookup.cpp','nvs_partition_manager.cpp','nvs_handle_simple.cpp','nvs_platform.cpp','nvs_api.cpp']]
 subprocess.run(command+['-o',str(exe)],check=True)
 core_source=(a.patched_core/'cores/esp32/esp32-hal-misc.c').read_text()
 prefix=core_source[core_source.index('static esp_err_t evilduck_nvs_error'):core_source.index('void initArduino()')]
 (a.build_dir/'core_startup.inc').write_text(prefix+s.body(core_source,'void initArduino()'))
 targets=[]
 for safe in [False,True]:
  startup=a.build_dir/('startup-safe' if safe else 'startup-normal');args=list(command)
  args[args.index(str(ROOT/'tests/stage24/protection.cpp'))]=str(ROOT/'tests/stage24/protection_startup.cpp')
  args+=['-DEVILDUCK_HOST_TEST','-I'+str(ROOT/'tests/stage17/mocks'),'-I'+str(ROOT/'tests/stage1/mocks')]
  if safe:args+=['-DEVILDUCK_DEPLOYMENT_SAFE_START=1']
  subprocess.run(args+['-o',str(startup)],check=True);targets.append(('safe' if safe else 'normal',startup))
 rows=[]
 for name in CASES:
  r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);status='PASS' if not r.returncode and m else 'FAIL'
  if status=='PASS' and name in OBS:status='OBSERVED'
  attempts=[dict(kind=k,address=int(o),bytes=int(n),error=int(e)) for k,o,n,e in re.findall(r'^ATTEMPT (\w+) (\d+) (\d+) (-?\d+)$',r.stdout,re.M)]
  lower=[dict(kind=k,address=int(o),bytes=int(n),success=e=='1') for k,o,n,e in re.findall(r'^LOWER (\w+) (\d+) (\d+) ([01])$',r.stdout,re.M)]
  rows.append(dict(name=name,status=status,assertions=int(m[1]) if m else 0,attempts=attempts,lower_flash_operations=lower,stdout=r.stdout,stderr=r.stderr));print(status,name,flush=True)
 verify(a.sdk_source)
 for profile,startup in targets:
  for name in ['healthy_writable','healthy_readonly','invalid_readonly','missing_readonly','settings_corrupt_readonly']:
   r=subprocess.run([str(startup),name],capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);status='PASS' if not r.returncode and m else 'FAIL'
   if status=='PASS' and profile=='normal' and name=='healthy_readonly':status='OBSERVED'
   attempts=[dict(kind=k,address=int(o),bytes=int(n),error=int(e)) for k,o,n,e in re.findall(r'^ATTEMPT (\w+) (\d+) (\d+) (-?\d+)$',r.stdout,re.M)]
   rows.append(dict(name=profile+'_'+name,status=status,assertions=int(m[1]) if m else 0,attempts=attempts,stdout=r.stdout,stderr=r.stderr,target='real C initializer/settings.cpp + exact core/app startup; service spies, no OTA/RTOS/global constructors'))
   print(status,profile,name,flush=True)
 check_sources(a.patched_core,True)
 verify_reference(a.reference_source)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL','OBSERVED']},assertions=sum(r['assertions'] for r in rows),source_commit=pin['commit'],sdk_iterator_cleanup_proposal=True,iterator_adapter_has_no_allocation=True,c_api_source_executed=True,platform_locks='actual LINUX_TARGET no-op branch; sequential tests',encryption_branch_executed=False,complete_idf_startup_executed=False,xtensa_sdk_executed=False,sanitizers='ASan/UBSan',owner_files_inspected=False,hardware_access=False)
 with a.results.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
