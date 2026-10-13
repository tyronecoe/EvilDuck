#!/usr/bin/env python3
"""Independent mock-only preview conformance. No production HID/device APIs."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CASES='harmless_fixture_files empty_comments line_endings_whitespace all_numeric_operators precedence_and_grouping variables_global_redeclaration constants_replacement if_else_chains while_and_mixed_flow inactive_side_effects functions_and_returns named_key_event_order delay_clock_and_wrap retry_does_not_duplicate cancellation_and_sink_errors budgets_and_no_progress clean_sessions_and_borrowing reentrant_callbacks malformed_structure_zero_events arithmetic_and_syntax_failures unsupported_explicit_rejection source_and_table_limits nesting_and_expression_boundaries deterministic_source_mutations no_core_heap_allocations'.split()
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external outputs required')
a.build_dir.mkdir();exe=a.build_dir/'preview-tests'
command=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',str(ROOT/'language_preview/core.cpp'),str(ROOT/'tests/stage27b/test_core.cpp'),'-o',str(exe)]
subprocess.run(command,check=True)
rows=[]
for case in CASES:
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 row=dict(name=case,status='PASS' if not r.returncode and m else 'FAIL',assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],case,r.stderr if r.returncode else '')
report=dict(results=rows,counts={s:sum(row['status']==s for row in rows) for s in ['PASS','FAIL']},assertions=sum(row['assertions'] for row in rows),sanitizers='ASan/UBSan and leak detection enabled',hardware_access=False,scope='New independent preview only; historical suites not reused',command=command)
with a.results.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
raise SystemExit(bool(report['counts']['FAIL']))
