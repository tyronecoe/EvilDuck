#!/usr/bin/env python3
"""Small new observable fixtures + selected existing suites. Mock output only."""
import argparse,importlib.util,json,os,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
old=load(ROOT/'tests/stage1/run_tests.py','legacy_harness');rows=[];commands=[]
# Reuse the production-module compiler. Add fixture path via a generated wrapper only.
wrapper=a.build_dir/'legacy-main.cpp';wrapper.write_text('#define COMPAT_FIXTURES '+json.dumps(str(ROOT/'tests/compatibility_pass/fixtures'))+'\n#include '+json.dumps(str(ROOT/'tests/compatibility_pass/legacy.cpp'))+'\n')
legacy=old.compile_target(wrapper,a.build_dir,'legacy')
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
def run(exe,n,group):
 r=subprocess.run([str(exe),n],capture_output=True,text=True,timeout=30,env=env);m=re.search(r'PASS \w+ \((\d+) assertions\)',r.stdout);row=dict(name=n,group=group,status='PASS' if r.returncode==0 and m else 'FAIL',exit=r.returncode,assertions=int(m[1]) if m else 0,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(row['status'],n,r.stderr,flush=True)
for n in ['legacy_variable_prefixes','legacy_define_prefixes','legacy_function_prefixes','legacy_interpolation_prefixes','legacy_unverified_aliases_rejected']:run(legacy,n,'new_legacy')
for n in ['stage8_modifier_aliases','stage8_hyphen_combinations','stage8_modifier_only_release','stage8_stop_and_runtime_error_release','stage8_multiline_control_function_keyboard']:run(legacy,n,'reused_keyboard')
for stage,names in [(3,['stage3_define_global_forward_and_word_matching','stage3_define_single_pass_and_declaration_exemption','stage3_define_duplicates_invalid_and_table_limits']), (6,['stage6_explicit_void_return','stage6_implicit_void_return','stage6_nested_return_expressions','stage6_return_unwinds_nested_control','stage6_inactive_conditions_do_not_call','stage6_unused_body_preflight_errors_zero_hid','stage6_unterminated_and_unmatched_functions','stage6_caller_control_restored','stage6_while_condition_calls_reevaluate']), (7,['stage7_string_leading_and_trailing_whitespace','stage7_stringln_removes_one_leading_tab','stage7_repeat_literal_text_and_whitespace'])]:
 exe=old.compile_target(ROOT/f'tests/stage{stage}/test_main.cpp',a.build_dir,'stage'+str(stage))
 for n in names:run(exe,n,'reused_language')
sys.path.insert(0,str(ROOT/'tests/stage28x'));x=load(ROOT/'tests/stage28x/run_tests.py','x_harness');s=x.prepare(a.build_dir/'x-sources');x.native_sources(s);cmd=x.command(a.build_dir/'route-b',s,ROOT/'tests/compatibility_pass/route_b.cpp');cmd.insert(1,'-DCOMPAT_FIXTURES='+json.dumps(str(ROOT/'tests/compatibility_pass/fixtures')));commands.append(cmd);subprocess.run(cmd,check=True)
for n in ['route_b_variable_prefixes','route_b_define_prefixes','route_b_function_prefixes','route_b_unverified_aliases_rejected','route_b_inactive_unsupported_rejected','route_b_bad_prefix_identifier_rejected','route_b_ownership_adapter_rejected']:run(a.build_dir/'route-b',n,'new_actual_route_b')
for n in ['W11','W15','W18','W19','W20','W33','W34']:run(a.build_dir/'route-b',n,'reused_actual_route_b')
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,commands=commands,legacy_compile_harness='unchanged tests/stage1/run_tests.py compile_target',sanitizers='ASan/UBSan/leaks enabled',physical=False,firmware_sources_changed=False)
a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts'],out['assertions']);raise SystemExit(bool(out['counts']['FAIL']))
