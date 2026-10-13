#!/usr/bin/env python3
"""Focused production startup/settings/SPIFFS/storage tests, synthetic interfaces only."""
import argparse,json,re,subprocess,sys,os
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CASES='network_failure valid_fresh missing_namespace missing_ssid missing_password missing_web_password blank_password blank_web_password legacy_password short_password long_password long_ssid newline_credentials credential_type_mismatch credential_read_failure allocation_failure corrupt_nul nvs_open_failure nvs_startup_failure stored_autorun mount_failure missing_filesystem interrupted_mount wrong_layout readonly_layout partition_lookup_failure duplicate_partition missing_partition wrong_chip settings_controls'.split()
def main():
 p=argparse.ArgumentParser();p.add_argument('--sdk-source',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
 sys.path.insert(0,str(ROOT/'tools'));from nvs_source_prepare import verify
 verify(a.sdk_source)
 if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external output required')
 a.build_dir.mkdir();exe=a.build_dir/'controlled-startup'
 includes=[ROOT/'tests/stage25_startup/mocks',ROOT/'tests/stage10/mocks',ROOT/'tests/stage19/mocks',ROOT/'tests/stage17/mocks',ROOT/'tests/stage1/mocks',a.sdk_source/'components/nvs_flash/include',a.sdk_source/'components/esp_common/include']
 cmd=['g++','-std=gnu++17','-O1','-g','-DEVILDUCK_HOST_TEST','-DEVILDUCK_CONTROLLED_START=1','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']+['-I'+str(d) for d in includes]+[str(ROOT/'tests/stage25_startup/test_main.cpp'),'-o',str(exe)]
 subprocess.run(cmd,check=True)
 rows=[]
 for name in CASES:
  r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
  row=dict(name=name,status='PASS' if not r.returncode and m else 'FAIL',assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],name)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),sanitizers='ASan/UBSan; leak detection enabled',production_sources=['settings.cpp','spiffs.cpp','storage.cpp','EvilDuckS3.ino','controlled_layout.h'],adapters=['typed NVS API','partition iterator/table','SPIFFS/SD File','services/clock/USB'],complete_sdk_startup_executed=False,hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
