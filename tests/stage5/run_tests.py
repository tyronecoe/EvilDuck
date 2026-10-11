#!/usr/bin/env python3
"""Compile Stage 5 firmware sources with mocked hardware and ASan/UBSan."""
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
    'stage5_false_while_following_commands',
    'stage5_zero_iteration_expressions',
    'stage5_single_iteration',
    'stage5_multiple_iterations',
    'stage5_decrementing_numeric_no_hid',
    'stage5_shared_expression_operators',
    'stage5_condition_reevaluated_at_header',
    'stage5_nested_two_loops',
    'stage5_nested_three_loops',
    'stage5_sequential_loops',
    'stage5_if_inside_while_else_if',
    'stage5_while_inside_if_else',
    'stage5_mixed_nested_structures',
    'stage5_fixture_spiffs_and_sd',
    'stage5_false_outer_suppresses_nested_conditions',
    'stage5_inactive_side_effects_and_assignments',
    'stage5_nested_updates_outer_variable',
    'stage5_global_declarations_reused',
    'stage5_exact_loop_depth',
    'stage5_mixed_exact_depth',
    'stage5_depth_plus_one_zero_hid',
    'stage5_malformed_conditions_zero_hid',
    'stage5_undefined_and_text_expression_rejection',
    'stage5_missing_unmatched_and_crossed_terminators',
    'stage5_keyword_boundaries_and_aliases',
    'stage5_legacy_bare_text_truthiness',
    'stage5_define_conditions_and_protected_keywords',
    'stage5_macro_manufactured_loop_delimiters_rejected',
    'stage5_define_collection_inside_inactive_loop',
    'stage5_rem_block_loop_text_ignored',
    'stage5_text_blocks_keep_literal_modes',
    'stage5_bom_crlf_no_final_newline_backedges',
    'stage5_header_across_read_budgets',
    'stage5_reader_marker_and_seek_boundaries',
    'stage5_runtime_seek_error',
    'stage5_runtime_read_error_after_backedge',
    'stage5_runtime_source_size_changed',
    'stage5_runtime_condition_error_and_inactive_skip',
    'stage5_runtime_undefined_path_dependent_variable',
    'stage5_repeat_structural_and_inactive_history',
    'stage5_repeat_expression_in_loop',
    'stage5_keyboard_combinations_in_loop',
    'stage5_expression_delays_in_loop',
    'stage5_stop_in_active_and_inactive_loops',
    'stage5_cancel_delay_inside_mixed_loop',
    'stage5_cancel_text_inside_nested_loop',
    'stage5_cancel_held_keys_and_usb_pressure',
    'stage5_control_only_loop_cooperative_and_live_ownership',
    'stage5_stalled_empty_loop_boundary',
    'stage5_stalled_same_assignment_and_inactive_actions',
    'stage5_nested_stall_not_masked_by_outer_progress',
    'stage5_variable_progress_beyond_stall_threshold',
    'stage5_total_iteration_limit_and_clean_restart',
    'stage5_exact_total_iteration_boundary',
    'stage5_variable_revision_atomic_and_reset',
    'stage5_cancellation_then_new_source',
    'stage5_large_inactive_region_cooperative',
    'stage5_small_nested_loop_reference_cases',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = args.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage5-'))
    exe = compile_target(ROOT / 'test_main.cpp', build, 'stage5_tests')
    failed = run_suite(exe, TESTS)
    firmware = ROOT.parents[1] / 'EvilDuckS3'
    probe = build / 'stage5_no_alloc'
    subprocess.run(['g++', '-std=gnu++17', '-g', '-O1', '-Wall', '-Wextra',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                    '-I' + str(ROOT.parent / 'stage1/mocks'), '-I' + str(firmware),
                    str(ROOT / 'no_alloc.cpp'), str(firmware / 'duck_expr.cpp'),
                    str(firmware / 'duck_vars.cpp'), '-o', str(probe)], check=True)
    failed += subprocess.run([str(probe)], timeout=20).returncode != 0
    return bool(failed)

if __name__ == '__main__':
    raise SystemExit(main())
