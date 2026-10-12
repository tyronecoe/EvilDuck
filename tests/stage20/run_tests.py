#!/usr/bin/env python3
"""Production settings writes + pinned SDK component alternatives; no hardware."""
import argparse,json,re,subprocess,sys,hashlib,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from nvs_source_prepare import verify
SAVES=['busy_save','busy_reset','healthy_save','valid_autorun','valid_reset','unloaded_save','unloaded_reset','read_failure_save','open_failure','open_full','commit_failure','invalid_delay','invalid_web_length','embedded_nul','set_full','set_flash_error','failed_set_may_change_bytes','mixed_autorun_after_failure','reset_failure']+['set_failure_'+str(n) for n in range(1,13)]
READONLY=['readonly_corrupt_string','corrupt_read_becomes_not_found','readonly_clean','readonly_incomplete_entry','readonly_bad_entry_crc','readonly_freeing','readonly_corrupt_activation']
def main():
 p=argparse.ArgumentParser()
 for name in ['sdk-source','partition-source','build-dir','results']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();verify(a.sdk_source);
 reference=json.loads((ROOT/'docs/stage20-partition-reference.json').read_text());expected=next(r['sha256'] for r in reference if r['url'].endswith('/partition_target.c'));source=a.partition_source.read_text();assert hashlib.sha256(a.partition_source.read_bytes()).hexdigest()==expected
 spec=importlib.util.spec_from_file_location('slice',ROOT/'tests/stage15/run_tests.py');slice_tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(slice_tool)
 a.build_dir.mkdir(parents=True,exist_ok=True);src=a.sdk_source/'components/nvs_flash'
 (a.build_dir/'actual_partition_api.inc').write_text('\n'.join(slice_tool.body(source,'esp_err_t '+n+'(') for n in ['esp_partition_write','esp_partition_write_raw','esp_partition_erase_range']))
 common=['g++','-std=gnu++17','-DEVILDUCK_HOST_TEST','-pthread','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage19/mocks'),'-I'+str(src/'include'),'-I'+str(a.sdk_source/'components/esp_common/include')]
 save=a.build_dir/'save';subprocess.run(common+[str(ROOT/'tests/stage20/settings_save.cpp'),'-o',str(save)],check=True)
 sdk=a.build_dir/'readonly';subprocess.run(common+['-DNO_DEBUG_STORAGE','-I'+str(a.build_dir),'-I'+str(src/'src'),'-I'+str(src/'private_include'),str(ROOT/'tests/stage20/readonly_source.cpp')]+[str(src/'src'/n) for n in ['nvs_page.cpp','nvs_pagemanager.cpp','nvs_types.cpp','nvs_item_hash_list.cpp','nvs_storage.cpp']]+['-o',str(sdk)],check=True)
 rows=[]
 for target,exe,names in [('application_nvs_api_standin',save,SAVES+['interrupted_save']),('actual_sdk_component_source',sdk,READONLY)]:
  for name in names:
   r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
   status='PASS' if not r.returncode and m else 'FAIL';assertions=int(m[1]) if m else 0
   if name=='interrupted_save':status='OBSERVED' if r.returncode==77 and 'SIMULATED_POWER_LOSS sets=4 commits=0' in r.stdout else 'FAIL';assertions=2
   if name=='corrupt_read_becomes_not_found' and status=='PASS':status='OBSERVED'
   operations=[dict(kind=o[0],address=int(o[1]),bytes=int(o[2]),success=o[3]=='1') for o in re.findall(r'^OP (\w+) (\d+) (\d+) ([01])$',r.stdout,re.M)]
   rows.append(dict(name=name,target=target,status=status,assertions=assertions,stdout=r.stdout,stderr=r.stderr,flash_operations=operations));print(status,target,name,flush=True)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL','OBSERVED']},assertions=sum(r['assertions'] for r in rows),sdk_binary_executed=False,sdk_source_components_executed=True,physical_operations=False,sanitizers='ASan/UBSan',original_nvs_immutability_proven=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
