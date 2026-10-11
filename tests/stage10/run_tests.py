#!/usr/bin/env python3
"""Fault-test production MSC/attackmode/SD adapters and runtime with no hardware."""
import argparse,subprocess,tempfile,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TESTS=[
 'startup_success_truthful','startup_missing_card','startup_missing_image_no_create','startup_wrong_size_no_truncate',
 'startup_open_failure','startup_probe_seek_failure','startup_probe_short_read','startup_sdk_failure_cleanup',
 'retry_failed_startup','repeated_begin_idempotent','retry_ejected_media','stale_host_load_after_off','stale_host_load_after_cancel','writable_reset_after_end',
 'read_nonzero_offset','write_nonzero_offset','cross_sector_unaligned','last_byte_and_exact_end',
 'invalid_range_and_overflow','zero_length_null','null_nonzero','transfer_limit',
 'read_seek_failure_no_wrong_read','write_seek_failure_no_wrong_write','short_read_quarantines',
 'short_write_prefix_and_quarantine','card_removal_callback','card_removal_main_loop','backing_size_changed',
 'fault_cleanup_and_explicit_recovery','eject_load_and_power_stop','cancel_before_open','cancel_after_open',
 'timeout_wrap_safe','media_absent_until_validated','script_waits_for_storage','script_startup_failure_stops_tail',
 'stop_pending_startup','stop_preserves_active_media','live_cli_ownership_while_preparing','script_and_host_activity',
 'function_condition_storage_startup','live_cli_failure_status_and_retry','callback_lock_contention_busy','callback_error_storm_no_io','concurrent_callback_mode_stop','sd_adapter_interleaving',
 'sd_adapter_removal_and_remount','off_cancels_pending','repeated_failure_recovery','no_callback_heap_allocation'
]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build-dir',type=Path);p.add_argument('--results',type=Path);a=p.parse_args()
 b=a.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage10-'));b.mkdir(parents=True,exist_ok=True)
 modules=['com','duckscript','duck_vars','duck_keys','keyboard_locale','locales','hid_backend','script_log','cli','script_source','script_parser','duck_expr','duck_constants','script_functions','attackmode','usb_msc','sd_card']
 sources=[ROOT/'tests/stage10/test_main.cpp',ROOT/'tests/stage1/mocks/host.cpp']+[ROOT/'EvilDuckS3'/f'{m}.cpp' for m in modules]
 exe=b/'stage10_tests';subprocess.run(['g++','-std=gnu++17','-g','-O1','-Wall','-Wextra','-pthread','-DEVILDUCK_HOST_TEST','-DEVILDUCK_PRODUCTION_STORAGE','-DCONFIG_TINYUSB_MSC_ENABLED=1','-DCONFIG_TINYUSB_MSC_BUFSIZE=4096','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage10/mocks'),'-I'+str(ROOT/'tests/stage1/mocks'),'-I'+str(ROOT/'EvilDuckS3'),*map(str,sources),'-o',str(exe)],check=True)
 results=[]
 for name in TESTS:
  r=subprocess.run([str(exe),name],capture_output=True,text=True,timeout=30)
  print(r.stdout,r.stderr,end='',flush=True)
  count=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
  results.append(dict(name=name,status='PASS' if r.returncode==0 else 'FAIL',assertions=int(count[1]) if count else 0,stdout=r.stdout,stderr=r.stderr))
 # Compile the real fallback path too; no SDK or hardware calls are linked.
 unavailable=b/'stage10_unavailable'
 subprocess.run(['g++','-std=gnu++17','-g','-O1','-Wall','-Wextra','-pthread','-DEVILDUCK_HOST_TEST','-DCONFIG_TINYUSB_MSC_ENABLED=0','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage1/mocks'),'-I'+str(ROOT/'EvilDuckS3'),str(ROOT/'tests/stage10/unavailable.cpp'),str(ROOT/'EvilDuckS3/usb_msc.cpp'),str(ROOT/'EvilDuckS3/attackmode.cpp'),'-o',str(unavailable)],check=True)
 r=subprocess.run([str(unavailable)],capture_output=True,text=True,timeout=30)
 print(r.stdout,r.stderr,end='',flush=True)
 results.append(dict(name='build_without_msc_reports_unavailable',status='PASS' if r.returncode==0 else 'FAIL',assertions=4 if r.returncode==0 else 0,stdout=r.stdout,stderr=r.stderr))
 report=dict(pass_count=sum(x['status']=='PASS' for x in results),fail_count=sum(x['status']=='FAIL' for x in results),assertions=sum(x['assertions'] for x in results),results=results,sanitizers='ASan/UBSan',hardware_access=False)
 if a.results:a.results.write_text(json.dumps(report,indent=2)+'\n')
 print(f"Stage10: {report['pass_count']} PASS, {report['fail_count']} FAIL, {report['assertions']} assertions")
 return bool(report['fail_count'])
if __name__=='__main__':raise SystemExit(main())
