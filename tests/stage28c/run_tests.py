#!/usr/bin/env python3
"""Independent mock-only preview conformance. No production HID/device APIs."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
CASES='memory_mock_chunk_equivalence empty_eof_bom_crlf_boundaries source_line_expansion_boundaries table_and_arena_boundaries read_errors_pass_one_two_seek_exception zero_progress_retry_invalid_counts cancel_every_phase_and_restart partial_line_block_cancel_boundaries incremental_inventory_validation_work reentrancy_and_callback_cancellation runtime_borrow_multiple_sessions_destructor stable_source_contract_and_failed_reuse reader_lifetime_release_after_terminal invalid_api_budgets_and_full_retry_limit seeded_chunk_mutations atomic_line_and_expression_worst_bounds no_heap_compiler_read_and_inventory'.split()
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external outputs required')
a.build_dir.mkdir();exe=a.build_dir/'preview-tests'
command=['g++','-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-DPREVIEW_FIXTURES="'+str(ROOT/'tests/stage27b/fixtures')+'"','-DPREVIEW_CALL_FIXTURES="'+str(ROOT/'tests/stage28a/fixtures')+'"','-DPREVIEW_BLOCK_FIXTURES="'+str(ROOT/'tests/stage28b/fixtures')+'"','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',str(ROOT/'language_preview/core.cpp'),str(ROOT/'tests/stage28c/test_compile.cpp'),'-o',str(exe)]
subprocess.run(command,check=True)
rows=[]
for case in CASES:
 r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=20,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1'));m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout)
 row=dict(name=case,status='PASS' if not r.returncode and m else 'FAIL',assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],case,r.stderr if r.returncode else '')
report=dict(results=rows,counts={s:sum(row['status']==s for row in rows) for s in ['PASS','FAIL']},assertions=sum(row['assertions'] for row in rows),sanitizers='ASan/UBSan and leak detection enabled',hardware_access=False,scope='Stage28C cooperative compiler tests only; regressions separate',command=command)
with a.results.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
raise SystemExit(bool(report['counts']['FAIL']))
