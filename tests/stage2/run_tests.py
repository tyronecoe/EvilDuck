#!/usr/bin/env python3
"""Execute the full Stage 1 and Stage 2 suites with the same production mocks."""
import argparse
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT.parent / "stage1"))
from run_tests import TESTS as STAGE1_TESTS, compile_target, run_suite

TESTS = [
    "stage2_rem_comments",
    "stage2_required_rem_block_fixture",
    "stage2_comment_block_literal_commands",
    "stage2_unterminated_rem_block_zero_hid",
    "stage2_unmatched_end_rem_zero_hid",
    "stage2_lf_source",
    "stage2_crlf_source",
    "stage2_utf8_bom",
    "stage2_missing_final_newline",
    "stage2_blank_lines",
    "stage2_spaces_tabs_and_payload_preservation",
    "stage2_maximum_line_length",
    "stage2_overlong_line_zero_hid",
    "stage2_source_byte_limits",
    "stage2_source_line_limits",
    "stage2_mismatched_control_blocks_zero_hid",
    "stage2_unterminated_control_blocks_zero_hid",
    "stage2_duplicate_else_zero_hid",
    "stage2_block_depth_limit_zero_hid",
    "stage2_text_blocks_literal_mode_and_deferred_runtime",
    "stage2_unterminated_text_blocks_zero_hid",
    "stage2_unmatched_text_terminators_zero_hid",
    "stage2_mismatched_text_terminators_zero_hid",
    "stage2_unknown_commands_zero_hid",
    "stage2_keyword_prefixes_are_not_commands",
    "stage2_malformed_statements_zero_hid",
    "stage2_supported_extensions_and_bare_keys",
    "stage2_storage_read_seek_faults",
    "stage2_preflight_cooperative_stop_and_live_ownership",
    "stage2_live_validation_and_limits",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=pathlib.Path)
    args = parser.parse_args()
    build = args.build_dir or pathlib.Path(tempfile.mkdtemp(prefix="evilduck-stage2-"))
    first = compile_target(ROOT.parent / "stage1/test_main.cpp", build, "stage1_tests")
    failed = run_suite(first, STAGE1_TESTS)
    second = compile_target(ROOT / "test_main.cpp", build, "stage2_tests")
    failed += run_suite(second, TESTS)
    print(f"Combined suite: {len(STAGE1_TESTS)+len(TESTS)} processes, unexpected failures={failed}; language XFAILs remain separate.", flush=True)
    return bool(failed)

if __name__ == "__main__":
    raise SystemExit(main())
