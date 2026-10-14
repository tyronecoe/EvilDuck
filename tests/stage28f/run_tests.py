#!/usr/bin/env python3
"""Independent mock-only preview conformance. No production HID/device APIs."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CASES='operand_domain_and_exact_runtime_events malformed_preflight_atomicity_and_blocked_commands define_literal_modes_and_source_endings identical_holds_releases_require_fresh_acceptance persistent_shift_and_independent_owner_selective_release shared_key_and_reserved_owner_conflict hold_through_delay_function_if_while six_key_boundary_seventh_and_held_tap_rejection hundred_hold_and_release_retries_exact_ack cancel_before_during_after_each_ownership_ack callback_cancel_accepted_retry_failed_throw hold_release_report_failure_source_and_first_error clock_wrap_attempt_and_elapsed_exhaustion stop_error_limits_and_pending_delay_cleanup fresh_neutral_drain_retries_failure_and_restart program_borrow_restart_and_report_reentry forty_seeded_ownership_union_backpressure ownership_preflight_reader_fault_and_cancel_atomicity confirmed_owner_api_fresh_noops_invalid_and_aliases zero_cpp_heap_and_fixed_report_capture'.split()
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external outputs required')
a.build_dir.mkdir();exe=a.build_dir/'preview-tests'
command=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-DPREVIEW_CALL_FIXTURES="'+str(ROOT/'tests/stage28a/fixtures')+'"','-DPREVIEW_BLOCK_FIXTURES="'+str(ROOT/'tests/stage28b/fixtures')+'"','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',str(ROOT/'language_preview/core.cpp'),str(ROOT/'language_preview/keyboard.cpp'),str(ROOT/'language_preview/bridge.cpp'),str(ROOT/'tests/stage28f/test_ownership.cpp'),'-o',str(exe)]
subprocess.run(command,check=True)
rows=[]
for case in CASES:
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 row=dict(name=case,status='PASS' if not r.returncode and m else 'FAIL',assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],case,r.stderr if r.returncode else '')
report=dict(results=rows,counts={s:sum(row['status']==s for row in rows) for s in ['PASS','FAIL']},assertions=sum(row['assertions'] for row in rows),sanitizers='ASan/UBSan and leak detection enabled',hardware_access=False,scope='Stage28F mock source ownership commands only; regressions separate',command=command)
with a.results.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
raise SystemExit(bool(report['counts']['FAIL']))
