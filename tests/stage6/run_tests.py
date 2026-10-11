#!/usr/bin/env python3
"""Compile Stage 6 firmware sources with mocked hardware and ASan/UBSan."""
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
    'stage6_declarations_skipped',
    'stage6_statement_invocation',
    'stage6_multiple_calls',
    'stage6_forward_invocation_and_globals',
    'stage6_fixture_spiffs_and_sd',
    'stage6_explicit_void_return',
    'stage6_implicit_void_return',
    'stage6_integer_return_assignment',
    'stage6_boolean_return_conditions',
    'stage6_statement_discards_return_value',
    'stage6_void_value_rejected',
    'stage6_top_level_and_live_return_compatibility',
    'stage6_enter_and_modifier_return_inside_function',
    'stage6_return_unwinds_nested_control',
    'stage6_caller_control_restored',
    'stage6_nested_statement_calls',
    'stage6_nested_return_expressions',
    'stage6_multiple_calls_in_expression',
    'stage6_earlier_variable_operand_preserved',
    'stage6_eager_logical_calls',
    'stage6_inactive_conditions_do_not_call',
    'stage6_while_condition_calls_reevaluate',
    'stage6_while_condition_changes_count_as_progress',
    'stage6_else_if_function_condition',
    'stage6_numeric_commands_with_calls',
    'stage6_function_globals_text_and_file_commands',
    'stage6_define_function_operands_and_names',
    'stage6_macro_structural_creation_rejected',
    'stage6_rem_and_text_modes',
    'stage6_literal_text_does_not_invoke',
    'stage6_names_case_sensitive',
    'stage6_malformed_names_parameters_and_collisions',
    'stage6_unknown_calls_zero_hid',
    'stage6_invalid_call_arguments_and_whitespace',
    'stage6_duplicate_and_nested_declarations',
    'stage6_unterminated_and_unmatched_functions',
    'stage6_return_syntax_and_context_errors',
    'stage6_unused_body_preflight_errors_zero_hid',
    'stage6_function_table_boundary',
    'stage6_function_identifier_boundary',
    'stage6_nested_call_depth_boundary',
    'stage6_recursive_depth_exhaustion',
    'stage6_recursive_expression_and_global_visibility',
    'stage6_shared_control_depth_exhaustion',
    'stage6_runtime_undefined_initialization',
    'stage6_runtime_arithmetic_after_calls',
    'stage6_repeat_history_around_calls',
    'stage6_stop_active_and_inactive_function_branches',
    'stage6_cancel_pending_function_delay',
    'stage6_cancel_nested_function_text',
    'stage6_cancel_held_keys_in_call',
    'stage6_cancel_call_under_usb_backpressure',
    'stage6_cancel_expression_then_clean_run',
    'stage6_live_ownership_and_stop',
    'stage6_seek_error_entering_function',
    'stage6_seek_error_returning_to_caller',
    'stage6_read_error_and_source_change_in_function',
    'stage6_runtime_body_read_failure',
    'stage6_bom_crlf_header_and_final_newline',
    'stage6_empty_function_loop_stalls',
    'stage6_total_call_budget',
    'stage6_postfix_arithmetic_matches_existing_evaluator',
    'stage6_expression_bounds_and_postfix_errors',
    'stage6_long_declaration_skip_is_cooperative',
]
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = args.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage6-'))
    exe = compile_target(ROOT / 'test_main.cpp', build, 'stage6_tests')
    failed = run_suite(exe, TESTS)
    firmware = ROOT.parents[1] / 'EvilDuckS3'
    probe = build / 'stage6_no_alloc'
    subprocess.run(['g++', '-std=gnu++17', '-g', '-O1', '-Wall', '-Wextra',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                    '-I' + str(ROOT.parent / 'stage1/mocks'), '-I' + str(firmware),
                    str(ROOT / 'no_alloc.cpp'), str(firmware / 'duck_expr.cpp'),
                    str(firmware / 'duck_vars.cpp'), '-o', str(probe)], check=True)
    failed += subprocess.run([str(probe)], timeout=20).returncode != 0
    return bool(failed)

if __name__ == '__main__':
    raise SystemExit(main())
