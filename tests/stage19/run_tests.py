#!/usr/bin/env python3
"""Actual pinned SDK recovery source + production settings/startup; synthetic only."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from nvs_source_prepare import verify
SDK=['storage_clean','storage_repeat_clean','storage_orphan_blob','storage_orphan_write_failure','storage_mismatched_index','storage_corrupt_string_read','valid_entry','erased_partition','incomplete_entry','incomplete_write_failure','bad_entry_crc','duplicate_entries','corrupt_only','new_version','partial_header_read','partial_table_read','mutation_before_later_read_failure','freeing_recovery','freeing_write_failure','freeing_erase_failure','no_free_pages']
SETTINGS=['allocation_failure','missing_keys','missing_namespace','open_failure','not_initialized','type_mismatch','read_failure','string_read_failure','invalid_bool','invalid_channel','invalid_ssid','invalid_password','invalid_rgb','invalid_delay','autorun_without_script','oversized_string','missing_nul','embedded_nul','zero_length_string','valid_autorun','maximum_string','repeat_failure','save_after_failure','latched_failure','save_open_failure']
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sdk-source',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args();pin=verify(a.sdk_source);a.build_dir.mkdir(parents=True,exist_ok=True)
    src=a.sdk_source/'components/nvs_flash';common=['g++','-std=gnu++17','-DNO_DEBUG_STORAGE','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage19/mocks'),'-I'+str(src/'include'),'-I'+str(a.sdk_source/'components/esp_common/include')]
    sdk=a.build_dir/'sdk';subprocess.run(common+['-I'+str(src/'src'),'-I'+str(src/'private_include'),str(ROOT/'tests/stage19/sdk_recovery.cpp')]+[str(src/'src'/n) for n in ['nvs_page.cpp','nvs_pagemanager.cpp','nvs_types.cpp','nvs_item_hash_list.cpp','nvs_storage.cpp']]+['-o',str(sdk)],check=True)
    targets=[('sdk_recovery_source',sdk,SDK)]
    for safe in [False,True]:
        exe=a.build_dir/('settings-safe' if safe else 'settings-normal');flags=['-DEVILDUCK_HOST_TEST','-I'+str(ROOT/'tests/stage17/mocks'),'-I'+str(ROOT/'tests/stage1/mocks')]
        if safe:flags+=['-DEVILDUCK_DEPLOYMENT_SAFE_START=1']
        subprocess.run(common+flags+[str(ROOT/'tests/stage19/settings_startup.cpp'),'-o',str(exe)],check=True);targets.append(('safe' if safe else 'normal',exe,SETTINGS))
    results=[]
    for target,exe,names in targets:
        for name in names:
            r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
            operations=[dict(kind=o[0],address=int(o[1]),bytes=int(o[2]),success=o[3]=='1') for o in re.findall(r'^OP (\w+) (\d+) (\d+) ([01])$',r.stdout,re.M)]
            results.append(dict(name=name,target=target,status='PASS' if r.returncode==0 and m else 'FAIL',assertions=int(m[1]) if m else 0,flash_operations=operations,stdout=r.stdout,stderr=r.stderr));print(results[-1]['status'],target,name,flush=True)
    verify(a.sdk_source)
    out=dict(results=results,counts={s:sum(r['status']==s for r in results) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in results),sdk_source_commit=pin['commit'],sdk_recovery_source_executed=True,complete_sdk_initializer_executed=False,xtensa_sdk_library_executed=False,sanitizers='ASan/UBSan',owner_files_inspected=False,hardware_access=False)
    a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
