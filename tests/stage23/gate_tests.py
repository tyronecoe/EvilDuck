#!/usr/bin/env python3
"""EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING. Synthetic only."""
import argparse, importlib.util, json, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from stage23_candidate import check_candidate, BASE
from nvs_source_prepare import verify
from startup_reference_prepare import verify as verify_reference
from patched_core import sha
CASES=['reject_'+s for s in 'missing_descriptor writable altered_flag offset size type subtype duplicate conflicting missing_table oom get_failure short_iteration canonical wrong_chip no_chip no_callback no_os permissive_callback table_bytes integrity_md5 table_read encrypted erase_geometry other_partition_flags old_slots'.split()]
CASES+='healthy cross_page_blob bad_page future_version freeing interrupted read_error corrupt_string write_erase diagnostics_unavailable'.split()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['sdk-source','partition-source','reference-source','candidate-core','build-dir','results']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();check_candidate(a.candidate_core);verify(a.sdk_source);verify_reference(a.reference_source)
 if a.build_dir.exists() or a.results.exists() or ROOT in a.build_dir.resolve().parents:raise ValueError('Fresh external outputs required')
 pin=json.loads((ROOT/'docs/stage20-partition-reference.json').read_text());expected=next(r['sha256'] for r in pin if r['url'].endswith('/partition_target.c'))
 if sha(a.partition_source)!=expected:raise ValueError('Partition source pin mismatch')
 spec=importlib.util.spec_from_file_location('slice',ROOT/'tests/stage15/run_tests.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 a.build_dir.mkdir(parents=True);source=a.partition_source.read_text()
 (a.build_dir/'partition_bodies.inc').write_text('\n'.join(m.body(source,'esp_err_t '+n+'(') for n in ['esp_partition_read','esp_partition_read_raw','esp_partition_write','esp_partition_write_raw','esp_partition_erase_range']))
 os=(a.reference_source/'components/spi_flash/spi_flash_os_func_app.c').read_text()
 patched_dir=a.build_dir/'patch/components/esp_partition';patched_dir.mkdir(parents=True)
 (patched_dir/'partition_target.c').write_text(source)
 subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(ROOT/'proposals/esp-idf-5.5-readonly-iterator-cleanup.patch')],cwd=a.build_dir/'patch',check=True)
 patched_source=(patched_dir/'partition_target.c').read_text()
 (a.build_dir/'main_region_bodies.inc').write_text(m.body(patched_source,'bool esp_partition_is_flash_region_writable(')+'\n'+m.body(os,'static esp_err_t main_flash_region_protected('))
 flash=(a.reference_source/'components/spi_flash/esp_flash_api.c').read_text()
 (a.build_dir/'check_write_address.inc').write_text(flash[flash.index('#define CHECK_WRITE_ADDRESS('):].split('\n\n',1)[0]+'\n')
 core=(a.candidate_core/'cores/esp32/esp32-hal-misc.c').read_text()
 prefix=core[core.index('static esp_err_t evilduck_nvs_error'):core.index('void initArduino()')]
 (a.build_dir/'candidate_startup.inc').write_text(prefix+m.body(core,'void initArduino()'))
 for src,dst in [('nvs_gate.h','evilduck_nvs_gate.h'),('expected_table.h','evilduck_expected_table.h')]: (a.build_dir/dst).write_bytes((BASE/src).read_bytes())
 src=a.sdk_source/'components/nvs_flash';exe=a.build_dir/'gate'
 args=['g++','-std=gnu++17','-O1','-g','-DNO_DEBUG_STORAGE','-DLINUX_TARGET=1','-DESP_PLATFORM=1','-DEVILDUCK_HOST_TEST','-DEVILDUCK_DEPLOYMENT_SAFE_START=1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
 args+=['-I'+str(d) for d in [ROOT/'tests/stage22/mocks',ROOT/'tests/stage21/mocks',ROOT/'tests/stage19/mocks',ROOT/'tests/stage17/mocks',ROOT/'tests/stage1/mocks',src/'src',src/'include',src/'private_include',a.sdk_source/'components/esp_common/include',a.build_dir]]
 args+=[str(ROOT/'tests/stage23/gate_startup.cpp')]+[str(src/'src'/n) for n in ['nvs_page.cpp','nvs_pagemanager.cpp','nvs_types.cpp','nvs_item_hash_list.cpp','nvs_storage.cpp','nvs_partition.cpp','nvs_partition_lookup.cpp','nvs_partition_manager.cpp','nvs_handle_simple.cpp','nvs_platform.cpp','nvs_api.cpp']]
 subprocess.run(args+['-o',str(exe)],check=True)
 rows=[]
 for name in CASES:
  r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30);match=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
  row=dict(name=name,status='PASS' if r.returncode==0 and match else 'FAIL',assertions=int(match[1]) if match else 0,stdout=r.stdout,stderr=r.stderr)
  rows.append(row);print(row['status'],name,flush=True)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),sanitizers='ASan/UBSan',complete_startup_executed=False,xtensa_executed=False,hardware_access=False,actual_sdk_plaintext_source=True,descriptor_and_bus_adapters=True)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
