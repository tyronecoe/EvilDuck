# Stage28B exact executed results

All three suites compile actual language_preview/core.cpp with mocks, ASan/UBSan and leak detection.
No physical HID/storage/owner files. Historical firmware diagnostic classifications are untouched, not rerun or counted here.

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| stage27b_regression | 25 | 0 | 2543 |
| stage28a_regression | 23 | 0 | 526 |
| stage28b_new | 26 | 0 | 4733 |
| Total | 74 | 0 | 7802 |

No skipped/XFAIL/XPASS cases in these preview runners. Every name/result below was executed.

## stage27b_regression

| Exact test group | Result | Assertions |
|---|---|---:|
| harmless_fixture_files | PASS | 13 |
| empty_comments | PASS | 30 |
| line_endings_whitespace | PASS | 24 |
| all_numeric_operators | PASS | 168 |
| precedence_and_grouping | PASS | 88 |
| variables_global_redeclaration | PASS | 43 |
| constants_replacement | PASS | 48 |
| if_else_chains | PASS | 30 |
| while_and_mixed_flow | PASS | 16 |
| inactive_side_effects | PASS | 8 |
| functions_and_returns | PASS | 29 |
| named_key_event_order | PASS | 18 |
| delay_clock_and_wrap | PASS | 13 |
| retry_does_not_duplicate | PASS | 9 |
| cancellation_and_sink_errors | PASS | 32 |
| budgets_and_no_progress | PASS | 21 |
| clean_sessions_and_borrowing | PASS | 24 |
| reentrant_callbacks | PASS | 10 |
| malformed_structure_zero_events | PASS | 64 |
| arithmetic_and_syntax_failures | PASS | 139 |
| unsupported_explicit_rejection | PASS | 67 |
| source_and_table_limits | PASS | 99 |
| nesting_and_expression_boundaries | PASS | 46 |
| deterministic_source_mutations | PASS | 1500 |
| no_core_heap_allocations | PASS | 4 |

## stage28a_regression

| Exact test group | Result | Assertions |
|---|---|---:|
| required_fixture | PASS | 7 |
| assignment_forward_nested_arithmetic | PASS | 8 |
| return_of_call_and_boolean | PASS | 8 |
| if_else_if_selected_calls_only | PASS | 6 |
| while_reevaluation_zero_iteration | PASS | 8 |
| left_to_right_capture_eager_power | PASS | 14 |
| delay_call_single_timing_owner | PASS | 12 |
| static_void_unknown_arity_zero_output | PASS | 52 |
| runtime_void_no_stale_return | PASS | 19 |
| depth_limit_cycles_and_frames | PASS | 32 |
| arithmetic_results_and_source_mapping | PASS | 31 |
| cancellation_stop_suspended_and_restart | PASS | 21 |
| retry_failure_timeout_and_budget_during_call | PASS | 26 |
| bounded_work_cooperative_and_reentrant | PASS | 27 |
| expression_function_token_limits | PASS | 21 |
| operators_with_function_operands | PASS | 144 |
| standalone_inside_value_call_no_leak | PASS | 8 |
| cancel_called_delay_and_restart_same_program | PASS | 17 |
| static_invalid_inactive_and_void_control_flow | PASS | 18 |
| define_call_and_mixed_function_control | PASS | 10 |
| suspended_clock_timeout_and_sink_exception | PASS | 14 |
| static_truth_facts_preserve_eager_calls | PASS | 18 |
| no_heap_multiple_continuations | PASS | 5 |

## stage28b_new

| Exact test group | Result | Assertions |
|---|---|---:|
| official_fixture_files | PASS | 14 |
| inline_commands_unchanged | PASS | 12 |
| empty_blank_adjacent | PASS | 24 |
| whitespace_preservation | PASS | 18 |
| source_endings_bom_eof | PASS | 33 |
| raw_commands_not_declarations | PASS | 24 |
| terminator_lookalikes_literal | PASS | 12 |
| malformed_structure_zero_events | PASS | 69 |
| forward_constants_boundaries_literal_hash | PASS | 24 |
| if_else_selection_and_inactive | PASS | 12 |
| while_zero_one_many | PASS | 18 |
| forward_nested_expression_function_blocks | PASS | 26 |
| source_line_arena_code_exact_limits | PASS | 46 |
| constant_expansion_exact_overflow_locations | PASS | 21 |
| compact_instruction_and_blank_metadata_limits | PASS | 13 |
| retry_character_and_enter_exactly_once | PASS | 7 |
| cancellation_at_every_output_boundary | PASS | 54 |
| stop_after_block_and_inactive_stop | PASS | 12 |
| sink_failure_exception_body_locations | PASS | 28 |
| reentrant_and_cancel_inside_callback | PASS | 13 |
| borrow_simultaneous_restart_revision | PASS | 17 |
| clock_wrap_stuck_tick_timeout_steps | PASS | 22 |
| one_attempt_per_tick_large_loop_text | PASS | 3274 |
| nested_structure_and_call_boundaries | PASS | 24 |
| bounded_seeded_block_mutations | PASS | 911 |
| no_heap_block_and_suspended_expressions | PASS | 5 |

Initial new forward-DEFINE test FAIL: expected WORD! to expand a bare label despite its punctuation.
The expectation was corrected to WORD! literal, consistent with prior passing boundary tests.
No caps, sanitizer requirements, historical expectations or production rules were weakened.
The full final new suite was executed after extending function/control-flow cases.
