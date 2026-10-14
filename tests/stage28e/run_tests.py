#!/usr/bin/env python3
"""Independent mock-only preview conformance. No production HID/device APIs."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CASES='initial_sync_and_identical_neighbors mixed_us_punctuation_exact_vectors multiline_blank_tabs_and_enter_order function_continuations_and_control_flow source_ack_waits_for_restoration press_release_long_retry_no_replay delay_timing_zero_and_two_segments wrap_and_stalled_delay_clock persistent_modifier_restore_and_completion_cleanup invalid_event_boundaries_and_bad_source held_key_and_seventh_rejection failed_and_throwing_report_sink cancel_every_handshake_and_delay_phase callback_cancel_accept_retry_throw explicit_drain_only_neutral_and_failures timeouts_after_press_and_attempt_budget stop_runtime_arithmetic_and_step_limits reentrant_report_source_and_program_borrow multi_bridge_lifetime_restart_and_no_stale_ids seeded_backpressure_exact_pairs sync_failure_and_cleanup_budget_boundaries delay_acceptance_after_retried_restoration callee_multiline_fault_source_location zero_heap_bridge_pipeline'.split()
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external outputs required')
a.build_dir.mkdir();exe=a.build_dir/'preview-tests'
command=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-DPREVIEW_CALL_FIXTURES="'+str(ROOT/'tests/stage28a/fixtures')+'"','-DPREVIEW_BLOCK_FIXTURES="'+str(ROOT/'tests/stage28b/fixtures')+'"','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',str(ROOT/'language_preview/core.cpp'),str(ROOT/'language_preview/keyboard.cpp'),str(ROOT/'language_preview/bridge.cpp'),str(ROOT/'tests/stage28e/test_bridge.cpp'),'-o',str(exe)]
subprocess.run(command,check=True)
rows=[]
for case in CASES:
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 row=dict(name=case,status='PASS' if not r.returncode and m else 'FAIL',assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],case,r.stderr if r.returncode else '')
report=dict(results=rows,counts={s:sum(row['status']==s for row in rows) for s in ['PASS','FAIL']},assertions=sum(row['assertions'] for row in rows),sanitizers='ASan/UBSan and leak detection enabled',hardware_access=False,scope='Stage28E mock Runtime/planner bridge only; regressions separate',command=command)
with a.results.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
raise SystemExit(bool(report['counts']['FAIL']))
