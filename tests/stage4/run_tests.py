#!/usr/bin/env python3
"""Compile Stage 4 firmware sources with mocked hardware and ASan/UBSan."""
import argparse
from pathlib import Path
import sys
import subprocess
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'stage1'))
from run_tests import compile_target, run_suite

TESTS = [
    'stage4_simple_true_if',
    'stage4_simple_false_if',
    'stage4_if_else_true_path',
    'stage4_if_else_false_path',
    'stage4_nested_true_true',
    'stage4_nested_true_false',
    'stage4_outer_false_nested_inactive',
    'stage4_multiple_nesting_levels',
    'stage4_exact_nesting_limit',
    'stage4_nesting_limit_plus_one',
    'stage4_else_if_first_true',
    'stage4_else_if_middle_true',
    'stage4_else_if_final_else',
    'stage4_else_if_multiple_entries',
    'stage4_nested_else_if_chains',
    'stage4_no_branch_true_without_else',
    'stage4_selected_assignments_and_later_conditions',
    'stage4_inactive_side_effects',
    'stage4_required_fixture_spiffs_and_sd',
    'stage4_define_conditions_and_protected_keywords',
    'stage4_macro_manufactured_structures_rejected',
    'stage4_compound_hex_boolean_conditions',
    'stage4_malformed_expressions_zero_hid',
    'stage4_undefined_and_text_variables',
    'stage4_missing_end_if',
    'stage4_unexpected_end_if',
    'stage4_duplicate_else',
    'stage4_else_outside_if',
    'stage4_malformed_then_and_else_if',
    'stage4_invalid_branch_ordering',
    'stage4_rem_block_conditional_text',
    'stage4_text_blocks_preserve_literal_modes',
    'stage4_stop_active_and_inactive_branches',
    'stage4_external_cancel_delay_text_and_keys',
    'stage4_repeat_active_inactive_and_structural_history',
    'stage4_clean_state_between_runs_and_live_ownership',
    'stage4_runtime_errors_only_in_eligible_conditions',
    'stage4_cooperative_large_inactive_region_and_preflight',
    'stage4_legacy_compatibility_aliases',
    'stage4_keyword_boundaries_whitespace_and_case',
    'stage4_mixed_while_nesting',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = args.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage4-'))
    exe = compile_target(ROOT / 'test_main.cpp', build, 'stage4_tests')
    failed = run_suite(exe, TESTS)
    firmware = ROOT.parents[1] / 'EvilDuckS3'
    probe = build / 'stage4_no_alloc'
    subprocess.run(['g++', '-std=gnu++17', '-g', '-O1', '-Wall', '-Wextra',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                    '-I' + str(ROOT.parent / 'stage1/mocks'), '-I' + str(firmware),
                    str(ROOT / 'no_alloc.cpp'), str(firmware / 'duck_expr.cpp'),
                    str(firmware / 'duck_vars.cpp'), '-o', str(probe)], check=True)
    failed += subprocess.run([str(probe)], timeout=20).returncode != 0
    return bool(failed)

if __name__ == '__main__':
    raise SystemExit(main())
