#!/usr/bin/env python3
"""Exact mocked HID payload/locale verification; ASan/UBSan, no USB hardware."""
import argparse
from pathlib import Path
import sys
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'stage1'))
from run_tests import compile_target, run_suite
TESTS = [
    'stage8_f1_f24_reference',
    'stage8_invalid_f_names',
    'stage8_navigation_editing_aliases',
    'stage8_named_punctuation_keys',
    'stage8_keypad_reference',
    'stage8_all_modifier_masks',
    'stage8_modifier_aliases',
    'stage8_hyphen_combinations',
    'stage8_malformed_hyphens_zero_hid',
    'stage8_case_tabs_and_order',
    'stage8_modifier_only_release',
    'stage8_six_key_limit_and_duplicates',
    'stage8_literal_punctuation_chord_us',
    'stage8_literal_punctuation_chord_de',
    'stage8_all_literal_punctuation_chords',
    'stage8_report_filter_and_raw_modifiers',
    'stage8_keycode_bounds_zero_hid',
    'stage8_us_ascii_table',
    'stage8_de_ascii_table',
    'stage8_us_ascii_translation',
    'stage8_de_ascii_translation',
    'stage8_printable_ascii_runtime_all_locales',
    'stage8_de_utf8_reference',
    'stage8_de_dead_keys',
    'stage8_locale_registration_and_switching',
    'stage8_named_keys_are_physical_not_locale_text',
    'stage8_unsupported_unicode_skip_warning',
    'stage8_utf8_bounds_and_invalid_sequences',
    'stage8_no_warn_supported_controls',
    'stage8_repeat_define_and_stringln_reports',
    'stage8_multiline_control_function_keyboard',
    'stage8_queue_refusal_press_and_release',
    'stage8_disconnect_mid_chord_recovery',
    'stage8_cancel_held_modifier_all_masks',
    'stage8_cancel_release_priority_new_live_command',
    'stage8_stop_and_runtime_error_release',
    'stage8_cancel_between_dead_key_strokes',
    'stage8_storage_fault_after_chord_release',
    'stage8_hid_disabled_and_live_ownership',
    'stage8_new_run_no_modifier_leak',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path)
    args = parser.parse_args()
    build = args.build_dir or Path(tempfile.mkdtemp(prefix='evilduck-stage8-'))
    exe = compile_target(ROOT / 'test_main.cpp', build, 'stage8_tests')
    failed = run_suite(exe, TESTS)
    probe = compile_target(ROOT / 'no_alloc.cpp', build, 'stage8_no_alloc')
    failed += run_suite(probe, ['stage8_translation_report_allocation_probe'])
    return bool(failed)
if __name__ == '__main__':
    raise SystemExit(main())
