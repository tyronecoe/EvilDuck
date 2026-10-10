#!/usr/bin/env python3
"""Compile Stage 3 firmware sources with mocked hardware and ASan/UBSan."""
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
    'stage3_addition', 'stage3_subtraction', 'stage3_multiplication', 'stage3_division',
    'stage3_modulo', 'stage3_exponentiation', 'stage3_equality', 'stage3_inequality',
    'stage3_less_than', 'stage3_greater_than', 'stage3_less_or_equal', 'stage3_greater_or_equal',
    'stage3_logical_and', 'stage3_logical_or', 'stage3_bitwise_and', 'stage3_bitwise_or',
    'stage3_left_shift', 'stage3_right_shift', 'stage3_precedence_and_grouping',
    'stage3_literals_booleans_and_whitespace', 'stage3_arithmetic_boundaries',
    'stage3_invalid_literals_and_unsupported_operators', 'stage3_malformed_expressions_and_limits',
    'stage3_numeric_declarations_assignment_and_no_hid', 'stage3_required_fixture_spiffs_and_sd',
    'stage3_variable_references_types_and_atomic_failure', 'stage3_text_compatibility_alias_and_read',
    'stage3_identifier_validation_and_table_exhaustion', 'stage3_preflight_zero_hid_and_runtime_errors',
    'stage3_define_global_forward_and_word_matching', 'stage3_define_single_pass_and_declaration_exemption',
    'stage3_define_comment_and_text_modes', 'stage3_define_duplicates_invalid_and_table_limits',
    'stage3_define_expansion_and_pool_boundaries', 'stage3_expression_timing_counts_and_cancellation',
    'stage3_collection_preflight_stop_and_state_isolation', 'stage3_interpolation_overflow_runtime_safe_stop',
    'stage3_syntax_mode_does_not_evaluate_runtime_values',
    'stage3_bounded_expression_fuzz',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = args.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage3-'))
    exe = compile_target(ROOT / 'test_main.cpp', build, 'stage3_tests')
    failed = run_suite(exe, TESTS)
    firmware = ROOT.parents[1] / 'EvilDuckS3'
    probe = build / 'stage3_no_alloc'
    subprocess.run(['g++', '-std=gnu++17', '-g', '-O1', '-Wall', '-Wextra',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                    '-I' + str(ROOT.parent / 'stage1/mocks'), '-I' + str(firmware),
                    str(ROOT / 'no_alloc.cpp'), str(firmware / 'duck_expr.cpp'),
                    str(firmware / 'duck_vars.cpp'), '-o', str(probe)], check=True)
    failed += subprocess.run([str(probe)], timeout=20).returncode != 0
    return bool(failed)

if __name__ == '__main__':
    raise SystemExit(main())
