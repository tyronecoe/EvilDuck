#!/usr/bin/env python3
"""Execute real S3 multiline runtime against mocked interfaces with ASan/UBSan."""
import argparse
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'stage1'))
from run_tests import compile_target, run_suite
TESTS = [
    'stage7_empty_blocks',
    'stage7_single_line_string',
    'stage7_single_line_stringln',
    'stage7_string_multiline_no_separators',
    'stage7_stringln_multiline_enters',
    'stage7_string_blank_lines',
    'stage7_stringln_blank_lines',
    'stage7_string_leading_and_trailing_whitespace',
    'stage7_stringln_removes_one_leading_tab',
    'stage7_internal_tabs_preserved',
    'stage7_literal_command_keywords',
    'stage7_terminator_prefixes_are_literal',
    'stage7_case_and_indented_delimiters',
    'stage7_inline_compatibility_unchanged',
    'stage7_lf_and_crlf_equivalent',
    'stage7_bom_only_at_source_start',
    'stage7_no_final_newline',
    'stage7_quoted_text_no_unescaping',
    'stage7_numeric_boolean_and_text_interpolation',
    'stage7_unknown_host_variables_are_literal',
    'stage7_variable_replacement_is_single_pass',
    'stage7_define_hash_and_word_replacement',
    'stage7_define_body_not_collected_or_expanded',
    'stage7_define_single_pass_and_variable_order',
    'stage7_expansion_cannot_close_or_execute',
    'stage7_value_whitespace_after_source_dedent',
    'stage7_maximum_body_line',
    'stage7_overlong_body_zero_hid',
    'stage7_define_expansion_boundary',
    'stage7_interpolation_boundary_and_overflow',
    'stage7_inactive_interpolation_has_no_runtime_effect',
    'stage7_unterminated_after_output_zero_hid',
    'stage7_mismatched_or_argument_terminators_zero_hid',
    'stage7_unmatched_terminators_zero_hid',
    'stage7_literal_openers_inside_body',
    'stage7_fixture_spiffs_and_sd',
    'stage7_if_else_active_inactive_blocks',
    'stage7_zero_iteration_loop_blocks',
    'stage7_nested_loops_interpolate_current_values',
    'stage7_function_repeat_calls_and_return',
    'stage7_nested_functions_with_blocks',
    'stage7_recursive_calls_with_blocks',
    'stage7_repeat_literal_text_and_whitespace',
    'stage7_repeat_blank_stringln',
    'stage7_empty_string_does_not_replace_history',
    'stage7_repeat_interpolates_again',
    'stage7_default_delays_per_body_line',
    'stage7_cancel_default_delay',
    'stage7_cancel_halfway_through_typing',
    'stage7_cancel_held_shift_and_usb_release_retry',
    'stage7_usb_backpressure_lossless_and_no_readahead',
    'stage7_stop_command_after_block',
    'stage7_live_ownership_and_clean_run',
    'stage7_live_block_opener_rejected',
    'stage7_preflight_source_errors_zero_hid',
    'stage7_rewind_seek_error_zero_hid',
    'stage7_runtime_body_read_error_spiffs_and_sd',
    'stage7_runtime_source_change',
    'stage7_loop_backedge_seek_error',
    'stage7_function_return_seek_error',
    'stage7_large_block_streamed_and_cooperative',
    'stage7_cancel_large_block_preflight',
    'stage7_source_limits_zero_hid',
    'stage7_hid_disabled_block_has_no_output',
    'stage7_malformed_later_control_zero_hid',
    'stage7_control_nesting_boundaries',
    'stage7_text_blocks_do_not_execute_calls',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = args.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage7-'))
    exe = compile_target(ROOT / 'test_main.cpp', build, 'stage7_tests')
    failed = run_suite(exe, TESTS)
    probe = compile_target(ROOT / 'bounded_text.cpp', build, 'stage7_bounded_text')
    failed += run_suite(probe, ['stage7_bounded_line_allocation_probe'])
    return bool(failed)
if __name__ == '__main__':
    raise SystemExit(main())
