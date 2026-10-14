#!/usr/bin/env python3
"""Independent mock-only preview conformance. No production HID/device APIs."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CASES='empty_sync_and_exact_single_key all_modifier_bits_and_combinations two_owners_shared_keys_and_modifiers idempotence_unmatched_invalid_usage_owner six_keys_seventh_reject_and_recovery single_owner_capacity_and_reordering persistent_transient_shift_and_lowercase_conflict us_printable_mapping_reference_vectors unsupported_bytes_and_held_tap_policy named_function_navigation_key_usage_vectors retry_press_and_release_without_replay cancel_all_phases_and_explicit_neutral_drain failure_exception_and_uncertain_release drain_retry_failure_and_retry_exhaustion wrap_timeout_and_stuck_clock reentrant_cancel_accepted_report_is_retained queue_single_action_and_restart_isolation budget_validation_and_noop_deduplication seeded_ownership_property_ordering hostile_cancel_retry_throw_and_one_attempt_bound zero_heap_planner_hot_path'.split()
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external outputs required')
a.build_dir.mkdir();exe=a.build_dir/'preview-tests'
command=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-DPREVIEW_CALL_FIXTURES="'+str(ROOT/'tests/stage28a/fixtures')+'"','-DPREVIEW_BLOCK_FIXTURES="'+str(ROOT/'tests/stage28b/fixtures')+'"','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',str(ROOT/'language_preview/core.cpp'),str(ROOT/'language_preview/keyboard.cpp'),str(ROOT/'tests/stage28d/test_keyboard.cpp'),'-o',str(exe)]
subprocess.run(command,check=True)
rows=[]
for case in CASES:
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 row=dict(name=case,status='PASS' if not r.returncode and m else 'FAIL',assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],case,r.stderr if r.returncode else '')
report=dict(results=rows,counts={s:sum(row['status']==s for row in rows) for s in ['PASS','FAIL']},assertions=sum(row['assertions'] for row in rows),sanitizers='ASan/UBSan and leak detection enabled',hardware_access=False,scope='Stage28D mock keyboard planner only; regressions separate',command=command)
with a.results.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
raise SystemExit(bool(report['counts']['FAIL']))
